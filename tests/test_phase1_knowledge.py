"""The knowledge base must not rot: every relative link resolves and every topic file has references."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
KNOW = ROOT / "learn"
FILES = sorted(list((ROOT / "learn").rglob("*.md")) + list((ROOT / "experiments").rglob("*.md")) + list((ROOT / "research").rglob("*.md")) + list((ROOT / "youtube").rglob("*.md")))
pytestmark = pytest.mark.phase1


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_relative_links_resolve(path):
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        assert (path.parent / target).resolve().exists(), f"{path.name}: broken link {target}"


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_topic_files_cite_something(path):
    text = path.read_text(encoding="utf-8")
    if path.parent.name in ("youtube", "chapters", "results", "assignments") or path.name == "README.md" or path.name in {"01_state_of_the_art_timeline.md", "02_open_problems.md", "00_GLOSSARY.md", "00_MISCONCEPTIONS.md", "BACKLOG.md", "DESIGN_PROCESS.md", "INDEX.md", "_TEMPLATE.md", "NEXT_100.md", "THESIS_OUTLINE.md", "VERIFICATION_PLAN.md", "tables.md", "THESIS_DRAFT.md", "COURSE_SYLLABUS.md"}:
        return  # synthesis files point into the topic files rather than citing directly
    assert re.search(r"\(\d{4}\)|\d{4}\)\.|Nature|Physical Review|arXiv|doi\.org", text), f"{path.name} has no references"


def test_knowledge_tree_is_complete():
    expected = ["learn/00_foundations", "learn/01_quantum_computing_core", "learn/02_qubit_modalities",
                "learn/03_quantum_communication", "research/cutting_edge", "research/theories",
                "experiments/done", "experiments/proposed", "experiments/lessons", "experiments/bench",
                "experiments/protocols"]
    for d in expected:
        assert (ROOT / d).is_dir(), d
    assert len(FILES) >= 50
