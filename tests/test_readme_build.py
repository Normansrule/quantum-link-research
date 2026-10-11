"""The README's closing build guide is generated from the code (scripts/build_readme_build.py) and must be current:
the Phase 1 bill of materials and budget, the twin's predictions, and the Majorana rehearsals and requirements."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.phase1


def test_readme_build_guide_is_current():
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_readme_build as B
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert B.START in text and B.END in text
    assert text[text.index(B.START):text.index(B.END) + len(B.END)] == B.section(), "run python scripts/build_readme_build.py"


def test_build_guide_totals_match_the_plan():
    from qll.systems import lab_scenes as L
    from qll.systems import program_plan as P
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    lo, hi = L.bom_total(L.two_room())
    assert f"**${lo:,.0f}–{hi:,.0f}**" in text
    tot = [sum(m.cost[i] for m in P.MILESTONES if m.phase == 1) for i in range(3)]
    assert f"| **Phase 1** | | **${tot[0]:,.0f}** | **${tot[1]:,.0f}** | **${tot[2]:,.0f}** |" in text and tot[2] <= 1400
