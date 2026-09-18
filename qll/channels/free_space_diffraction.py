"""Geometric loss of a diverging Gaussian beam over a free-space path.

Physics
-------
A Gaussian beam of waist w0 has Rayleigh range z_R = pi w0^2 / lambda and radius
w(L) = w0 sqrt(1 + (L/z_R)^2) [siegman1986]; far-field half-angle theta = lambda/(pi w0).
A circular receiver of radius r_R centred on the beam collects eta = 1 - exp(-2 r_R^2 / w(L)^2)
(exact Gaussian-over-aperture integral), which reduces to (D_R/2w)^2 for a small aperture and to
1 for a large one [bourgoin2013] [liao2017]. The far-field limit gives the 1/L^2 law of REQ-CHN-002.
Beam truncation at the transmitter and obscuration are folded into eta_optics in link_budget.py.
"""
from __future__ import annotations

import math


def rayleigh_range_m(lambda_m: float, w0_m: float) -> float:
    return math.pi * w0_m**2 / lambda_m


def divergence_half_angle_rad(lambda_m: float, w0_m: float) -> float:
    """theta = lambda/(pi*w0) [liao2017]."""
    return lambda_m / (math.pi * w0_m)


def beam_radius_m(L_m: float, lambda_m: float, w0_m: float) -> float:
    """Exact Gaussian beam radius w(L) = w0 sqrt(1 + (L/z_R)^2) [siegman1986]."""
    return w0_m * math.sqrt(1.0 + (L_m / rayleigh_range_m(lambda_m, w0_m)) ** 2)


def geometric_transmittance(L_m: float, lambda_m: float, w0_m: float, D_rx_m: float) -> float:
    """Exact fraction of a Gaussian beam caught by a centred circular aperture of diameter D_rx."""
    w = beam_radius_m(L_m, lambda_m, w0_m)
    return 1.0 - math.exp(-2.0 * (D_rx_m / 2.0) ** 2 / w**2)


def geometric_transmittance_far_field(L_m: float, lambda_m: float, w0_m: float, D_rx_m: float) -> float:
    """Small-aperture, far-field approximation min(1, (D_rx/2w)^2), kept for comparison and teaching."""
    w = max(w0_m, divergence_half_angle_rad(lambda_m, w0_m) * L_m)
    return min(1.0, (D_rx_m / (2.0 * w)) ** 2)
