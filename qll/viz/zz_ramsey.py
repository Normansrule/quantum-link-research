"""Measuring ZZ the way a student would on a cloud processor: conditional Ramsey fringes of qubit 0 with its neighbour
in |0> and |1> (simulated in Qiskit Aer with a known ZZ injected), and the ZZ recovered by the fit across coupler
frequencies, on top of the exact-diagonalisation curve it should reproduce."""
from __future__ import annotations

import numpy as np

from qll.circuits.zz_ramsey import fit_ramsey, measure_zz, simulate
from qll.hardware.tunable_coupler import CoupledPair
from qll.viz._common import cli, finish

DELAYS = np.linspace(0, 30, 121)      # microseconds
DETUNING = 0.5                         # MHz, virtual
T2 = 40.0                              # microseconds


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    pair = CoupledPair()
    fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.3), gridspec_kw={"width_ratios": [1.25, 1]})
    zz = pair.zz(6.0) * 1e3                                     # MHz
    d = simulate(DELAYS, DETUNING, zz, T2)
    fine = np.linspace(0, DELAYS[-1], 800)
    for s, c in ((0, "C0"), (1, "C3")):
        f, T = fit_ramsey(DELAYS, d[s])
        a.plot(DELAYS, d[s], "o", ms=2.6, color=c, alpha=0.7)
        a.plot(fine, 0.5 - 0.5 * np.exp(-fine / T) * np.cos(2 * np.pi * f * fine), color=c, lw=1.2, alpha=0.8,
               label=f"neighbour in |{s}⟩: f = {1e3 * f:.1f} kHz")
    a.set(xlabel="delay τ (µs)", ylabel="P(qubit 0 reads 1)", xlim=(0, 12), ylim=(-0.03, 1.12),
          title=f"Coupler at 6.00 GHz: ZZ = {1e3 * zz:.1f} kHz injected, {1e3 * measure_zz(DELAYS, d[0], d[1]):.1f} kHz recovered")
    a.legend(fontsize=8.5, loc="upper right", ncol=2)

    wc = np.linspace(4.7, 7.2, 160)
    b.plot(wc, [1e6 * pair.zz(w) for w in wc], color="0.4", lw=1.6, label="exact diagonalisation")
    pts = [4.8, 5.0, 5.221, 5.6, 6.0, 6.6, 7.2]
    rec = []
    for w in pts:
        z = pair.zz(w) * 1e3
        dd = simulate(DELAYS, DETUNING, z, T2, seed=11)
        rec.append(1e3 * measure_zz(DELAYS, dd[0], dd[1]))
    b.plot(pts, rec, "o", color="C1", ms=7, label="recovered from simulated Ramsey")
    b.axhline(0, color="0.8", lw=0.8)
    b.axvline(pair.zz_free_frequency(5.0, 5.5), color="C2", ls="--", lw=1, label="idle point (ZZ = 0)")
    b.set(xlabel="coupler frequency ω_c/2π (GHz)", ylabel="static ZZ (kHz)", title="The experiment tracks the model")
    b.legend(fontsize=8.5)
    fig.text(0.5, -0.02, f"Qiskit Aer, 4000 shots per point, virtual detuning {DETUNING} MHz, T2 = {T2:.0f} µs, "
             f"delays 0–{DELAYS[-1]:.0f} µs (qll/circuits/zz_ramsey.py). On hardware the RZZ is replaced by a delay.",
             ha="center", fontsize=8.5, color="0.3")
    finish(fig, args)


if __name__ == "__main__":
    main()
