"""Write docs/network/data.json for the network page from the tested models, so the page replays computed runs rather
than inventing its own: the three-node entanglement service (qll/network/pair_ledger.py) for two memory lifetimes and
two serving policies, the logical-memory scan at distances 3, 5, and 7 (qll/circuits/logical_memory.py), and the
mountain mesh (qll/link/mesh_messenger.py). Every number on the page is labelled SIMULATED.

    python scripts/build_network_data.py
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "docs" / "network" / "data.json"
QEC_PS = (0.001, 0.002, 0.004, 0.006, 0.008, 0.012)


def service_runs() -> dict:
    from qll.network.pair_ledger import ChainDesign, freshest_first, oldest_first, simulate_service
    runs = {}
    for t_mem in (0.5, 5.0):
        for pol in (oldest_first, freshest_first):
            r = simulate_service(ChainDesign(t_mem_s=t_mem), demand_hz=2.0, horizon_s=30.0, seed=7, policy=pol)
            runs[f"{t_mem:g}s/{pol.__name__}"] = {k: r[k] for k in ("design", "policy", "requests", "served", "missed", "availability",
                                                                   "mean_fidelity", "mean_wait_s", "counts", "kinds", "swap_failures",
                                                                   "end_to_end_rate_hz", "samples")}
    return runs


def qec_scan(shots: int = 20_000) -> dict:
    from qll.circuits import logical_memory as LM
    return {"ps": list(QEC_PS), "resources": [asdict(LM.resources(d)) for d in LM.DISTANCES],
            "rows": {str(d): [LM.logical_error(d, p, shots=shots, seed=100 + 10 * d + i) for i, p in enumerate(QEC_PS)] for d in LM.DISTANCES}}


def mesh_summary() -> dict:
    from qll.link import mesh_messenger as M
    out = {}
    for relay in (True, False):
        mesh = M.mountain_scenario(relay)
        d = M.send(mesh, "hiker A", "hiker B")
        out["with ridge relay" if relay else "without ridge relay"] = {
            "nodes": [{"name": n.name, "x_km": n.x_km, "y_km": n.y_km, "height_m": n.height_m, "relay": n.relay} for n in mesh.nodes.values()],
            "links": sorted([sorted([a, b]) for a in mesh.nodes for b in mesh.neighbours(a) if a < b]),
            "state": d.state, "history": d.history, "airtime_64B_s": M.time_on_air_s(64, mesh.sf, mesh.bw_hz)}
    return out


def compute() -> dict:
    return {"label": "SIMULATED: model outputs from the tested code, not measurements", "service": service_runs(),
            "qec": qec_scan(), "mesh": mesh_summary()}


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(compute(), indent=1, default=float) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
