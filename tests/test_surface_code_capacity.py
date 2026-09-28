"""The rotated surface code under bit-flip noise, decoded by matching: the code has the right stabilizer count and
logicals, every shot's correction clears its syndrome, a single error is always corrected, and the curves cross near
the code-capacity threshold."""
import numpy as np
import pytest

from qll.circuits.surface_code_capacity import logical_failure_rate, rotated_code, sample_shots

pytestmark = pytest.mark.phase1


@pytest.mark.parametrize("d", [3, 5, 7])
def test_code_structure(d):
    c = rotated_code(d)
    assert c.H.shape == ((d * d - 1) // 2, d * d)
    assert set(c.H.sum(axis=1)) == {2, 4} and c.H.sum(axis=0).max() == 2          # graphlike: matching applies
    logical_x = np.zeros(d * d, dtype=np.uint8); logical_x[:d] = 1                  # a row, left edge to right edge
    assert not ((c.H @ logical_x) % 2).any() and (logical_x @ c.logical_z) % 2 == 1
    assert (c.H.sum() - 2 * (d - 1)) == 4 * ((d - 1) ** 2 // 2)                     # interior weight 4, boundary 2


def test_every_correction_clears_its_syndrome_and_single_errors_never_fail():
    c = rotated_code(5)
    for shot in sample_shots(5, 0.08, 200, seed=4):
        x = np.zeros(c.n, dtype=np.uint8); x[shot["errors"]] = 1
        k = np.zeros(c.n, dtype=np.uint8); k[shot["correction"]] = 1
        assert list(np.flatnonzero((c.H @ x) % 2)) == shot["defects"]
        assert not ((c.H @ (x ^ k)) % 2).any()
        assert bool(((x ^ k) @ c.logical_z) % 2) == shot["logical_error"]
        if len(shot["errors"]) <= (5 - 1) // 2:
            assert not shot["logical_error"]                                         # corrects floor((d-1)/2) errors
        for a, b in shot["pairs"]:
            assert a in shot["defects"] and (b == -1 or b in shot["defects"])


def test_threshold_crossing():
    low = [logical_failure_rate(d, 0.05, 20000, seed=1) for d in (3, 5, 7)]
    high = [logical_failure_rate(d, 0.13, 20000, seed=1) for d in (3, 5, 7)]
    assert low[0] > low[1] > low[2]                  # below threshold: bigger is better
    assert high[0] < high[1] < high[2]               # above: bigger is worse
    diff = [logical_failure_rate(9, p, 20000, seed=2) - logical_failure_rate(5, p, 20000, seed=2) for p in (0.085, 0.105)]
    assert diff[0] < 0 < diff[1]                     # d = 5 and d = 9 cross between 8.5 % and 10.5 %


def test_small_p_scaling():
    # below threshold the failure rate falls like p^((d+1)/2): halving p cuts d = 5 failures by ~2^3
    r = logical_failure_rate(5, 0.02, 200000, seed=5) / logical_failure_rate(5, 0.01, 200000, seed=5)
    assert 5 < r < 11


def test_validation():
    with pytest.raises(ValueError):
        rotated_code(4)
    with pytest.raises(ValueError):
        logical_failure_rate(3, 1.5)
