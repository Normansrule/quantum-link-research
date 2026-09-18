"""Entanglement-based QKD certified by a Bell violation.

Physics
-------
Alice and Bob share Bell pairs; matched-basis outcomes form the key, mismatched settings estimate the
CHSH value S [ekert1991] [bennett1992bbm]. Device-independent rate against collective attacks:
r >= 1 - h2((1 + sqrt(S^2/4 - 1))/2) - h2(Q) [acin2007] [pironio2009]; for the ideal S = 2 sqrt 2, Q = 0
this gives 1 bit per matched round. Settings come from a declared EntropySource (INV-7); the settings and
outcomes must be exchanged classically, so certification under planetary latency is proposal E10.
"""
from __future__ import annotations

import math

from qll.qkd.binary_entropy import h2


def di_rate_per_round(S: float, Q: float) -> float:
    if S <= 2.0:
        return 0.0
    S = min(S, 2 * math.sqrt(2))
    return max(0.0, 1 - h2((1 + math.sqrt(S**2 / 4 - 1)) / 2) - h2(Q))


def e91_rate_from_werner(f: float) -> float:
    """Rate when the shared pairs are Werner states of fraction f: S = 2 sqrt 2 (4f-1)/3, Q = (1-f)*2/3."""
    S = 2 * math.sqrt(2) * (4 * f - 1) / 3
    Q = 2 * (1 - f) / 3
    return di_rate_per_round(S, Q)
