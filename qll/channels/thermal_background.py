"""Thermal photons from a warm scene entering an optical receiver.

Physics
-------
Each spatio-temporal mode of a blackbody at temperature T carries n = 1/(exp(h*nu/(k_B*T)) - 1)
photons [clerk2010] [mandel1995]. A receiver of area A and field of view Omega sees
M = A*Omega/lambda**2 spatial modes, and a filter of bandwidth B (Hz) admits B temporal modes
per second, so the background count rate is N = n * M * B * eta_det per polarization.
Derivation check (0.17.0): Planck's spectral radiance L_nu = (2 h nu^3 / c^2) n counts both polarizations;
the photon flux through A*Omega in bandwidth B is L_nu A Omega B /(h nu) = 2 n B A Omega nu^2/c^2
= 2 n B (A Omega/lambda^2), so the single-polarization rate is exactly n*B*M: the prefactor is 1 for one
polarization and 2 for both [planck1901] [mandel1995]. background_count_rate_from_radiance implements the
Planck route independently and the tests require the two to agree. Daylight sky is not a blackbody; for it
use background_from_spectral_radiance with a measured L_lambda (W m^-2 sr^-1 m^-1) [er-long2005].
"""
from __future__ import annotations

import numpy as np

from qll.constants.physical import H_PLANCK, K_BOLTZMANN


def blackbody_occupation(nu_hz: float, T: float) -> float:
    """Mean photon number per mode at frequency ``nu_hz`` and temperature ``T`` [mandel1995]."""
    if T <= 0.0:
        return 0.0
    x = H_PLANCK * nu_hz / (K_BOLTZMANN * T)
    if x > 700.0:
        return 0.0
    return float(1.0 / np.expm1(x))


def spatial_modes(area_m2: float, solid_angle_sr: float, lambda_m: float) -> float:
    """Number of spatial modes A*Omega/lambda**2 (1 for a diffraction-limited receiver)."""
    return area_m2 * solid_angle_sr / lambda_m**2


def background_count_rate(nu_hz: float, T: float, bandwidth_hz: float, area_m2: float,
                          solid_angle_sr: float, eta_det: float, polarizations: int = 1) -> float:
    """Background counts per second from a blackbody scene; one polarization by default (a polarization-encoded
    receiver sees one), two for an unpolarized detector."""
    lambda_m = 299_792_458.0 / nu_hz
    n = blackbody_occupation(nu_hz, T)
    return polarizations * n * bandwidth_hz * spatial_modes(area_m2, solid_angle_sr, lambda_m) * eta_det


def planck_spectral_radiance_nu(nu_hz: float, T: float) -> float:
    """L_nu in W m^-2 sr^-1 Hz^-1, both polarizations [planck1901]."""
    c = 299_792_458.0
    return 2 * H_PLANCK * nu_hz**3 / c**2 * blackbody_occupation(nu_hz, T)


def background_count_rate_from_radiance(nu_hz: float, T: float, bandwidth_hz: float, area_m2: float,
                                        solid_angle_sr: float, eta_det: float) -> float:
    """Independent route: photon flux = L_nu * A * Omega * B / (h nu), both polarizations."""
    return planck_spectral_radiance_nu(nu_hz, T) * area_m2 * solid_angle_sr * bandwidth_hz / (H_PLANCK * nu_hz) * eta_det


def background_from_spectral_radiance(L_lambda_W_m2_sr_m: float, lambda_m: float, bandwidth_m: float, area_m2: float,
                                      solid_angle_sr: float, eta_det: float) -> float:
    """Counts per second from a measured sky spectral radiance L_lambda over a filter of width bandwidth_m (metres).
    Daylight zenith sky at 800 nm is of order 1e-2 to 1e-1 W m^-2 sr^-1 nm^-1 = 1e7 to 1e8 W m^-2 sr^-1 m^-1
    [er-long2005] (TODO: verify for the site); night sky is 1e6-1e8 times darker."""
    c = 299_792_458.0
    E_ph = H_PLANCK * c / lambda_m
    return L_lambda_W_m2_sr_m * area_m2 * solid_angle_sr * bandwidth_m / E_ph * eta_det
