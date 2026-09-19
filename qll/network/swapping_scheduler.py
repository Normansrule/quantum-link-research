"""When to swap: the nested (doubling) schedule and its time cost with classical heralds.

Physics
-------
A chain of 2^n segments generates elementary pairs in parallel; at each nesting level neighbouring pairs
are swapped once both exist, and the swap outcome must be heralded classically over the span of the new
pair (INV-1). For elementary success probability p0 per attempt with attempt period t0 = L0/c (one
herald round trip for a midpoint-heralded segment), the expected time to obtain both of two independent
pairs is ~ (3/2) times the time for one [sangouard2011 §III], so the nested total is
    T_n ~ (3/2)^n * t0 / (p0 * P_s^n)  with swap success P_s,
and the memory must hold a pair for ~T_n in the worst case (this sets the cutoff in repeater_chain.py).
The exact expectation of the maximum of two geometric waiting times is used here instead of the 3/2 rule.
"""
from __future__ import annotations

import math

from qll.channels.light_time_delay import round_trip_delay_s


def expected_max_of_two_geometric(p: float) -> float:
    """E[max(X,Y)] for i.i.d. geometric(p) attempts (support 1,2,...): 2/p - 1/(1-(1-p)^2) [sangouard2011]."""
    if p >= 1.0:
        return 1.0
    if p <= 0.0:
        return float("inf")
    return 2 / p - 1 / (p * (2 - p))   # 1 - (1-p)^2 = p(2-p), written stably for tiny p


def nested_expected_time_s(L_m: float, n_levels: int, p0: float, p_swap: float, fiber_index: float = 1.47) -> float:
    """Expected time to one end-to-end pair over 2^n segments of a chain of length L (heralded at midpoints)."""
    n_seg = 2**n_levels
    L0 = L_m / n_seg
    t0 = round_trip_delay_s(L0 / 2 * fiber_index)            # elementary herald: midpoint to node and back
    attempts = 1 / p0
    for _ in range(n_levels):
        # wait for both pairs (max of two geometrics in units of the current stage), then swap
        attempts = expected_max_of_two_geometric(1 / attempts) if attempts > 1 else 1.0
        attempts = attempts / p_swap
    t_swap_heralds = sum(round_trip_delay_s(L0 * 2**k * fiber_index / 2) for k in range(n_levels))
    return attempts * t0 + t_swap_heralds


def three_halves_rule_time_s(L_m: float, n_levels: int, p0: float, p_swap: float, fiber_index: float = 1.47) -> float:
    L0 = L_m / 2**n_levels
    t0 = round_trip_delay_s(L0 / 2 * fiber_index)
    return (1.5**n_levels) * t0 / (p0 * p_swap**n_levels)
