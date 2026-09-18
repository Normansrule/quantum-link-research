"""Pick a path through a graph of links maximizing end-to-end entanglement rate subject to fidelity.

Physics
-------
For a path of links with per-slot success probabilities p_i and swap success q, the greedy end-to-end rate per
slot is ~ q^(k-1) * min_i p_i for k links (the slowest link gates the chain), and the Werner fraction after
k-1 swaps of pairs with fractions f_i follows the swapping recurrence. Routing therefore maximizes the bottleneck
rate subject to a fidelity floor: a widest-path (maximin) problem on the link graph, solved here with a modified
Dijkstra over networkx [pant2019] [chakraborty2019]. Every path's classical control traffic scales with its
physical length (INV-1), which is reported as the herald round trip.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass

import networkx as nx

from qll.channels.light_time_delay import round_trip_delay_s
from qll.circuits.entanglement_swapping import swapped_fraction_analytic


@dataclass(frozen=True)
class Route:
    path: list
    bottleneck_rate: float
    fidelity_fraction: float
    herald_round_trip_s: float


def widest_path(G: nx.Graph, src, dst, q_swap: float = 0.5, f_min: float = 0.5) -> Route | None:
    """Maximize the bottleneck link rate; edges need attributes 'rate' (per slot), 'fraction' (Werner f), 'length_m'."""
    best = {src: (float("inf"), 1.0, [src])}
    heap = [(-float("inf"), src)]
    while heap:
        negw, u = heapq.heappop(heap)
        w_u, f_u, path_u = best[u]
        if u == dst:
            break
        for v, d in G[u].items():
            w = min(w_u, d["rate"])
            f = d["fraction"] if len(path_u) == 1 else _swap(f_u, d["fraction"])
            if f < f_min:
                continue
            if v not in best or w > best[v][0]:
                best[v] = (w, f, path_u + [v])
                heapq.heappush(heap, (-w, v))
    if dst not in best:
        return None
    w, f, path = best[dst]
    hops = len(path) - 1
    length = sum(G[path[i]][path[i + 1]]["length_m"] for i in range(hops))
    return Route(path, w * q_swap ** max(0, hops - 1), f, round_trip_delay_s(length))


def _swap(fa: float, fb: float) -> float:
    """Swapping two Werner pairs of different fractions: f' = fa fb + (1-fa)(1-fb)/3 [briegel1998]."""
    return fa * fb + (1 - fa) * (1 - fb) / 3


def swap_symmetric_check(f: float) -> float:
    return swapped_fraction_analytic(f)
