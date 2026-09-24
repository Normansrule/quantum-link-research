"""Quantum frequency conversion: moving a photon from an emitter's wavelength to the telecom band.

Physics
-------
Difference-frequency generation in a periodically poled lithium-niobate (PPLN) waveguide with a strong pump
converts a signal photon at lambda_s to lambda_t = (1/lambda_s - 1/lambda_p)^-1 with internal efficiency
    eta_int(P) = sin^2( sqrt(eta_nor * P) * L ),
periodic in pump power with a first maximum of 100 % at P_max = pi^2 / (4 eta_nor L^2) [kumar1990] [zaske2012].
The pump also generates noise photons at the target wavelength (anti-Stokes Raman, SPDC), at a rate ~ linear in P,
so the signal-to-noise ratio is maximised below full conversion; the noise per nanosecond gate sets the QBER floor
exactly as background does in link_budget.py. NV: 637 -> 1588 nm with a 1064 nm pump [dreau2018]; SiV 737 -> 1550 nm needs a 1405 nm pump
(demonstrated conversions of SiV emission to ~1350 nm used a longer pump [bersin2024], TODO: verify). External efficiency multiplies eta_int by coupling and filter transmissions,
typically 0.3-0.6 [vanleent2020].
"""
from __future__ import annotations

import math
from dataclasses import dataclass


def target_wavelength_m(lambda_signal_m: float, lambda_pump_m: float) -> float:
    """Difference frequency: 1/lambda_t = 1/lambda_s - 1/lambda_p (pump must be redder than the signal)."""
    if lambda_pump_m <= lambda_signal_m:
        raise ValueError("pump wavelength must exceed the signal wavelength for DFG")
    return 1.0 / (1.0 / lambda_signal_m - 1.0 / lambda_pump_m)


def internal_efficiency(P_pump_W: float, eta_nor_per_W_cm2: float, L_cm: float) -> float:
    """sin^2(sqrt(eta_nor P) L); eta_nor in W^-1 cm^-2 (PPLN waveguides: ~1 W^-1 cm^-2, quoted as ~100 %/W/cm^2) [zaske2012]."""
    return math.sin(math.sqrt(eta_nor_per_W_cm2 * P_pump_W) * L_cm) ** 2


def pump_power_for_full_conversion_W(eta_nor_per_W_cm2: float, L_cm: float) -> float:
    return math.pi**2 / (4 * eta_nor_per_W_cm2 * L_cm**2)


@dataclass(frozen=True)
class Converter:
    eta_nor_per_W_cm2: float = 1.0
    L_cm: float = 4.0
    coupling: float = 0.7          # fibre-to-waveguide and back
    filter_transmission: float = 0.8
    noise_per_W_per_s_per_nm: float = 1e4   # noise photons per second per watt of pump per nm of filter bandwidth (TODO: verify)
    filter_bandwidth_nm: float = 0.1

    def external_efficiency(self, P_pump_W: float) -> float:
        return internal_efficiency(P_pump_W, self.eta_nor_per_W_cm2, self.L_cm) * self.coupling * self.filter_transmission

    def noise_rate_hz(self, P_pump_W: float) -> float:
        return self.noise_per_W_per_s_per_nm * P_pump_W * self.filter_bandwidth_nm

    def qber_floor(self, P_pump_W: float, signal_rate_hz: float, gate_s: float, rep_rate_hz: float) -> float:
        """Background-induced QBER from conversion noise (same law as link_budget.qber_from_background). Because the
        signal grows as sin^2 and the noise linearly, the signal-to-noise ratio falls monotonically with pump power;
        the operating point is a trade between converted rate and this floor, usually at 60-90 % of P_max."""
        from qll.channels.link_budget import LinkBudget
        return LinkBudget.qber_from_background(self.external_efficiency(P_pump_W) * signal_rate_hz, self.noise_rate_hz(P_pump_W), gate_s, rep_rate_hz)
