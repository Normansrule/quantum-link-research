"""Earth-Mars geometry versus time.

Physics
-------
Two-body heliocentric Kepler orbits with the IAU/JPL mean elements (semi-major axis a, eccentricity e,
mean longitude L, longitude of perihelion varpi, epoch J2000, coplanar to first order: Mars' inclination
of 1.85 deg changes ranges by < 0.1 %) [standish1992] [iau2012]. The eccentric anomaly is solved from
Kepler's equation M = E - e sin E by Newton iteration; range d(t) = |r_Mars - r_Earth|; one-way light time
d/c from channels.light_time_delay. The synodic period 1/(1/365.25 - 1/686.98) = 779.9 d sets the cadence of
oppositions and conjunctions. This is a mean-element model good to ~1 % in range; Phase 5 stretch: load a
JPL Horizons table (load_horizons_csv) and the model is bypassed. Constants in qll.constants.astro are the
envelope of this model.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from qll.channels.light_time_delay import one_way_delay_s
from qll.constants.astro import AU_METERS

J2000_JD = 2451545.0
SYNODIC_PERIOD_DAYS = 1.0 / (1.0 / 365.256 - 1.0 / 686.980)


@dataclass(frozen=True)
class MeanElements:
    a_au: float
    e: float
    L_deg: float          # mean longitude at J2000
    varpi_deg: float      # longitude of perihelion at J2000
    period_days: float


# Mean elements at J2000 (Standish 1992 / JPL "Keplerian elements for approximate positions"), inclination dropped.
EARTH = MeanElements(1.00000011, 0.01671022, 100.46435, 102.94719, 365.256)
MARS = MeanElements(1.52366231, 0.09341233, 355.45332, 336.04084, 686.980)


def kepler_E(M: float, e: float, tol: float = 1e-12) -> float:
    E = M if e < 0.8 else math.pi
    for _ in range(50):
        dE = (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
        E -= dE
        if abs(dE) < tol:
            break
    return E


def heliocentric_xy_au(el: MeanElements, t_days: float) -> tuple[float, float]:
    """Position in the ecliptic plane at t days after J2000."""
    L = math.radians(el.L_deg) + 2 * math.pi * t_days / el.period_days
    varpi = math.radians(el.varpi_deg)
    M = (L - varpi) % (2 * math.pi)
    E = kepler_E(M, el.e)
    nu = 2 * math.atan2(math.sqrt(1 + el.e) * math.sin(E / 2), math.sqrt(1 - el.e) * math.cos(E / 2))
    r = el.a_au * (1 - el.e * math.cos(E))
    theta = nu + varpi
    return r * math.cos(theta), r * math.sin(theta)


def earth_mars_range_m(t_days: float | np.ndarray) -> float | np.ndarray:
    t = np.atleast_1d(np.asarray(t_days, dtype=float))
    out = np.empty_like(t)
    for i, ti in enumerate(t):
        ex, ey = heliocentric_xy_au(EARTH, ti)
        mx, my = heliocentric_xy_au(MARS, ti)
        out[i] = math.hypot(mx - ex, my - ey) * AU_METERS
    return out if out.size > 1 else float(out[0])


def sun_earth_mars_angle_deg(t_days: float) -> float:
    """Angle at Earth between the Sun and Mars (solar elongation of Mars)."""
    ex, ey = heliocentric_xy_au(EARTH, t_days)
    mx, my = heliocentric_xy_au(MARS, t_days)
    sun = np.array([-ex, -ey]); mars = np.array([mx - ex, my - ey])
    c = float(np.dot(sun, mars) / (np.linalg.norm(sun) * np.linalg.norm(mars)))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def one_way_light_time_s(t_days: float | np.ndarray) -> float | np.ndarray:
    d = earth_mars_range_m(t_days)
    return one_way_delay_s(d) if np.isscalar(d) else np.array([one_way_delay_s(x) for x in d])


def range_envelope_m(years: float = 32.0, step_days: float = 1.0) -> tuple[float, float]:
    """Min and max range over ~15 synodic cycles (the 15-17 year cycle of favourable oppositions)."""
    t = np.arange(0.0, years * 365.25, step_days)
    d = earth_mars_range_m(t)
    return float(d.min()), float(d.max())


def load_horizons_csv(path: str) -> tuple[np.ndarray, np.ndarray]:
    """Read a JPL Horizons observer table exported as CSV with columns 'JD' and 'delta' (au); returns (t_days, range_m)."""
    import csv

    t, d = [], []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            t.append(float(row["JD"]) - J2000_JD)
            d.append(float(row["delta"]) * AU_METERS)
    return np.asarray(t), np.asarray(d)
