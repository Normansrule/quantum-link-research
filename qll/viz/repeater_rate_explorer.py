"""Repeater chain versus direct transmission: end-to-end entanglement rate against distance
for a chain of N segments with generation probability p0 = eta_segment * p_source, swap success
q, and a memory that must survive the classical herald round trip. Rate formula from the nested
scheme with geometric waiting (Sangouard et al. 2011, Muralidharan et al. 2016)."""
from __future__ import annotations

import math

import numpy as np

from qll.channels.fiber_loss import transmittance
from qll.channels.light_time_delay import round_trip_delay_s
from qll.viz._common import cli, finish


def chain_rate(L_km: float, n_seg: int, p_src: float, q: float, T2_s: float, alpha: float = 0.2) -> float:
    """Pairs per second for a symmetric chain (crude nested estimate, memory cutoff included)."""
    seg = L_km / n_seg
    p0 = p_src * transmittance(seg / 2, alpha) ** 2  # heralded at a midpoint: both halves must arrive
    t0 = round_trip_delay_s(seg * 1e3 / 2 * 1.47)      # fiber index 1.47
    levels = max(0, round(math.log2(n_seg)))
    rate = 1.0 / t0
    for _ in range(levels):
        rate *= q * 2.0 / 3.0                           # each nesting level: wait for both, then swap
    rate *= p0
    t_hold = t0 * (2 ** levels)                        # total hold time in the worst case
    return rate * math.exp(-t_hold / T2_s)


def direct_rate(L_km: float, p_src: float, rep_hz: float = 1e9, alpha: float = 0.2) -> float:
    return rep_hz * p_src * transmittance(L_km, alpha)


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    L = np.logspace(1, 4, 300)
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.loglog(L, [direct_rate(x, 0.05) for x in L], "k", lw=2, label="direct transmission, 1 GHz source")
    lines = {}
    for n, c in ((4, "C0"), (16, "C1"), (64, "C2")):
        (ln,) = ax.loglog(L, [chain_rate(x, n, 0.05, 0.5, 1.0) for x in L], color=c, lw=2, label=f"chain, {n} segments, T2 = 1 s")
        lines[n] = ln
    ax.axhline(1, ls=":", color="0.5"); ax.text(12, 1.3, "1 pair per second", fontsize=8, color="0.4")
    ax.axhline(1 / 86400, ls=":", color="0.5"); ax.text(12, 1.6 / 86400, "1 pair per day", fontsize=8, color="0.4")
    ax.set(xlabel="end-to-end distance (km)", ylabel="entangled pairs per second", ylim=(1e-8, 1e8),
           title="Where a repeater chain beats direct transmission (REQ-NET-001)")
    ax.legend(fontsize=8, loc="lower left")
    ax.text(0.98, 0.97, "What to look for: the crossover distance moves left as\nsegments increase; the chain dies when the hold time\nexceeds T2 (try the slider).", transform=ax.transAxes, ha="right", va="top", fontsize=8, color="0.3")
    if not args.save:
        from matplotlib.widgets import Slider

        fig.subplots_adjust(bottom=0.22)
        s = Slider(fig.add_axes([0.15, 0.06, 0.7, 0.03]), "memory T2 (s)", 0.001, 100.0, valinit=1.0)

        def update(_):
            for n, ln in lines.items():
                ln.set_ydata([chain_rate(x, n, 0.05, 0.5, s.val) for x in L])
            fig.canvas.draw_idle()

        s.on_changed(update)
    finish(fig, args)


if __name__ == "__main__":
    main()
