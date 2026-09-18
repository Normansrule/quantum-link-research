"""Pointing error is a random offset of the beam centre; average the collected power over it.

Physics
-------
For Gaussian pointing jitter with angular standard deviation sigma_p (per axis) and beam radius w at
range L, the mean transmittance relative to perfect pointing is eta_point = w^2 / (w^2 + 4 sigma_p^2 L^2)
[bourgoin2013 App. A]. Micius: coarse pointing ~ 1e-4 rad from the attitude loop, fine pointing ~ 1e-6 rad
from a fast-steering mirror; Jinan-1 reports fine tracking near 1 urad [li2025jinan].
"""
from __future__ import annotations


def pointing_efficiency(sigma_rad: float, L_m: float, w_m: float) -> float:
    if sigma_rad < 0 or w_m <= 0:
        raise ValueError("sigma must be non-negative and w positive")
    return w_m**2 / (w_m**2 + 4.0 * sigma_rad**2 * L_m**2)
