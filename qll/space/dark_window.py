"""The dark-sky window: the fraction of each day during which a ground station sees Mars above a minimum elevation
while the Sun is below the horizon by a chosen depression.

Physics
-------
A body at hour angle H and declination delta, seen from latitude phi, has altitude h with
    sin h = sin phi sin delta + cos phi cos delta cos H        [meeus1998].
For an equatorial station (phi = 0) and bodies on the celestial equator (delta = 0) this is h = 90 deg - |H|, so a
body is above elevation e for |H| <= 90 - e, and the Sun is more than s below the horizon for |H_sun| >= 90 + s. Mars
sits at the solar elongation epsilon from the Sun, H_mars = H_sun + epsilon, so the two conditions overlap on an arc of
hour angle of length
    clip(epsilon - e - s, 0, min(180 - 2e, 180 - 2s))   degrees,
out of 360 per day. The window closes entirely when epsilon < e + s: for weeks to months either side of conjunction
Mars is up only in daylight. The model neglects the obliquity of the ecliptic (23.4 deg) and the station's latitude,
which shift the window by some days but not the conclusion; with the Sun up, the best a station can do is to observe
Mars on the side away from the Sun, where the Sun's zenith angle is 90 - e + epsilon.
"""
from __future__ import annotations

import numpy as np


def _check(*values) -> None:
    for v in values:
        if isinstance(v, (complex, np.complexfloating)):
            raise TypeError("dark-window inputs must be real")


def dark_fraction(elongation_deg: float, min_elevation_deg: float = 40.0, sun_depression_deg: float = 12.0) -> float:
    """Fraction of the day with Mars above min_elevation_deg and the Sun more than sun_depression_deg below the horizon."""
    _check(elongation_deg, min_elevation_deg, sun_depression_deg)
    eps, e, s = abs(float(elongation_deg)), float(min_elevation_deg), float(sun_depression_deg)
    if not (0.0 <= e < 90.0 and 0.0 <= s < 90.0):
        raise ValueError("elevation and depression must lie in [0, 90)")
    arc = min(max(eps - e - s, 0.0), 180.0 - 2 * e, 180.0 - 2 * s)
    return arc / 360.0

