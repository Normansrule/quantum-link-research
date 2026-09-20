"""Delegate discrete-event network simulation to SeQUeNCe; translate its results into qll objects and
check INV-1 (no herald before the light round trip) on its timeline.

Physics
-------
SeQUeNCe simulates memories, quantum and classical channels, midpoint Bell-state measurements, and the
resource/network managers that turn requests into entanglement [wu2021sequence]. This adapter builds a
two-router link with a meet-in-the-middle BSM, requests entanglement, and returns per-memory delivery
times and fidelities. The delivery time of every pair must exceed the classical herald round trip
(distance/2 to the midpoint and back, at c/n in fiber): that is the no-signaling invariant verified inside a
third-party simulator rather than in our own code.
"""
from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass

from qll.channels.light_time_delay import round_trip_delay_s

FIBER_INDEX = 1.47
SPEED_IN_FIBER_M_PER_S = 299792458.0 / FIBER_INDEX


@dataclass(frozen=True)
class LinkRun:
    distance_m: float
    delivery_times_s: tuple[float, ...]     # time from request start to each memory's entanglement
    fidelities: tuple[float, ...]
    herald_round_trip_s: float
    n_requested: int

    @property
    def n_delivered(self) -> int:
        return len(self.delivery_times_s)

    @property
    def mean_delivery_s(self) -> float:
        return sum(self.delivery_times_s) / len(self.delivery_times_s) if self.delivery_times_s else float("inf")


def two_router_link(distance_m: float, n_pairs: int = 5, memo_size: int = 20, coherence_time_s: float = 1.0,
                    raw_fidelity: float = 0.95, efficiency: float = 0.5, attenuation_db_per_m: float = 2e-4,
                    start_s: float = 1.0, stop_s: float = 4.0, target_fidelity: float = 0.8, seed: int = 0) -> LinkRun:
    """Run SeQUeNCe on a two-router meet-in-the-middle link and return delivery times and fidelities."""
    from sequence.topology.router_net_topo import RouterNetTopo

    cc_delay_ps = int(distance_m / SPEED_IN_FIBER_M_PER_S * 1e12)
    cfg = {
        "is_parallel": False, "stop_time": int(stop_s * 1e12),
        "nodes": [{"name": "r1", "type": "QuantumRouter", "seed": seed, "memo_size": memo_size},
                  {"name": "r2", "type": "QuantumRouter", "seed": seed + 1, "memo_size": memo_size}],
        "qconnections": [{"node1": "r1", "node2": "r2", "attenuation": attenuation_db_per_m, "distance": distance_m, "type": "meet_in_the_middle"}],
        "cconnections": [{"node1": "r1", "node2": "r2", "delay": cc_delay_ps}],
    }
    path = tempfile.mktemp(suffix=".json")
    with open(path, "w") as fh:
        json.dump(cfg, fh)
    topo = RouterNetTopo(path)
    tl = topo.get_timeline()
    routers = topo.get_nodes_by_type(RouterNetTopo.QUANTUM_ROUTER)
    r1 = next(r for r in routers if r.name == "r1")
    for r in routers:
        for mem in r.get_components_by_type("Memory"):
            mem.update_memory_params("coherence_time", coherence_time_s)
            mem.update_memory_params("fidelity", raw_fidelity)
            mem.update_memory_params("efficiency", efficiency)
    tl.init()
    r1.network_manager.request("r2", start_time=int(start_s * 1e12), end_time=int(stop_s * 1e12) + int(1e12),
                               memory_size=n_pairs, target_fidelity=target_fidelity)
    tl.run()
    times, fids = [], []
    for info in r1.resource_manager.memory_manager:
        if info.state == "ENTANGLED":
            times.append(info.entangle_time / 1e12 - start_s)
            fids.append(float(info.fidelity))
    return LinkRun(distance_m, tuple(sorted(times)), tuple(fids), round_trip_delay_s(distance_m / 2 * FIBER_INDEX), n_pairs)
