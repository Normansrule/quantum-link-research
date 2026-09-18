"""Modality comparison as a radar chart, generated from learn/02_qubit_modalities/modalities.json so
the figure and the table cannot drift apart. Scores 1–5 are qualitative (see the JSON for sources)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from qll.viz._common import cli, finish

DATA = Path(__file__).resolve().parents[2] / "learn" / "02_qubit_modalities" / "modalities.json"


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    data = json.loads(DATA.read_text())
    axes_names = data["axes"]
    n = len(axes_names)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist() + [0]
    fig, axs = plt.subplots(2, 4, figsize=(14, 7.4), subplot_kw=dict(polar=True))
    for ax, (name, row) in zip(axs.flat, data["platforms"].items()):
        vals = [row["scores"][a] for a in axes_names] + [row["scores"][axes_names[0]]]
        ax.plot(ang, vals, lw=2, color=row["color"]); ax.fill(ang, vals, color=row["color"], alpha=0.2)
        ax.set_xticks(ang[:-1]); ax.set_xticklabels(axes_names, fontsize=7)
        ax.set_ylim(0, 5); ax.set_yticks([1, 3, 5]); ax.set_yticklabels(["1", "3", "5"], fontsize=6)
        ax.set_title(name, fontsize=10, pad=12)
    fig.suptitle("Qubit modalities scored 1–5 on what a network link needs (data: learn/02_qubit_modalities/modalities.json)", fontsize=11)
    finish(fig, args)


if __name__ == "__main__":
    main()
