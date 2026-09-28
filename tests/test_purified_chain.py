"""Purification between swap levels: no rounds reproduces the plain chain exactly, one round follows the BBPSSW
recurrence and its cost, and the design-space answers (which memories make a useful fiber repeater, and how long a
memory must live) are pinned."""
import numpy as np
import pytest

from qll.network.memory_decoherence import MEMORY_TABLE
from qll.network.purification import bbpssw_step
from qll.network.purified_chain import (best_useful_chain, minimum_useful_memory_s, purified_chain,
                                        useful_distance_range_km)
from qll.network.repeater_chain import memory_chain

pytestmark = pytest.mark.phase1


@pytest.mark.parametrize("L, n, T", [(50.0, 0, 1.0), (393.0, 3, 1.0), (800.0, 2, 10.0), (1600.0, 4, 100.0)])
def test_no_rounds_is_the_plain_chain(L, n, T):
    a, b = memory_chain(L, n, T), purified_chain(L, n, T)
    assert (b.rate_hz, b.fidelity_fraction, b.hold_time_s) == (a.rate_hz, a.fidelity_fraction, a.hold_time_s)
    assert b.pairs_per_output == pytest.approx(2**n / 0.5**n)            # 2^n elementary pairs per try, 1/P_s tries


def test_one_elementary_round_follows_bbpssw_and_pays_for_it():
    T = 1e12                                                               # no storage decay: recurrences only
    plain, pur = purified_chain(100.0, 1, T), purified_chain(100.0, 1, T, (1, 0))
    f1, p1 = bbpssw_step(0.95)
    f_swapped = f1**2 + (1 - f1) ** 2 / 3
    assert pur.fidelity_fraction == pytest.approx(f_swapped, rel=1e-12)
    assert pur.fidelity_fraction > plain.fidelity_fraction
    assert pur.pairs_per_output == pytest.approx(plain.pairs_per_output * 2 / p1)
    assert pur.hold_time_s > plain.hold_time_s


def test_the_headline_chain_cannot_be_made_useful():
    # 393 km with 1 s memories: no nesting depth or purification schedule reaches F > 2/3 (learn 03/19)
    assert best_useful_chain(393.0, 1.0) is None


def test_minimum_memory_for_a_useful_chain_grows_steeply_with_distance():
    t = [minimum_useful_memory_s(L) for L in (500.0, 1000.0, 2000.0)]
    assert 3.5 < t[0] < 6 and 30 < t[1] < 50 and 1000 < t[2] < 1800
    assert t[0] < t[1] < t[2]


def test_which_demonstrated_memories_make_a_useful_fiber_repeater():
    ranges = {p.name: useful_distance_range_km(p.lifetime_s, p.efficiency) for p in MEMORY_TABLE}
    yb = ranges["171Yb+ hyperfine"]
    assert yb is not None and yb[0] < 1000 < yb[1] and yb[1] > 2000
    assert ranges["NV 13C register"] is not None
    assert ranges["SiV nuclear spin in cavity"] is None                  # 1 s is too short
    assert ranges["Eu:YSO nuclear spin, 13.1 h"] is None                 # long-lived, but 0.5 % retrieval kills swaps


def test_validation():
    with pytest.raises(ValueError):
        purified_chain(100.0, 2, 1.0, (1, 0))
    with pytest.raises(TypeError):
        purified_chain(100.0 + 0j, 1, 1.0)
    assert np.isfinite(purified_chain(100.0, 1, 1.0, (2, 2)).hold_time_s)
