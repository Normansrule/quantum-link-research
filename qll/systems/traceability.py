"""Machine-checked requirements traceability.

A requirement is "verified" only when its tests ran and passed on the revision in question. The CSV's status column
is a claim; this module checks it three ways:
  1. static     the declared test file exists and the named test is a real top-level test function in it, found by
                parsing the file (a comment or a string mentioning the name does not count);
  2. executed   with --junit reports/*.xml (pytest --junitxml), every requirement marked verified must have at least
                one test that ran and passed, and none that failed or was skipped;
and it lists rows whose verification method (Test, Analysis, Demonstration, Inspection: the classic IADT set) or
parent stakeholder need is not declared. ``python -m qll.systems.traceability [--junit FILE ...]`` exits 1 on any
miss, and reports mapped, passed, failed, skipped, and not-run counts separately.
"""
from __future__ import annotations

import argparse
import ast
import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "systems" / "traceability_matrix.csv"
COLUMNS = ["req_id", "statement", "phase", "test_path", "status", "method", "need"]
METHODS = ("Test", "Test (bench)", "Analysis", "Demonstration", "Inspection")
NEEDS = ("N-1", "N-2", "N-3", "N-4", "N-5")


def load_matrix(path: Path = MATRIX) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if rows and list(rows[0].keys()) != COLUMNS:
        raise ValueError(f"traceability matrix columns must be {COLUMNS}")
    return rows


def test_functions(path: Path) -> set[str]:
    """Names of the top-level test functions (and methods of Test classes) defined in a test file."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = set()
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test"):
            out.add(n.name)
        elif isinstance(n, ast.ClassDef) and n.name.startswith("Test"):
            out |= {f"{n.name}::{m.name}" for m in n.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name.startswith("test")}
    return out


def missing_tests(rows: list[dict[str, str]] | None = None) -> list[str]:
    rows = load_matrix() if rows is None else rows
    missing = []
    for row in rows:
        tp = row["test_path"].strip()
        if tp and tp.upper() != "TBD":
            file_part, _, func = tp.partition("::")
            f = ROOT / file_part
            if not f.exists() or (func and func not in test_functions(f)) or (not func and not test_functions(f)):
                missing.append(row["req_id"])
    return missing


def junit_outcomes(paths) -> dict[tuple[str, str], str]:
    """{(test file, test name without parameters): worst outcome} from pytest JUnit XML: failed > skipped > passed."""
    rank = {"passed": 0, "skipped": 1, "failed": 2}
    out: dict[tuple[str, str], str] = {}
    for p in paths:
        for tc in ET.parse(p).getroot().iter("testcase"):
            mod = tc.get("classname", "")
            parts = mod.split(".")
            cls = [x for x in parts if x[:1].isupper()]
            file = "/".join(x for x in parts if not x[:1].isupper()) + ".py"
            name = tc.get("name", "").split("[")[0]
            key = (file, "::".join(cls + [name]))
            res = "failed" if tc.find("failure") is not None or tc.find("error") is not None else "skipped" if tc.find("skipped") is not None else "passed"
            prev = out.get(key)
            out[key] = res if prev is None else max(prev, res, key=rank.get)
    return out


def executed(rows: list[dict[str, str]], outcomes: dict[tuple[str, str], str]) -> dict[str, dict]:
    """Per requirement: which mapped tests passed, failed, were skipped, or never ran."""
    report = {}
    for row in rows:
        tp = row["test_path"].strip()
        if not tp or tp.upper() == "TBD":
            continue
        file_part, _, func = tp.partition("::")
        results = [o for (f, n), o in outcomes.items() if f == file_part and (not func or n == func)]
        report[row["req_id"]] = {"status": row["status"], "passed": results.count("passed"), "failed": results.count("failed"),
                                 "skipped": results.count("skipped"), "ran": bool(results)}
    return report


def malformed(rows: list[dict[str, str]] | None = None) -> list[str]:
    """Rows whose verification method or parent need is not one of the declared values."""
    rows = load_matrix() if rows is None else rows
    return [r["req_id"] for r in rows if r["method"] not in METHODS or r["need"] not in NEEDS]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--junit", nargs="*", default=[], help="pytest --junitxml reports from this revision")
    a = ap.parse_args(argv)
    rows = load_matrix()
    miss = missing_tests(rows)
    claimed = [r for r in rows if r["status"].strip().lower().startswith("verified")]
    print(f"{len(rows)} requirements, {len(claimed)} marked verified, {len(miss)} dangling test paths")
    for req in miss:
        print(f"  DANGLING {req}")
    bad = malformed(rows)
    for req in bad:
        print(f"  MALFORMED {req}")
    unproven = []
    if a.junit:
        rep = executed(rows, junit_outcomes(a.junit))
        for r in claimed:
            e = rep.get(r["req_id"])
            if e is None:
                continue
            if not e["ran"] or e["failed"] or e["skipped"] or not e["passed"]:
                unproven.append(r["req_id"])
                print(f"  NOT PROVEN {r['req_id']}: passed {e['passed']}, failed {e['failed']}, skipped {e['skipped']}, ran {e['ran']}")
        proven = sum(1 for r in claimed if r["req_id"] in rep and r["req_id"] not in unproven)
        print(f"executed: {proven} of {len(claimed)} verified requirements proven by passing tests in the reports")
    return 1 if miss or bad or unproven else 0


if __name__ == "__main__":
    sys.exit(main())
