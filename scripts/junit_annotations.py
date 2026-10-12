"""Print each failed or erroring test of the given JUnit reports as a GitHub Actions error annotation, so the reason a
job failed is readable from the run summary and the API (check-runs/<id>/annotations), not only from the raw log.

    python scripts/junit_annotations.py reports/*.xml

GitHub keeps at most 10 error annotations per step, so the first nine failures are annotated individually and the
tenth line counts the rest. Always exits 0: the test step itself is what fails the job.
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def _escape(s: str) -> str:
    """Workflow-command escaping (https://github.com/actions/toolkit/blob/main/packages/core/src/command.ts)."""
    return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def failures(paths: list[str]) -> list[tuple[str, str, str]]:
    out = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            continue
        for tc in ET.parse(path).getroot().iter("testcase"):
            bad = tc.find("failure")
            if bad is None:
                bad = tc.find("error")
            if bad is None:
                continue
            name = f"{tc.get('classname', '')}::{tc.get('name', '')}"
            detail = (bad.get("message") or "") + "\n" + (bad.text or "")
            out.append((path.name, name, detail.strip()))
    return out


def main(argv: list[str]) -> int:
    found = failures(argv)
    for report, name, detail in found[:9]:
        tail = "\n".join(detail.splitlines()[-25:])[-1800:]
        print(f"::error title={_escape(name)[:200]}::{_escape(f'[{report}] {tail}')}")
    if len(found) > 9:
        print(f"::error title={len(found) - 9} more failures::see the uploaded JUnit reports for the rest")
    print(f"{len(found)} failing tests in {len(argv)} reports")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
