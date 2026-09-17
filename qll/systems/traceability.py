"""Machine-checked requirements traceability.

A requirement is "verified" only when its test_path exists and passes in CI. This module lists
rows whose declared test_path does not exist; ``python -m qll.systems.traceability`` exits 1
on any miss.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "systems" / "traceability_matrix.csv"
COLUMNS = ["req_id", "statement", "phase", "test_path", "status"]


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
            file_part = tp.split("::")[0]
            if not (ROOT / file_part).exists():
                missing.append(row["req_id"])
    return missing


def main() -> int:
    rows = load_matrix()
    miss = missing_tests(rows)
    verified = sum(1 for r in rows if r["status"].strip().lower() == "verified")
    print(f"{len(rows)} requirements, {verified} verified, {len(miss)} dangling test paths")
    for req in miss:
        print(f"  DANGLING {req}")
    return 1 if miss else 0


if __name__ == "__main__":
    sys.exit(main())
