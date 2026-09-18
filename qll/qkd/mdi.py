"""Measurement-device-independent QKD: an untrusted midpoint performs the Bell measurement.

Physics
-------
Alice and Bob each send BB84 states to Charlie, who announces which Bell state he projected onto;
detector side channels disappear because Charlie may be the adversary [lo2012] [braunstein2012].
The gain scales as eta_A * eta_B (a two-photon coincidence), i.e. as eta for a symmetric link with the
midpoint in the middle, the same scaling as direct BB84 but with half the range per arm. Rate (asymptotic,
single-photon contributions): R = Q_11 [1 - h2(e_11)] - Q_rect f h2(E_rect) [lo2012].
"""
from __future__ import annotations

from qll.qkd.binary_entropy import h2


def mdi_rate_per_pulse(eta_total: float, mu: float = 0.3, e_det: float = 0.015, f_ec: float = 1.16, Y0: float = 1e-6) -> float:
    """Symmetric MDI with each arm having transmittance sqrt(eta_total); crude single-photon-only estimate."""
    import math

    eta_arm = math.sqrt(eta_total)
    Q11 = (mu * math.exp(-mu)) ** 2 * eta_arm**2 / 2          # both single photons arrive and interfere
    e11 = e_det + Y0 / max(Q11, 1e-30) * 0.5
    Qrect = Q11 + Y0
    return max(0.0, Q11 * (1 - h2(min(e11, 0.5))) - Qrect * f_ec * h2(min(e11, 0.5)))
