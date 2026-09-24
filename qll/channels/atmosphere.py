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


# --- turbulence (added 0.20.0) --------------------------------------------------------------------------------
def hufnagel_valley_cn2(h_m: float, wind_m_s: float = 21.0, A: float = 1.7e-14) -> float:
    """Hufnagel-Valley 5/7 profile of C_n^2 (m^-2/3) versus altitude [andrews2005]."""
    return (0.00594 * (wind_m_s / 27) ** 2 * (1e-5 * h_m) ** 10 * math.exp(-h_m / 1000)
            + 2.7e-16 * math.exp(-h_m / 1500) + A * math.exp(-h_m / 100))


def cn2_integral(zenith_deg: float = 0.0, h_max_m: float = 20e3, n: int = 2000, **kw) -> float:
    """sec(zeta) * int C_n^2 dh for a slant path through the HV-5/7 atmosphere."""
    hs = [h_max_m * (i + 0.5) / n for i in range(n)]
    return sum(hufnagel_valley_cn2(h, **kw) for h in hs) * (h_max_m / n) / math.cos(math.radians(zenith_deg))


def rytov_variance(lambda_m: float, zenith_deg: float = 0.0, h_max_m: float = 20e3, n: int = 400, **kw) -> float:
    """Plane-wave Rytov variance for a downlink, sigma_R^2 = 2.25 k^(7/6) sec^(11/6)(zeta) int C_n^2(h) h^(5/6) dh
    [andrews2005]; < 1 is weak turbulence (typical for downlinks), > 1 strong (uplinks)."""
    k = 2 * math.pi / lambda_m
    hs = [h_max_m * (i + 0.5) / n for i in range(n)]
    integral = sum(hufnagel_valley_cn2(h, **kw) * h ** (5 / 6) for h in hs) * (h_max_m / n)
    return 2.25 * k ** (7 / 6) * (1 / math.cos(math.radians(zenith_deg))) ** (11 / 6) * integral


def scintillation_index(sigma_R2: float) -> float:
    """Aperture-unaveraged irradiance variance in weak turbulence: sigma_I^2 ~ exp(sigma_R^2) - 1 ~ sigma_R^2."""
    return math.exp(sigma_R2) - 1


def aperture_averaging_factor(D_m: float, lambda_m: float, L_m: float) -> float:
    """Reduction of scintillation by a receiver of diameter D: A ~ [1 + 1.06 (k D^2 / 4L)^(7/6)]^-1 [andrews2005]."""
    k = 2 * math.pi / lambda_m
    return 1 / (1 + 1.06 * (k * D_m**2 / (4 * L_m)) ** (7 / 6))


def uplink_beam_wander_rad(w0_m: float, cn2_int: float) -> float:
    """rms angular beam wander for an uplink from a transmitter of waist w0 [andrews2005]: sigma ~ 0.54 (C_n^2 L) ... simplified
    as sqrt(2.87 * cn2_int * w0^(-1/3)) which is the leading-order Fried-type scaling; order 1-10 urad for w0 ~ 10 cm."""
    return math.sqrt(2.87 * cn2_int * w0_m ** (-1 / 3))
