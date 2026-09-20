"""The thesis results tables must regenerate from the code and carry the headline numbers."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.phase1


def test_results_tables_regenerate_and_contain_headlines():
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_results_tables.py")], check=True, cwd=ROOT)
    text = (ROOT / "research" / "thesis" / "results" / "tables.md").read_text(encoding="utf-8")
    for needle in ("11.00 %", "0.3711", "2.6755", "779.9 d", "171Yb+ hyperfine", "✓ | ✓ | ✓ | ✓ | ✓ | ✓", "Micius 2017 | 30°"):
        assert needle in text, needle
