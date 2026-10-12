"""A required job cannot pass by skipping what it checks (audit C01), and the CI status a deploy publishes comes from
executed JUnit results, failing on an empty or red run."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.phase1
PROBE = 'import pytest\ndef test_needs_node():\n    pytest.skip("node is not installed")\n'


def test_required_skip_fails_and_optional_skip_skips(pytester, monkeypatch):
    pytester.makeconftest((ROOT / "tests" / "conftest.py").read_text(encoding="utf-8").replace('pytest_plugins = ["pytester"]', ""))
    pytester.makepyfile(test_probe=PROBE)
    monkeypatch.setenv("QLL_REQUIRE", "node")
    pytester.runpytest_subprocess().assert_outcomes(failed=1)
    monkeypatch.setenv("QLL_REQUIRE", "chromium")
    pytester.runpytest_subprocess().assert_outcomes(skipped=1)


def _report(tmp_path, cases):
    p = tmp_path / "r.xml"
    body = "".join(f'<testcase classname="tests.t" name="t{i}">{x}</testcase>' for i, x in enumerate(cases))
    p.write_text(f'<?xml version="1.0"?><testsuites><testsuite>{body}</testsuite></testsuites>', encoding="utf-8")
    return p


@pytest.mark.parametrize("cases, code", [(["", "", "<skipped/>"], 0), (["", "<failure/>"], 1), ([], 1)])
def test_ci_status_reflects_what_ran(tmp_path, cases, code):
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "ci_status_from_junit.py"), str(_report(tmp_path, cases)), "--sha", "abc1234def", "--out", str(tmp_path / "site")],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == code, r.stdout + r.stderr
    st = json.loads((tmp_path / "site" / "ci_status.json").read_text(encoding="utf-8"))
    assert st["revision"] == "abc1234def" and st["outcome"] == ("pass" if code == 0 else "fail")


def test_the_workflow_deploys_only_what_passed():
    wf = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    deploy = wf[wf.index("  deploy:"):]
    assert "needs: [test, browser]" in deploy and "github.event_name == 'push'" in deploy
    assert deploy.index("ci_status_from_junit.py") < deploy.index("upload-pages-artifact") < deploy.index("deploy-pages")
    assert "MANIFEST.sha256" in deploy and "REVISION" in deploy
    assert wf.count("if: always()") >= 2 and wf.count("--junitxml=") >= 3          # reports uploaded even on failure
    for job in ("  test:", "  browser:"):
        body = wf[wf.index(job):]
        assert "QLL_REQUIRE:" in body.split("steps:")[0]                          # required tools fail instead of skipping
    assert "windows-latest" in wf and "ubuntu-latest" in wf


def test_failures_become_readable_annotations(tmp_path):
    p = _report(tmp_path, ["", '<failure message="assert 1 == 2">long trace\nlast line</failure>'])
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "junit_annotations.py"), str(p)], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("::error")]
    assert len(lines) == 1 and "assert 1 == 2" in lines[0] and "%0A" in lines[0] and "last line" in lines[0]
