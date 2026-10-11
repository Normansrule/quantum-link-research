"""Run the free cloud-processor milestones of mission Phase 4: teleportation with feed-forward (M4.1) and superdense
coding (M4.2), each with its control. Writes one JSON per run with the configuration, the counts, and the verdict.

    python experiments/bench/frontier/run_frontier.py teleport --backend aer
    python experiments/bench/frontier/run_frontier.py teleport --backend fake_torino --layout 0 1 2
    python experiments/bench/frontier/run_frontier.py superdense --backend ibm_torino --layout 0 1
    python experiments/bench/frontier/run_frontier.py majorana --backend aer                       # M4.6, protocol P13
    python experiments/bench/frontier/run_frontier.py delay --backend aer --T1 200 --T2 150        # M4.3, proposal E01
    python experiments/bench/frontier/run_frontier.py chain --backend aer --hops 1 2 3              # M4.8, proposal E20
    python experiments/bench/frontier/run_frontier.py analyze results/*.json

`aer` is the ideal simulator (add --noise 0.05 for a depolarized pair); `fake_<name>` a noisy local copy of a
device; any other name a real device through a saved IBM Quantum account. Teleportation runs all three modes
(feed-forward, deferred, no bits); on a device without feed-forward the feed-forward mode is skipped and recorded.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from qll.circuits import cloud_run as R  # noqa: E402
from qll.circuits import majorana_chain as CH  # noqa: E402
from qll.circuits import majorana_cloud as MC  # noqa: E402
from qll.circuits import superdense_cloud as S  # noqa: E402
from qll.circuits import teleport_cloud as T  # noqa: E402
from qll.circuits import teleport_delay_cloud as TD  # noqa: E402


def _run(a, circuits):
    if a.backend == "aer":
        nm = T.noise_model_depolarizing(a.noise) if a.noise else None
        return R.run_aer(circuits, a.shots, a.seed, nm, "density_matrix" if nm else "automatic")
    return R.run_backend(R.get_backend(a.backend), circuits, a.shots, a.layout, a.seed)


def _save(a, kind, payload) -> Path:
    utc = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    rec = {"experiment": kind, "utc": utc, "backend": a.backend, "layout": a.layout, "shots_per_circuit": a.shots,
           "noise_injected": a.noise, "seed": a.seed, **payload}
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    path = out / f"{kind.split()[0]}_{a.backend}_{utc.replace(':', '')}.json"
    path.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(f"wrote {path}")
    return path


def cmd_teleport(a) -> Path:
    ff = a.backend == "aer" or R.supports_feedforward(R.get_backend(a.backend))
    runs = {}
    for mode in T.MODES:
        if mode == "feedforward" and not ff:
            runs[mode] = {"skipped": "backend has no feed-forward"}
            continue
        counts = _run(a, T.circuits(mode))
        v = T.analyze(counts, mode)
        runs[mode] = {"counts": counts, "verdict": v.row()}
        print(f"{mode:>12}: average fidelity {v.average:.4f} [{v.interval[0]:.4f}, {v.interval[1]:.4f}]"
              f"{'  above the classical 2/3' if v.beats_classical else ''}")
    return _save(a, "teleport (M4.1)", {"states": list(T.CARDINAL), "runs": runs})


def cmd_majorana(a) -> Path:
    ff = a.backend == "aer" or R.supports_feedforward(R.get_backend(a.backend))
    runs = {}
    for mode in MC.MODES:
        if mode != "no_bits" and not ff:
            runs[mode] = {"skipped": "backend has no feed-forward"}
            continue
        counts = _run(a, MC.circuits(mode))
        v = T.analyze(counts, mode)
        runs[mode] = {"counts": counts, "verdict": v.row(), "expected_ideal": MC.EXPECTED[mode]}
        print(f"{mode:>14}: average fidelity {v.average:.4f} [{v.interval[0]:.4f}, {v.interval[1]:.4f}] (ideal {MC.EXPECTED[mode]:.3f})")
    return _save(a, "majorana (M4.6)", {"states": list(T.CARDINAL), "runs": runs})


def cmd_superdense(a) -> Path:
    runs = {}
    for mode in S.MODES:
        counts = _run(a, S.circuits(mode))
        v = S.analyze(counts, mode)
        runs[mode] = {"counts": counts, "verdict": v.row(), "confusion": v.confusion.tolist()}
        print(f"{mode:>12}: success {v.success:.4f}, {v.bits_per_use:.3f} bits per use")
    return _save(a, "superdense (M4.2)", {"messages": [list(m) for m in S.MESSAGES], "runs": runs})


def cmd_delay(a) -> Path:
    """Teleportation with Bob's qubit idle before the corrections (E01's cheapest version, M4.3). On the simulator the
    idle is a thermal-relaxation map with --T1 and --T2; on a device it is a real delay, so the device's own qubit does
    the decaying, and the fitted crossover is compared with the calibrated T1 and T2 recorded in the file."""
    delays = a.delays or TD.sweep_delays_us(a.T2)
    hardware = a.backend != "aer"
    if a.shots is None:                       # Aer's sampling of a Kraus map before feed-forward settles to the model only past ~20,000 shots
        a.shots = 4000 if hardware else 20000
    if hardware and a.layout:                 # the device's calibrated T1 and T2 for Bob's qubit replace the defaults
        qp = R.get_backend(a.backend).qubit_properties(a.layout[2])
        if qp is not None and qp.t1 and qp.t2:
            a.T1, a.T2 = qp.t1 * 1e6, min(qp.t2, 2 * qp.t1) * 1e6
            print(f"Bob's qubit {a.layout[2]}: T1 = {a.T1:.0f} µs, T2 = {a.T2:.0f} µs (calibration)")
    runs, k = {}, None
    for d in delays:
        counts = _run(a, TD.circuits(d, "feedforward", "hardware" if hardware else "emulated", T1_us=a.T1, T2_us=a.T2))
        v = T.analyze(counts, "feedforward")
        if hardware and d == 0:
            k = 2 * (v.average - 0.5)          # gate and readout errors, measured at zero delay
        expect = TD.with_offset(d, a.T1, a.T2, k) if k is not None else TD.average_fidelity(d, a.T1, a.T2, a.noise)
        runs[f"{d:g}us"] = {"delay_us": d, "counts": counts, "verdict": v.row(), "expected": expect}
        print(f"{d:>8.1f} µs: F = {v.average:.4f} [{v.interval[0]:.4f}, {v.interval[1]:.4f}]  (model {expect:.4f}){'  above 2/3' if v.beats_classical else ''}")
    control = T.analyze(_run(a, TD.circuits(delays[-1], "no_bits", "hardware" if hardware else "emulated", T1_us=a.T1, T2_us=a.T2)), "no_bits")
    print(f"no bits at {delays[-1]:g} µs: F = {control.average:.4f} (must be 1/2)")
    return _save(a, "delay (M4.3)", {"states": list(T.CARDINAL), "T1_us": a.T1, "T2_us": a.T2, "zero_delay_shrink_k": k, "crossover_model_us": TD.crossover_delay_us(a.T1, a.T2, a.noise),
                                     "runs": runs, "no_bits": {"delay_us": delays[-1], "verdict": control.row()}})


def cmd_chain(a) -> Path:
    """Majorana parity teleportation along 1..N hops (E20, M4.8) on 2N + 1 qubits in a line, with the no-bits control at
    the longest length. The per-hop Bloch shrink is fitted from F_N = (1 + s^N)/2 over the lengths run."""
    runs, fs, line = {}, [], a.layout
    for n in a.hops:
        a.layout = line[:2 * n + 1] if line else None              # the first 2N + 1 qubits of the line
        counts = _run(a, CH.circuits(n))
        v = T.analyze(counts, "two_bit")
        runs[f"{n}"] = {"hops": n, "counts": counts, "verdict": v.row(), "expected_with_noise": CH.expected_fidelity(n, a.noise)}
        fs.append((n, v.average))
        print(f"{n} hop{'s' if n > 1 else ' '}: F = {v.average:.4f} [{v.interval[0]:.4f}, {v.interval[1]:.4f}]{'  above 2/3' if v.beats_classical else ''}")
    pts = [(n, f) for n, f in fs if f > 0.5]
    fit = np.polyfit([n for n, _ in pts], [np.log(2 * f - 1) for _, f in pts], 1) if len(pts) >= 2 else None   # ln(2F - 1) = ln k + N ln s
    shrink, offset = (float(np.exp(fit[0])), float(np.exp(fit[1]))) if fit is not None else (None, None)
    control = T.analyze(_run(a, CH.circuits(a.hops[-1], "no_bits")), "no_bits")
    a.layout = line
    print(f"no bits at {a.hops[-1]} hops: F = {control.average:.4f} (must be 1/2)")
    if shrink:
        print(f"fitted shrink per hop s = {shrink:.4f}, offset k = {offset:.4f}: the chain stays above 2/3 for up to {CH.max_hops(shrink, offset)} hops")
    return _save(a, "chain (M4.8)", {"states": list(T.CARDINAL), "runs": runs, "shrink_per_hop": shrink, "offset_k": offset,
                                     "max_hops_above_two_thirds": CH.max_hops(shrink, offset) if shrink else None, "no_bits": {"hops": a.hops[-1], "verdict": control.row()}})


def cmd_analyze(a) -> None:
    for f in a.files:
        rec = json.loads(Path(f).read_text(encoding="utf-8"))
        for mode, r in rec["runs"].items():
            if "skipped" in r:
                print(f"{Path(f).name} {mode}: skipped ({r['skipped']})"); continue
            if rec["experiment"].startswith("chain"):
                v = T.analyze(r["counts"], "two_bit")
                print(f"{Path(f).name} {mode} hops: F = {v.average:.4f} [{v.interval[0]:.4f}, {v.interval[1]:.4f}]")
            elif rec["experiment"].startswith("delay"):
                v = T.analyze(r["counts"], "feedforward")
                print(f"{Path(f).name} {mode}: F = {v.average:.4f} [{v.interval[0]:.4f}, {v.interval[1]:.4f}] (model {r['expected']:.4f})")
            elif rec["experiment"].startswith(("teleport", "majorana")):
                v = T.analyze(r["counts"], mode)
                print(f"{Path(f).name} {mode}: F = {v.average:.4f} [{v.interval[0]:.4f}, {v.interval[1]:.4f}]")
            else:
                v = S.analyze(r["counts"], mode)
                print(f"{Path(f).name} {mode}: success {v.success:.4f}, {v.bits_per_use:.3f} bits per use")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("teleport", "superdense", "majorana"):
        p = sub.add_parser(name)
        p.add_argument("--backend", default="aer"); p.add_argument("--shots", type=int, default=4000)
        p.add_argument("--layout", type=int, nargs="+", default=None); p.add_argument("--noise", type=float, default=0.0)
        p.add_argument("--seed", type=int, default=0); p.add_argument("--out", default="results")
    d = sub.add_parser("delay")
    d.add_argument("--backend", default="aer"); d.add_argument("--shots", type=int, default=None)
    d.add_argument("--layout", type=int, nargs="+", default=None); d.add_argument("--noise", type=float, default=0.0)
    d.add_argument("--seed", type=int, default=0); d.add_argument("--out", default="results")
    d.add_argument("--T1", type=float, default=TD.T1_DEFAULT_US, help="µs; the device's calibrated value for Bob's qubit on hardware")
    d.add_argument("--T2", type=float, default=TD.T2_DEFAULT_US, help="µs")
    d.add_argument("--delays", type=float, nargs="+", default=None, help="µs; default six from 0 to 2 T2")
    ch = sub.add_parser("chain")
    ch.add_argument("--backend", default="aer"); ch.add_argument("--shots", type=int, default=4000)
    ch.add_argument("--layout", type=int, nargs="+", default=None); ch.add_argument("--noise", type=float, default=0.0)
    ch.add_argument("--seed", type=int, default=0); ch.add_argument("--out", default="results")
    ch.add_argument("--hops", type=int, nargs="+", default=[1, 2, 3], help="chain lengths; N hops use 2N + 1 qubits in a line")
    z = sub.add_parser("analyze"); z.add_argument("files", nargs="+")
    a = ap.parse_args(argv)
    return {"teleport": cmd_teleport, "superdense": cmd_superdense, "majorana": cmd_majorana, "delay": cmd_delay, "chain": cmd_chain, "analyze": cmd_analyze}[a.cmd](a)


if __name__ == "__main__":
    main()
