"""Solar conjunction: when the Sun blocks (or blinds) the Earth-Mars line of sight.

Physics
-------
Deep Space Network (DSN) practice suspends critical commanding when the Sun-Earth-probe (SEP) angle falls
below ~3 deg (coronal plasma degrades X/Ka-band links) and degrades optical links well before that: the
receiver looks into the solar corona and sky background rises steeply within ~10 deg [dsn2020] [biswas2024].
Every synodic period (779.9 d) Mars passes through conjunction once (SEP -> 0) and opposition once
(SEP -> 180 deg, closest approach). This module finds the blackout windows for a given SEP threshold.
"""
from __future__ import annotations

import numpy as np

from qll.space.ephemeris import SYNODIC_PERIOD_DAYS, sun_earth_mars_angle_deg


def sep_angle_series(t_days: np.ndarray) -> np.ndarray:
    return np.array([sun_earth_mars_angle_deg(t) for t in t_days])


def blackout_windows(t_days: np.ndarray, sep_threshold_deg: float = 3.0) -> list[tuple[float, float]]:
    sep = sep_angle_series(t_days)
    blocked = sep < sep_threshold_deg
    windows, start = [], None
    for i, b in enumerate(blocked):
        if b and start is None:
            start = t_days[i]
        if not b and start is not None:
            windows.append((start, t_days[i - 1])); start = None
    if start is not None:
        windows.append((start, t_days[-1]))
    return windows


def availability(t_days: np.ndarray, sep_threshold_deg: float = 3.0) -> float:
    """Fraction of time the line of sight is clear of the Sun."""
    return float(np.mean(sep_angle_series(t_days) >= sep_threshold_deg))


def expected_conjunctions(span_days: float) -> float:
    return span_days / SYNODIC_PERIOD_DAYS
