"""The systems-engineering documents cannot drift from the code: the requirements document is exactly what the
traceability matrix generates, every requirement appears in it, and the trade-study tables are current."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
pytestmark = pytest.mark.phase1


def test_requirements_document_is_generated_from_the_matrix():
    import build_systems_docs as b
    from qll.systems.traceability import load_matrix

    text = (ROOT / "systems" / "requirements.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert text == b.requirements_md() + "\n"
    for r in load_matrix():
        assert f"| {r['req_id']} |" in text


def test_trade_study_tables_are_current():
    import build_systems_docs as b

    text = (ROOT / "systems" / "trade_studies.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert b.fill_trade_studies(text, b.trade_tables()) == text
    for key in ("architecture", "wavelength", "memory", "aperture"):
        start, end = f"<!-- trade:{key}:start -->", f"<!-- trade:{key}:end -->"
        assert text.count("|", text.index(start), text.index(end)) > 10       # a filled table, not empty markers
