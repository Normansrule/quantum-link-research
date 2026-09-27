"""Write docs/status.json and docs/status.md from the traceability matrix, the test count, and the tree,
so README, the website, and the thesis quote the same numbers. Run: python scripts/build_status.py"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_reference_index import parse_bib  # noqa: E402


def count_md(d: str) -> int:
    return len(list((ROOT / d).rglob("*.md")))


def write_badges(status: dict) -> None:
    """Shields.io endpoint badges (https://shields.io/badges/endpoint-badge), so the README's badges read the same
    numbers as status.json instead of hand-edited text."""
    d = ROOT / "docs" / "badges"
    d.mkdir(exist_ok=True)
    badges = {
        "version": ("version", f"v{status['version']}", "0b1224"),
        "tests": ("tests", f"{status['tests']:,} collected", "2ea44f"),
        "requirements": ("requirements", f"{status['requirements_verified']}/{status['requirements']} verified", "8A2BE2"),
        "references": ("references", f"{status['references']:,} cited", "1f6feb"),
        "learn": ("learn", f"{status['learn_files']} lessons", "ff8a4c"),
    }
    for name, (label, message, color) in badges.items():
        (d / f"{name}.json").write_text(json.dumps({"schemaVersion": 1, "label": label, "message": message, "color": color,
                                                     "labelColor": "0b1224"}) + "\n")


def main() -> None:
    from qll.systems.traceability import load_matrix
    rows = load_matrix()
    verified = sum(1 for r in rows if r["status"].strip().lower().startswith("verified"))
    tests = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q"], capture_output=True, text=True, cwd=ROOT).stdout
    m = re.search(r"(\d+) tests? collected", tests)
    n_tests = int(m.group(1)) if m else 0
    refs = set()
    for b in (ROOT / "docs").glob("references*.bib"):
        refs |= {k for k, _ in parse_bib(b.read_text(encoding="utf-8"))}
    n_verified_refs = 0
    for b in (ROOT / "docs").glob("references*.bib"):
        n_verified_refs += sum(1 for _, f in parse_bib(b.read_text(encoding="utf-8")) if "verified" in f.get("note", "").lower() and "todo" not in f.get("note", "").lower())
    version = re.search(r'version = "([^"]+)"', (ROOT / "pyproject.toml").read_text()).group(1)
    status = {
        "version": version, "tests": n_tests, "requirements": len(rows), "requirements_verified": verified,
        "references": len(refs), "references_verified": n_verified_refs,
        "learn_files": count_md("learn"), "experiment_files": count_md("experiments"), "research_files": count_md("research"),
        "simulations": len(list((ROOT / "simulations").glob("s0*.py"))), "figures": len(list((ROOT / "docs" / "figures").glob("*.svg"))),
        "phases_done": 6,
    }
    (ROOT / "docs" / "status.json").write_text(json.dumps(status, indent=1) + "\n")
    write_badges(status)
    md = ["# Status", "", f"Version {version} · {n_tests} tests · {verified}/{len(rows)} requirements verified · {len(refs)} references ({n_verified_refs} verified) · {status['learn_files']} learn files · {status['simulations']} simulations · {status['figures']} figures", "",
          "| Requirement | Statement | Phase | Status |", "|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['req_id']} | {r['statement']} | {r['phase']} | {r['status']} |")
    (ROOT / "docs" / "status.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(status))


if __name__ == "__main__":
    main()
