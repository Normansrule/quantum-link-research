"""Earth-Mars link availability and best-relay pair yield over two synodic cycles for three relay placements:
Earth orbit only, plus Sun-Earth L4/L5, plus Mars orbit. Blackouts at SEP < 3 deg are the grey bands."""
from __future__ import annotations

import numpy as np

from qll.space.conjunction import sep_angle_series
from qll.space.ephemeris import SYNODIC_PERIOD_DAYS
from qll.space.relay_constellation import Relay, best_relay_pairs_per_day, constellation_availability
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    t = np.arange(0.0, 2 * SYNODIC_PERIOD_DAYS, 4.0)
    sets = {
        "Earth orbit only": [Relay("E", "earth_orbit")],
        "+ L4 and L5": [Relay("E", "earth_orbit"), Relay("L4", "L4"), Relay("L5", "L5")],
        "+ Mars orbit": [Relay("E", "earth_orbit"), Relay("L4", "L4"), Relay("L5", "L5"), Relay("M", "mars_orbit")],
    }
    fig, (a, b) = plt.subplots(2, 1, figsize=(9.5, 6.5), sharex=True)
    sep = sep_angle_series(t)
    for ax in (a, b):
        ax.fill_between(t / 365.25, 0, 1, where=sep < 3.0, transform=ax.get_xaxis_transform(), color="0.8", alpha=0.6, label="direct line of sight blocked (SEP < 3°)")
    for name, relays in sets.items():
        y = [best_relay_pairs_per_day(relays, ti) for ti in t]
        a.semilogy(t / 365.25, np.maximum(y, 1e-3), lw=2, label=f"{name}: availability {constellation_availability(relays, t):.0%}")
    a.set(ylabel="entangled pairs per day (best relay)", title="Relay placement: what survives conjunction, and what it yields")
    a.legend(fontsize=8, loc="lower right")
    b.plot(t / 365.25, sep, color="C3", lw=1.5)
    b.axhline(3, ls="--", color="0.5"); b.set(xlabel="years", ylabel="Sun–Earth–Mars angle (°)")
    a.text(0.01, 0.97, "What to look for: an L4/L5 relay keeps a path open through every conjunction;\nyield still collapses near conjunction because the long leg is longest there.", transform=a.transAxes, va="top", fontsize=8, color="0.3")
    finish(fig, args)


if __name__ == "__main__":
    main()
