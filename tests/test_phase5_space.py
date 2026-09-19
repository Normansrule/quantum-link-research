"""Phase 5: ephemeris envelope matches the constants, conjunction cadence matches the synodic period,
relays raise availability, coolers table, classical link limits."""
import math

import numpy as np
import pytest

from qll.channels.light_time_delay import one_way_delay_s
from qll.constants.astro import AU_METERS, EARTH_MARS_MAX_M, EARTH_MARS_MIN_M
from qll.space.classical_link import (DSOC_PSYCHE, holevo_capacity_bits_per_mode, holevo_limited_rate_bps,
                                      ppm_data_rate_bps, received_photons_per_s)
from qll.space.conjunction import availability, blackout_windows, expected_conjunctions
from qll.space.ephemeris import (EARTH, MARS, SYNODIC_PERIOD_DAYS, earth_mars_range_m, heliocentric_xy_au,
                                 kepler_E, one_way_light_time_s, range_envelope_m, sun_earth_mars_angle_deg)
from qll.space.platform_thermal import COOLERS, coolers_reaching, flyable
from qll.space.relay_constellation import Relay, constellation_availability, legs, relay_position_au

pytestmark = pytest.mark.phase5


def test_kepler_solver_and_orbit_radii():
    for M in (0.1, 1.0, 3.0, 6.0):
        E = kepler_E(M, 0.0934)
        assert abs(E - 0.0934 * math.sin(E) - M) < 1e-10
    r = [math.hypot(*heliocentric_xy_au(MARS, t)) for t in np.linspace(0, 687, 200)]
    assert min(r) == pytest.approx(MARS.a_au * (1 - MARS.e), rel=1e-3) and max(r) == pytest.approx(MARS.a_au * (1 + MARS.e), rel=1e-3)
    assert 365 < SYNODIC_PERIOD_DAYS < 1000 and SYNODIC_PERIOD_DAYS == pytest.approx(779.9, abs=0.5)


def test_range_envelope_matches_constants():                                      # closes the astro TODO to 1 %
    lo, hi = range_envelope_m()
    assert lo == pytest.approx(EARTH_MARS_MIN_M, rel=0.01) and hi == pytest.approx(EARTH_MARS_MAX_M, rel=0.01)
    assert 3.0 < one_way_delay_s(lo) / 60 < 3.2 and 22.0 < one_way_delay_s(hi) / 60 < 22.6


def test_conjunction_cadence_and_blackout_length():
    t = np.arange(0.0, 20 * 365.25, 1.0)
    w = blackout_windows(t, 3.0)
    assert abs(len(w) - expected_conjunctions(20 * 365.25)) <= 1
    lengths = [b - a for a, b in w]
    assert 10 < np.mean(lengths) < 35                                              # DSN experience: ~2-3 weeks
    assert 0.9 < availability(t, 3.0) < 1.0
    sep = [sun_earth_mars_angle_deg(x) for x in t[:1000]]
    assert 0 <= min(sep) and max(sep) <= 180


def test_relays_raise_availability_and_l4_geometry():
    t = np.arange(0.0, SYNODIC_PERIOD_DAYS * 2, 3.0)
    direct = [Relay("E", "earth_orbit")]
    with_l4 = direct + [Relay("L4", "L4"), Relay("L5", "L5")]
    assert constellation_availability(with_l4, t) > constellation_availability(direct, t)
    assert constellation_availability(with_l4, t) > 0.999
    ex, ey = heliocentric_xy_au(EARTH, 100.0); lx, ly = relay_position_au(Relay("L4", "L4"), 100.0)
    assert math.hypot(lx - ex, ly - ey) == pytest.approx(math.hypot(ex, ey), rel=1e-6)   # equilateral triangle
    lg = legs(Relay("M", "mars_orbit"), 50.0)
    assert lg["mars"]["range_m"] < 1.0 and lg["earth"]["range_m"] == pytest.approx(earth_mars_range_m(50.0), rel=1e-9)


def test_platform_thermal_table():
    assert flyable(5.0, 0.01) and flyable(0.1, 1e-7)
    assert not flyable(0.01, 1e-6)                                                  # no flown dilution fridge
    assert not flyable(5.0, 0.2)                                                    # 200 mW at 4-6 K exceeds flown coolers (tens of mW)
    assert any(c.flown for c in coolers_reaching(0.4)) and not all(c.flown for c in coolers_reaching(0.4)) and len(COOLERS) == 5


def test_classical_link_limits():
    assert holevo_capacity_bits_per_mode(1e-3) / (1e-3 * math.log2(1e3)) == pytest.approx(1.0, rel=0.2)
    assert holevo_capacity_bits_per_mode(0.0) == 0.0
    ph_far = received_photons_per_s(L_m=2.5 * AU_METERS, **DSOC_PSYCHE)
    assert 1e6 < ppm_data_rate_bps(ph_far) < 1e8                                    # tens of Mb/s beyond 2 au (DSOC class)
    assert ppm_data_rate_bps(received_photons_per_s(L_m=0.2 * AU_METERS, **DSOC_PSYCHE)) == 267e6   # modulator cap
    assert holevo_limited_rate_bps(1e7, 1e9) > ppm_data_rate_bps(1e7)              # PPM sits below Holevo
    assert one_way_light_time_s(0.0) > 0
