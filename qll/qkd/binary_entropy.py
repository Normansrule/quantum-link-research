"""Binary Shannon entropy.

Physics
-------
h2(x) = -x log2 x - (1-x) log2 (1-x), with h2(0) = h2(1) = 0 [nielsen2010].
"""
from __future__ import annotations

import math


def h2(x: float) -> float:
    if not 0.0 <= x <= 1.0:
        raise ValueError("argument must lie in [0, 1]")
    if x in (0.0, 1.0):
        return 0.0
    return -x * math.log2(x) - (1.0 - x) * math.log2(1.0 - x)
