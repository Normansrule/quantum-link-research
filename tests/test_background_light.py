"""Background light for the Earth-Mars link: the Lambert sphere's phase function against direct integration, the
single-mode photon rate against the blackbody occupation number, the Airy envelope against the exact pattern, and the
dark-sky window against a brute-force sweep of the hour angle."""
import math

import numpy as np
import pytest
from scipy.special import j1

from qll.channels.planetshine import (PLANETS, airy_leakage, filter_width_nm, lambert_phase, planetshine_photon_flux,
                                      single_mode_photon_rate, solar_irradiance, sunlit_radiance)
from qll.constants.physical import C_LIGHT, H_PLANCK, K_BOLTZMANN
from qll.space.dark_window import dark_fraction

pytestmark = pytest.mark.phase1
LAM = 1550e-9


def _lambert_sphere_brightness(alpha: float, n: int = 400) -> float:
    """Direct integral of cos(i) cos(e) over the lit and visible hemisphere of a unit Lambertian sphere."""
    th, ph = np.meshgrid(np.linspace(0, np.pi, n), np.linspace(0, 2 * np.pi, 2 * n), indexing="ij")
    normal = np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)])
    sun = np.array([1.0, 0.0, 0.0])[:, None, None]
    obs = np.array([math.cos(alpha), math.sin(alpha), 0.0])[:, None, None]
    mu0, mu = np.clip((normal * sun).sum(0), 0, None), np.clip((normal * obs).sum(0), 0, None)
    return float(np.trapezoid(np.trapezoid(mu0 * mu * np.sin(th), dx=2 * np.pi / (2 * n - 1), axis=1), dx=np.pi / (n - 1)))


def test_lambert_phase_function_is_the_integrated_sphere():
    assert lambert_phase(0.0) == pytest.approx(1.0) and lambert_phase(math.pi) == pytest.approx(0.0, abs=1e-15)
    assert lambert_phase(math.pi / 2) == pytest.approx(1 / math.pi)
    full = _lambert_sphere_brightness(0.0)
    for a in (0.3, 1.0, math.pi / 2, 2.5):
        assert _lambert_sphere_brightness(a) / full == pytest.approx(lambert_phase(a), abs=2e-3)


def test_unresolved_flux_scales_and_normalizes():
    base = planetshine_photon_flux(LAM, 1e8, 1e11, 0.0)
    assert planetshine_photon_flux(LAM, 1e8, 2e11, 0.0) == pytest.approx(base / 4)
    assert planetshine_photon_flux(LAM, 3e8, 1e11, 0.0) == pytest.approx(3 * base)
    R, p, _ = PLANETS["earth"]
    watts = solar_irradiance(LAM) * p * (R / 1e11) ** 2 * filter_width_nm(LAM, 1e8)
    assert base == pytest.approx(watts / (H_PLANCK * C_LIGHT / LAM))
    assert filter_width_nm(LAM, 1e8) == pytest.approx(8.01e-4, rel=1e-3)          # 100 MHz at 1550 nm is 0.8 pm


def test_lambertian_patch_reflects_its_albedo():
    # a Lambertian surface of radiance L has exitance pi L, which must equal A E cos z
    _, A, _ = PLANETS["earth"]
    for z in (0.0, 0.7, 1.3):
        assert math.pi * sunlit_radiance(LAM, z) == pytest.approx(A * solar_irradiance(LAM) * math.cos(z))
    assert sunlit_radiance(LAM, 2.0) == 0.0


def test_single_mode_rate_is_the_blackbody_occupation_number():
    # a blackbody puts 1/(exp(h nu / kT) - 1) photons per second per hertz into each mode and polarization
    for T, lam in ((5772.0, 1550e-9), (3000.0, 810e-9), (1500.0, 2e-6)):
        nu = C_LIGHT / lam
        B_lambda = 2 * H_PLANCK * C_LIGHT**2 / lam**5 / math.expm1(H_PLANCK * nu / (K_BOLTZMANN * T))   # W m^-2 sr^-1 m^-1
        n_bar = 1 / math.expm1(H_PLANCK * nu / (K_BOLTZMANN * T))
        assert single_mode_photon_rate(B_lambda * 1e-9, lam, 1e8) == pytest.approx(2 * n_bar * 1e8, rel=1e-9)


def test_airy_envelope_bounds_the_exact_pattern():
    D = 4.0
    x = np.linspace(20.0, 400.0, 200001)
    exact = (2 * j1(x) / x) ** 2
    env = 8 / (np.pi * x**3)
    assert np.all(exact <= env * 1.02)
    for x0 in (50.0, 200.0):          # the envelope touches the pattern's local maxima
        sel = (x > x0) & (x < x0 + math.pi)
        assert (exact * x**3)[sel].max() == pytest.approx(8 / np.pi, rel=0.01)
    theta_core = 3.0 * LAM / (math.pi * D)
    assert airy_leakage(theta_core, D, LAM) == 1.0
    theta = 100.0 * LAM / (math.pi * D)
    assert airy_leakage(theta, D, LAM) == pytest.approx(8 / (math.pi * 100.0**3))
    assert airy_leakage(-theta, D, LAM) == airy_leakage(theta, D, LAM)


def test_dark_window_matches_a_sweep_of_the_hour_angle():
    H = np.linspace(-180.0, 180.0, 720001)[:-1]
    for eps in (0.0, 30.0, 52.0, 60.0, 90.0, 140.0, 180.0):
        for e, s in ((40.0, 12.0), (20.0, 18.0), (60.0, 6.0)):
            h_sun = 90.0 - np.abs(H)
            h_mars = 90.0 - np.abs((H + eps + 180.0) % 360.0 - 180.0)
            brute = float(np.mean((h_sun <= -s) & (h_mars >= e)))
            assert dark_fraction(eps, e, s) == pytest.approx(brute, abs=2e-5)
    assert dark_fraction(51.9) == 0.0 and dark_fraction(180.0) == pytest.approx(100 / 360)


def test_validation():
    with pytest.raises(TypeError):
        lambert_phase(1j)
    with pytest.raises(TypeError):
        planetshine_photon_flux(LAM, 1e8, 1e11 + 0j, 0.0)
    with pytest.raises(TypeError):
        dark_fraction(90.0 + 0j)
    with pytest.raises(ValueError):
        dark_fraction(90.0, 95.0)
