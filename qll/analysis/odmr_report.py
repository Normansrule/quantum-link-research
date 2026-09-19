"""python -m qll.analysis.odmr_report data/odmr/<file>.csv [--dips N]: fit, print, and plot an ODMR run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from qll.analysis.odmr_fit import D_TEMPERATURE_COEFF_HZ_PER_K, fit_odmr, load_csv, lorentzian_dips
from qll.hardware.nv_node import D_ZFS_HZ


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--dips", type=int, default=2); ap.add_argument("--save")
    a = ap.parse_args()
    f, s = load_csv(a.csv)
    side = Path(a.csv).with_suffix(".json")
    meta = json.loads(side.read_text()) if side.exists() else {}
    fit = fit_odmr(f, s, a.dips, meta.get("photon_rate_hz"))
    T = meta.get("temperature_k", 300.0)
    D_expected = D_ZFS_HZ + D_TEMPERATURE_COEFF_HZ_PER_K * (T - 300.0)
    print(f"file            {a.csv}")
    for c, w, C in zip(fit.centers_hz, fit.widths_hz, fit.contrasts):
        print(f"line            {c/1e9:.6f} GHz  width {w/1e6:.2f} MHz  contrast {C*100:.2f} %")
    if fit.D_hz:
        flag = "" if abs(fit.D_hz - D_expected) < fit.widths_hz.max() else "  <-- differs from expected by more than the linewidth"
        print(f"D               {fit.D_hz/1e9:.6f} GHz  (expected {D_expected/1e9:.6f} at {T} K){flag}")
        print(f"B_parallel      {fit.B_parallel_gauss:.2f} G")
    if fit.sensitivity_t_per_sqrt_hz:
        print(f"sensitivity     {fit.sensitivity_t_per_sqrt_hz*1e9:.1f} nT/sqrt(Hz)")
    print(f"residual rms    {fit.residual_rms*100:.3f} % of baseline")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.plot(f / 1e9, s, ".", ms=3, color="0.5", label="data")
    params = [fit.baseline] + [v for trio in zip(fit.centers_hz, fit.widths_hz, fit.contrasts) for v in trio]
    ax.plot(f / 1e9, lorentzian_dips(f, *params), "C3", lw=2, label="Lorentzian fit")
    ax.set(xlabel="microwave frequency (GHz)", ylabel="normalized fluorescence", title=Path(a.csv).name)
    ax.legend()
    out = a.save or str(Path("docs/figures") / f"data_{Path(a.csv).stem}.svg")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(); fig.savefig(out, bbox_inches="tight"); print(f"figure          {out}")


if __name__ == "__main__":
    main()
