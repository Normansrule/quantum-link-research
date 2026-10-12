"""Windows portability: every text-mode file read or write in the package, the scripts, and the tests names its
encoding. Without it Python uses the locale encoding (cp1252 on Windows CI), and files holding en dashes, µ, or Greek
letters fail to decode or decode to different text than the generators wrote."""
import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.phase1


def _offenders():
    for d in ("qll", "scripts", "tests", "experiments", "simulations"):
        for f in (ROOT / d).rglob("*.py"):
            tree = ast.parse(f.read_text(encoding="utf-8"))
            for n in ast.walk(tree):
                if not isinstance(n, ast.Call) or any(k.arg == "encoding" for k in n.keywords):
                    continue
                fn = n.func
                if isinstance(fn, ast.Attribute) and fn.attr in ("read_text", "write_text"):
                    yield f"{f.relative_to(ROOT)}:{n.lineno} {fn.attr}"
                elif isinstance(fn, ast.Attribute) and fn.attr in ("run", "check_output", "Popen") and any(
                        k.arg == "text" and getattr(k.value, "value", False) for k in n.keywords):
                    yield f"{f.relative_to(ROOT)}:{n.lineno} subprocess {fn.attr}(text=True)"
                elif isinstance(fn, ast.Name) and fn.id == "open":
                    mode = n.args[1] if len(n.args) > 1 else next((k.value for k in n.keywords if k.arg == "mode"), None)
                    if "b" not in str(getattr(mode, "value", "r")):
                        yield f"{f.relative_to(ROOT)}:{n.lineno} open"


def test_text_file_io_names_its_encoding():
    bad = list(_offenders())
    assert not bad, "add encoding=\"utf-8\":\n" + "\n".join(bad)
