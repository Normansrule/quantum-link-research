"""Turn the JUnit reports of one CI run into the status the website and README badges show (audit C01, U03), so a
badge reports what executed on a named revision rather than a counter committed to the tree.

    python scripts/ci_status_from_junit.py --sha $GITHUB_SHA --out site/ reports/*.xml

Writes <out>/badges/tests.json (shields.io endpoint: "N passed · F failed · S skipped") and <out>/ci_status.json
(totals, per-report counts, revision, time, and a run URL when given). Exits 1 when no tests ran or any failed, so a
deploy step that depends on it cannot publish a red or empty run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def counts(path: Path) -> dict[str, int]:
    c = {"tests": 0, "passed": 0, "failed": 0, "skipped": 0}
    for tc in ET.parse(path).getroot().iter("testcase"):
        c["tests"] += 1
        if tc.find("failure") is not None or tc.find("error") is not None:
            c["failed"] += 1
        elif tc.find("skipped") is not None:
            c["skipped"] += 1
        else:
            c["passed"] += 1
    return c


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reports", nargs="+"); ap.add_argument("--sha", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--run-url", default="")
    a = ap.parse_args(argv)
    per = {Path(r).name: counts(Path(r)) for r in a.reports}
    tot = {k: sum(c[k] for c in per.values()) for k in ("tests", "passed", "failed", "skipped")}
    ok = tot["tests"] > 0 and tot["failed"] == 0
    out = Path(a.out)
    (out / "badges").mkdir(parents=True, exist_ok=True)
    badge = {"schemaVersion": 1, "label": f"tests @ {a.sha[:7]}", "message": f"{tot['passed']} passed · {tot['failed']} failed · {tot['skipped']} skipped",
             "color": "2ea44f" if ok else "d73a49", "labelColor": "0b1224"}
    (out / "badges" / "tests.json").write_text(json.dumps(badge), encoding="utf-8")
    status = {"revision": a.sha, "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "run_url": a.run_url,
              "outcome": "pass" if ok else "fail", "totals": tot, "reports": per,
              "note": "executed results from CI JUnit reports for this revision; committed counters elsewhere are inventory, not evidence"}
    (out / "ci_status.json").write_text(json.dumps(status, indent=1), encoding="utf-8")
    print(f"{a.sha[:7]}: {badge['message']} -> {'pass' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
