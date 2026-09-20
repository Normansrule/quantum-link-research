"""Every notebook must execute headlessly (slow; skipped without nbconvert)."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = [pytest.mark.phase1, pytest.mark.slow]


@pytest.mark.parametrize("nb", sorted(p.name for p in (ROOT / "notebooks").glob("*.ipynb")))
def test_notebook_executes(nb, tmp_path):
    pytest.importorskip("nbconvert")
    r = subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--ExecutePreprocessor.timeout=300",
                        str(ROOT / "notebooks" / nb), "--output", str(tmp_path / nb)], capture_output=True, text=True, cwd=ROOT,
                       env={**__import__("os").environ, "MPLBACKEND": "Agg"})
    assert r.returncode == 0, r.stderr[-2000:]
