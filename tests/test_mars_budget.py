"""The Earth-Mars link budget: stages multiply to the total, each stage is the tested lower-level model, conjunction
closes the link, the dual-downlink relay pays diffraction twice, and the fidelity and key follow the memory model."""
import math
from dataclasses import replace

import numpy as np
import pytest

from qll.channels.free_space_diffraction import geometric_transmittance
from qll.channels.planetshine import airy_leakage, planetshine_photon_flux, single_mode_photon_rate
from qll.channels.light_time_delay import one_way_delay_s
from qll.network.memory_decoherence import MEMORY_TABLE, fraction_after_storage_analytic
from qll.space.ephemeris import earth_mars_range_m, sun_earth_mars_angle_deg
from qll.systems.mars_budget import MarsLinkDesign, budget, compare_memories, required_rejection

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
    f_stored = fraction_after_storage_analytic(D.f0, t_store, yb.lifetime_s)
    assert b.extra["fraction_stored"] == pytest.approx(f_stored, rel=1e-12)
    assert b.fraction == pytest.approx(0.25 + b.purity * (f_stored - 0.25), rel=1e-12)     # noise heralds are Werner 1/4
    assert b.teleport_fidelity == pytest.approx((2 * b.fraction + 1) / 3, rel=1e-12)
    perfect = budget(replace(D, f0=1.0, memory="Eu:YSO nuclear spin, 13.1 h", storage_factor=0.0, stray_light=0.0), T_CLOSE)
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
    with pytest.raises(ValueError):
        budget(replace(D, tx_offset_m=1e6), 0.0)                                   # on Earth's disk is not "in space"
    with pytest.raises(TypeError):
        budget(replace(D, stray_light=1e-9 + 0j), 0.0)


def test_baseline_meets_req_cap_003_every_available_day():
    days = np.arange(0.0, 780.0, 1.0)
    got = [budget(D, float(t)) for t in days]
    available = [b for b in got if b.pairs_per_day > 0]
    assert len(available) > 0.95 * len(days)                                    # only conjunction weeks are lost
    assert min(b.pairs_per_day for b in available) >= 1e5
    assert all(b.useful for b in available)


GROUND = replace(D, architecture="earth_source")


def test_a_ground_source_is_blind_in_daylight():
    for t in (T_CLOSE, T_FAR):
        b = budget(GROUND, t)
        assert b.extra["purity_daylight"] < 0.01                                     # daytime heralds are > 99 % noise
        assert b.noise_per_mode_s == pytest.approx(single_mode_photon_rate(D.night_radiance, D.wavelength_m, D.filter_hz))
    assert budget(GROUND, T_CLOSE).purity > 0.99                                    # at night the airglow is faint


def test_a_ground_source_loses_the_months_around_conjunction():
    got = [budget(GROUND, float(t)) for t in np.arange(0.0, 780.0, 1.0)]
    dark = [next(s.factor for s in b.stages if "dark-sky" in s.name) for b in got]
    assert sum(1 for x in dark if x == 0) > 0.3 * len(got)                          # no night-time view of Mars at all
    assert max(dark) == pytest.approx(100 / 360)                                     # best case: 40 % of the night at opposition
    available = [b for b in got if b.pairs_per_day > 0]
    assert min(b.pairs_per_day for b in available) < 1e5                             # REQ-CAP-003 fails for this design


def test_space_source_background_is_the_off_axis_earth():
    for t in (T_CLOSE, T_FAR):
        b = budget(D, t)
        theta = D.tx_offset_m / b.range_m
        rej = max(airy_leakage(theta, D.rx_diameter_mars_m, D.wavelength_m), D.stray_light)
        flux = planetshine_photon_flux(D.wavelength_m, D.filter_hz, b.range_m, math.radians(sun_earth_mars_angle_deg(t)))
        assert b.noise_per_mode_s == pytest.approx(flux * math.pi * (D.rx_diameter_mars_m / 2) ** 2 * rej, rel=1e-12)
        S = D.source_rate_hz * D.eta_tx * math.prod(s.factor for s in b.stages if "space to Mars" in s.name and "receiver" not in s.name)
        assert b.purity == pytest.approx(S / (S + b.noise_per_mode_s), rel=1e-12)
        assert b.heralds_per_day == pytest.approx(b.pairs_per_day / b.purity, rel=1e-12)
        assert b.key_bits_per_day == pytest.approx(b.heralds_per_day / b.memory_factor * b.key_bits_per_pair, rel=1e-12)
    # with the floor above the Airy wing, a bigger receiver buys signal and background alike: purity does not move
    big = budget(replace(D, rx_diameter_mars_m=8.0), T_FAR)
    assert big.pairs_per_day > 3.9 * budget(D, T_FAR).pairs_per_day
    assert big.purity == pytest.approx(budget(D, T_FAR).purity, rel=1e-3)
    # a GEO transmitter is only 0.1 mrad from Earth at maximum range: the Airy wing, not the floor, then dominates
    geo = budget(replace(D, tx_offset_m=4.2e7, stray_light=0.0), T_FAR)
    assert geo.extra["rejection"] > 1e-9 and geo.purity < budget(D, T_FAR).purity


def test_required_rejection_restores_the_target_purity():
    for t in (T_CLOSE, T_FAR):
        c = required_rejection(D, t, purity=0.99)
        assert budget(replace(D, stray_light=c), t).purity == pytest.approx(0.99, rel=1e-6)
    assert required_rejection(D, T_FAR) < required_rejection(D, T_CLOSE)          # full-phase Earth is the hard case


def test_req_cap_005_stray_light_keeps_heralds_clean_every_available_day():
    got = [budget(D, float(t)) for t in np.arange(0.0, 780.0, 1.0)]
    assert min(b.purity for b in got if b.pairs_per_day > 0) >= 0.95


def test_key_does_not_wait_for_the_memory():
    # BBM92 measures each photon on arrival: key depends on f0 and the background, not on storage or the memory
    for t in (T_CLOSE, T_FAR):
        b = budget(D, t)
        f_key = 0.25 + b.purity * (D.f0 - 0.25)
        assert b.extra["key_error_rate"] == pytest.approx(2 * (1 - f_key) / 3, rel=1e-12)
        assert budget(replace(D, storage_factor=10.0), t).key_bits_per_pair == b.key_bits_per_pair
        crystal = budget(replace(D, memory="Eu:YSO nuclear spin, 13.1 h"), t)
        assert crystal.key_bits_per_day == pytest.approx(b.key_bits_per_day, rel=1e-12)    # 0.5 % retrieval is irrelevant
        assert crystal.pairs_per_day < 1e-3 * b.pairs_per_day                               # but teleportation pays it
    # so key flows on every day with a link, even at maximum range where the stored pairs are too noisy for key
    far = budget(D, T_FAR)
    assert far.key_bits_per_day > 1e5 and 2 * (1 - far.fraction) / 3 > 0.11
