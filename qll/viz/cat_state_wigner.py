"""Wigner functions of a coherent state, a squeezed vacuum, and an even cat state (QuTiP), with the negative
interference fringes that make the cat non-classical and the ingredient of cat and GKP bosonic codes (T03)."""
from __future__ import annotations

import numpy as np

from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt
    import qutip as qt

    N = 60
    alpha = 2.0
    states = {
        "coherent |α=2⟩": qt.coherent(N, alpha),
        "squeezed vacuum r = 0.7": qt.squeeze(N, 0.7) * qt.basis(N, 0),
        "even cat (|α⟩+|−α⟩)": (qt.coherent(N, alpha) + qt.coherent(N, -alpha)).unit(),
    }
    x = np.linspace(-5, 5, 161)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    for ax, (name, st) in zip(axes, states.items()):
        W = qt.wigner(st, x, x)
        lim = np.abs(W).max()
        ax.contourf(x, x, W, 60, cmap="RdBu_r", vmin=-lim, vmax=lim)
        ax.set(title=f"{name}\nmin W = {W.min():.3f}", xlabel="x", ylabel="p", aspect="equal")
    fig.suptitle("Wigner functions: negativity marks non-classicality; the cat's fringes are what a cat code protects")
    finish(fig, args)


if __name__ == "__main__":
    main()
