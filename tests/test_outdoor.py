"""Outdoors and toward orbit: the outdoor twin reduces to the two-room twin, its sky background is the radiance
formula, the night/day and detector conclusions hold, and the pass geometry and losses match closed forms and the
published Micius range."""
import math
from dataclasses import replace

import pytest

from qll.channels.free_space_diffraction import geometric_transmittance
from qll.channels.link_budget import MICIUS_2017, slant_range_m
from qll.channels.thermal_background import background_from_spectral_radiance
from qll.link import outdoor_link as O
from qll.link import satellite_pass as S
from qll.link import two_room
from qll.link.expected_session import expected_session

pytestmark = pytest.mark.phase3


def test_outdoor_twin_is_the_two_room_twin_with_an_outdoor_path():
    p = O.OutdoorParts(distance_m=10.0, sky_radiance=0.0, air_db_per_km=0.0, pointing_urad=0.0, coupling_loss_db=0.0, rx_aperture_m=0.2)
    assert O.path_loss_db(p) == pytest.approx(0.0, abs=1e-9)
    c, c2 = O.config(p), two_room.config(replace(two_room.TwoRoomParts(), free_space_loss_db=O.path_loss_db(p)))
    for k in ("extra_loss_db", "dark_count_prob", "crosstalk_click_prob", "misalignment_error", "detector_efficiency"):
        assert getattr(c, k) == pytest.approx(getattr(c2, k), rel=1e-12, abs=1e-15), k


def test_factors_are_the_channel_modules():
    p = O.OutdoorParts(distance_m=800.0, pointing_urad=15.0, air_db_per_km=2.0)
    f = O.factors(p)
    assert f["geometric"] == pytest.approx(geometric_transmittance(800.0, 405e-9, p.tx_waist_m, p.rx_aperture_m), rel=1e-12)
    assert f["air"] == pytest.approx(10 ** (-0.16), rel=1e-12)
    w = f["beam_radius_m"]
    assert f["pointing"] == pytest.approx(w ** 2 / (w ** 2 + 4 * (15e-6 * 800) ** 2), rel=1e-12)
    assert O.path_loss_db(p) == pytest.approx(-10 * math.log10(f["geometric"] * f["pointing"] * f["air"] * f["coupling"]), rel=1e-12)


def test_sky_background_is_the_radiance_formula():
    p = O.OutdoorParts(sky_radiance=0.05, filter_nm=1.0, fov_mrad=0.5, rx_aperture_m=0.1)
    area, omega = math.pi * 0.05 ** 2, math.pi * (0.25e-3) ** 2
    eta = 10 ** (-p.receiver.receiver_loss_db / 10) * p.receiver.sipm_pde
    assert O.sky_counts_per_s(p) == pytest.approx(background_from_spectral_radiance(0.05e9, 405e-9, 1e-9, area, omega, eta), rel=1e-12)


def test_the_outdoor_conclusions():
    spad = O.RECEIVERS["spad"]
    night = lambda L, r: O.predict(O.OutdoorParts(distance_m=L, sky_radiance=O.SKY["city night"], receiver=r))
    assert night(300, O.RECEIVERS["sipm"])["key_bits"] == 0                    # SiPM dark counts end the key outdoors
    assert night(300, spad)["key_bits"] > night(1000, spad)["key_bits"] > night(2000, spad)["key_bits"] > 0
    day = O.predict(O.OutdoorParts(distance_m=300, sky_radiance=O.SKY["sunlit day"], receiver=spad))
    assert day["key_bits"] == 0 and day["qber"] > 0.4                           # daylight swamps a 405 nm receiver


def test_pass_geometry_closed_forms():
    h = 500e3
    assert S.elevation_deg(0.0, h) == pytest.approx(90.0)
    th = S.pass_half_angle(h, 15.0)
    assert S.elevation_deg(th, h) == pytest.approx(15.0, abs=1e-9)
    assert S.at_time(S.PRESETS["micius"], 0.0)["range_m"] == pytest.approx(h, rel=1e-12)
    assert 2 * math.pi / S.angular_rate(h) == pytest.approx(5677, rel=2e-3)    # a 500 km orbit takes about 94.6 minutes
    r = S.at_time(S.PRESETS["micius"], 120.0)
    assert r["range_m"] == pytest.approx(slant_range_m(h, r["elevation_deg"]), rel=1e-12)
    assert r["loss_db"] == pytest.approx(MICIUS_2017.loss_db(r["range_m"], r["elevation_deg"]), rel=1e-12)


def test_micius_pass_losses_and_a_positive_key():
    s = S.pass_summary(S.PRESETS["micius"])
    assert 300 < s["duration_s"] < 420
    assert 20 < s["min_loss_db"] < s["max_loss_db"] < 45                          # one downlink, 500-1400 km
    assert s["key_bits"] > 0
    dark = S.pass_summary(replace(S.PRESETS["micius"], y0=1e-2))                  # daylight-like background: no key
    assert dark["key_bits"] == 0
