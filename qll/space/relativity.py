"""Relativistic corrections to timing and frequency on an Earth-Mars link.

Physics
-------
Three effects matter at the parts-in-10^-8 level that nanosecond coincidence windows over minutes of light
time require [ashby2003] [komar2014]:
  gravitational redshift between two clocks at potentials Phi_1, Phi_2: (f_2 - f_1)/f = (Phi_2 - Phi_1)/c^2,
      with Phi = -GM/r summed over the Sun and the local planet;
  first-order Doppler from the line-of-sight relative velocity v_r: (f_rx - f_tx)/f = -v_r/c, with the
      second-order (time-dilation) term -v^2/(2c^2);
  Shapiro delay of a signal passing the Sun at impact parameter b: Delta t = (2GM/c^3) ln(4 r_E r_M / b^2)
      (first order; the exact form uses r + r.n), up to ~250 us near conjunction [shapiro1964].
For a time-bin qubit the early/late separation (ns) is unchanged in shape, but its arrival must be predicted to the
coincidence window, so these enter the timing model, not the physics of the qubit. The relative velocity is taken
by finite difference of the Kepler ephemeris.
"""
from __future__ import annotations

import math

import numpy as np

from qll.constants.astro import AU_METERS
from qll.space.ephemeris import EARTH, MARS, earth_mars_range_m, heliocentric_xy_au

G = 6.67430e-11
M_SUN = 1.98892e30
M_EARTH = 5.9722e24
M_MARS = 6.4171e23
R_EARTH = 6.371e6
R_MARS = 3.3895e6
C = 299_792_458.0
GM_SUN = G * M_SUN


def surface_potential(mass_kg: float, radius_m: float) -> float:
    return -G * mass_kg / radius_m


def gravitational_redshift_earth_mars(t_days: float = 0.0) -> float:
    """Fractional frequency difference (Mars clock minus Earth clock) from the Sun and local planets: order 1e-9."""
    ex, ey = heliocentric_xy_au(EARTH, t_days); mx, my = heliocentric_xy_au(MARS, t_days)
    phi_e = -GM_SUN / (math.hypot(ex, ey) * AU_METERS) + surface_potential(M_EARTH, R_EARTH)
    phi_m = -GM_SUN / (math.hypot(mx, my) * AU_METERS) + surface_potential(M_MARS, R_MARS)
    return (phi_m - phi_e) / C**2


def line_of_sight_velocity_m_s(t_days: float, dt_days: float = 0.01) -> float:
    """Range rate d(range)/dt by finite difference (positive = receding)."""
    return (earth_mars_range_m(t_days + dt_days) - earth_mars_range_m(t_days - dt_days)) / (2 * dt_days * 86400)


def doppler_fractional(t_days: float) -> float:
    """First-order Doppler shift of a signal from Mars received at Earth: -v_r/c (order 1e-4)."""
    return -line_of_sight_velocity_m_s(t_days) / C


def shapiro_delay_s(t_days: float) -> float:
    """First-order Shapiro delay for the Earth-Mars path at time t (largest near conjunction)."""
    ex, ey = heliocentric_xy_au(EARTH, t_days); mx, my = heliocentric_xy_au(MARS, t_days)
    e = np.array([ex, ey]) * AU_METERS; m = np.array([mx, my]) * AU_METERS
    r_e, r_m = np.linalg.norm(e), np.linalg.norm(m)
    d = m - e; n = d / np.linalg.norm(d)
    return 2 * GM_SUN / C**3 * math.log((r_e + r_m + np.linalg.norm(d)) / (r_e + r_m - np.linalg.norm(d)))


def timing_budget_ns(t_days: float, window_s: float = 60.0) -> dict[str, float]:
    """How much each effect moves an arrival time over a window of `window_s` seconds of uncorrected clock."""
    return {
        "gravitational_redshift_ns": abs(gravitational_redshift_earth_mars(t_days)) * window_s * 1e9,
        "doppler_ns": abs(doppler_fractional(t_days)) * window_s * 1e9,
        "second_order_doppler_ns": (line_of_sight_velocity_m_s(t_days) ** 2 / (2 * C**2)) * window_s * 1e9,
        "shapiro_ns": shapiro_delay_s(t_days) * 1e9,
    }
