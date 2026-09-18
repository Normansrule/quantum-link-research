"""A distance-3 surface code patch: data qubits, X and Z stabilizers, and how one error lights up
two syndromes. Static teaching figure; Stim + PyMatching do the real thing (experiments/protocols P12)."""
from __future__ import annotations

from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon

    d = 3
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 5.2))
    for ax, title, err in ((a, "distance-3 surface code: 9 data + 8 check qubits", None), (b, "one X error on a data qubit flips the two Z checks touching it", (1, 1))):
        ax.set(xlim=(-0.8, d - 0.2), ylim=(-0.8, d - 0.2), title=title); ax.set_aspect("equal"); ax.axis("off")
        for i in range(d):
            for j in range(d):
                c = "C3" if err == (i, j) else "white"
                ax.add_patch(Circle((i, j), 0.18, fc=c, ec="k", lw=1.5, zorder=3))
        # plaquettes: Z-type (blue) and X-type (orange) alternating
        for i in range(d - 1):
            for j in range(d - 1):
                z = (i + j) % 2 == 0
                col = "C0" if z else "C1"
                lit = err is not None and z and abs(err[0] - i - 0.5) < 1 and abs(err[1] - j - 0.5) < 1
                ax.add_patch(Polygon([(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)], fc=col, alpha=0.6 if lit else 0.15, ec=col, zorder=1))
                ax.text(i + 0.5, j + 0.5, ("Z" if z else "X") + (" !" if lit else ""), ha="center", va="center", fontsize=9, fontweight="bold" if lit else None)
        # boundary half-plaquettes
        for i in range(d - 1):
            if i % 2 == 0:
                ax.add_patch(Polygon([(i, -0.5), (i + 1, -0.5), (i + 1, 0)], fc="C1", alpha=0.15, ec="C1"))
                ax.add_patch(Polygon([(i, d - 1), (i + 1, d - 1), (i + 1, d - 0.5)], fc="C1", alpha=0.15, ec="C1"))
        for j in range(d - 1):
            if j % 2 == 1:
                ax.add_patch(Polygon([(-0.5, j), (-0.5, j + 1), (0, j + 1)], fc="C0", alpha=0.15, ec="C0"))
                ax.add_patch(Polygon([(d - 1, j), (d - 1, j + 1), (d - 0.5, j)], fc="C0", alpha=0.15, ec="C0"))
    b.text(1.0, -0.7, "decoder pairs the two lit checks along the shortest path → applies X → error gone.\nΛ = how much the logical error drops when d grows by 2.", ha="center", fontsize=8, color="0.3")
    finish(fig, args)


if __name__ == "__main__":
    main()
