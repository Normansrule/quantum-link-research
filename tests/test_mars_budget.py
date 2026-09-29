"""The Earth-Mars link budget: stages multiply to the total, each stage is the tested lower-level model, conjunction
closes the link, the dual-downlink relay pays diffraction twice, and the fidelity and key follow the memory model."""
import math
from dataclasses import replace

import numpy as np
import pytest

from qll.channels.free_space_diffraction import geometric_transmittance
from qll.channels.light_time_delay import one_way_delay_s
from qll.network.memory_decoherence import MEMORY_TABLE, fraction_after_storage_analytic
from qll.space.ephemeris import earth_mars_range_m, sun_earth_mars_angle_deg
from qll.systems.mars_budget import MarsLinkDesign, budget, compare_memories

pytestmark = pytest.mark.phase1
D = MarsLinkDesign()
T_DAYS = np.arange(0.0, 800.0, 2.0)
T_CLOSE = float(T_DAYS[np.argmin(earth_mars_range_m(T_DAYS))])
T_FAR = float(T_DAYS[np.argmax(earth_mars_range_m(T_DAYS))])


def test_stages_multiply_to_the_total():
    b = budget(D, T_CLOSE)
    prod = b.stages[0].rate_per_s * math.prod(s.factor for s in b.stages[1:])
    assert b.stages[-1].rate_per_s == pytest.approx(prod, rel=1e-12)
    assert b.pairs_per_day == pytest.approx(86400 * prod, rel=1e-12)
    assert b.total_db == pytest.approx(10 * math.log10(prod / b.stages[0].rate_per_s), rel=1e-12)


def test_diffraction_stage_is_the_gaussian_beam_model():
    b = budget(D, T_CLOSE)
    diff = next(s for s in b.stages if "diffraction" in s.name)
    assert diff.factor == pytest.approx(geometric_transmittance(b.range_m, D.wavelength_m, D.tx_waist_m, D.rx_diameter_mars_m), rel=1e-12)
    # doubling the receiver diameter in the far field quadruples the collected light
    b2 = budget(replace(D, rx_diameter_mars_m=2 * D.rx_diameter_mars_m), T_CLOSE)
    assert b2.pairs_per_day / b.pairs_per_day == pytest.approx(4.0, rel=1e-3)


def test_conjunction_closes_the_direct_link():
    t_conj = next(float(t) for t in np.arange(0.0, 800.0, 0.5) if sun_earth_mars_angle_deg(float(t)) < 3.0)
    assert budget(D, t_conj).pairs_per_day == 0.0
    assert budget(D, T_CLOSE).pairs_per_day > 0.0


def test_dual_downlink_pays_diffraction_twice():
    for t in (T_CLOSE, T_FAR, 400.0):
        direct, relay = budget(D, t), budget(replace(D, architecture="relay_dual"), t)
        if direct.pairs_per_day > 0 and relay.pairs_per_day > 0:
            assert relay.pairs_per_day < 1e-6 * direct.pairs_per_day
            assert len(relay.extra["legs_m"]) == 2


def test_fidelity_and_key_follow_the_memory_model():
    b = budget(D, T_FAR)
    yb = next(p for p in MEMORY_TABLE if p.name == D.memory)
    t_store = 2 * one_way_delay_s(b.range_m)
    assert b.storage_s == pytest.approx(t_store, rel=1e-12)
    assert b.fraction == pytest.approx(fraction_after_storage_analytic(D.f0, t_store, yb.lifetime_s), rel=1e-12)
    assert b.teleport_fidelity == pytest.approx((2 * b.fraction + 1) / 3, rel=1e-12)
    perfect = budget(replace(D, f0=1.0, memory="Eu:YSO nuclear spin, 13.1 h", storage_factor=0.0), T_CLOSE)
    assert perfect.key_bits_per_pair == pytest.approx(1.0) and perfect.teleport_fidelity == pytest.approx(1.0)
    # the Werner error rate Q = 2(1 - f)/3 crosses the BB84/BBM92 threshold near 11 %: at f = 0.83 no key is left
    assert budget(replace(D, f0=0.83, storage_factor=0.0), T_CLOSE).key_bits_per_pair == 0.0


def test_the_memory_trade_rate_against_fidelity():
    rows = {name: (rate, F) for name, rate, F in compare_memories(D, T_FAR)}
    yb, eu = rows["171Yb+ hyperfine"], rows["Eu:YSO nuclear spin, 13.1 h"]
    assert yb[0] > 1e4 * eu[0]                  # 99 % vs 0.5 % retrieval, paid at both ends
    assert eu[1] > yb[1] > 2 / 3                # the crystal keeps the pair better; both are useful at maximum range
    assert rows["SiV nuclear spin in cavity"][1] == pytest.approx(0.5, abs=1e-6)   # 1 s is nothing against 45 min


def test_validation():
    with pytest.raises(ValueError):
        budget(replace(D, architecture="teleporter"), 0.0)
    with pytest.raises(ValueError):
        budget(replace(D, memory="unobtainium"), 0.0)


def test_baseline_meets_req_cap_003_every_available_day():
    days = np.arange(0.0, 780.0, 1.0)
    got = [budget(D, float(t)) for t in days]
    available = [b for b in got if b.pairs_per_day > 0]
    assert len(available) > 0.95 * len(days)                                    # only conjunction weeks are lost
    assert min(b.pairs_per_day for b in available) >= 1e5
    assert all(b.useful for b in available)
