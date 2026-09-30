"""The key bank: the sequent-peak capacity against the square-wave result and a day-by-day simulation, and the
Earth-Mars ledger built on the link budget."""
import numpy as np
import pytest

from qll.app.key_bank import max_demand_for_capacity, sequent_peak, simulate, sustainable_demand
from qll.systems.key_ledger import daily_key_bits, demand_for_capacity, ledger, longest_gap_days
from qll.systems.mars_budget import MarsLinkDesign

pytestmark = pytest.mark.phase6
KEY = daily_key_bits(MarsLinkDesign())


def test_square_wave_supply_needs_the_off_season_deficit():
    # supply s for n_on days then nothing for n_off days; a constant demand d <= mean must be banked for n_off days
    s, n_on, n_off = 10.0, 30, 20
    supply = np.r_[np.full(n_on, s), np.zeros(n_off)]
    for d in (1.0, 3.0, 6.0):
        assert sequent_peak(supply, d) == pytest.approx(d * n_off)
    assert sustainable_demand(supply) == pytest.approx(6.0)
    assert sequent_peak(supply, 0.0) == 0.0


def test_the_deficit_that_wraps_around_needs_the_second_cycle():
    supply = np.r_[np.zeros(5), np.full(10, 4.0), np.zeros(5)]      # the dry season straddles the record's end
    assert sequent_peak(supply, 2.0, cycles=1) == pytest.approx(10.0)
    assert sequent_peak(supply, 2.0) == pytest.approx(20.0)


def test_bank_at_capacity_never_refuses_and_a_smaller_one_does():
    rng = np.random.default_rng(7)
    supply = rng.exponential(5.0, 365) * (rng.random(365) > 0.2)
    d = 0.8 * supply.mean()
    K = sequent_peak(supply, d)
    two = np.r_[supply, supply]
    run = simulate(two, d, K)
    assert run.refused_days == 0
    assert K - run.level == pytest.approx(np.array([_s for _s in _deficits(two, d)]), abs=1e-9)   # K - L_t = S_t
    assert simulate(two, d, 0.98 * K).refused_days > 0
    assert simulate(supply, d, 0.0, 0.0).refused_days > 0


def _deficits(s, d):
    S = 0.0
    for st in s:
        S = max(0.0, S + d - st)
        yield S


def test_largest_demand_for_a_capacity_inverts_the_rule():
    supply = np.r_[np.full(30, 10.0), np.zeros(20)]
    assert max_demand_for_capacity(supply, 60.0) == pytest.approx(3.0, rel=1e-6)
    assert max_demand_for_capacity(supply, 1e9) == pytest.approx(6.0)
    with pytest.raises(ValueError):
        sequent_peak([1.0, -1.0], 0.5)
    with pytest.raises(TypeError):
        sequent_peak(np.array([1.0 + 0j]), 0.5)


def test_mars_key_flows_every_day_outside_conjunction():
    assert len(KEY) == 780
    assert int(np.sum(KEY > 0)) >= 755 and longest_gap_days(KEY) <= 25
    assert KEY[KEY > 0].min() > 1e5


def test_req_app_003_a_bank_carries_the_messenger_through_every_conjunction():
    L = ledger(MarsLinkDesign(), 1e6, KEY)
    assert L.refused_days_without_bank > 21                     # the day's own key falls short near maximum range too
    two = np.r_[KEY, KEY]
    assert simulate(two, 1e6, L.capacity_bits).refused_days == 0
    assert simulate(two, 1e6, 0.99 * L.capacity_bits).refused_days > 0
    assert L.capacity_bits / 8 < 50e6                            # tens of megabytes: the store is cheap, its secrecy is not
    assert demand_for_capacity(MarsLinkDesign(), L.capacity_bits, KEY) == pytest.approx(1e6, rel=1e-4)
    with pytest.raises(ValueError):
        ledger(MarsLinkDesign(), 2 * L.sustainable_bits_per_day, KEY)
