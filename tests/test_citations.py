"""CONTRIBUTING rule 3: every [bibkey] cited in a qll docstring must exist in docs/references*.bib."""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_reference_index import parse_bib  # noqa: E402

pytestmark = pytest.mark.phase1
KEY = re.compile(r"\[([a-z][a-z0-9_-]*\d{4}[a-z0-9_-]*)\]")


def _bib_keys() -> set[str]:
    keys: set[str] = set()
    for b in (ROOT / "docs").glob("references*.bib"):
        keys |= {k for k, _ in parse_bib(b.read_text(encoding="utf-8"))}
    return keys


def test_every_code_citation_has_a_bib_entry():
    keys = _bib_keys()
    missing = {}
    for py in (ROOT / "qll").rglob("*.py"):
        for k in KEY.findall(py.read_text(encoding="utf-8")):
            if k not in keys:
                missing.setdefault(k, []).append(str(py.relative_to(ROOT)))
    assert not missing, f"cited without a BibTeX entry: {missing}"


def test_bib_has_no_unclosed_entries():
    for b in (ROOT / "docs").glob("references*.bib"):
        text = b.read_text(encoding="utf-8")
        assert text.count("{") == text.count("}"), f"{b.name}: unbalanced braces"
