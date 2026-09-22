import math
import pytest

from qll.channels.deep_space_geometry import split_path
from qll.channels.fiber_loss import attenuation_length_km, transmittance
from qll.channels.free_space_diffraction import divergence_half_angle_rad, geometric_transmittance

pytestmark = pytest.mark.phase1


def test_fiber_law_15_and_100_km():
    assert math.isclose(transmittance(15.0), 10 ** -0.3, rel_tol=1e-12)
    assert math.isclose(transmittance(100.0), 0.01, rel_tol=1e-12)


def test_attenuation_length():
    assert 21.5 < attenuation_length_km() < 22.0


def test_near_field_transmittance_is_one():
    assert geometric_transmittance(1.0, 850e-9, 0.05, 0.3) == pytest.approx(1.0, abs=1e-6)


def test_far_field_inverse_square():
    eta1 = geometric_transmittance(1e6, 850e-9, 0.05, 0.3)
    eta2 = geometric_transmittance(2e6, 850e-9, 0.05, 0.3)
    assert math.isclose(eta1 / eta2, 4.0, rel_tol=2e-3)   # exact Gaussian: 1/L^2 to first order in the far field


def test_divergence_850nm_5cm_waist():
    theta = divergence_half_angle_rad(850e-9, 0.05)
    assert 3e-6 < theta < 10e-6


def test_split_path_sums_to_total():
    segs = split_path(1000.0, [0.2, 0.3, 0.5])
    assert len(segs) == 3 and math.isclose(sum(segs), 1000.0)


def test_background_prefactor_derivation_check():                              # REQ-CHN-003 (prefactor)
    from qll.channels.thermal_background import background_count_rate, background_count_rate_from_radiance, background_from_spectral_radiance
    args = (3.7e14, 300.0, 1e9, 0.5, 1e-9, 0.7)
    both = background_count_rate(*args, polarizations=2)
    assert both == pytest.approx(background_count_rate_from_radiance(*args), rel=1e-9)   # Planck route = mode-counting route
    assert background_count_rate(*args) == pytest.approx(both / 2, rel=1e-12)
    # daylight: 1e7 W m^-2 sr^-1 m^-1 at 810 nm through a 1 nm filter, 1 m^2, 10 urad FOV -> ~1e5-1e6 /s
    N = background_from_spectral_radiance(1e7, 810e-9, 1e-9, 1.0, math.pi * (10e-6) ** 2, 0.5)
    assert 1e4 < N < 1e7
