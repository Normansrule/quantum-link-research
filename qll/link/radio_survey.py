"""A LoRa range walk, measured: the hardware log that checks the off-grid mesh model (qll/link/mesh_messenger.py)
against two real radios.

The experiment (experiments/protocols/P16_lora_range_walk.md)
-------------------------------------------------------------
One board sends a numbered packet every few seconds (Meshtastic's Range Test module); the other, plugged into a
laptop, records each packet it hears with the received signal strength (RSSI) and signal-to-noise ratio (SNR) the
radio reports. The operator walks the receiver out to a list of stops and records the distance to each. The log
answers three questions the model only assumes: how fast the signal falls with distance here, how much the ground,
buildings, and trees take on top of free space, and how often a packet arrives at a given margin.

Log format
----------
One CSV row per packet the sender transmitted while the receiver stood at a stop:

    stop, distance_m, seq, received, rssi_dbm, snr_db

`received` is 1 or 0; `rssi_dbm` and `snr_db` are blank exactly when `received` is 0. A sidecar <file>.run.json holds
what the radios were set to (spreading factor, bandwidth, coding rate, frequency, transmit power, antenna gains and
heights, payload size) and the origin: "measured" (written by the operator or the logger in scripts/) or
"synthetic" (written by `simulate_survey`). Ingestion is strict, as in hardware_log.py: unknown or duplicate
columns, malformed numbers, a blank where a reading belongs, a reading on a lost packet, or a missing radio setting
are refused, never repaired. Each input's SHA-256 is recorded. A survey is labelled MEASURED HARDWARE only when its
sidecar says "measured"; anything this module wrote says "synthetic" and is labelled SIMULATED.

Physics
-------
The radio's packet RSSI is the power of signal plus noise in the channel, so the signal alone is

    S = RSSI + SNR - 10 log10(1 + 10^(SNR/10))          (dB; SNR is negative below the noise floor) [semtech2013sx1276]

which matters near the edge of coverage, where LoRa still decodes 7.5 to 20 dB below the noise. The model predicts
S = P_tx + G_tx + G_rx - L_cable - FSPL(d) - L_excess with the free-space path loss of mesh_messenger [friis1946].
The data are fitted with the log-distance law with log-normal shadowing,

    S(d) = S(d0) - 10 n log10(d / d0) + X_sigma,          d0 = 100 m [rappaport2002]

where n = 2 in free space and about 2.7 to 4 near the ground among buildings, and sigma is the spread from stop to
stop. The excess loss the mesh model assumes (20 dB by default) is estimated as the median of the free-space
prediction minus the measured signal. The packet delivery ratio at each stop carries a two-sided 95 % Clopper-Pearson
interval [clopper1934]. Presets are Meshtastic's published modem settings [meshtastic2026presets].
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy import stats

from qll.link import mesh_messenger as M

COLUMNS = ["stop", "distance_m", "seq", "received", "rssi_dbm", "snr_db"]
RUN_REQUIRED = ["origin", "sf", "bw_hz", "cr", "f_mhz", "tx_dbm", "tx_gain_dbi", "rx_gain_dbi", "tx_height_m",
                "rx_height_m", "payload_bytes"]
RUN_OPTIONAL = ["cable_loss_db", "noise_figure_db", "preset", "site", "date", "operator", "notes", "writer", "sender_interval_s"]
ORIGINS = ("measured", "synthetic")
# Meshtastic modem presets: spreading factor, bandwidth, coding rate index (1 = 4/5 ... 4 = 4/8) [meshtastic2026presets]
PRESETS = {"SHORT_FAST": (7, 250e3, 1), "SHORT_SLOW": (8, 250e3, 1), "MEDIUM_FAST": (9, 250e3, 1),
           "MEDIUM_SLOW": (10, 250e3, 1), "LONG_FAST": (11, 250e3, 1), "LONG_MODERATE": (11, 125e3, 4)}
D0_M = 100.0
LABELS = {"measured": "MEASURED HARDWARE", "synthetic": "SIMULATED"}
_NUM = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)")
_INT = re.compile(r"[+-]?[0-9]+")


@dataclass(frozen=True)
class Survey:
    run: dict
    stop: np.ndarray
    distance_m: np.ndarray
    seq: np.ndarray
    received: np.ndarray            # bool
    rssi_dbm: np.ndarray            # nan where not received
    snr_db: np.ndarray
    inputs: list


# ------------------------------------------------------------------------------------------------------ physics
def signal_dbm(rssi_dbm, snr_db):
    """Signal power from the packet RSSI (signal plus noise) and SNR."""
    rssi, snr = np.asarray(rssi_dbm, float), np.asarray(snr_db, float)
    return rssi + snr - 10 * np.log10(1 + 10 ** (snr / 10))


def noise_floor_dbm(bw_hz: float, noise_figure_db: float = 6.0) -> float:
    return -174.0 + 10 * math.log10(bw_hz) + noise_figure_db


def predicted_signal_dbm(run: dict, distance_m, excess_loss_db: float = 0.0):
    """The mesh model's received signal at each distance, with a given excess loss on top of free space."""
    d_km = np.asarray(distance_m, float) / 1000.0
    fspl = np.array([M.free_space_loss_db(float(x), run["f_mhz"]) for x in d_km.ravel()]).reshape(d_km.shape)
    return (run["tx_dbm"] + run["tx_gain_dbi"] + run["rx_gain_dbi"] - run.get("cable_loss_db", 0.0)) - fspl - excess_loss_db


