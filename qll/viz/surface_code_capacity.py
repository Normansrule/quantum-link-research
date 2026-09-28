"""The rotated surface code under independent bit flips with perfect syndrome measurement, decoded by matching:
logical error rate against physical error rate for d = 3 to 9, crossing near the code-capacity threshold."""
from __future__ import annotations

import numpy as np

from qll.circuits.surface_code_capacity import logical_failure_rate
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    ps = np.linspace(0.01, 0.16, 16)
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for d, c in ((3, "C1"), (5, "C0"), (7, "C4"), (9, "C2")):
        f = np.array([logical_failure_rate(d, float(p), 20000, seed=d) for p in ps])
        ax.semilogy(ps * 100, np.where(f > 0, f, np.nan), "o-", color=c, ms=4, label=f"d = {d} ({d * d} qubits)")
    ax.semilogy(ps * 100, ps, "k--", lw=1, label="unencoded qubit")
    ax.axvspan(9.5, 10.3, color="C2", alpha=0.12)
    ax.text(9.6, 2.2e-4, "threshold\n≈ 10 %", fontsize=8.5, color="C2")
    ax.set(xlabel="physical bit-flip probability p (%)", ylabel="logical error rate", ylim=(1e-4, 0.6),
           title="Surface code, code capacity, matching decoder")
    ax.legend(fontsize=8.5, loc="lower right")
    ax.text(0.01, 0.97, "20 000 shots per point; qll/circuits/surface_code_capacity.py (PyMatching)", transform=ax.transAxes,
            fontsize=7.5, color="0.35", va="top")
    finish(fig, args)


if __name__ == "__main__":
    main()
