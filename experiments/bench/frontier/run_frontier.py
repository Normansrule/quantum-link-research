"""Run the free cloud-processor milestones of mission Phase 4: teleportation with feed-forward (M4.1) and superdense
coding (M4.2), each with its control. Writes one JSON per run with the configuration, the counts, and the verdict.

    python experiments/bench/frontier/run_frontier.py teleport --backend aer
    python experiments/bench/frontier/run_frontier.py teleport --backend fake_torino --layout 0 1 2
    python experiments/bench/frontier/run_frontier.py superdense --backend ibm_torino --layout 0 1
    python experiments/bench/frontier/run_frontier.py majorana --backend aer                       # M4.6, protocol P13
    python experiments/bench/frontier/run_frontier.py analyze results/*.json

`aer` is the ideal simulator (add --noise 0.05 for a depolarized pair); `fake_<name>` a noisy local copy of a
device; any other name a real device through a saved IBM Quantum account. Teleportation runs all three modes
(feed-forward, deferred, no bits); on a device without feed-forward the feed-forward mode is skipped and recorded.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from qll.circuits import cloud_run as R  # noqa: E402
from qll.circuits import majorana_cloud as MC  # noqa: E402
from qll.circuits import superdense_cloud as S  # noqa: E402
from qll.circuits import teleport_cloud as T  # noqa: E402


def _run(a, circuits):
    if a.backend == "aer":
        nm = T.noise_model_depolarizing(a.noise) if a.noise else None
        return R.run_aer(circuits, a.shots, a.seed, nm, "density_matrix" if nm else "automatic")
    return R.run_backend(R.get_backend(a.backend), circuits, a.shots, a.layout, a.seed)


def _save(a, kind, payload) -> Path:
    utc = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    rec = {"experiment": kind, "utc": utc, "backend": a.backend, "layout": a.layout, "shots_per_circuit": a.shots,
           "noise_injected": a.noise, "seed": a.seed, **payload}
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    path = out / f"{kind.split()[0]}_{a.backend}_{utc.replace(':', '')}.json"
    path.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(f"wrote {path}")
    return path


def cmd_teleport(a) -> Path:
    ff = a.backend == "aer" or R.supports_feedforward(R.get_backend(a.backend))
    runs = {}
    for mode in T.MODES:
        if mode == "feedforward" and not ff:
            runs[mode] = {"skipped": "backend has no feed-forward"}
            continue
        counts = _run(a, T.circuits(mode))
        v = T.analyze(counts, mode)
        runs[mode] = {"counts": counts, "verdict": v.row()}
        print(f"{mode:>12}: average fidelity {v.average:.4f} [{v.interval[0]:.4f}, {v.interval[1]:.4f}]"
              f"{'  above the classical 2/3' if v.beats_classical else ''}")
    return _save(a, "teleport (M4.1)", {"states": list(T.CARDINAL), "runs": runs})


def cmd_majorana(a) -> Path:
    ff = a.backend == "aer" or R.supports_feedforward(R.get_backend(a.backend))
    runs = {}
    for mode in MC.MODES:
        if mode != "no_bits" and not ff:
            runs[mode] = {"skipped": "backend has no feed-forward"}
            continue
        counts = _run(a, MC.circuits(mode))
        v = T.analyze(counts, mode)
        runs[mode] = {"counts": counts, "verdict": v.row(), "expected_ideal": MC.EXPECTED[mode]}
        print(f"{mode:>14}: average fidelity {v.average:.4f} [{v.interval[0]:.4f}, {v.interval[1]:.4f}] (ideal {MC.EXPECTED[mode]:.3f})")
    return _save(a, "majorana (M4.6)", {"states": list(T.CARDINAL), "runs": runs})


def cmd_superdense(a) -> Path:
    runs = {}
    for mode in S.MODES:
        counts = _run(a, S.circuits(mode))
        v = S.analyze(counts, mode)
        runs[mode] = {"counts": counts, "verdict": v.row(), "confusion": v.confusion.tolist()}
        print(f"{mode:>12}: success {v.success:.4f}, {v.bits_per_use:.3f} bits per use")
    return _save(a, "superdense (M4.2)", {"messages": [list(m) for m in S.MESSAGES], "runs": runs})


def cmd_analyze(a) -> None:
    for f in a.files:
        rec = json.loads(Path(f).read_text(encoding="utf-8"))
        for mode, r in rec["runs"].items():
            if "skipped" in r:
                print(f"{Path(f).name} {mode}: skipped ({r['skipped']})"); continue
            if rec["experiment"].startswith(("teleport", "majorana")):
                v = T.analyze(r["counts"], mode)
                print(f"{Path(f).name} {mode}: F = {v.average:.4f} [{v.interval[0]:.4f}, {v.interval[1]:.4f}]")
            else:
                v = S.analyze(r["counts"], mode)
                print(f"{Path(f).name} {mode}: success {v.success:.4f}, {v.bits_per_use:.3f} bits per use")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("teleport", "superdense", "majorana"):
        p = sub.add_parser(name)
        p.add_argument("--backend", default="aer"); p.add_argument("--shots", type=int, default=4000)
        p.add_argument("--layout", type=int, nargs="+", default=None); p.add_argument("--noise", type=float, default=0.0)
        p.add_argument("--seed", type=int, default=0); p.add_argument("--out", default="results")
    z = sub.add_parser("analyze"); z.add_argument("files", nargs="+")
    a = ap.parse_args(argv)
    return {"teleport": cmd_teleport, "superdense": cmd_superdense, "majorana": cmd_majorana, "analyze": cmd_analyze}[a.cmd](a)


if __name__ == "__main__":
    main()