def sensitivity_dbm(run: dict) -> float:
    return M.sensitivity_dbm(run["sf"], run["bw_hz"], run.get("noise_figure_db", 6.0))


def clopper_pearson(k: int, n: int, level: float = 0.95) -> tuple[float, float]:
    if n <= 0 or not 0 <= k <= n:
        raise ValueError("need 0 <= k <= n and n > 0")
    a = (1 - level) / 2
    lo = 0.0 if k == 0 else float(stats.beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(stats.beta.ppf(1 - a, k + 1, n - k))
    return lo, hi


# ---------------------------------------------------------------------------------------------------- ingestion
def _read_run(path: Path) -> dict:
    side = path.with_name(path.name + ".run.json")
    if not side.exists():
        raise ValueError(f"{path.name} has no {side.name}: the radio settings and origin are required")
    run = json.loads(side.read_text(encoding="utf-8"))
    if not isinstance(run, dict):
        raise ValueError(f"{side.name} must hold one JSON object")
    if "preset" in run and run["preset"] is not None:
        if run["preset"] not in PRESETS:
            raise ValueError(f"{side.name}: unknown preset {run['preset']!r}; give sf, bw_hz, and cr instead")
        sf, bw, cr = PRESETS[run["preset"]]
        for k, v in (("sf", sf), ("bw_hz", bw), ("cr", cr)):
            if k in run and run[k] != v:
                raise ValueError(f"{side.name}: {k}={run[k]} contradicts preset {run['preset']}")
            run.setdefault(k, v)
    unknown = sorted(set(run) - set(RUN_REQUIRED) - set(RUN_OPTIONAL))
    missing = [k for k in RUN_REQUIRED if k not in run]
    if unknown or missing:
        raise ValueError(f"{side.name}: unknown keys {unknown}, missing keys {missing}")
    if run["origin"] not in ORIGINS:
        raise ValueError(f"{side.name}: origin must be one of {ORIGINS}")
    for k in RUN_REQUIRED[1:] + [k for k in ("cable_loss_db", "noise_figure_db", "sender_interval_s") if k in run]:
        if isinstance(run[k], bool) or not isinstance(run[k], (int, float)) or not math.isfinite(run[k]):
            raise ValueError(f"{side.name}: {k} must be a number")
    if run["sf"] not in M.SNR_MIN_DB or run["cr"] not in (1, 2, 3, 4) or run["bw_hz"] <= 0 or run["f_mhz"] <= 0:
        raise ValueError(f"{side.name}: invalid LoRa settings")
    return run


def provenance(path: Path) -> dict:
    path = Path(path)
    side = path.with_name(path.name + ".run.json")
    return {"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "run_sha256": hashlib.sha256(side.read_bytes()).hexdigest() if side.exists() else None}


def read_survey(path: Path) -> Survey:
    path = Path(path)
    run = _read_run(path)
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        try:
            header = [h.strip() for h in next(reader)]
        except StopIteration:
            raise ValueError(f"{path.name} is empty") from None
        if header != COLUMNS:
            raise ValueError(f"{path.name}: header must be exactly {','.join(COLUMNS)}")
        for line, r in enumerate(reader, start=2):
            if not r:
                continue
            if len(r) != len(COLUMNS):
                raise ValueError(f"{path.name} line {line}: {len(r)} fields for {len(COLUMNS)} columns")
            v = [x.strip() for x in r]
            if not all(_INT.fullmatch(x) for x in (v[0], v[2], v[3])) or not _NUM.fullmatch(v[1]):
                raise ValueError(f"{path.name} line {line}: stop, seq, and received must be integers and distance a number")
            got = int(v[3])
            if got not in (0, 1):
                raise ValueError(f"{path.name} line {line}: received must be 0 or 1")
            if got:
                if not (_NUM.fullmatch(v[4]) and _NUM.fullmatch(v[5])):
                    raise ValueError(f"{path.name} line {line}: a received packet needs its RSSI and SNR")
                rssi, snr = float(v[4]), float(v[5])
            else:
                if v[4] or v[5]:
                    raise ValueError(f"{path.name} line {line}: a lost packet cannot have a reading")
                rssi = snr = math.nan
            d = float(v[1])
            if d <= 0:
                raise ValueError(f"{path.name} line {line}: distance must be positive")
            rows.append((int(v[0]), d, int(v[2]), got, rssi, snr))
    if not rows:
        raise ValueError(f"{path.name} has no rows")
    a = np.array(rows, dtype=float)
    stop, dist, seq = a[:, 0].astype(int), a[:, 1], a[:, 2].astype(int)
    for s in np.unique(stop):
        k = stop == s
        if np.unique(dist[k]).size != 1:
            raise ValueError(f"{path.name}: stop {s} has more than one distance")
        if np.unique(seq[k]).size != k.sum():
            raise ValueError(f"{path.name}: stop {s} repeats a sequence number")
    return Survey(run, stop, dist, seq, a[:, 3].astype(bool), a[:, 4], a[:, 5], [provenance(path) | {"origin": run["origin"]}])


def write_survey(path: Path, rows: list[tuple], run: dict) -> Path:
    """Write a survey and its sidecar; rows are (stop, distance_m, seq, received, rssi_dbm or None, snr_db or None)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        for s, d, q, got, rssi, snr in rows:
            w.writerow([s, f"{d:g}", q, int(got), "" if not got else f"{rssi:.1f}", "" if not got else f"{snr:.2f}"])
    path.with_name(path.name + ".run.json").write_text(json.dumps(run, indent=1), encoding="utf-8")
    return path


def append_stop(path: Path, rows: list[tuple], run: dict) -> Path:
    """Add one stop's rows to a survey, creating it (with its sidecar) on the first stop. The radio settings must not
    change within a survey and a stop number may be used once; both are refused rather than merged."""
    path = Path(path)
    if not path.exists():
        return write_survey(path, rows, run)
    old = read_survey(path)
    if {k: v for k, v in old.run.items() if k in RUN_REQUIRED} != {k: v for k, v in _with_preset(run).items() if k in RUN_REQUIRED}:
        raise ValueError("the radio settings differ from the survey's; start a new survey file")
    if set(old.stop) & {r[0] for r in rows}:
        raise ValueError("that stop number is already in the survey")
    with open(path, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        for s, d, q, got, rssi, snr in rows:
            w.writerow([s, f"{d:g}", q, int(got), "" if not got else f"{rssi:.1f}", "" if not got else f"{snr:.2f}"])
    return path


def _with_preset(run: dict) -> dict:
    run = dict(run)
    if run.get("preset") in PRESETS:
        for k, v in zip(("sf", "bw_hz", "cr"), PRESETS[run["preset"]]):
            run.setdefault(k, v)
    return run


def rows_from_heard(heard: list[tuple], stop: int, distance_m: float, expected: int) -> list[tuple]:
    """Turn the packets heard at one stop, as (seq, rssi_dbm, snr_db), into log rows with the losses filled in.

    Gaps in the sender's sequence numbers are losses. Packets lost before the first or after the last one heard
    cannot be numbered, so when fewer than `expected` packets are accounted for (expected = time at the stop divided by
    the sender's interval), the shortfall is appended as lost packets numbered after the last; that undercounts
    nothing and never invents a reception."""
    if expected < 0:
        raise ValueError("expected must be non-negative")
    by_seq = {}
    for q, rssi, snr in heard:
        by_seq.setdefault(int(q), (float(rssi), float(snr)))          # a duplicate (a relayed copy) counts once
    rows = []
    if by_seq:
        lo, hi = min(by_seq), max(by_seq)
        for q in range(lo, hi + 1):
            rows.append((stop, distance_m, q, 1, *by_seq[q]) if q in by_seq else (stop, distance_m, q, 0, None, None))
        nxt = hi + 1
    else:
        nxt = 0
    for i in range(max(expected - len(rows), 0)):
        rows.append((stop, distance_m, nxt + i, 0, None, None))
    return rows


_SEQ = re.compile(r"([0-9]+)")


def parse_packet(packet: dict, sender: str | None = None) -> tuple[int, float, float] | None:
    """(seq, rssi_dbm, snr_db) from one packet dictionary as the meshtastic Python library delivers it, or None when
    the packet is not a direct Range Test packet from the sender. Relayed copies (hop_start differs from hop_limit)
    are dropped: the survey measures one radio link, not the mesh."""
    dec = packet.get("decoded") or {}
    if dec.get("portnum") != "RANGE_TEST_APP":
        return None
    if sender is not None and packet.get("fromId") != sender:
        return None
    if "hopStart" in packet and packet.get("hopStart") != packet.get("hopLimit"):
        return None
    if "rxRssi" not in packet or "rxSnr" not in packet:
        return None
    text = dec.get("text")
    if text is None:
        raw = dec.get("payload", b"")
        text = raw.decode("utf-8", "replace") if isinstance(raw, (bytes, bytearray)) else str(raw)
    m = _SEQ.search(text)
    if m is None:
        return None
    return int(m.group(1)), float(packet["rxRssi"]), float(packet["rxSnr"])


# ------------------------------------------------------------------------------------------------------ analysis
def fitted_signal_dbm(fit: dict, distance_m):
    return fit["s_d0_dbm"] - 10 * fit["n"] * np.log10(np.asarray(distance_m, float) / fit["d0_m"])


def per_stop(s: Survey, excess_loss_db: float = 0.0, fit: dict | None = None) -> list[dict]:
    """Delivery and signal at each stop, beside a prediction: the mesh model with the given excess loss, or, when a
    fit is given, the fitted log-distance law."""
    sens = sensitivity_dbm(s.run)
    sig = signal_dbm(s.rssi_dbm, s.snr_db)
    out = []
    for st in np.unique(s.stop):
        k = s.stop == st
        n, got = int(k.sum()), int(s.received[k].sum())
        d = float(s.distance_m[k][0])
        lo, hi = clopper_pearson(got, n)
        pred = float(fitted_signal_dbm(fit, d) if fit else predicted_signal_dbm(s.run, [d], excess_loss_db)[0])
        out.append({"stop": int(st), "distance_m": d, "sent": n, "received": got, "pdr": got / n, "pdr_low": lo,
                    "pdr_high": hi,
                    "median_signal_dbm": float(np.median(sig[k & s.received])) if got else None,
                    "median_snr_db": float(np.median(s.snr_db[k & s.received])) if got else None,
                    "predicted_signal_dbm": pred, "predicted_margin_db": pred - sens})
    return out


def fit_log_distance(s: Survey) -> dict:
    """Least-squares fit of S = S(d0) - 10 n log10(d/d0) to every received packet; sigma is the residual spread."""
    k = s.received
    if np.unique(s.distance_m[k]).size < 2:
        raise ValueError("a fit needs packets received at two or more distances")
    x = -10 * np.log10(s.distance_m[k] / D0_M)
    y = signal_dbm(s.rssi_dbm[k], s.snr_db[k])
    A = np.column_stack([np.ones_like(x), x])
    (s0, n), *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - (s0 + n * x)
    sigma = float(np.sqrt(np.sum(resid ** 2) / max(len(y) - 2, 1)))
    return {"s_d0_dbm": float(s0), "d0_m": D0_M, "n": float(n), "sigma_db": sigma, "packets": int(k.sum()),
            "d_min_m": float(s.distance_m[k].min()), "d_max_m": float(s.distance_m[k].max())}


def excess_loss_db(s: Survey) -> float:
    """Median of the free-space prediction minus the measured signal: the value to give Mesh(excess_loss_db=...)."""
    k = s.received
    if not k.any():
        raise ValueError("no packet was received")
    return float(np.median(predicted_signal_dbm(s.run, s.distance_m[k]) - signal_dbm(s.rssi_dbm[k], s.snr_db[k])))


def range_for_margin_m(fit: dict, sensitivity: float, margin_db: float = 10.0) -> float:
    """Distance at which the fitted signal falls to sensitivity + margin (an extrapolation beyond d_max_m)."""
    return fit["d0_m"] * 10 ** ((fit["s_d0_dbm"] - sensitivity - margin_db) / (10 * fit["n"]))


def agrees(row: dict, margin_db: float = 10.0) -> bool:
    """Does one stop agree with the mesh model's link rule (a link exists when the margin is at least margin_db)?

    The model says yes or no; the measurement says how often a packet arrived, with an interval. The stop agrees when
    the model's yes is not contradicted (the interval reaches 90 % delivery) and its no is not contradicted (the
    interval reaches below 50 %). Stops whose interval sits between are counted as agreeing, because too few packets
    were sent to tell; send more packets per stop to make the test sharper."""
    if row["predicted_margin_db"] >= margin_db:
        return row["pdr_high"] >= 0.9
    return row["pdr_low"] < 0.5


def report(path: Path, margin_db: float = 10.0) -> dict:
    s = read_survey(path)
    fit = fit_log_distance(s)
    excess = excess_loss_db(s)
    sens = sensitivity_dbm(s.run)
    rows_default = per_stop(s, M.Mesh({}).excess_loss_db)
    rows_fitted = per_stop(s, fit=fit)
    return {
        "label": LABELS[s.run["origin"]], "inputs": s.inputs, "run": s.run, "sensitivity_dbm": sens,
        "fit": fit, "excess_loss_db": excess, "model_default_excess_loss_db": M.Mesh({}).excess_loss_db,
        "range_at_margin_m": range_for_margin_m(fit, sens, margin_db), "margin_db": margin_db,
        "stops": rows_fitted,
        "agreement_default_model": sum(agrees(r, margin_db) for r in rows_default) / len(rows_default),
        "agreement_fitted_model": sum(agrees(r, margin_db) for r in rows_fitted) / len(rows_fitted),
    }


# ------------------------------------------------------------------------------------------------------ synthetic
def default_run(**over) -> dict:
    run = {"origin": "synthetic", "preset": "LONG_FAST", "sf": 11, "bw_hz": 250e3, "cr": 1, "f_mhz": 906.875,
           "tx_dbm": 20.0, "tx_gain_dbi": 2.0, "rx_gain_dbi": 2.0, "tx_height_m": 1.5, "rx_height_m": 1.5,
           "payload_bytes": 16, "cable_loss_db": 0.0, "noise_figure_db": 6.0, "sender_interval_s": 30.0,
           "writer": "qll.link.radio_survey.simulate_survey", "notes": "simulated record; never measured evidence"}
    run.update(over)
    return run


def simulate_survey(path: Path, distances_m=(50, 100, 200, 400, 800, 1200, 1600, 2000, 2400, 3200), packets: int = 20,
                    n: float = 3.5, s_d0_dbm: float | None = None, shadow_sigma_db: float = 4.0,
                    fade_sigma_db: float = 2.0, seed: int = 0, **run_over) -> Path:
    """Write a synthetic range walk drawn from the log-distance law, with per-stop shadowing and per-packet fading;
    a packet arrives when its signal clears the sensitivity. Labelled synthetic, so never reported as measured."""
    run = default_run(**run_over)
    run["origin"] = "synthetic"
    rng = np.random.default_rng(seed)
    if s_d0_dbm is None:
        s_d0_dbm = float(predicted_signal_dbm(run, [D0_M])[0]) - 25.0       # 25 dB of clutter already at 100 m
    sens = sensitivity_dbm(run)
    floor = noise_floor_dbm(run["bw_hz"], run["noise_figure_db"])
    rows, q = [], 0
    for i, d in enumerate(distances_m):
        shadow = rng.normal(0, shadow_sigma_db)
        for _ in range(packets):
            s = s_d0_dbm - 10 * n * math.log10(d / D0_M) + shadow + rng.normal(0, fade_sigma_db)
            if s >= sens:
                snr = round((s - floor) * 4) / 4                                 # SX127x reports SNR in 0.25 dB steps
                rssi = 10 * math.log10(10 ** (s / 10) + 10 ** (floor / 10))
                rows.append((i, float(d), q, 1, round(rssi, 1), snr))
            else:
                rows.append((i, float(d), q, 0, None, None))
            q += 1
    return write_survey(path, rows, run)


# ------------------------------------------------------------------------------------------------------------ CLI
def _print_report(r: dict) -> None:
    f = r["fit"]
    print(f"{r['label']}  ({', '.join(i['file'] + ' sha256 ' + i['sha256'][:12] for i in r['inputs'])})")
    print(f"radio: SF{r['run']['sf']}, {r['run']['bw_hz'] / 1e3:g} kHz, {r['run']['tx_dbm']:g} dBm; "
          f"sensitivity {r['sensitivity_dbm']:.1f} dBm")
    print(f"fit: S(100 m) = {f['s_d0_dbm']:.1f} dBm, path-loss exponent n = {f['n']:.2f}, spread {f['sigma_db']:.1f} dB "
          f"({f['packets']} packets, {f['d_min_m']:g} to {f['d_max_m']:g} m)")
    print(f"excess loss over free space: {r['excess_loss_db']:.1f} dB (the model assumes {r['model_default_excess_loss_db']:g} dB)")
    print(f"range at {r['margin_db']:g} dB margin from the fit: {r['range_at_margin_m']:.0f} m"
          + ("  (extrapolated)" if r["range_at_margin_m"] > f["d_max_m"] else ""))
    print("stop  distance_m  received  PDR [95 % interval]   signal_dBm  fit_dBm  margin_dB")
    for s in r["stops"]:
        sig = f"{s['median_signal_dbm']:.1f}" if s["median_signal_dbm"] is not None else "-"
        print(f"{s['stop']:>4}  {s['distance_m']:>10g}  {s['received']:>3}/{s['sent']:<4}  {s['pdr']:.2f} "
              f"[{s['pdr_low']:.2f}, {s['pdr_high']:.2f}]   {sig:>10}  {s['predicted_signal_dbm']:>9.1f}  "
              f"{s['predicted_margin_db']:>9.1f}")
    print(f"stops agreeing with the link rule: {r['agreement_default_model']:.0%} with the default excess loss, "
          f"{r['agreement_fitted_model']:.0%} with the fitted law")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m qll.link.radio_survey", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    rp = sub.add_parser("report", help="analyse a survey log")
    rp.add_argument("log", type=Path)
    rp.add_argument("--json", action="store_true")
    rp.add_argument("--margin-db", type=float, default=10.0)
    sp = sub.add_parser("simulate", help="write a synthetic survey (labelled synthetic)")
    sp.add_argument("out", type=Path)
    sp.add_argument("--seed", type=int, default=0)
    a = p.parse_args(argv)
    if a.cmd == "simulate":
        print(simulate_survey(a.out, seed=a.seed))
        return 0
    try:
        r = report(a.log, a.margin_db)
    except (ValueError, OSError, json.JSONDecodeError) as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(r, indent=1))
    else:
        _print_report(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
