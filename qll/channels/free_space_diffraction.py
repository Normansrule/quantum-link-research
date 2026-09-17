"""Geometric loss of a diverging beam over a free-space path.

Physics
-------
A Gaussian beam of waist w0 diverges with half-angle theta = lambda/(pi*w0) [liao2017]
[bourgoin2013]. In the far field the beam radius grows as w = theta*L, and a receiver of
diameter D_r collects the fraction min(1, (D_r/(2w))**2) of the power, giving the 1/L**2 law.
Phase 3 replaces the far-field forms with the exact Gaussian expressions
(see docs/physics_module_design.md).
"""
from __future__ import annotations

import math


def divergence_half_angle_rad(lambda_m: float, w0_m: float) -> float:
    """theta = lambda/(pi*w0) [liao2017]."""
    return lambda_m / (math.pi * w0_m)


def beam_radius_m(L_m: float, lambda_m: float, w0_m: float) -> float:
    """Far-field beam radius w = theta*L; returns w0 when the far-field radius is smaller."""
    return max(w0_m, divergence_half_angle_rad(lambda_m, w0_m) * L_m)


def geometric_transmittance(L_m: float, lambda_m: float, w0_m: float, D_rx_m: float) -> float:
    """min(1, (D_r/(2w))**2): fraction of a uniformly spread beam caught by the aperture [bourgoin2013]."""
    w = beam_radius_m(L_m, lambda_m, w0_m)
    return min(1.0, (D_rx_m / (2.0 * w)) ** 2)
