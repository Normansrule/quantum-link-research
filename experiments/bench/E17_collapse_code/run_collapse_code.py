"""Run the collapse-code experiment (experiments/proposed/E17, protocol P11) and analyze it.

    python experiments/bench/E17_collapse_code/run_collapse_code.py run --backend aer --scheme basis --shots 20000
    python experiments/bench/E17_collapse_code/run_collapse_code.py run --backend fake_torino --layout 0 1
    python experiments/bench/E17_collapse_code/run_collapse_code.py run --backend ibm_torino --layout 0 1 --repeats 5
    python experiments/bench/E17_collapse_code/run_collapse_code.py analyze results/*.json

`aer` is the ideal simulator; `fake_<name>` rehearses on a noisy local copy of a real device; any other name runs on
IBM Quantum hardware through a saved account (QiskitRuntimeService.save_account). Each run writes one JSON file with
the configuration, the counts, and the verdict, so the analysis can be repeated by anyone from the file alone.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from qll.circuits import collapse_signalling as C  # noqa: E402


def _backend(name: str):
    if name.startswith("fake_"):
        import qiskit_ibm_runtime.fake_provider as fp
        cls = "Fake" + name[5:].capitalize()
        return getattr(fp, cls)()
    from qiskit_ibm_runtime import QiskitRuntimeService
    return QiskitRuntimeService().backend(name)


def _verdict(counts) -> dict:
    x, b = C.counts_to_outcomes({int(k): v for k, v in counts.items()})
    v = C.analyze(x, b)
    return {"n": int(v.table.sum()), "p1_given_x": list(map(float, v.p1_given_x)), "bias": float(v.bias),
            "bias_interval_99": list(map(float, v.bias_interval)), "g": v.g_statistic, "p_value": v.p_value,
            "mi_upper_bits_per_use_99": v.mi_upper, "signalling_detected": bool(v.signalling_detected)}


def cmd_run(a) -> Path:
    if a.backend == "aer":
        counts = C.run_aer(a.scheme, a.shots * a.repeats, leak=a.leak, seed=a.seed)
    else:
        counts = C.run_on_backend(_backend(a.backend), a.scheme, a.shots, tuple(a.layout), a.repeats, a.seed)
    rec = {"experiment": "E17 collapse code", "utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "backend": a.backend, "scheme": a.scheme, "layout": a.layout, "shots_per_circuit": a.shots,
           "repeats": a.repeats, "leak_injected": a.leak, "seed": a.seed, "counts": counts, "verdict": _verdict(counts)}
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    path = out / f"{a.backend}_{a.scheme}_q{a.layout[0]}-{a.layout[1]}_{rec['utc'].replace(':', '')}.json"
    path.write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(json.dumps(rec["verdict"], indent=1)); print(f"wrote {path}")
    return path


def cmd_analyze(a) -> None:
    for f in a.files:
        rec = json.loads(Path(f).read_text(encoding="utf-8"))
        v = _verdict(rec["counts"])
        print(f"{Path(f).name}: n={v['n']:,}  bias={v['bias']:+.4f}  p={v['p_value']:.3g}  "
              f"I<={v['mi_upper_bits_per_use_99']:.2e} bit/use  {'SIGNAL (check for crosstalk)' if v['signalling_detected'] else 'no signal'}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--backend", default="aer"); r.add_argument("--scheme", choices=C.SCHEMES, default="basis")
    r.add_argument("--shots", type=int, default=4000); r.add_argument("--repeats", type=int, default=1)
    r.add_argument("--layout", type=int, nargs=2, default=[0, 1]); r.add_argument("--leak", type=float, default=0.0)
    r.add_argument("--seed", type=int, default=0); r.add_argument("--out", default="results")
    z = sub.add_parser("analyze"); z.add_argument("files", nargs="+")
    a = ap.parse_args(argv)
    return cmd_run(a) if a.cmd == "run" else cmd_analyze(a)


if __name__ == "__main__":
    main()
