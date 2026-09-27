"""The CZ gate, simulated: the flux pulse on qubit 1 for two shapes, each calibrated to a conditional phase of pi,
the |11> and |20> populations along each, and the conditional phase accumulating. Shaped in the |11>-|20> mixing angle
(after Martinis and Geller) the 59.5 ns pulse returns everything to |11>; shaped in frequency with the same ramps it
leaves a few percent in |20>. The 17 % of bare |20> at the interaction point is hybridization, not leakage."""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from qll.hardware.cz_gate import FREQUENCY_SHAPED_FLAT_NS as FREQ_FLAT
from qll.hardware.cz_gate import CZPulse
from qll.hardware.tunable_coupler import static_zz_exact
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    good = CZPulse()
    bad = replace(good, shape="frequency", t_flat=FREQ_FLAT)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    ax = axes[0]
    t = np.linspace(0, good.duration, 600)
    ax.plot(t, good.w1(t), color="C2", lw=2.2, label="shaped in mixing angle")
    tb = np.linspace(0, bad.duration, 600)
    ax.plot(tb, bad.w1(tb), color="C3", lw=1.6, ls="--", label="shaped in frequency")
    ax.axhline(good.w2 - good.alpha, color="0.5", lw=1, ls=":")
    ax.text(1, good.w2 - good.alpha + 0.012, "|11⟩–|20⟩ crossing", fontsize=8, color="0.35")
    ax.set(xlabel="time (ns)", ylabel="qubit 1 frequency $\\omega_1/2\\pi$ (GHz)", title="Flux pulses, each calibrated to a CZ")
    ax.legend(fontsize=8, loc="upper center")

    ax = axes[1]
    for pulse, c, ls, name in ((good, "C2", "-", "angle"), (bad, "C3", "--", "frequency")):
        ts, p11, p20 = pulse.populations_from_11(dt=0.02, every=5)
        ax.plot(ts, p11, color=c, ls=ls, lw=2 if ls == "-" else 1.5, label=f"|11⟩ ({name})")
        ax.plot(ts, p20, color=c, ls=ls, lw=1, alpha=0.6, label=f"|20⟩ ({name})")
    th = 0.5 * np.arctan2(2 * np.sqrt(2) * good.g, good.w1_int - (good.w2 - good.alpha))
    ax.axhline(np.sin(th) ** 2, color="0.5", lw=0.8, ls=":",
               label=f"hybridization: dressed |11⟩ is {100 * np.sin(th) ** 2:.0f} % bare |20⟩")
    ax.set(xlabel="time (ns)", ylabel="bare-state population", ylim=(-0.02, 1.02),
           title=f"Left in |20⟩ afterwards: {good.leakage(0.02):.0e} vs {bad.leakage(0.02):.0e}")
    ax.legend(fontsize=7.5, loc="center right")

    ax = axes[2]
    zeta = np.array([static_zz_exact(float(w), good.w2, good.alpha, good.alpha, good.g, levels=3) for w in good.w1(t)])
    phase = -2 * np.pi * np.concatenate([[0.0], np.cumsum(0.5 * (zeta[1:] + zeta[:-1]) * np.diff(t))])
    ax.plot(t, phase / np.pi, color="C0", lw=2.2, label="adiabatic estimate, −2π∫ZZ dt")
    ax.axhline(1, color="C2", ls="--", lw=1.2)
    ax.text(good.duration * 0.72, 1.04, "π: a CZ", color="C2", fontsize=9)
    ax.set(xlabel="time (ns)", ylabel="conditional phase / π", ylim=(-0.05, 1.2),
           title=f"Simulated phase π, CZ fidelity {good.average_fidelity(0.02):.5f}")
    ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(0.0, 0.93))
    ax2 = ax.twinx()
    ax2.plot(t, -zeta * 1e3, color="0.6", lw=1)
    ax2.set_ylabel("|ZZ| along the pulse (MHz)", color="0.45")
    fig.text(0.5, -0.02, "Qubits at 6.00 → 5.25 GHz and 5.00 GHz, α = −200 MHz, g = 20 MHz; full three-level simulation "
             "(qll/hardware/cz_gate.py). Local Z phases are removed as a virtual frame change.", ha="center", fontsize=8.5,
             color="0.3")
    finish(fig, args)


if __name__ == "__main__":
    main()
