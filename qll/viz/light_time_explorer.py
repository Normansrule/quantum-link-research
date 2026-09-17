"""One-way and round-trip light time versus distance, from a fiber spool to Mars at conjunction.

The horizontal bands are demonstrated quantum-memory lifetimes: the memory must outlast the
classical round trip for teleportation to complete (REQ-CAP-001) [zhong2015] [wang2025memory]
[bradley2019] [knaut2024].
"""
from __future__ import annotations

import numpy as np

from qll.channels.light_time_delay import one_way_delay_s, round_trip_delay_s
from qll.constants.astro import AU_METERS, EARTH_MARS_MAX_M, EARTH_MARS_MIN_M
from qll.viz._common import cli, finish

MEMORIES = [  # (label, seconds, bibkey)
    ("atomic ensemble ~ms [liu2024]", 1e-3),
    ("SiV nuclear spin ~1 s [knaut2024]", 1.0),
    ("NV C-13 register ~1 min [bradley2019]", 60.0),
    ("Yb+ ion > 1 h [wang2021ion]", 3600.0),
    ("Eu:YSO 6 h [zhong2015]", 6 * 3600.0),
    ("Eu:YSO 13.1 h [wang2025memory]", 13.1 * 3600.0),
]


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    d = np.logspace(3, 12, 400)
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.loglog(d / 1e3, [one_way_delay_s(x) for x in d], lw=2, label="one way  τ = d/c")
    ax.loglog(d / 1e3, [round_trip_delay_s(x) for x in d], lw=2, label="round trip  2d/c")
    for x, name in ((1e3, "1 km fiber"), (5e5, "LEO"), (3.6e7, "GEO"), (3.844e8, "Moon"),
                    (EARTH_MARS_MIN_M, "Mars min"), (AU_METERS, "1 au"), (EARTH_MARS_MAX_M, "Mars max")):
        ax.axvline(x / 1e3, ls="--", color="0.7")
        ax.text(x / 1e3 * 1.1, 2e-5, name, rotation=90, va="bottom", fontsize=8, color="0.4")
    for label, sec in MEMORIES:
        ax.axhline(sec, color="C3", alpha=0.35, lw=1)
        ax.text(1.2, sec * 1.15, label, fontsize=7, color="C3")
    ax.set(xlabel="distance d (km)", ylabel="time (s)", ylim=(1e-6, 1e6),
           title="Classical bits arrive no earlier than d/c; the memory must outlast 2d/c")
    ax.legend(loc="upper left")
    finish(fig, args)


if __name__ == "__main__":
    main()
