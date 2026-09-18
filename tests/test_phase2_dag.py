"""Import DAG: nothing imports upward in the physical stack (REQ-SYS-002)."""
import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.phase2
ROOT = Path(__file__).resolve().parents[1] / "qll"
LEVEL = {"constants": 0, "channels": 1, "hardware": 1, "circuits": 2, "qkd": 3, "network": 4, "space": 5, "app": 6, "viz": 7, "systems": 8}


def test_no_upward_imports():
    for py in ROOT.rglob("*.py"):
        pkg = py.relative_to(ROOT).parts[0]
        if pkg not in LEVEL:
            continue
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            mod = None
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("qll."):
                mod = node.module.split(".")[1]
            elif isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.startswith("qll."):
                        mod = a.name.split(".")[1]
            if mod in LEVEL and pkg not in ("viz", "systems"):
                assert LEVEL[mod] <= LEVEL[pkg], f"{py.relative_to(ROOT)} imports upward from qll.{mod}"
