"""The command line fails loudly: validation and the demonstration exit non-zero when a check fails, so automation
cannot mistake a printed FAIL for success (audit C02). Tested through real subprocesses."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.phase3

INJECT = """
import sys
from qll.link import run, scenarios
real = scenarios.validation_checks
scenarios.validation_checks = lambda: real() + [{"check": "injected failure", "expected": 1, "observed": 0, "pass": False}]
sys.exit(run.main(["validate"]))
"""


def _run(args, **kw):
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=600, **kw)


def test_validate_passes_with_exit_zero(tmp_path):
    r = _run(["-m", "qll.link.run", "validate", "--out", str(tmp_path)])
    assert r.returncode == 0, r.stdout + r.stderr
    assert "validation PASS" in r.stdout and (tmp_path / "validation.json").exists()


def test_an_injected_failure_exits_one():
    r = _run(["-c", INJECT])
    assert r.returncode == 1 and "FAIL  injected failure" in r.stdout and "validation FAIL" in r.stdout


def test_bad_usage_exits_two():
    assert _run(["-m", "qll.link.run", "no-such-command"]).returncode == 2
