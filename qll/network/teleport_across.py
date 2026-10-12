"""Teleportation across a distance with entanglement banked in memories, directly or through a swapping node
(milestones M4.3, M4.4, and M4.5; proposal E01). The twin of the frontier lab.

Physics
-------
Pairs are made ahead of time and their halves held in a memory at each end; the message moment needs only Alice's
Bell measurement and two classical bits [bennett1993]. Every step is timed by light: the bits take t_c = n L / c to
reach Bob (light_time_delay.py), and Bob must hold his half until they arrive. Nothing about Bob's qubit changes
before then; averaged over Alice's outcomes it is I/2, so his fidelity without the bits is 1/2 [peres2004].

Memory. A depolarizing memory multiplies the Werner parameter w = (4 f - 1)/3 of a stored pair by exp(-t/T_mem)
(memory_decoherence.fraction_after_storage_analytic) [werner1989]. Alice's half waits the banking time t_b, Bob's
waits t_b + t_c, so
    w = w0 exp(-(2 t_b + t_c) / T_mem),    f = (3 w + 1)/4,
and the teleportation fidelity is F = (2 f + 1)/3 [horodecki1996], which beats every measure-and-prepare strategy
(2/3) only while f > 1/2 [massar1995]. Hence the bank must be used within
    t_b < (T_mem ln(4 f0 - 1) - t_c)/2,
and a link of light time t_c needs T_mem > t_c / ln(4 f0 - 1) even with no banking at all. Each use succeeds with
probability eta_mem^2 p_bsm (two retrievals and one Bell measurement, which linear optics completes half the time
[calsamiglia2001]). Memory coherence times come from the cited experiments; their photon efficiencies are assumed
operating points (memory_decoherence.MemoryPlatform), so success rates here are conditional on those assumptions.

Swapping node. With a node C halfway, pairs A-C and C-B of fractions f1 and f2 become one A-B pair when C measures
in the Bell basis; for Werner pairs the Werner parameters multiply, f = f1 f2 + (1 - f1)(1 - f2)/3
(entanglement_swapping.swapped_fraction_analytic for f1 = f2) [zukowski1993] [briegel1998]. A and B each wait
L/2 at light speed for C's announcement [hermans2022]. C's outcomes are uniformly random and independent of the
pair it creates, so C learns nothing about a key made from it, unlike a trusted relay that holds both keys
[dur1999]. Each segment heralds with its fiber transmittance eta(L/2) = 10^(-alpha L/20); with memories the two
segments wait for each other (expected rounds E[max of two geometric]) instead of needing both photons at once, so
the attempts per end-to-end pair fall from 1/eta(L) to about 3/(2 eta(L/2)) [sangouard2011].
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

from qll.channels.fiber_loss import transmittance
from qll.channels.light_time_delay import one_way_delay_s
from qll.constants.astro import EARTH_MARS_MAX_M, EARTH_MARS_MIN_M
from qll.network.memory_decoherence import MEMORY_TABLE
from qll.network.swapping_scheduler import expected_max_of_two_geometric

FIBER_INDEX = 1.47
CLASSICAL_LIMIT = 2 / 3
SCENARIOS: dict[str, tuple[float, float]] = {        # name: (distance in metres, refractive index of the classical path)
    "two rooms": (10.0, FIBER_INDEX),
    "campus": (1.0e3, FIBER_INDEX),
    "city to city, 100 km fiber": (1.0e5, FIBER_INDEX),
    "Los Angeles to New York, 3,940 km": (3.94e6, FIBER_INDEX),   # great-circle distance, as fiber
    "low Earth orbit, 1,000 km": (1.0e6, 1.0),
    "the Moon": (3.844e8, 1.0),
    "Mars at its closest": (EARTH_MARS_MIN_M, 1.0),
    "Mars at its farthest": (EARTH_MARS_MAX_M, 1.0),
}
MEMORIES = {m.name: m for m in MEMORY_TABLE}


@dataclass(frozen=True)
class Link:
    distance_m: float = 10.0
    index: float = FIBER_INDEX       # 1.47 for fiber, 1 for free space
    f0: float = 0.95                 # fully entangled fraction when the pair is made
    T_mem_s: float = 1.0             # memory lifetime at both ends (depolarizing model)
    bank_s: float = 0.0              # how long the pair waited in both memories before Alice used it
    eta_mem: float = 0.9             # retrieval efficiency of each memory
    p_bsm: float = 0.5               # Bell-measurement success: 1/2 with linear optics, near 1 with matter qubits


def werner(f: float) -> float:
    return (4 * f - 1) / 3


def fraction(w: float) -> float:
    return (3 * w + 1) / 4


def light_time_s(distance_m: float, index: float = FIBER_INDEX) -> float:
    return one_way_delay_s(index * distance_m)


def link(p: Link = Link()) -> dict:
    """Timeline and fidelity of one teleportation from banked pairs."""
    tc = light_time_s(p.distance_m, p.index)
    tA, tB = p.bank_s, p.bank_s + tc
    f = fraction(werner(p.f0) * math.exp(-(tA + tB) / p.T_mem_s))
    ln = math.log(4 * p.f0 - 1) if p.f0 > 0.5 else 0.0
    return {"light_time_s": tc, "alice_wait_s": tA, "bob_wait_s": tB, "fraction": f,
            "fidelity_with_bits": (2 * f + 1) / 3, "fidelity_without_bits": 0.5,
            "beats_classical": (2 * f + 1) / 3 > CLASSICAL_LIMIT, "success_per_use": p.eta_mem ** 2 * p.p_bsm,
            "max_bank_s": max(0.0, (p.T_mem_s * ln - tc) / 2) if ln > 0 else 0.0,
            "min_memory_s": tc / ln if ln > 0 else math.inf,
            "events": [("pair made", -p.bank_s, None), ("Alice's Bell measurement", 0.0, 0.0), ("bits arrive; Bob corrects", tc, 1.0)]}


def for_scenario(name: str, memory: str, **kw) -> dict:
    L, n = SCENARIOS[name]
    m = MEMORIES[memory]
    return link(Link(distance_m=L, index=n, T_mem_s=m.lifetime_s, eta_mem=m.efficiency, **kw))


def memory_table(f0: float = 0.95) -> dict[str, dict[str, bool]]:
    """Which memory survives which scenario with no banking: F > 2/3 when the bits arrive."""
    return {m.name: {s: for_scenario(s, m.name, f0=f0)["beats_classical"] for s in SCENARIOS} for m in MEMORY_TABLE}


@dataclass(frozen=True)
class Swap:
    distance_m: float = 20.0          # A to B, with the swapping node C halfway
    index: float = FIBER_INDEX
    f0: float = 0.95                  # each segment's pair
    T_mem_s: float = 1.0
    alpha_db_per_km: float = 0.2
    p_swap: float = 0.5               # C's Bell measurement


def swapped_fraction(f1: float, f2: float) -> float:
    return f1 * f2 + (1 - f1) * (1 - f2) / 3


def swap(s: Swap = Swap()) -> dict:
    """One end-to-end pair through the node, then a teleportation from A to B with it."""
    half = light_time_s(s.distance_m / 2, s.index)
    w = werner(swapped_fraction(s.f0, s.f0)) * math.exp(-2 * half / s.T_mem_s)        # A and B wait for C's announcement
    f_pair = fraction(w)
    tele = link(Link(distance_m=s.distance_m, index=s.index, f0=f_pair, T_mem_s=s.T_mem_s))
    L_km = s.distance_m / 1e3
    eta_full, eta_seg = transmittance(L_km, s.alpha_db_per_km), transmittance(L_km / 2, s.alpha_db_per_km)
    return {"half_light_time_s": half, "pair_fraction": f_pair, "direct_fraction": s.f0,
            "fidelity_with_bits": tele["fidelity_with_bits"], "beats_classical": tele["beats_classical"],
            "announce_s": half, "teleport_s": tele["light_time_s"], "total_s": half + tele["light_time_s"],
            "eta_direct": eta_full, "eta_segment": eta_seg,
            "attempts_direct": 1 / eta_full, "attempts_swapped": expected_max_of_two_geometric(eta_seg) / s.p_swap,
            "node_learns_key": False, "trusted_relay_learns_key": True}


def with_memory(p: Link, memory: str) -> Link:
    m = MEMORIES[memory]
    return replace(p, T_mem_s=m.lifetime_s, eta_mem=m.efficiency)
