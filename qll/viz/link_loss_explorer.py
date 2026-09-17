"""Channel transmittance versus distance: fiber [pirandola2017] against free-space diffraction
[bourgoin2013], with the PLOB repeaterless key-capacity bound [pirandola2017] on the same axis.

Interactive: sliders for receiver aperture and transmitter waist.
"""
from __future__ import annotations

import numpy as np

from qll.channels.fiber_loss import transmittance
from qll.channels.free_space_diffraction import geometric_transmittance
from qll.qkd.plob_bound import plob_bits_per_use
from qll.viz._common import cli, finish

LAMBDA = 810e-9  # SPDC photons, Micius-class downlink


def free_space_curve(L_m: np.ndarray, w0: float, D_rx: float) -> np.ndarray:
    return np.array([geometric_transmittance(L, LAMBDA, w0, D_rx) for L in L_m])


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    L_km = np.logspace(0, 8.5, 600)
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.loglog(L_km, [transmittance(L, 0.2) for L in L_km], lw=2, label="fiber, 0.2 dB/km (1550 nm)")
    ax.loglog(L_km, [transmittance(L, 2.0) for L in L_km], lw=1.5, ls=":", label="fiber, 2 dB/km (810 nm)")
    (fs,) = ax.loglog(L_km, free_space_curve(L_km * 1e3, 0.15, 1.0), lw=2,
                      label="free space, w₀ = 15 cm, D_rx = 1 m")
    (pl,) = ax.loglog(L_km, [plob_bits_per_use(min(e, 1 - 1e-15)) for e in free_space_curve(L_km * 1e3, 0.15, 1.0)],
                      lw=1, color="k", alpha=0.5, label="PLOB bound on free-space link (bits/use)")
    for x, name in ((1200, "Micius 1200 km"), (384_400, "Moon"), (5.6e7, "Mars (closest)")):
        ax.axvline(x, ls="--", color="0.6")
        ax.text(x * 1.15, 3e-1, name, rotation=90, va="top", color="0.4", fontsize=8)
    ax.set(xlabel="distance L (km)", ylabel="transmittance η  /  bits per use", ylim=(1e-18, 2),
           title="η_fiber = 10^(−αL/10)     η_free = min(1, (D_rx / 2θL)²),  θ = λ/(πw₀)")
    ax.legend(loc="lower left", fontsize=8)
    if not args.save:
        from matplotlib.widgets import Slider

        fig.subplots_adjust(bottom=0.3)
        s_d = Slider(fig.add_axes([0.15, 0.12, 0.7, 0.03]), "D_rx (m)", 0.1, 10.0, valinit=1.0)
        s_w = Slider(fig.add_axes([0.15, 0.06, 0.7, 0.03]), "w₀ (m)", 0.01, 1.0, valinit=0.15)

        def update(_):
            eta = free_space_curve(L_km * 1e3, s_w.val, s_d.val)
            fs.set_ydata(eta)
            pl.set_ydata([plob_bits_per_use(min(e, 1 - 1e-15)) for e in eta])
            fig.canvas.draw_idle()

        s_d.on_changed(update)
        s_w.on_changed(update)
    finish(fig, args)


if __name__ == "__main__":
    main()
