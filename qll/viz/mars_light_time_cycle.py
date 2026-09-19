"""One-way light time over two synodic cycles from the Phase 5 Kepler mean-element ephemeris
(qll.space.ephemeris), whose range envelope matches qll.constants.astro to 1 %; conjunction bands from
qll.space.conjunction (SEP < 3 deg)."""
from __future__ import annotations

import numpy as np

from qll.channels.light_time_delay import one_way_delay_s
from qll.viz._common import cli, finish

SYNODIC_DAYS = 779.9


from qll.space.conjunction import sep_angle_series
from qll.space.ephemeris import earth_mars_range_m


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    t = np.linspace(0, 2 * SYNODIC_DAYS, 1200)
    d = earth_mars_range_m(t)
    delay_min = np.array([one_way_delay_s(x) / 60 for x in d])
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.plot(t / 365.25, delay_min, lw=2, label="one-way light time")
    ax.plot(t / 365.25, 2 * delay_min, lw=2, label="round trip (memory must outlast this)")
    for T, lab, c in ((1.0, "NV ¹³C ~1 min", "C3"), (60.0, "ion ~1 h", "C4"), (13.1 * 60, "Eu:YSO 13 h", "C2")):
        ax.axhline(T, ls="--", color=c, lw=1); ax.text(0.05, T * 1.08, lab, fontsize=8, color=c)
    sun = sep_angle_series(t) < 3.0
    ax.fill_between(t / 365.25, 0, 1e4, where=sun, color="orange", alpha=0.15, label="near solar conjunction (link blocked)")
    ax.set(xlabel="years", ylabel="minutes", yscale="log", ylim=(0.5, 3000),
           title="Earth–Mars light time over two synodic cycles (Kepler mean elements)")
    ax.legend(fontsize=8, loc="upper right")
    ax.text(0.01, 0.02, "What to look for: the round trip is never below ~6 min; only hour-class memories clear it;\nconjunction blocks the line of sight for weeks every 26 months.", transform=ax.transAxes, fontsize=8, color="0.3")
    finish(fig, args)


if __name__ == "__main__":
    main()
