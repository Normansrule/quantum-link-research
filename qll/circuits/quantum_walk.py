"""The discrete-time quantum walk on a line: ballistic spreading instead of diffusion.

Physics
-------
A walker with a coin qubit moves left or right according to the coin after a Hadamard coin flip each step; after t
steps the position variance grows as t^2 (ballistic) against t for the classical random walk (diffusive) [aharonov2001]
[kempe2003]. Quantum walks underlie search algorithms with quadratic speedups and are exactly what a photon does in a
waveguide array; the standard deviation ratio quantum/classical grows as sqrt(t).
"""
from __future__ import annotations

import numpy as np


def hadamard_walk_distribution(t: int) -> np.ndarray:
    """Probability over positions -t..t after t steps from |0> ⊗ (|L> + i|R>)/sqrt2 (the symmetric initial coin)."""
    n = 2 * t + 1
    amp = np.zeros((n, 2), dtype=complex)          # position index, coin (0 = left, 1 = right)
    amp[t, 0] = 1 / np.sqrt(2); amp[t, 1] = 1j / np.sqrt(2)
    H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    for _ in range(t):
        amp = amp @ H.T
        new = np.zeros_like(amp)
        new[:-1, 0] = amp[1:, 0]                     # left movers shift by -1
        new[1:, 1] = amp[:-1, 1]                     # right movers shift by +1
        amp = new
    return (np.abs(amp) ** 2).sum(axis=1)


def classical_walk_distribution(t: int) -> np.ndarray:
    from math import comb

    p = np.zeros(2 * t + 1)
    for k in range(t + 1):
        p[2 * k] = comb(t, k) / 2**t                 # position -t + 2k
    return p


def std(dist: np.ndarray) -> float:
    """Standard deviation of a probability distribution over positions -t..t (must be real and non-negative)."""
    dist = np.asarray(dist)
    if np.iscomplexobj(dist) or (dist < -1e-12).any():
        raise ValueError("std expects a real, non-negative probability distribution")
    x = np.arange(len(dist)) - (len(dist) - 1) / 2
    mean = float((x * dist).sum())
    return float(np.sqrt(((x - mean) ** 2 * dist).sum()))
