"""REQ-CAP-001 in one figure: for each demonstrated memory, the storage time at which a stored Bell pair stops
being useful for teleportation (F = 2/3), against the classical round trip of each baseline. A memory is
"capable" for a baseline when its crossover sits to the right of that baseline's bar."""
from __future__ import annotations

import numpy as np

from qll.network.memory_decoherence import BASELINES, MEMORY_TABLE, crossover_time_s
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9.5, 5))
    names = [p.name for p in MEMORY_TABLE]
    y = np.arange(len(names))
    for i, p in enumerate(MEMORY_TABLE):
        tc = crossover_time_s(0.95, p.lifetime_s, p.model)
        ax.barh(i, tc, color="C2" if tc >= BASELINES["Mars max"] else "C1" if tc >= BASELINES["Moon"] else "C0", alpha=0.8)
        ax.text(tc * 1.15, i, f"eff. {p.efficiency:.0%}", va="center", fontsize=8, color="0.3")
    for k, (name, t) in enumerate(BASELINES.items()):
        ax.axvline(t, ls="--", color="0.5", lw=1)
        ax.text(t, len(names) - 0.4 + 0.0, name, rotation=90, fontsize=7, va="bottom", ha="right", color="0.4")
    ax.set(xscale="log", yticks=y, yticklabels=names, xlabel="storage time until teleportation fidelity drops to 2/3 (s), initial f = 0.95",
           title="REQ-CAP-001: which memory outlives which classical round trip", xlim=(1e-4, 1e6))
    ax.text(0.01, 0.02, "What to look for: the rare-earth bars pass the Mars lines but carry the lowest retrieval efficiency;\nthe hour-class ion memory clears Mars max with margin < 1.5x. Blue = below lunar, orange = lunar, green = Mars-capable.", transform=ax.transAxes, fontsize=8, color="0.3")
    finish(fig, args)


if __name__ == "__main__":
    main()
