"""A chain of memory nodes versus direct transmission, and the all-photonic alternative.

Physics
-------
Direct: R_direct = R_src * eta(L), eta = 10^(-alpha L/10) (exponential in L).
Memory-based nested repeater [briegel1998] [sangouard2011]: elementary segments of length L0 = L/2^n succeed
per attempt with p0 = p_src * eta(L0/2)^2 (two photons meet at a midpoint); pairs are swapped up the nesting
tree with success P_s; the end-to-end time is nested_expected_time_s; the fidelity after 2^n - 1 swaps of
Werner pairs with fraction f is f_end with f_end from the swapping recurrence f' = f^2 + (1-f)^2/3 applied
n times; memory decoherence over the hold time multiplies the fraction by exp(-T_hold/T_mem) toward 1/4.
Rate: R = 1 / T_n, valid when the memory cutoff exceeds T_n (else the chain stalls: rate -> 0).
All-photonic repeater [azuma2015]: no memories; each node emits a redundantly encoded photonic graph
state and loss is tolerated per segment with probability p_fusion = 1 - (1 - eta_seg * eta_det)^m for m
redundant photons per arm; end-to-end rate R_ap = R_src * prod_segments p_fusion, at the cost of
~m photons per segment per attempt. Both models are deliberately simple and documented as such; the
must-pass target (REQ-NET-001) is the *existence* of a crossover distance beyond which the chain beats direct.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from qll.channels.fiber_loss import transmittance
from qll.circuits.entanglement_swapping import swapped_fraction_analytic
from qll.network.memory_decoherence import fraction_after_storage_analytic
from qll.network.swapping_scheduler import nested_expected_time_s

FIBER_INDEX = 1.47


@dataclass(frozen=True)
class ChainResult:
    rate_hz: float
    fidelity_fraction: float
    hold_time_s: float
    n_segments: int


def direct_rate_hz(L_km: float, R_src: float = 1e9, p_src: float = 0.05, alpha: float = 0.2) -> float:
    return R_src * p_src * transmittance(L_km, alpha)


def memory_chain(L_km: float, n_levels: int, T_mem_s: float, R_attempt: float = 1e6, p_src: float = 0.05,
                 p_swap: float = 0.5, f0: float = 0.95, alpha: float = 0.2) -> ChainResult:
    n_seg = 2**n_levels
    L0 = L_km / n_seg
    p0 = p_src * transmittance(L0 / 2, alpha) ** 2
    T_n = nested_expected_time_s(L_km * 1e3, n_levels, p0, p_swap, FIBER_INDEX)
    # attempts are limited by the attempt rate too
    T_n = max(T_n, 1 / (p0 * R_attempt))
    f = f0
    for _ in range(n_levels):
        f = swapped_fraction_analytic(f)
    f = fraction_after_storage_analytic(f, T_n, T_mem_s)
    stalled = T_n > 3 * T_mem_s                       # memory cutoff: pairs expire before the chain completes
    rate = 0.0 if stalled else 1.0 / T_n
    return ChainResult(rate, f, T_n, n_seg)


def all_photonic_chain(L_km: float, n_segments: int, m_redundant: int = 8, R_src: float = 1e6,
                       eta_det: float = 0.9, alpha: float = 0.2) -> float:
    eta_seg = transmittance(L_km / n_segments / 2, alpha)   # each photon travels half a segment to a fusion midpoint
    p_fusion = 1 - (1 - eta_seg * eta_det) ** m_redundant
    return R_src * p_fusion ** n_segments


def crossover_distance_km(n_levels: int, T_mem_s: float, L_grid_km=None, **kw) -> float | None:
    """Smallest distance at which the memory chain beats direct transmission (REQ-NET-001), or None."""
    import numpy as np
    grid = L_grid_km if L_grid_km is not None else np.logspace(1, 4, 400)
    for L in grid:
        if memory_chain(L, n_levels, T_mem_s, **kw).rate_hz > direct_rate_hz(L):
            return float(L)
    return None
