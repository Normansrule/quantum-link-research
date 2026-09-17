"""Thermal occupation n̄(ω, T) for a microwave qubit and an optical photon [clerk2010].

Interactive: a slider sets the qubit frequency; the optical carrier is fixed at 193 THz.
The two vertical lines mark a dilution refrigerator (15 mK) and room temperature (300 K).
"""
from __future__ import annotations

import math

import numpy as np

from qll.circuits.noise.thermal import bose_einstein_occupation
from qll.viz._common import cli, finish


def occupation_curve(f_hz: float, T: np.ndarray) -> np.ndarray:
    return np.array([max(bose_einstein_occupation(2 * math.pi * f_hz, t), 1e-40) for t in T])


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    T = np.logspace(-3, 3, 400)
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    (line_mw,) = ax.loglog(T, occupation_curve(5e9, T), lw=2, label="5 GHz microwave qubit")
    ax.loglog(T, occupation_curve(193.4e12, T), lw=2, label="193 THz photon (1550 nm)")
    for t, name in ((0.015, "15 mK"), (300.0, "300 K")):
        ax.axvline(t, ls="--", color="0.5")
        ax.text(t * 1.1, 1e-25, name, color="0.4")
    ax.set(xlabel="temperature T (K)", ylabel="mean thermal occupation n̄", ylim=(1e-40, 1e5),
           title="n̄ = 1 / (exp(ħω / k_B T) − 1)")
    ax.legend(loc="lower right")
    if not args.save:
        from matplotlib.widgets import Slider

        fig.subplots_adjust(bottom=0.25)
        s = Slider(fig.add_axes([0.15, 0.08, 0.7, 0.03]), "qubit f (GHz)", 0.5, 50.0, valinit=5.0)

        def update(_):
            line_mw.set_ydata(occupation_curve(s.val * 1e9, T))
            line_mw.set_label(f"{s.val:.1f} GHz microwave qubit")
            ax.legend(loc="lower right")
            fig.canvas.draw_idle()

        s.on_changed(update)
    finish(fig, args)


if __name__ == "__main__":
    main()
