"""Evidence logging: every session leaves a folder that reproduces it.

Layout
------
<out>/<scenario>/<run_id>/config.json   the complete LinkConfig (rerunning it reproduces the session exactly)
                          metrics.json  every metric, the decision, and the timestamp
                          events.jsonl  the monitor's event log, one event per line
                          summary.txt   the per-run summary block
<out>/<scenario>/sessions.csv           one row per session, for plots and spreadsheets
Raw bit arrays are not written by default: they are regenerated exactly from the configuration and seed.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from qll.link.monitor import SessionMetrics, summary
from qll.link.protocol_bb84 import SessionResult

CSV_FIELDS = [k for k in SessionMetrics.__dataclass_fields__ if k != "events"]


def write_session(r: SessionResult, out: Path) -> Path:
    d = Path(out) / r.config.scenario / r.metrics.run_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "config.json").write_text(json.dumps(r.config.to_dict(), indent=1, sort_keys=True), encoding="utf-8")
    (d / "metrics.json").write_text(json.dumps(r.metrics.to_dict(with_events=False), indent=1), encoding="utf-8")
    (d / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in r.metrics.events), encoding="utf-8")
    (d / "summary.txt").write_text(summary(r.metrics) + "\n", encoding="utf-8")
    return d


def write_table(rows: list[SessionMetrics], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        w.writeheader()
        for m in rows:
            w.writerow(m.to_dict(with_events=False))


def read_config(folder: Path):
    from qll.link.config import LinkConfig
    return LinkConfig.from_dict(json.loads((Path(folder) / "config.json").read_text(encoding="utf-8")))
