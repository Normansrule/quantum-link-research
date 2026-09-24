"""BBPSSW purification as a map: F' versus F, the cobweb toward the fixed point at 1, and the pairs consumed.
Every point comes from qll.network.purification (verified against a full 16x16 simulation)."""
from __future__ import annotations

import numpy as np

from qll.network.purification import bbpssw_rounds_to_target, bbpssw_step
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    F = np.linspace(0.25, 1.0, 300)
    Fp = np.array([bbpssw_step(f)[0] for f in F]); ps = np.array([bbpssw_step(f)[1] for f in F])
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.4))
    a.plot(F, Fp, lw=2, label="F' = BBPSSW(F, F)"); a.plot(F, F, "k:", label="F' = F")
    a.axvline(0.5, ls="--", color="0.6"); a.text(0.505, 0.3, "unstable fixed point ½", fontsize=8, color="0.4")
    f = 0.6
    for _ in range(6):            # cobweb
        f2 = bbpssw_step(f)[0]; a.plot([f, f, f2], [f, f2, f2], color="C3", lw=1); f = f2
    a.set(xlabel="input fidelity F", ylabel="output fidelity F'", title="One BBPSSW round: F > ½ improves, F < ½ degrades"); a.legend(fontsize=8)
    Fs = np.linspace(0.55, 0.95, 9)
    cost = [bbpssw_rounds_to_target(f, 0.99)[2] for f in Fs]; rounds = [bbpssw_rounds_to_target(f, 0.99)[0] for f in Fs]
    b.semilogy(Fs, cost, "o-", lw=2, label="input pairs per output pair (target 0.99)")
    for x, r in zip(Fs, rounds):
        b.text(x, cost[list(Fs).index(x)] * 1.3, f"{r} rounds", fontsize=7, ha="center")
    b.set(xlabel="input fidelity F", ylabel="pairs consumed", title="Cost: each round halves the pairs and costs one classical round trip"); b.legend(fontsize=8)
    b.text(0.02, 0.05, "What to look for: from F = 0.6 the price is hundreds of pairs and 5 round trips;\nat Mars that is hours of classical exchange per purified pair.", transform=b.transAxes, fontsize=8, color="0.3")
    finish(fig, args)


if __name__ == "__main__":
    main()
