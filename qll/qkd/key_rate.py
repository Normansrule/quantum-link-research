"""Asymptotic BB84 secret-key rate and its QBER threshold.

Physics
-------
With one-way post-processing the secret fraction per sifted bit is r = 1 - 2 h2(Q) for a
symmetric QBER Q [shor2000]. It reaches zero at Q = 0.1100 (the 11% threshold).
"""
from __future__ import annotations

from scipy.optimize import brentq

from qll.qkd.binary_entropy import h2


def bb84_rate_per_sifted_bit(Q: float) -> float:
    """max(0, 1 - 2 h2(Q)) [shor2000]."""
    return max(0.0, 1.0 - 2.0 * h2(Q))


def bb84_qber_threshold() -> float:
    """Solve 1 - 2 h2(Q) = 0 on (0, 0.5) by Brent's method; equals 0.1100 [shor2000]."""
    return float(brentq(lambda q: 1.0 - 2.0 * h2(q), 1e-6, 0.5 - 1e-6))
