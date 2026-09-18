"""S04 — Repetition code logical error vs distance in Stim with a majority-vote decoder.

Physics: a distance-d bit-flip repetition code with physical error p fails when more than (d−1)/2
data qubits flip in one round; below threshold (p < 1/2 for this toy code) the logical error falls
exponentially with d. This is the concept behind Λ in the surface-code experiments, with the
simplest possible decoder. Reference: Nielsen & Chuang §10.1; Google Quantum AI (2023, 2025).
"""
from __future__ import annotations

import numpy as np


def logical_error_rate(d: int, p: float, shots: int = 20000, seed: int = 11) -> float:
    import stim

    c = stim.Circuit()
    for q in range(d):
        c.append("X_ERROR", [q], p)
    c.append("M", list(range(d)))
    sampler = c.compile_sampler(seed=seed)
    m = sampler.sample(shots)
    flips = m.sum(axis=1)
    return float(np.mean(flips > d // 2))


def main() -> None:
    from _common import report, save
    import matplotlib.pyplot as plt

    ps = [0.02, 0.05, 0.1, 0.2, 0.3, 0.45]
    ds = [1, 3, 5, 7, 9, 11]
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    rows = []
    for p in ps:
        pl = [logical_error_rate(d, p) for d in ds]
        ax.semilogy(ds, pl, "o-", label=f"p = {p}")
        rows.append((f"p = {p}: Λ = p_L(d=3)/p_L(d=5)", f"{pl[1]/max(pl[2],1e-9):.2f}"))
    report("S04 repetition code (Stim, majority vote)", rows)
    ax.set(xlabel="code distance d", ylabel="logical error probability", title="S04: below threshold, more qubits = fewer errors")
    ax.legend(fontsize=8); save(fig, "repetition_code")


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); main()
