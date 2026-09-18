"""Extinction and turbulence of a slant path through the atmosphere.

Physics
-------
Beer-Lambert: eta_atm = exp(-tau_zenith * airmass), airmass ~ 1/sin(elevation) for elevation > ~10 deg
[andrews2005]. Zenith optical depth tau depends on wavelength and aerosol load; representative clear-sky
values (MODTRAN-class, as used by [bourgoin2013] and [bedington2017]): ~0.35 at 780-850 nm, ~0.15 at
1550 nm for a rural aerosol model, i.e. 1.5 dB and 0.65 dB at zenith. Turbulence: the Fried parameter
r0 = (0.423 k^2 sec(zeta) int C_n^2 dz)^(-3/5); beam wander and scintillation are second-order for a
downlink (the beam is already wide when it meets the turbulence) and first-order for an uplink, which
is why downlinks are used for quantum signals [bourgoin2013].
"""
from __future__ import annotations

import math

ZENITH_OPTICAL_DEPTH = {810e-9: 0.35, 850e-9: 0.32, 1550e-9: 0.15}  # TODO: verify against MODTRAN for the site
ATMOSPHERE_SCALE_HEIGHT_M = 8_000.0


def airmass(elevation_deg: float) -> float:
    if elevation_deg <= 0:
        raise ValueError("elevation must be positive")
    return 1.0 / math.sin(math.radians(elevation_deg))


def atmospheric_transmittance(elevation_deg: float, lambda_m: float = 810e-9, tau_zenith: float | None = None) -> float:
    """Beer-Lambert transmittance for a slant path [andrews2005]."""
    if tau_zenith is None:
        key = min(ZENITH_OPTICAL_DEPTH, key=lambda k: abs(k - lambda_m))
        tau_zenith = ZENITH_OPTICAL_DEPTH[key]
    return math.exp(-tau_zenith * airmass(elevation_deg))


def fried_parameter_m(cn2_integral: float, lambda_m: float, zenith_deg: float = 0.0) -> float:
    """r0 = (0.423 k^2 sec(zeta) * int C_n^2 dz)^(-3/5); typical night-time sites give r0 ~ 5-20 cm at 500 nm."""
    k = 2 * math.pi / lambda_m
    return (0.423 * k**2 / math.cos(math.radians(zenith_deg)) * cn2_integral) ** (-3 / 5)
