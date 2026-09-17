"""Repeaterless secret-key capacity bound (PLOB).

Physics
-------
For a lossy channel of transmittance eta, no repeaterless protocol can exceed
K = -log2(1 - eta) secret bits per channel use [pirandola2017]; for eta << 1 this is ~1.44 eta.
"""
from __future__ import annotations

import math


def plob_bits_per_use(eta: float) -> float:
    if not 0.0 <= eta < 1.0:
        raise ValueError("eta must lie in [0, 1)")
    return -math.log2(1.0 - eta)
