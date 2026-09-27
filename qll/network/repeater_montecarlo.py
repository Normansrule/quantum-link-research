"""Monte Carlo of the nested repeater protocol, to check the closed-form waiting time it is usually summarized by.

Physics
-------
The chain of 2^n segments (repeater_chain.py) generates elementary pairs by repeated attempts: each segment succeeds
per attempt with p0, one attempt per herald round trip t0 (or per 1/R_attempt, whichever is longer). At nesting level
k, two neighbouring pairs are swapped once both exist, the outcome is heralded over the new span, and with probability
1 - P_s the swap fails, both pairs are lost, and both subtrees start again from that moment [briegel1998]
[sangouard2011]. This module samples that process exactly (geometric attempt counts, the maximum of the two children,
restart on failure) and averages it.

The closed form in swapping_scheduler.py replaces each level's waiting time by the maximum of two geometric variables
whose success probability is the reciprocal of the previous level's mean. That is exact for n = 0 and n = 1 up to the
herald bookkeeping, and an approximation above, because a level-k waiting time is not geometric. Sampling shows the
approximation is conservative: it overestimates the mean time by about 4 % for n = 2 and 8 % for n = 3 (20 000 runs,
standard error 0.6 %, P_s = 0.5; tests/test_repeater_montecarlo.py holds both numbers), so rates quoted from it are
slightly low. The gap grows as swaps become reliable (about 19 % for 8 segments at P_s = 1): with frequent failures a
level's waiting time is dominated by restarts and is close to geometric, which is what the closed form assumes.
"""
from __future__ import annotations

import math

import numpy as np

from qll.channels.fiber_loss import transmittance
from qll.channels.light_time_delay import round_trip_delay_s
from qll.network.repeater_chain import FIBER_INDEX


def _check(L_km: float, n_levels: int, p_src: float, p_swap: float) -> None:
    for v in (L_km, p_src, p_swap):
        if isinstance(v, (complex, np.complexfloating)):
            raise TypeError("repeater parameters must be real")
    if not isinstance(n_levels, (int, np.integer)) or n_levels < 0:
        raise ValueError("n_levels must be a non-negative integer")
    if not (0 < p_src <= 1 and 0 < p_swap <= 1) or L_km <= 0:
        raise ValueError("probabilities in (0, 1] and a positive length are required")


def sample_chain_time_s(L_km: float, n_levels: int, rng: np.random.Generator, p_src: float = 0.05,
                        p_swap: float = 0.5, alpha: float = 0.2, R_attempt: float = 1e6) -> float:
    """One sampled time to the first end-to-end pair."""
    _check(L_km, n_levels, p_src, p_swap)
    L0 = L_km / 2**n_levels
    p0 = p_src * transmittance(L0 / 2, alpha) ** 2
    t0 = max(round_trip_delay_s(L0 * 1e3 / 2 * FIBER_INDEX), 1 / R_attempt)

    def build(k: int, t: float) -> float:
        if k == 0:
            return t + rng.geometric(p0) * t0
        while True:
            both = max(build(k - 1, t), build(k - 1, t))
            herald = both + round_trip_delay_s(L0 * 1e3 * 2 ** (k - 1) * FIBER_INDEX / 2)
            if rng.random() < p_swap:
                return herald
            t = herald

    return build(n_levels, 0.0)


def mean_chain_time_s(L_km: float, n_levels: int, runs: int = 2000, seed: int = 0, **kw) -> tuple[float, float]:
    """Sample mean and its standard error over `runs` independent runs."""
    rng = np.random.default_rng(seed)
    x = np.array([sample_chain_time_s(L_km, n_levels, rng, **kw) for _ in range(runs)])
    return float(x.mean()), float(x.std(ddof=1) / math.sqrt(runs))
