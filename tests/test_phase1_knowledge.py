"""The knowledge base must not rot: every relative link resolves and every topic file has references."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
KNOW = ROOT / "knowledge"
FILES = sorted(KNOW.rglob("*.md"))
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
    if path.name == "README.md" or path.name in {"01_state_of_the_art_timeline.md", "02_open_problems.md", "GLOSSARY.md", "MISCONCEPTIONS.md"}:
        return  # synthesis files point into the topic files rather than citing directly
    assert re.search(r"\(\d{4}\)|\d{4}\)\.|Nature|Physical Review|arXiv|doi\.org", text), f"{path.name} has no references"


def test_knowledge_tree_is_complete():
    expected = ["00_foundations", "01_quantum_computing_core", "02_qubit_modalities",
                "03_quantum_communication", "04_cutting_edge", "05_experiments/done",
                "05_experiments/proposed", "05_experiments/lessons"]
    for d in expected:
        assert (KNOW / d).is_dir(), d
    assert len(FILES) >= 50
