"""Repetition-code threshold under circuit-level noise: logical error vs physical error for d = 3, 5, 7, decoded by
minimum-weight perfect matching (Stim + PyMatching). The curves cross at the threshold."""
from __future__ import annotations

import numpy as np

from qll.circuits.decoders import logical_error_rate
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    ps = np.array([0.01, 0.02, 0.03, 0.05, 0.07, 0.09, 0.12, 0.16])
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for d, c in ((3, "C0"), (5, "C1"), (7, "C2")):
        ax.loglog(ps, [max(logical_error_rate(d, p, shots=6000, seed=d), 1e-5) for p in ps], "o-", color=c, lw=2, label=f"d = {d}, matching")
    ax.loglog(ps, [logical_error_rate(5, p, shots=6000, decoder="none") for p in ps], "k:", lw=1.5, label="d = 5, no decoding")
    ax.loglog(ps, ps, color="0.6", ls="--", lw=1, label="unencoded (p)")
    ax.axvspan(0.07, 0.09, color="C3", alpha=0.08); ax.text(0.071, 1.3e-4, "threshold\n(curves cross)", fontsize=8, color="C3")
    ax.set(xlabel="physical error per operation p", ylabel="logical error per memory experiment", ylim=(1e-5, 1),
           title="Below threshold, bigger codes win; above it, they lose")
    ax.legend(fontsize=8, loc="lower right")
    finish(fig, args)


if __name__ == "__main__":
    main()
