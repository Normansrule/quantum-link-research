"""One-way light time and Earth–Mars range over a synodic cycle, from circular coplanar orbits
(1.000 au and 1.524 au). Simplified model: the real ephemeris (JPL Horizons) replaces it in Phase 5;
the envelope agrees with qll.constants.astro to within the eccentricity of Mars (~0.09)."""
from __future__ import annotations

import numpy as np

from qll.channels.light_time_delay import one_way_delay_s
from qll.constants.astro import AU_METERS
from qll.viz._common import cli, finish

SYNODIC_DAYS = 779.9


def earth_mars_range_m(t_days: np.ndarray, a_e: float = 1.0, a_m: float = 1.524) -> np.ndarray:
    w_e = 2 * np.pi / 365.25
    w_m = 2 * np.pi / 686.98
    dx = a_m * np.cos(w_m * t_days) - a_e * np.cos(w_e * t_days)
    dy = a_m * np.sin(w_m * t_days) - a_e * np.sin(w_e * t_days)
    return np.sqrt(dx**2 + dy**2) * AU_METERS


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
    sun = (np.abs(np.angle(np.exp(1j * (2 * np.pi / 686.98 * t - 2 * np.pi / 365.25 * t)))) < np.radians(6)) & (d > 2.3 * AU_METERS)
    ax.fill_between(t / 365.25, 0, 1e4, where=sun, color="orange", alpha=0.15, label="near solar conjunction (link blocked)")
    ax.set(xlabel="years", ylabel="minutes", yscale="log", ylim=(0.5, 3000),
           title="Earth–Mars light time over two synodic cycles (circular-orbit model)")
    ax.legend(fontsize=8, loc="upper right")
    ax.text(0.01, 0.02, "What to look for: the round trip is never below ~6 min; only hour-class memories clear it;\nconjunction blocks the line of sight for weeks every 26 months.", transform=ax.transAxes, fontsize=8, color="0.3")
    finish(fig, args)


if __name__ == "__main__":
    main()
