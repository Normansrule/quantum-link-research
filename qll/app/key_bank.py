"""A key bank: how much secret key to store so that a messenger that fails closed never has to refuse.

Physics and method
------------------
Quantum key arrives unevenly. Over a synodic period the Earth-Mars link makes key at a daily rate s_t that swings by
two orders of magnitude with range and drops to zero for the weeks of solar conjunction, while the messenger spends it
at a demand d_t. Key is classical once distilled, so, unlike an entangled pair, it can be stored for as long as the
store stays secret. Sizing that store is the reservoir problem of hydrology, and the sequent-peak rule solves it
[loucks2017]: accumulate the deficit
    S_t = max(0, S_{t-1} + d_t - s_t),   S_0 = 0,
over two repetitions of a periodic record (the second captures a deficit that wraps around the end of the first);
the capacity K = max_t S_t is the smallest bank that, starting full, never refuses. The level of a bank of capacity C
that starts full obeys L_t = min(C, L_{t-1} + s_t - d_t), so K - L_t = S_t exactly as long as nothing is refused,
which is how the rule is tested. A demand above the mean supply cannot be sustained by any bank.

Spending: a one-time pad consumes one key bit per message bit and is information-theoretically secure
[vernam1926] [shannon1949]; a hybrid session key (qll/app/hybrid_kem.py) consumes 256 bits per session.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

AES_KEY_BITS = 256


def _series(x, n: int | None = None) -> np.ndarray:
    if np.iscomplexobj(np.asarray(x)):
        raise TypeError("key flows must be real")
    a = np.asarray(x, dtype=float)
    if a.ndim == 0:
        a = np.full(n or 1, float(a))
    if np.any(a < 0) or not np.all(np.isfinite(a)):
        raise ValueError("key flows must be finite and non-negative")
    return a


def sequent_peak(supply, demand, cycles: int = 2) -> float:
    """Smallest capacity (bits) that, starting full, meets `demand` from the periodic `supply` without refusal."""
    s = _series(supply)
    d = _series(demand, len(s))
    if len(d) != len(s):
        raise ValueError("supply and demand must have the same length")
    S = K = 0.0
    for _ in range(cycles):
        for st, dt in zip(s, d):
            S = max(0.0, S + dt - st)
            K = max(K, S)
    return K


@dataclass(frozen=True)
class BankRun:
    level: np.ndarray          # bits in the bank at the end of each day
    served: np.ndarray         # bits spent each day
    refused: np.ndarray        # demand that could not be met each day (the messenger fails closed)

    @property
    def refused_days(self) -> int:
        """Days with a shortfall larger than floating-point rounding (one part in 10^9 of that day's demand)."""
        return int(np.sum(self.refused > 1e-9 * (self.served + self.refused)))


def simulate(supply, demand, capacity: float, level0: float | None = None) -> BankRun:
    """Day-by-day bank: serve what the level plus today's key allows, keep the rest up to the capacity."""
    s = _series(supply)
    d = _series(demand, len(s))
    C = float(capacity)
    L = C if level0 is None else float(level0)
    level, served, refused = np.empty(len(s)), np.empty(len(s)), np.empty(len(s))
    for i, (st, dt) in enumerate(zip(s, d)):
        use = min(dt, L + st)
        L = min(C, L + st - use)
        level[i], served[i], refused[i] = L, use, dt - use
    return BankRun(level, served, refused)


def sustainable_demand(supply) -> float:
    """The largest constant daily demand any bank can carry: the mean supply."""
    return float(np.mean(_series(supply)))


def max_demand_for_capacity(supply, capacity: float, tol: float = 1e-9) -> float:
    """Largest constant daily demand a bank of `capacity` carries without refusal (bisection; K rises with demand)."""
    s = _series(supply)
    lo, hi = 0.0, float(np.mean(s))
    if sequent_peak(s, hi) <= capacity:
        return hi
    while hi - lo > tol * max(hi, 1.0):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if sequent_peak(s, mid) <= capacity else (lo, mid)
    return lo
