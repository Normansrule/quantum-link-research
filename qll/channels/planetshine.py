"""Sunlight reflected by a planet into a single-mode receiver that is pointed at, or near, that planet.

Physics
-------
A receiver near Mars listening for single photons from the Earth end of the link is diffraction limited: it accepts
one spatial mode, whose etendue is A Omega = lambda^2 (the antenna theorem [siegman1986]). Earth is not a point for such
a receiver. At the closest approach its disk subtends about 190 microradians, and a 4 m telescope resolves
lambda / D = 0.39 microradian at 1550 nm, so the mode sees only a small patch of Earth around the transmitter. The
background photons per second in that mode, both polarizations, in a filter of bandwidth B_nu, are
    N = L_lambda Delta_lambda lambda^2 / (h c / lambda),   Delta_lambda = lambda^2 B_nu / c,
with L_lambda the spectral radiance of the patch. A sunlit Lambertian patch of normal albedo A, with the Sun at zenith
angle z, has L_lambda = A E_sun,lambda(r) cos z / pi [hapke2012], E_sun,lambda(r) = E_sun,lambda(1 au) / r^2
[gueymard2004]. On the night side the patch still glows: near 1.5 micrometres the hydroxyl airglow of the upper
atmosphere dominates [rousselot2000]; NIGHT_RADIANCE below is an order-of-magnitude, line-averaged value (a narrow
filter placed between the lines does better). The receiver aperture does not appear in N, and the signal collected
in the same mode grows with the aperture, which is why a larger telescope helps signal-to-noise only through the signal.

When the planet is off the receiver's axis by an angle theta much larger than its own angular radius it acts as an
unresolved source of spectral flux
    F_lambda = E_sun,lambda(r) p (R / d)^2 Phi(alpha)
at distance d, with p the geometric albedo, R the radius, and for a Lambertian sphere [russell1916]
    Phi(alpha) = (sin alpha + (pi - alpha) cos alpha) / pi,
1 at full phase (alpha = 0) and 0 at new phase (alpha = pi). The power that reaches the on-axis mode is F_lambda A_rx
times the receiver's off-axis rejection: for a clear circular aperture the Airy envelope 8 / (pi x^3),
x = pi D theta / lambda, beyond the first dark ring [born1999]; for a real telescope never better than its stray-light
floor (scatter from mirrors and baffles), a design parameter. The solar irradiance values are representative of the
standard extraterrestrial spectrum to about 10 %; the albedos are representative near-infrared values and are the
least certain inputs (TODO: replace with band-resolved values).
"""
from __future__ import annotations

import math

import numpy as np

from qll.constants.physical import C_LIGHT, H_PLANCK

# Solar spectral irradiance at 1 au, W m^-2 nm^-1, near the two link wavelengths [gueymard2004]
SOLAR_IRRADIANCE_1AU = {810e-9: 1.13, 1550e-9: 0.26}
PLANETS = {  # radius (m), representative near-infrared albedo (approximate), mean distance from the Sun (au)
    "earth": (6.371e6, 0.30, 1.0),
    "mars": (3.3895e6, 0.25, 1.524),
}
# Line-averaged hydroxyl airglow near 1.5 micrometres, W m^-2 sr^-1 nm^-1, order of magnitude [rousselot2000]
NIGHT_RADIANCE = 1e-7


def _check(*values) -> None:
    for v in values:
        if isinstance(v, (complex, np.complexfloating)):
            raise TypeError("planetshine inputs must be real")


def solar_irradiance(lambda_m: float) -> float:
    """Solar spectral irradiance at 1 au (W m^-2 nm^-1) for the tabulated wavelength nearest lambda_m."""
    _check(lambda_m)
    key = min(SOLAR_IRRADIANCE_1AU, key=lambda k: abs(k - lambda_m))
    return SOLAR_IRRADIANCE_1AU[key]


def filter_width_nm(lambda_m: float, bandwidth_hz: float) -> float:
    """Wavelength width of a filter of frequency width bandwidth_hz: lambda^2 B / c, in nanometres."""
    _check(lambda_m, bandwidth_hz)
    return lambda_m**2 * bandwidth_hz / C_LIGHT * 1e9


def lambert_phase(alpha_rad: float) -> float:
    """Phase function of a Lambertian sphere, 1 at full phase and 0 at new phase [russell1916]."""
    _check(alpha_rad)
    a = min(max(float(alpha_rad), 0.0), math.pi)
    return (math.sin(a) + (math.pi - a) * math.cos(a)) / math.pi


def sunlit_radiance(lambda_m: float, sun_zenith_rad: float = 0.0, planet: str = "earth") -> float:
    """Spectral radiance (W m^-2 sr^-1 nm^-1) of a sunlit Lambertian patch: A E cos z / pi, zero with the Sun down."""
    _check(lambda_m, sun_zenith_rad)
    _, albedo, r_au = PLANETS[planet]
    return albedo * solar_irradiance(lambda_m) / r_au**2 * max(0.0, math.cos(sun_zenith_rad)) / math.pi


def single_mode_photon_rate(radiance: float, lambda_m: float, bandwidth_hz: float) -> float:
    """Photons per second, both polarizations, that an extended source of spectral radiance `radiance`
    (W m^-2 sr^-1 nm^-1) puts into one diffraction-limited spatial mode (etendue lambda^2) [siegman1986]."""
    _check(radiance, lambda_m, bandwidth_hz)
    return radiance * filter_width_nm(lambda_m, bandwidth_hz) * lambda_m**2 / (H_PLANCK * C_LIGHT / lambda_m)


def planetshine_photon_flux(lambda_m: float, bandwidth_hz: float, distance_m: float, phase_angle_rad: float,
                            planet: str = "earth") -> float:
    """Reflected-sunlight photons per second per square metre at distance_m from an unresolved planet."""
    _check(lambda_m, bandwidth_hz, distance_m, phase_angle_rad)
    R, p, r_au = PLANETS[planet]
    F_nm = solar_irradiance(lambda_m) / r_au**2 * p * (R / distance_m) ** 2 * lambert_phase(phase_angle_rad)
    return F_nm * filter_width_nm(lambda_m, bandwidth_hz) / (H_PLANCK * C_LIGHT / lambda_m)


def airy_leakage(theta_rad: float, diameter_m: float, lambda_m: float) -> float:
    """Off-axis rejection of a clear circular aperture relative to its on-axis peak: 1 inside the first dark ring
    (x < 3.83), the Airy envelope 8 / (pi x^3) outside, x = pi D theta / lambda [born1999]."""
    _check(theta_rad, diameter_m, lambda_m)
    x = math.pi * diameter_m * abs(theta_rad) / lambda_m
    return 1.0 if x < 3.8317 else min(1.0, 8.0 / (math.pi * x**3))
