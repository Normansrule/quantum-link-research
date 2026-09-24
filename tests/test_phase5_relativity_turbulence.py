"""Relativistic timing terms have the textbook magnitudes; the turbulence model reproduces standard site numbers."""
import math

import numpy as np
import pytest

from qll.channels.atmosphere import (aperture_averaging_factor, cn2_integral, fried_parameter_m, hufnagel_valley_cn2,
                                     rytov_variance, scintillation_index)
from qll.space.conjunction import sep_angle_series
from qll.space.relativity import (C, doppler_fractional, gravitational_redshift_earth_mars, line_of_sight_velocity_m_s,
                                  shapiro_delay_s, surface_potential, timing_budget_ns, M_EARTH, R_EARTH)

pytestmark = pytest.mark.phase5


def test_relativity_magnitudes():
    assert surface_potential(M_EARTH, R_EARTH) / C**2 == pytest.approx(-6.95e-10, rel=0.02)   # GPS textbook number
    z = gravitational_redshift_earth_mars(0.0)
    assert 2e-9 < z < 5e-9                                                                     # Sun dominates: Mars clock runs fast
    t = np.arange(0.0, 800.0, 2.0)
    vmax = max(abs(line_of_sight_velocity_m_s(x)) for x in t)
    assert 10e3 < vmax < 25e3 and max(abs(doppler_fractional(x)) for x in t) == pytest.approx(vmax / C, rel=1e-6)
    sep = sep_angle_series(t)
    tc, to = t[np.argmin(sep)], t[np.argmax(sep)]
    assert 100e-6 < shapiro_delay_s(tc) < 300e-6 and shapiro_delay_s(to) < 10e-6                # ~150-250 us at conjunction
    b = timing_budget_ns(tc, window_s=60.0)
    assert b["doppler_ns"] > 1e4 > b["gravitational_redshift_ns"] > b["second_order_doppler_ns"]   # ordering of the terms


def test_turbulence_model_reproduces_site_numbers():
    assert 0.03 < fried_parameter_m(cn2_integral(), 500e-9) < 0.25                              # 3-25 cm at 500 nm
    assert fried_parameter_m(cn2_integral(), 1550e-9) > fried_parameter_m(cn2_integral(), 500e-9)  # r0 ∝ λ^(6/5)
    s = rytov_variance(810e-9)
    assert 0.01 < s < 1.0                                                                       # weak turbulence for a downlink
    assert rytov_variance(810e-9, zenith_deg=60) > 2 * s                                        # sec^(11/6) growth
    assert scintillation_index(s) == pytest.approx(math.exp(s) - 1)
    assert aperture_averaging_factor(1.0, 810e-9, 1e6) < 0.5 < aperture_averaging_factor(0.05, 810e-9, 1e6)
    assert hufnagel_valley_cn2(0.0) > hufnagel_valley_cn2(5000.0) > hufnagel_valley_cn2(20000.0)
