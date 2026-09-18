"""Randomly varied pulse intensities expose photon-number-splitting attacks on weak coherent sources.

Physics
-------
GLLP rate for a weak-coherent BB84 source with decoy states [gottesman2004] [lo2005] [ma2005]:
R = q { -Q_mu f h2(E_mu) + Q_1 [1 - h2(e_1)] }, where Q_mu = 1 - exp(-eta mu) + Y_0 (gain),
Q_1 = Y_1 mu e^{-mu} (single-photon gain), Y_1 = eta + Y_0 (single-photon yield, tight with decoys),
e_1 = (e_0 Y_0 + e_d eta)/Y_1, E_mu = (e_0 Y_0 + e_d (1 - e^{-eta mu}))/Q_mu, q = 1/2 sifting.
With mu ~ 0.5 the rate scales as eta, not eta^2; the optimum mu is near 0.5-0.7 [ma2005].
"""
from __future__ import annotations

import math

from qll.qkd.binary_entropy import h2


def decoy_rate_per_pulse(eta: float, mu: float = 0.5, Y0: float = 1e-6, e_det: float = 0.015, f_ec: float = 1.16, q: float = 0.5) -> float:
    e0 = 0.5
    Q_mu = 1 - math.exp(-eta * mu) + Y0
    E_mu = (e0 * Y0 + e_det * (1 - math.exp(-eta * mu))) / Q_mu
    Y1 = eta + Y0
    e1 = (e0 * Y0 + e_det * eta) / Y1
    Q1 = Y1 * mu * math.exp(-mu)
    return max(0.0, q * (-Q_mu * f_ec * h2(min(E_mu, 0.5)) + Q1 * (1 - h2(min(e1, 0.5)))))


def no_decoy_pns_rate_per_pulse(eta: float, mu: float = 0.1, e_det: float = 0.015, f_ec: float = 1.16, q: float = 0.5) -> float:
    """Without decoys, security requires attributing all multiphoton pulses to Eve (GLLP): rate ~ eta^2 at optimum."""
    Q_mu = 1 - math.exp(-eta * mu)
    p_multi = 1 - math.exp(-mu) * (1 + mu)
    delta = min(1.0, p_multi / Q_mu) if Q_mu > 0 else 1.0   # fraction of detections that may be multiphoton
    if delta >= 1.0:
        return 0.0
    return max(0.0, q * Q_mu * ((1 - delta) * (1 - h2(min(e_det / (1 - delta), 0.5))) - f_ec * h2(e_det)))
