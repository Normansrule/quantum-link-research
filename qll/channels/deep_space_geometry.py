"""Ranges and relay placement along an interplanetary path.

Physics
-------
Only geometry lives here: the Earth-Mars range envelope from ``qll.constants.astro`` and the
division of a path into relay segments. Loss, delay, and noise are computed by the other
channel modules from these distances.
"""
from __future__ import annotations

from qll.constants.astro import earth_mars_envelope_m


def earth_mars_range_envelope_m() -> tuple[float, float]:
    """(min, max) Earth-Mars range in meters [iau2012]; TODO: verify vs JPL Horizons."""
    return earth_mars_envelope_m()


def split_path(total_m: float, fractions: list[float]) -> list[float]:
    """Split ``total_m`` into segments proportional to ``fractions`` (which must sum to 1)."""
    if abs(sum(fractions) - 1.0) > 1e-9:
        raise ValueError("fractions must sum to 1")
    return [total_m * f for f in fractions]
