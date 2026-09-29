import pytest

from qll.systems.traceability import load_matrix, malformed, missing_tests
from qll.systems.trl import TRL

pytestmark = pytest.mark.phase1


def test_no_dangling_test_paths():
    rows = load_matrix()
    assert len(rows) >= 17 and missing_tests(rows) == [] and malformed(rows) == []
    assert len({r["req_id"] for r in rows}) == len(rows)                      # unique identifiers


def test_trl_keys_one_to_nine():
    assert sorted(TRL) == list(range(1, 10))
