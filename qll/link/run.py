"""python -m qll.link.run {session,validate,scenarios,demo}: the two-site link simulation from the command line.

  session   [--config FILE.json] [--set name=value ...] [--out DIR]   one session; prints the per-run summary
  validate  [--out DIR]                                                 controlled cases against the closed-form models
  scenarios [--out DIR] [--sessions]                                    scenarios 1-6 and the demonstration; writes CSVs,
                                                                        plots, and a report (about 20 s on a laptop)
  demo                                                                  deliver accepted keys to the demonstration apps
  ingest    LOG.csv [--config FILE.json] [--set ...] [--out DIR]       process an experiment's log with the same protocol

Default evidence folder: systems/see510/evidence/. Everything written there is regenerated from configurations and
seeds; rerunning reproduces every number except execution times and timestamps.
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import time
from pathlib import Path

import numpy as np

from qll.link import models, scenarios as S
from qll.link.config import LinkConfig
from qll.link.logger import write_session, write_table
from qll.link.monitor import REJECT_REASONS, summary
from qll.link.protocol_bb84 import run_session

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "systems" / "see510" / "evidence"


def _parse_set(items: list[str]) -> dict:
    out = {}
    for it in items or []:
        k, v = it.split("=", 1)
        try:
            out[k] = json.loads(v)
        except json.JSONDecodeError:
            out[k] = v
    return out


def _config(path: str | None, sets: list[str]) -> LinkConfig:
    d = json.loads(Path(path).read_text(encoding="utf-8")) if path else {}
    d.update(_parse_set(sets))
    return LinkConfig.from_dict(d)


def cmd_session(a) -> None:
    r = run_session(_config(a.config, a.set))
    print(summary(r.metrics))
    for e in r.metrics.events:
        print(f"  [{e['level']:>7}] {e['step']:<10} {e['message']}")
    if a.out:
        print(f"wrote {write_session(r, Path(a.out))}")


def _md_table(rows: list[dict], cols: list[str]) -> str:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows]
    return "\n".join(out)


def cmd_validate(a) -> list[dict]:
    rows = S.validation_checks()
    for r in rows:
        print(f"{'PASS' if r['pass'] else 'FAIL'}  {r['check']}\n      expected {r['expected']}\n      observed {r['observed']}")
    if a.out:
        Path(a.out).mkdir(parents=True, exist_ok=True)
        with open(Path(a.out) / "validation.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader(); w.writerows(rows)
    return rows


def cmd_ingest(a) -> None:
    """Process an experiment log (systems/see510/10_real_world_experiments.md) with the protocol code."""
    from qll.link.hardware_log import run_from_log
    c = _config(a.config, a.set).with_(scenario=f"experiment:{Path(a.log).stem}")
    r = run_from_log(Path(a.log), c)
    print(summary(r.metrics))
    for e in r.metrics.events:
        print(f"  [{e['level']:>7}] {e['step']:<10} {e['message']}")
    if a.out:
        print(f"wrote {write_session(r, Path(a.out))}")


def cmd_demo(a) -> dict:
    d = S.demonstration()
    print(f"accepted session {d['accepted_session'].run_id}: {d['keys_from_good']} keys of 256 bits delivered to both sites")
    print(f"rejected session {d['rejected_session'].run_id} ({d['rejected_session'].reject_reason}): {d['keys_from_bad']} keys delivered")
    print(f"{d['messages']} test messages encrypted at Site A and decrypted at Site B: {'all match' if d['roundtrips_ok'] else 'MISMATCH'}")
    print(f"request with an empty key store: {'refused (fail closed)' if d['refused_when_empty'] else 'NOT refused'}")
    return d


def cmd_scenarios(a) -> None:
    out = Path(a.out or EVIDENCE)
    t0 = time.perf_counter()
    base = LinkConfig()
    res = {"1_baseline": S.baseline(base), "2_distance": S.distance(base), "3_interception": S.interception(base),
           "4_high_loss": S.high_loss(base)}
    pairs = S.noise_vs_adversary(base)
    res["5_noise_vs_adversary"] = [r for p in pairs for r in p if r is not None]
    rep = S.reproducibility(base)
    res["6_reproducibility"] = rep["runs"]
    demo = S.demonstration(base)
    validation = S.validation_checks()
    for name, rs in res.items():
        write_table([r.metrics for r in rs], out / "sessions" / f"{name}.csv")
        if a.sessions:
            for r in rs:
                write_session(r, out / "runs")
    example = write_session(res["1_baseline"][0], out / "example_run")
    from qll.link.plots import make_all
    plots = make_all([r.metrics for r in res["2_distance"]], [r.metrics for r in res["3_interception"]],
                     [r.metrics for r in res["4_high_loss"]], pairs, base, out / "plots")
    elapsed = time.perf_counter() - t0
    (out / "README.md").write_text(_report(res, pairs, rep, demo, validation, plots, example, out, base, elapsed), encoding="utf-8")
    print(f"wrote {out}/README.md, {len(plots)} plots, and {len(res)} scenario tables in {elapsed:.1f} s")


def _row(m) -> dict:
    return {"distance (km)": f"{m.distance_km:g}", "loss (dB)": f"{m.channel_loss_db:.1f}", "adversary": m.adversary.replace("intercept-resend on ", "IR "),
            "detected": f"{m.states_detected:,}", "sifted": f"{m.sifted_bits:,}", "QBER": f"{100 * m.qber_estimate:.2f} %",
            "alert": "yes" if m.alert else "", "decision": "accepted" if m.accepted else f"rejected ({m.reject_reason})",
            "final key bits": f"{m.final_key_bits:,}", "seed": m.seed}


def _report(res, pairs, rep, demo, validation, plots, example, out, base, elapsed) -> str:
    rel = lambda p: Path(p).relative_to(out).as_posix()
    cols = ["distance (km)", "loss (dB)", "adversary", "detected", "sifted", "QBER", "alert", "decision", "final key bits", "seed"]
    L = [
        "# Simulation evidence: Scalable Two-Node Fiber-Optic Quantum Communication Link",
        "",
        "Generated by `python -m qll.link.run scenarios`. Every number below comes from a configuration and a seed recorded "
        "in `sessions/*.csv`; rerunning the command reproduces them exactly (scenario 6), except execution times and "
        "timestamps. **These are simulation results under the assumptions of `../03_assumptions.md`; they are not "
        "measurements of hardware and not a proof of real-world security.**",
        "",
        f"Baseline configuration: {base.n_pulses:,} pulses per session at {base.pulse_rate_hz / 1e6:g} MHz, "
        f"{base.attenuation_db_per_km:g} dB/km fiber, {base.receiver_loss_db:g} dB receiver loss, detector efficiency "
        f"{base.detector_efficiency:g}, dark-count probability {base.dark_count_prob:g} per gate, misalignment "
        f"{100 * base.misalignment_error:g} %, abort threshold {100 * base.qber_threshold:g} %, alert level "
        f"{100 * base.qber_alert:g} %. Python {platform.python_version()}, NumPy {np.__version__}; all scenarios ran in about "
        f"{max(1, round(elapsed / 5) * 5)} s on one core.",
        "",
        "## Validation against the closed-form models",
        "",
        _md_table([{"check": r["check"], "expected": r["expected"], "observed": r["observed"], "result": "PASS" if r["pass"] else "FAIL"} for r in validation],
                  ["check", "expected", "observed", "result"]),
        "",
        "## Scenario 1: baseline (0 km, no adversary)",
        "",
        _md_table([_row(r.metrics) for r in res["1_baseline"]], cols),
        "",
        f"Per-run summary of the first session (also in `{rel(example)}/summary.txt`):",
        "",
        "```",
        summary(res["1_baseline"][0].metrics),
        "```",
        "",
        "## Scenario 2: increasing distance",
        "",
        f"![loss]({rel(plots[0])}) ![detection]({rel(plots[1])})",
        "",
        f"![qber]({rel(plots[2])}) ![key]({rel(plots[3])})",
        "",
        f"![acceptance]({rel(plots[4])})",
        "",
        _md_table([_row(r.metrics) for r in res["2_distance"] if r.metrics.seed == S.SEEDS[0]], cols),
        "",
        f"The expected error rate stays near the misalignment floor until dark counts compete with the signal; the model puts "
        f"the {100 * base.qber_threshold:g} % crossing at about {models.max_distance_km(base):.0f} km. Long before that, a "
        f"session of {base.n_pulses:,} pulses runs out of detections: the finite block, not the error rate, ends the key. "
        "Sessions ten times longer (orange in the key plot) reach further.",
        "",
        "## Scenario 3: interception (intercept-and-resend) and classical tampering",
        "",
        f"![adversary]({rel(plots[5])}) ![amplification]({rel(plots[6])})",
        "",
        _md_table([_row(r.metrics) for r in res["3_interception"]], cols),
        "",
        "Interception raises the error rate by a quarter of the intercepted fraction, as the model predicts. Above the "
        "alert level the operator is warned; above the abort threshold the key is rejected. Below it, the session can still "
        "be accepted, because privacy amplification removes more bits than the adversary knew (right-hand plot); that is "
        "how BB84 tolerates partial interception, and it holds only under this model's assumptions. Altering one "
        "classical message makes authentication fail and the session is rejected.",
        "",
        "## Scenario 4: high loss from an inserted attenuator",
        "",
        f"![high loss]({rel(plots[8])})",
        "",
        _md_table([_row(r.metrics) for r in res["4_high_loss"]], cols),
        "",
        "## Scenario 5: ordinary noise against an adversary with the same expected error rate",
        "",
        f"![noise]({rel(plots[7])})",
        "",
        _md_table([_row(r.metrics) for r in res["5_noise_vs_adversary"]], cols),
        "",
        "Within this model, the error rate and the detection rate cannot tell ordinary noise from interception: both rise "
        "the same way. The protocol therefore treats every error as if an adversary caused it, which is what makes it "
        "safe, and the monitor reports an elevated error rate as consistent with either cause. Distinguishing them would "
        "need other evidence (for example, error-rate history, decoy-state statistics, or physical inspection).",
        "",
        "## Scenario 6: reproducibility",
        "",
        f"Same configuration and seed twice: metrics identical **{rep['same_metrics']}**, keys identical **{rep['same_keys']}**, "
        f"run identifier identical **{rep['same_run_id']}**. A different seed gives a different key: **{rep['other_seed_differs']}**.",
        "",
        "## Demonstration: external secure-communication application",
        "",
        f"An accepted session delivered {demo['keys_from_good']} keys of 256 bits to both sites; a rejected session "
        f"(full interception) delivered {demo['keys_from_bad']}. {demo['messages']} test messages were encrypted with AES-256-GCM at "
        f"Site A and decrypted at Site B: {'all matched' if demo['roundtrips_ok'] else 'mismatch'}. With the store empty "
        f"the application {'refused to send (fail closed)' if demo['refused_when_empty'] else 'did not refuse'}.",
        "",
        "## All sessions",
        "",
        f"![outcomes]({rel(plots[9])})",
        "",
        "Rejection reasons: " + "; ".join(f"`{k}`: {v}" for k, v in REJECT_REASONS.items()) + ".",
        "",
    ]
    return "\n".join(L)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("session"); p.add_argument("--config"); p.add_argument("--set", nargs="*"); p.add_argument("--out")
    p = sub.add_parser("validate"); p.add_argument("--out")
    p = sub.add_parser("scenarios"); p.add_argument("--out"); p.add_argument("--sessions", action="store_true")
    sub.add_parser("demo")
    p = sub.add_parser("ingest"); p.add_argument("log"); p.add_argument("--config"); p.add_argument("--set", nargs="*"); p.add_argument("--out")
    a = ap.parse_args(argv)
    {"session": cmd_session, "validate": cmd_validate, "scenarios": cmd_scenarios, "demo": cmd_demo, "ingest": cmd_ingest}[a.cmd](a)


if __name__ == "__main__":
    main()
