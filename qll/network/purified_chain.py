"""A nested repeater chain with entanglement purification between swap levels, and the design space it opens.

Physics
-------
repeater_chain.memory_chain swaps Werner pairs up 2^n segments; each swap maps the fraction f to f^2 + (1-f)^2/3 and
storage pulls it toward 1/4, so long chains deliver fast but useless pairs (learn 03/19). Purification trades pairs
for fidelity: one BBPSSW round takes two pairs of fraction f and, with probability p(f), returns one of fraction f'
[bennett1996]; the nested "purify, then swap" scheme is the original repeater proposal [briegel1998] [dur1999].

This module adds r_k BBPSSW rounds at nesting level k (k = 0 for the elementary pairs, up to k = n for the end-to-end
pair) to the same closed-form bookkeeping as swapping_scheduler.nested_expected_time_s:
  - waiting, in units of the elementary attempt period t0: a purification round needs two pairs of the current
    level (the expected maximum of two geometric waits) and succeeds with p(f); a swap needs two purified pairs and
    succeeds with P_s;
  - classical heralds: every swap and every purification round costs one round trip over the span of the pair;
  - fidelity: the swapping and BBPSSW recurrences level by level, then storage decay over the expected total time,
    exactly as memory_chain does (so r_k = 0 everywhere reproduces memory_chain to machine precision).
The same simplifications apply (repeater_montecarlo shows the waiting-time closed form is conservative by a few
percent without purification). Distances in km, times in seconds.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.channels.fiber_loss import transmittance
from qll.channels.light_time_delay import round_trip_delay_s
from qll.circuits.entanglement_swapping import swapped_fraction_analytic
from qll.network.memory_decoherence import fraction_after_storage_analytic
from qll.network.purification import bbpssw_step
from qll.network.repeater_chain import FIBER_INDEX, ChainResult, direct_rate_hz
from qll.network.swapping_scheduler import expected_max_of_two_geometric


@dataclass(frozen=True)
class PurifiedChainResult(ChainResult):
    rounds: tuple[int, ...]
    pairs_per_output: float          # elementary pairs consumed per end-to-end pair (expected)

    @property
    def teleport_fidelity(self) -> float:
        return (2 * self.fidelity_fraction + 1) / 3


def _wait(attempts: float) -> float:
    return expected_max_of_two_geometric(1 / attempts) if attempts > 1 else 1.0


def purified_chain(L_km: float, n_levels: int, T_mem_s: float, rounds=None, R_attempt: float = 1e6,
                   p_src: float = 0.05, p_swap: float = 0.5, f0: float = 0.95, alpha: float = 0.2) -> PurifiedChainResult:
    """Rate, delivered fraction, and cost of a 2^n-segment chain with rounds[k] BBPSSW rounds at level k."""
    for v in (L_km, T_mem_s, p_src, p_swap, f0):
        if isinstance(v, (complex, np.complexfloating)):
            raise TypeError("chain parameters must be real")
    rounds = tuple(int(r) for r in (rounds if rounds is not None else [0] * (n_levels + 1)))
    if len(rounds) != n_levels + 1 or min(rounds) < 0:
        raise ValueError("rounds needs one non-negative entry per level 0..n")
    n_seg = 2**n_levels
    L0 = L_km / n_seg
    p0 = p_src * transmittance(L0 / 2, alpha) ** 2
    t0 = round_trip_delay_s(L0 * 1e3 / 2 * FIBER_INDEX)
    span_rt = lambda k: round_trip_delay_s(L0 * 1e3 * 2**k * FIBER_INDEX / 2)

    attempts, f, heralds, pairs = 1 / p0, f0, 0.0, 1.0
    for k in range(n_levels + 1):
        for _ in range(rounds[k]):                      # purify at level k
            f_new, p_pur = bbpssw_step(f)
            attempts = _wait(attempts) / p_pur
            heralds += span_rt(k)
            pairs = 2 * pairs / p_pur
            f = f_new
        if k < n_levels:                                # swap up to level k + 1
            attempts = _wait(attempts) / p_swap
            heralds += span_rt(k)
            pairs = 2 * pairs / p_swap
            f = swapped_fraction_analytic(f)
    T_n = max(attempts * t0 + heralds, 1 / (p0 * R_attempt))
    f = fraction_after_storage_analytic(f, T_n, T_mem_s)
    stalled = T_n > 3 * T_mem_s
    return PurifiedChainResult(0.0 if stalled else 1.0 / T_n, f, T_n, n_seg, rounds, pairs)


def best_useful_chain(L_km: float, T_mem_s: float, max_levels: int = 4, max_rounds: int = 2, **kw):
    """The fastest configuration (levels n <= max_levels, the same r <= max_rounds rounds at every level, or rounds
    only at the elementary level) that delivers teleportation fidelity above 2/3; None if no configuration does."""
    best = None
    for n in range(max_levels + 1):
        schedules = {(r,) * (n + 1) for r in range(max_rounds + 1)} | {(r,) + (0,) * n for r in range(max_rounds + 1)}
        for sch in sorted(schedules):
            res = purified_chain(L_km, n, T_mem_s, sch, **kw)
            if res.rate_hz > 0 and res.teleport_fidelity > 2 / 3 and (best is None or res.rate_hz > best.rate_hz):
                best = res
    return best


def useful_advantage_map(L_grid_km, T_grid_s, **kw) -> np.ndarray:
    """log10(best useful chain rate / direct rate) on a (T, L) grid; NaN where no configuration is useful."""
    out = np.full((len(T_grid_s), len(L_grid_km)), np.nan)
    for i, T in enumerate(T_grid_s):
        for j, L in enumerate(L_grid_km):
            b = best_useful_chain(float(L), float(T), **kw)
            if b is not None:
                out[i, j] = np.log10(b.rate_hz / direct_rate_hz(float(L)))
    return out


def minimum_useful_memory_s(L_km: float, T_lo: float = 1e-2, T_hi: float = 1e6, **kw) -> float | None:
    """Shortest memory coherence time for which some configuration delivers useful pairs (F > 2/3) faster than direct
    transmission over L_km; None if even T_hi is not enough. Bisection in log T (the advantage grows with T)."""
    def ok(T: float) -> bool:
        b = best_useful_chain(L_km, T, **kw)
        return b is not None and b.rate_hz > direct_rate_hz(L_km)
    if not ok(T_hi):
        return None
    if ok(T_lo):
        return T_lo
    lo, hi = np.log10(T_lo), np.log10(T_hi)
    while hi - lo > 1e-3:
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if ok(10**mid) else (mid, hi)
    return float(10**hi)


def useful_distance_range_km(T_mem_s: float, retrieval_efficiency: float = 1.0, L_grid_km=None, p_swap: float = 0.5,
                             **kw) -> tuple[float, float] | None:
    """Distances at which a chain of memories with this coherence time and retrieval efficiency delivers useful pairs
    faster than direct transmission. A swap needs both memories read out, so its success is P_s * eta_ret^2."""
    grid = L_grid_km if L_grid_km is not None else np.logspace(2, np.log10(5000), 240)
    good = [float(L) for L in grid
            if (b := best_useful_chain(float(L), T_mem_s, p_swap=p_swap * retrieval_efficiency**2, **kw)) is not None
            and b.rate_hz > direct_rate_hz(float(L))]
    return (min(good), max(good)) if good else None
