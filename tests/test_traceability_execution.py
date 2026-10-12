"""Traceability counts what ran, not what is written (audit C03): a test named only in a comment is dangling, and a
requirement marked verified is proven only by passing tests in a JUnit report from the same run."""
import pytest

from qll.systems import traceability as T

pytestmark = pytest.mark.phase1


def test_a_comment_does_not_define_a_test(tmp_path):
    f = tmp_path / "test_x.py"
    f.write_text('# def test_claimed(): pass\nX = "def test_also_claimed("\ndef test_real():\n    pass\n', encoding="utf-8")
    assert T.test_functions(f) == {"test_real"}


def _junit(tmp_path, cases):
    body = "".join(f'<testcase classname="tests.test_x" name="{n}">{extra}</testcase>' for n, extra in cases)
    p = tmp_path / "r.xml"
    p.write_text(f'<?xml version="1.0"?><testsuites><testsuite name="pytest">{body}</testsuite></testsuites>', encoding="utf-8")
    return p


def test_outcomes_from_junit_take_the_worst_result(tmp_path):
    p = _junit(tmp_path, [("test_a[1]", ""), ("test_a[2]", '<failure message="x"/>'), ("test_b", '<skipped message="no chromium"/>'), ("test_c", "")])
    out = T.junit_outcomes([p])
    assert out[("tests/test_x.py", "test_a")] == "failed" and out[("tests/test_x.py", "test_b")] == "skipped" and out[("tests/test_x.py", "test_c")] == "passed"
    rows = [{"req_id": "R1", "test_path": "tests/test_x.py::test_a", "status": "verified"}, {"req_id": "R2", "test_path": "tests/test_x.py::test_b", "status": "verified"},
            {"req_id": "R3", "test_path": "tests/test_x.py::test_c", "status": "verified"}, {"req_id": "R4", "test_path": "tests/test_y.py", "status": "verified"}]
    rep = T.executed(rows, out)
    assert rep["R1"]["failed"] == 1 and rep["R2"]["skipped"] == 1 and rep["R3"]["passed"] == 1 and not rep["R4"]["ran"]
