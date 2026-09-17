"""Thermal photons from a warm scene entering an optical receiver.

Physics
-------
Each spatio-temporal mode of a blackbody at temperature T carries n = 1/(exp(h*nu/(k_B*T)) - 1)
photons [clerk2010] [mandel1995]. A receiver of area A and field of view Omega sees
M = A*Omega/lambda**2 spatial modes, and a filter of bandwidth B (Hz) admits B temporal modes
per second, so the background count rate is N = n * M * B * eta_det per polarization.
TODO: verify prefactor (polarization and mode-counting conventions) in Phase 3.
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
                          solid_angle_sr: float, eta_det: float) -> float:
    """Background counts per second, single polarization. TODO: verify prefactor."""
    lambda_m = 299_792_458.0 / nu_hz
    n = blackbody_occupation(nu_hz, T)
    return n * bandwidth_hz * spatial_modes(area_m2, solid_angle_sr, lambda_m) * eta_det
