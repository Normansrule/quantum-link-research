"""python -m qll.analysis.bench_report {predict,synthetic,schedule,report} ...: the tabletop Mars-link bench (P09).

  predict  [--config bench.json]                    what every stage should measure with your parts
  synthetic --out DIR [--seed N]                     a complete fake data set, so the pipeline runs before the bench
  schedule --out FILE [--steps 780]                  the attenuation steps that compress a synodic period into a run
  report   DIR [--save FIG.svg]                      fit every stage found in DIR and compare it with the twin

Data files in DIR (any subset; signal columns in consistent units within a file, dark readings subtracted here):
  bench.json       overrides of BenchDesign fields (your measured parts)
  calibration.csv  photocurrent_a
  phase.csv        phase_deg, signal, dark                       (watts, for an albedo; any unit for the shape)
  etendue.csv      fiber, distance_m, filter_nm, signal, dark
  rejection.csv    fiber, theta_rad, signal, dark
  purity.csv       fiber, placement, offset_radii, phase_deg, signal_only, background_only
  errors.csv       purity, right, wrong
  run.csv          step, extra_od, signal, background, right, wrong, seconds   (signal and background in photons/s)
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, fields, replace
from pathlib import Path

import numpy as np

from qll.analysis.bench_fit import fit_error_fraction, fit_phase, fit_rejection, loglog_slope
from qll.app.key_bank import sequent_peak, simulate
from qll.channels.planetshine import lambert_phase
from qll.systems.bench_twin import (BenchDesign, background_power_w, ball_flux_w, error_fraction, field_of_view_rad,
                                    in_logged_unit, irradiance_from_photocurrent, key_fraction, mars_schedule, mode_ratio,
                                    photon_energy_j, purity, rejection, signal_power_w, surface_power_w)

PLACEMENTS = (("day", 0.0, 0.0), ("night", 0.0, 0.0), ("space", 3.0, 0.0), ("space", 10.0, 0.0))
TRUE_FOR_SYNTHETIC = {"albedo": 0.85, "stray_light": 3e-6, "e_opt": 0.03, "lamp_irradiance_nm": 0.25}


def load_design(path: Path | None) -> BenchDesign:
    if path is None or not Path(path).exists():
        return BenchDesign()
    over = json.loads(Path(path).read_text(encoding="utf-8"))
    names = {f.name for f in fields(BenchDesign)}
    return replace(BenchDesign(), **{k: v for k, v in over.items() if k in names})


def _read(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write(path: Path, header: list[str], rows: list[list]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


# predict -----------------------------------------------------------------------------------------------------------
def predictions(b: BenchDesign) -> dict:
    out = {
        "ball_angular_radius_mrad": 1e3 * b.ball_diameter_m / 2 / b.distance_m,
        "fov_smf_mrad": 1e3 * field_of_view_rad(b, "smf"), "fov_mmf_mrad": 1e3 * field_of_view_rad(b, "mmf"),
        "phase_full_w": ball_flux_w(b, 0.0, b.phase_distance_m), "phase_90_w": ball_flux_w(b, math.pi / 2, b.phase_distance_m),
        "surface_smf_w": surface_power_w(b, "smf"), "surface_mmf_w": surface_power_w(b, "mmf"),
        "surface_smf_photons_s": surface_power_w(b, "smf") / photon_energy_j(b), "mode_ratio": mode_ratio(b),
        "signal_w": signal_power_w(b, "mmf"), "purity": {},
    }
    for fiber in ("smf", "mmf"):
        for place, off, ph in PLACEMENTS:
            N = background_power_w(b, fiber, place, ph, off)
            out["purity"][f"{fiber} {place}{'' if place != 'space' else f' {off:g} radii'}"] = purity(signal_power_w(b, fiber), N)
    return out


def print_predictions(b: BenchDesign) -> None:
    p = predictions(b)
    print(f"ball angular radius   {p['ball_angular_radius_mrad']:.2f} mrad  (receiver fields: SMF {p['fov_smf_mrad']:.3f}, MMF {p['fov_mmf_mrad']:.2f} mrad; the ball is resolved)")
    print(f"Stage 1 calibration   {b.lamp_irradiance_nm * b.responsivity_a_per_w * b.detector_area_m2 * b.filter_nm:.3g} A photocurrent from the filtered photodiode at the ball")
    print(f"Stage 2 phase curve   {p['phase_full_w']:.3g} W at full phase, {p['phase_90_w']:.3g} W at 90 degrees (bare photodiode at {b.phase_distance_m:g} m)")
    print(f"Stage 3 lit card      SMF {p['surface_smf_w']:.3g} W ({p['surface_smf_photons_s']:.3g} photons/s: needs a photon counter), "
          f"MMF {p['surface_mmf_w']:.3g} W; ratio {p['mode_ratio']:.0f}")
    print(f"Stage 5 signal        {p['signal_w']:.3g} W at OD {b.tx_od:g}")
    for k, w in p["purity"].items():
        print(f"        purity        {k:<18s} {w:.4f}")
    print(f"Stage 6 error         e = w {b.e_opt:g} + (1 - w)/2; key fraction {key_fraction(b.e_opt):.3f} at w = 1")


# synthetic ---------------------------------------------------------------------------------------------------------
def write_synthetic(out: Path, seed: int = 1) -> BenchDesign:
    """A full data set from a 'true' bench that differs from the defaults, with 2 % noise, so a report must fit."""
    rng = np.random.default_rng(seed)
    truth = replace(BenchDesign(), **TRUE_FOR_SYNTHETIC)
    noisy = lambda x: float(x * (1 + 0.02 * rng.standard_normal()))
    out.mkdir(parents=True, exist_ok=True)
    (out / "bench.json").write_text(json.dumps({"_note": "synthetic data from qll.analysis.bench_report synthetic",
                                                "lamp_irradiance_nm": 0.2, "albedo": 0.9}, indent=1), encoding="utf-8")
    I = truth.lamp_irradiance_nm * truth.responsivity_a_per_w * truth.detector_area_m2 * truth.filter_nm
    _write(out / "calibration.csv", ["photocurrent_a"], [[noisy(I)] for _ in range(5)])
    _write(out / "phase.csv", ["phase_deg", "signal", "dark"],
           [[a, noisy(ball_flux_w(truth, math.radians(a), truth.phase_distance_m)) + 1e-12, 1e-12] for a in range(0, 151, 10)])
    rows = []
    for fiber in ("smf", "mmf"):
        for dist in (0.3, 0.5, 0.8, 1.2):
            rows.append([fiber, dist, 10.0, noisy(surface_power_w(truth, fiber)), 0.0])
        for fw in (3.0, 10.0, 40.0):
            rows.append([fiber, 0.5, fw, noisy(surface_power_w(truth, fiber, filter_nm=fw)), 0.0])
    _write(out / "etendue.csv", ["fiber", "distance_m", "filter_nm", "signal", "dark"], rows)
    rows = []
    for fiber in ("smf", "mmf"):
        for th in np.r_[0.0, np.linspace(2e-5, 6e-4, 12), np.linspace(1e-3, 3e-3, 5), np.geomspace(5e-3, 5e-2, 6)]:
            rows.append([fiber, th, noisy(rejection(truth, th, fiber)), 0.0])
    _write(out / "rejection.csv", ["fiber", "theta_rad", "signal", "dark"], rows)
    rows = []
    for fiber in ("smf", "mmf"):
        for place, off, ph in PLACEMENTS:
            rows.append([fiber, place, off, ph, noisy(signal_power_w(truth, fiber)), noisy(background_power_w(truth, fiber, place, ph, off))])
    _write(out / "purity.csv", ["fiber", "placement", "offset_radii", "phase_deg", "signal_only", "background_only"], rows)
    rows = []
    for w in np.linspace(0.3, 1.0, 12):
        n = 1e6
        e = error_fraction(w, truth.e_opt)
        rows.append([w, int(rng.binomial(n, 1 - e)), 0])
        rows[-1][2] = int(n - rows[-1][1])
    _write(out / "errors.csv", ["purity", "right", "wrong"], rows)
    sched = _schedule(60)
    E, S0, N = photon_energy_j(truth), signal_power_w(truth, "mmf"), background_power_w(truth, "mmf", "space", 0.0, 6.0)
    rows = []
    for i, od in enumerate(sched):
        S = 0.0 if not np.isfinite(od) else S0 * 10 ** (-od)
        e = error_fraction(purity(S, N), truth.e_opt)
        tot = (S + N) / E * 0.3 * 5.0
        right = int(rng.binomial(int(tot), 1 - e)) if S > 0 else 0
        rows.append([i, "inf" if not np.isfinite(od) else od, S / E, N / E, right, int(tot) - right if S > 0 else 0, 5.0])
    _write(out / "run.csv", ["step", "extra_od", "signal", "background", "right", "wrong", "seconds"], rows)
    return truth


# schedule ----------------------------------------------------------------------------------------------------------
def _schedule(steps: int) -> np.ndarray:
    from qll.systems.mars_budget import MarsLinkDesign, budget
    days = np.linspace(0.0, 779.0, steps)
    rel = np.array([budget(MarsLinkDesign(), float(t)).pairs_per_day for t in days])
    return mars_schedule(rel)


# report ------------------------------------------------------------------------------------------------------------
def report(folder: Path, save: str | None = None, quiet: bool = False) -> dict:
    folder = Path(folder)
    b = load_design(folder / "bench.json")
    res: dict = {}
    say = (lambda *a: None) if quiet else print
    if (folder / "calibration.csv").exists():
        I = float(np.mean([float(r["photocurrent_a"]) for r in _read(folder / "calibration.csv")]))
        b = replace(b, lamp_irradiance_nm=irradiance_from_photocurrent(b, I))
        res["lamp_irradiance_nm"] = b.lamp_irradiance_nm
        say(f"Stage 1  lamp irradiance       {b.lamp_irradiance_nm:.4g} W m^-2 nm^-1 at the ball (used below)")
    if (folder / "phase.csv").exists():
        rows = _read(folder / "phase.csv")
        a = np.radians([float(r["phase_deg"]) for r in rows])
        P = np.array([float(r["signal"]) - float(r["dark"]) for r in rows])
        fit = fit_phase(a, P)
        res.update(phase_rms=fit.rms_relative, phase=(a, P, fit.scale))
        msg = ""
        if b.signal_unit == "watts":
            A = 1.5 * fit.scale / (b.lamp_irradiance_nm * b.filter_nm * (b.ball_diameter_m / 2 / b.phase_distance_m) ** 2 * b.detector_area_m2)
            b = replace(b, albedo=A)
            res["albedo"] = A
            msg = f"; albedo {A:.3f}"
        say(f"Stage 2  Lambert phase curve   residual {100 * fit.rms_relative:.1f} % of peak (pass < 5 %): "
            f"{'PASS' if fit.rms_relative < 0.05 else 'CHECK'}{msg}")
    if (folder / "etendue.csv").exists():
        rows = _read(folder / "etendue.csv")
        for fiber in ("smf", "mmf"):
            R = [r for r in rows if r["fiber"] == fiber]
            base = [r for r in R if float(r["filter_nm"]) == b.filter_nm]
            fw = [r for r in R if float(r["distance_m"]) == float(R[0]["distance_m"])] if R else []
            if len(base) >= 2:
                s = loglog_slope([float(r["distance_m"]) for r in base], [float(r["signal"]) - float(r["dark"]) for r in base])
                res[f"distance_slope_{fiber}"] = s
                say(f"Stage 3  {fiber} vs distance        slope {s:+.3f} (radiance conserved: 0 ± 0.1): {'PASS' if abs(s) < 0.1 else 'CHECK'}")
            fws = sorted({float(r["filter_nm"]) for r in R})
            if len(fws) >= 2:
                pts = [(float(r["filter_nm"]), float(r["signal"]) - float(r["dark"])) for r in R if float(r["distance_m"]) == 0.5]
                if len({x for x, _ in pts}) >= 2:
                    s = loglog_slope([x for x, _ in pts], [y for _, y in pts])
                    res[f"filter_slope_{fiber}"] = s
                    say(f"Stage 3  {fiber} vs filter width    slope {s:+.3f} (1 ± 0.15): {'PASS' if abs(s - 1) < 0.15 else 'CHECK'}")
        sm = [float(r["signal"]) - float(r["dark"]) for r in rows if r["fiber"] == "smf"]
        mm = [float(r["signal"]) - float(r["dark"]) for r in rows if r["fiber"] == "mmf"]
        if sm and mm:
            ratio = float(np.median(mm) / np.median(sm))
            res["mode_ratio"] = ratio
            say(f"Stage 3  MMF / SMF             {ratio:.0f} measured, {mode_ratio(b):.0f} predicted from G / lambda^2 "
                f"(within a factor 2): {'PASS' if 0.5 < ratio / mode_ratio(b) < 2 else 'CHECK'}")
    if (folder / "rejection.csv").exists():
        rows = _read(folder / "rejection.csv")
        for fiber in ("smf", "mmf"):
            R = [r for r in rows if r["fiber"] == fiber]
            if len(R) < 4:
                continue
            th = np.array([float(r["theta_rad"]) for r in R])
            P = np.array([float(r["signal"]) - float(r["dark"]) for r in R])
            fit = fit_rejection(th, P, fiber, far_rad=10 * field_of_view_rad(b, fiber))
            want = field_of_view_rad(b, fiber)
            res[f"mode_{fiber}"], res[f"floor_{fiber}"] = fit.mode_rad, fit.floor
            res.setdefault("rejection", {})[fiber] = (th, P / P[np.argmin(np.abs(th))])
            say(f"Stage 4  {fiber} rejection         field {1e3 * fit.mode_rad:.3f} mrad (predicted {1e3 * want:.3f}); "
                f"stray floor {fit.floor:.2g}: {'PASS' if 0.7 < fit.mode_rad / want < 1.3 else 'CHECK'}")
        floors = [res[k] for k in ("floor_smf", "floor_mmf") if k in res]
        if floors:
            b = replace(b, stray_light=float(np.median(floors)))
    if (folder / "purity.csv").exists():
        say("Stage 5  herald purity         measured   twin    background measured / twin  (twin: your measured signal,")
        say("                                                   and the fitted lamp, albedo, and floor)")
        res["purity"] = {}
        for r in _read(folder / "purity.csv"):
            S, N = float(r["signal_only"]), float(r["background_only"])
            w_meas = purity(S, N)
            place, off, ph = r["placement"], float(r["offset_radii"]), math.radians(float(r["phase_deg"]))
            N_twin = in_logged_unit(b, background_power_w(b, r["fiber"], place, ph, off))
            w_twin = purity(S, N_twin)
            label = f"{r['fiber']} {place}" + (f" {off:g} radii" if place == "space" else "")
            res["purity"][label] = (w_meas, w_twin)
            say(f"         {label:<20s}  {w_meas:8.4f}  {w_twin:8.4f}   {N / N_twin if N_twin > 0 else float('nan'):8.2f}")
    if (folder / "errors.csv").exists():
        rows = _read(folder / "errors.csv")
        w = np.array([float(r["purity"]) for r in rows])
        e = np.array([float(r["wrong"]) / (float(r["right"]) + float(r["wrong"])) for r in rows])
        e_opt, rms = fit_error_fraction(w, e)
        b = replace(b, e_opt=e_opt)
        res.update(e_opt=e_opt, error_rms=rms, errors=(w, e))
        say(f"Stage 6  error vs purity       e_opt {100 * e_opt:.2f} %, residual {100 * rms:.2f} points (pass < 1): {'PASS' if rms < 0.01 else 'CHECK'}")
    if (folder / "run.csv").exists():
        rows = _read(folder / "run.csv")
        right = np.array([float(r["right"]) for r in rows]); wrong = np.array([float(r["wrong"]) for r in rows])
        n = right + wrong
        e = np.where(n > 0, wrong / np.maximum(n, 1), 0.5)
        key = np.array([0.5 * k * key_fraction(x) if k > 0 else 0.0 for k, x in zip(n, e)])
        demand = 0.5 * float(key.mean())
        K = sequent_peak(key, demand)
        refused_without = simulate(key, demand, 0.0, 0.0).refused_days
        refused_with = simulate(np.r_[key, key], demand, K).refused_days
        res.update(run_key=key, run_demand=demand, run_bank=K, run_refused_without=refused_without, run_refused_with=refused_with)
        say(f"Stage 7  compressed cycle      {len(key)} steps, {key.sum():.3g} key bits, {int(np.sum(key == 0))} steps with none; "
            f"demand {demand:.3g}/step needs a bank of {K:.3g} bits; refusals {refused_without} without it, {refused_with} with it: "
            f"{'PASS' if refused_with == 0 else 'CHECK'}")
    res["design"] = asdict(b)
    if save:
        _figure(res, save)
    return res


def _figure(res: dict, path: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(10, 7))
    if "phase" in res:
        a, P, k = res["phase"]
        g = np.linspace(0, np.pi * 0.9, 200)
        ax[0, 0].plot(np.degrees(a), P / k, "o", ms=4, label="measured")
        ax[0, 0].plot(np.degrees(g), [lambert_phase(x) for x in g], "-", label="Lambert sphere")
        ax[0, 0].set(xlabel="phase angle (deg)", ylabel="relative brightness", title="Stage 2: the ball's phase curve")
        ax[0, 0].legend()
    for fiber, (th, r) in res.get("rejection", {}).items():
        ax[0, 1].loglog(np.maximum(th, 1e-5) * 1e3, np.maximum(r, 1e-12), "o-", ms=3, label=fiber)
    ax[0, 1].set(xlabel="off-axis angle (mrad)", ylabel="rejection", title="Stage 4: off-axis rejection")
    if res.get("rejection"):
        ax[0, 1].legend()
    if "errors" in res:
        w, e = res["errors"]
        g = np.linspace(w.min(), 1, 50)
        ax[1, 0].plot(w, 100 * e, "o", ms=4, label="measured")
        ax[1, 0].plot(g, [100 * error_fraction(x, res["e_opt"]) for x in g], "-", label="w e_opt + (1 - w)/2")
        ax[1, 0].set(xlabel="herald purity w", ylabel="error fraction (%)", title="Stage 6: background makes errors")
        ax[1, 0].legend()
    if "run_key" in res:
        key = res["run_key"]
        C = res["run_bank"]
        ax[1, 1].plot(key, label="key per step")
        ax[1, 1].axhline(res["run_demand"], ls="--", color="C1", label="demand")
        ax[1, 1].plot(simulate(key, res["run_demand"], C).level, color="C4", label="bank level")
        ax[1, 1].set(xlabel="step (a slice of the synodic period)", ylabel="bits", title="Stage 7: a synodic period and its key bank")
        ax[1, 1].legend()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("predict"); p.add_argument("--config")
    p = sub.add_parser("synthetic"); p.add_argument("--out", required=True); p.add_argument("--seed", type=int, default=1)
    p = sub.add_parser("schedule"); p.add_argument("--out", required=True); p.add_argument("--steps", type=int, default=780)
    p = sub.add_parser("report"); p.add_argument("folder"); p.add_argument("--save")
    a = ap.parse_args(argv)
    if a.cmd == "predict":
        print_predictions(load_design(Path(a.config) if a.config else None))
    elif a.cmd == "synthetic":
        write_synthetic(Path(a.out), a.seed)
        print(f"wrote a synthetic bench data set to {a.out}")
    elif a.cmd == "schedule":
        od = _schedule(a.steps)
        _write(Path(a.out), ["step", "mars_day", "extra_od"],
               [[i, round(779.0 * i / max(a.steps - 1, 1), 2), "inf" if not np.isfinite(x) else round(float(x), 4)] for i, x in enumerate(od)])
        print(f"wrote {a.steps} steps to {a.out}: add each step's extra_od to the base attenuation; 'inf' closes the shutter (conjunction)")
    else:
        report(Path(a.folder), a.save)


if __name__ == "__main__":
    main()
