"""Sampling the nested repeater protocol checks the closed-form waiting time: exact without nesting, and a slightly
conservative approximation with it."""
import numpy as np
import pytest

from qll.network.repeater_chain import memory_chain
from qll.network.repeater_montecarlo import mean_chain_time_s, sample_chain_time_s

pytestmark = pytest.mark.phase1


def _ratio(L, n, runs, seed=5):
    m, se = mean_chain_time_s(L, n, runs, seed=seed)
    a = memory_chain(L, n, 1e9).hold_time_s          # memory long enough that the chain never stalls
    return m / a, se / a


def test_no_nesting_is_a_geometric_wait_and_matches_exactly():
    r, se = _ratio(300.0, 0, 20000)
    assert abs(r - 1) < 4 * se


def test_one_level_matches_within_sampling_error_and_herald_bookkeeping():
    r, se = _ratio(100.0, 1, 20000)
    assert abs(r - 1) < 0.03


@pytest.mark.parametrize("L, n, lo, hi", [(400.0, 2, 0.94, 0.985), (800.0, 3, 0.89, 0.945)])
def test_closed_form_is_conservative_when_nested(L, n, lo, hi):
    r, se = _ratio(L, n, 20000)
    assert lo < r < hi and se < 0.01


def test_sampling_is_reproducible_and_validates_input():
    a = sample_chain_time_s(400.0, 2, np.random.default_rng(1))
    b = sample_chain_time_s(400.0, 2, np.random.default_rng(1))
    assert a == b > 0
    with pytest.raises(TypeError):
        sample_chain_time_s(400.0 + 0j, 2, np.random.default_rng(1))
    with pytest.raises(ValueError):
        sample_chain_time_s(400.0, -1, np.random.default_rng(1))


def test_the_gap_grows_as_swaps_become_reliable():
    ratios = []
    for ps in (0.3, 1.0):
        m, se = mean_chain_time_s(800.0, 3, 10000, seed=2, p_swap=ps)
        ratios.append(m / memory_chain(800.0, 3, 1e9, p_swap=ps).hold_time_s)
    assert 0.91 < ratios[0] < 0.97 and 0.78 < ratios[1] < 0.84
