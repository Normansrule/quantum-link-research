"""Rydberg blockade and the neutral-atom gate budget.

Physics
-------
Two atoms excited to a Rydberg state |nS> interact by van der Waals C6/R^6 with C6 ~ n^11; when the interaction
exceeds the excitation Rabi frequency Omega the second excitation is blocked within the blockade radius
R_b = (C6 / hbar Omega)^(1/6) [jaksch2000] [saffman2010]. For Rb 70S, C6/h ~ 860 GHz um^6 [saffman2010] (TODO: verify
the exact value), giving R_b ~ 5-10 um at Omega/2pi ~ 1-10 MHz, larger than the ~3 um tweezer spacing.
Gate infidelity contributions [levine2019] [evered2023]: Rydberg-state decay ~ t_gate / tau_R (tau_R ~ 100-300 us,
falls with blackbody temperature), Doppler dephasing from atom temperature, laser phase noise, and finite blockade
(Omega/V)^2. A room-temperature blackbody roughly halves tau_R relative to a cryogenic enclosure [beterov2009].
"""
from __future__ import annotations

import math

HBAR = 1.054571817e-34
H = 6.62607015e-34
C6_RB70S_GHZ_UM6 = 860.0   # C6/h for Rb 70S in GHz*um^6 (TODO: verify)


def blockade_radius_um(omega_2pi_hz: float, c6_ghz_um6: float = C6_RB70S_GHZ_UM6) -> float:
    """R_b = (C6 / (h * Omega/2pi))^(1/6) in micrometres, with C6/h in GHz um^6 and Omega/2pi in Hz."""
    return (c6_ghz_um6 * 1e9 / omega_2pi_hz) ** (1 / 6)


def interaction_hz(R_um: float, c6_ghz_um6: float = C6_RB70S_GHZ_UM6) -> float:
    return c6_ghz_um6 * 1e9 / R_um**6


def gate_infidelity(t_gate_s: float, tau_rydberg_s: float, omega_2pi_hz: float, R_um: float, doppler_s: float = 5e-6, extra: float = 0.0) -> dict[str, float]:
    """Budget of leading infidelity terms; each is an estimate to the factor-of-two level."""
    V = interaction_hz(R_um)
    return {
        "decay": t_gate_s / tau_rydberg_s,
        "finite_blockade": (omega_2pi_hz / V) ** 2,
        "doppler": (t_gate_s / doppler_s) ** 2,
        "other": extra,
    }


def rydberg_lifetime_blackbody_s(tau_0_s: float, T_kelvin: float, T_ref: float = 300.0) -> float:
    """Crude: blackbody-induced decay rate scales ~T, so 1/tau = 1/tau_0 * (0.5 + 0.5 T/T_ref) with tau_0 the 300 K value."""
    return tau_0_s / (0.5 + 0.5 * T_kelvin / T_ref)
