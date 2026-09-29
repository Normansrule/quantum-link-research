"""Machine-checked requirements traceability.

A requirement is "verified" only when its test_path exists and passes in CI. This module lists rows whose declared
test file, or the named test function in it, does not exist, and rows whose verification method (Test, Analysis,
Demonstration, Inspection: the classic IADT set) or parent stakeholder need is not declared;
``python -m qll.systems.traceability`` exits 1 on any miss.
"""
from __future__ import annotations

import csv
import sys
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


def missing_tests(rows: list[dict[str, str]] | None = None) -> list[str]:
    rows = load_matrix() if rows is None else rows
    missing = []
    for row in rows:
        tp = row["test_path"].strip()
        if tp and tp.upper() != "TBD":
            file_part, _, func = tp.partition("::")
            f = ROOT / file_part
            if not f.exists() or (func and f"def {func}(" not in f.read_text(encoding="utf-8")):
                missing.append(row["req_id"])
    return missing


def malformed(rows: list[dict[str, str]] | None = None) -> list[str]:
    """Rows whose verification method or parent need is not one of the declared values."""
    rows = load_matrix() if rows is None else rows
    return [r["req_id"] for r in rows if r["method"] not in METHODS or r["need"] not in NEEDS]


def main() -> int:
    rows = load_matrix()
    miss = missing_tests(rows)
    verified = sum(1 for r in rows if r["status"].strip().lower().startswith("verified"))
    print(f"{len(rows)} requirements, {verified} verified, {len(miss)} dangling test paths")
    for req in miss:
        print(f"  DANGLING {req}")
    bad = malformed(rows)
    for req in bad:
        print(f"  MALFORMED {req}")
    return 1 if miss or bad else 0


if __name__ == "__main__":
    sys.exit(main())
