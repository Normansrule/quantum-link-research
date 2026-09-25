"""Trapped-ion gate physics: Lamb-Dicke parameter, the Mølmer-Sørensen gate, and its heating-limited fidelity.

Physics
-------
An ion of mass m in a trap of secular frequency omega_z couples to a laser of wavevector k with Lamb-Dicke parameter
eta = k sqrt(hbar / (2 m omega_z)) (times a geometry factor). The Mølmer-Sørensen (MS) gate drives a bichromatic field
detuned by +-delta from the motional sideband; with Rabi frequency Omega the gate time for a maximally entangling
phase is t_g = 2 pi K / delta with delta = 2 eta Omega sqrt(K) for K closed loops in phase space [molmer1999]
[sorensen2000]. Leading infidelities [ballance2016] [gaebler2016]: motional heating during the gate ~ n_dot t_g (eta^2
scale), spontaneous scattering from the Raman beams, laser phase and amplitude noise, and off-resonant coupling
(Omega/omega_z)^2. State-of-the-art two-qubit fidelities are 99.9 % (Ca+ 2016, Be+ 2016) with gate times of tens of
microseconds; faster gates cost more scattering and heating.
"""
from __future__ import annotations

import math

HBAR = 1.054571817e-34
AMU = 1.66053906660e-27


def lamb_dicke(lambda_m: float, mass_amu: float, omega_z_2pi_hz: float, geometry: float = 1.0) -> float:
    k = 2 * math.pi / lambda_m * geometry
    return k * math.sqrt(HBAR / (2 * mass_amu * AMU * 2 * math.pi * omega_z_2pi_hz))


def ms_gate_time_s(eta: float, omega_rabi_2pi_hz: float, loops: int = 1) -> float:
    delta = 2 * eta * (2 * math.pi * omega_rabi_2pi_hz) * math.sqrt(loops)
    return 2 * math.pi * loops / delta


def ms_infidelity(eta: float, omega_rabi_2pi_hz: float, heating_quanta_per_s: float, omega_z_2pi_hz: float,
                  scattering_per_s: float = 0.0, loops: int = 1) -> dict[str, float]:
    t = ms_gate_time_s(eta, omega_rabi_2pi_hz, loops)
    return {
        "heating": heating_quanta_per_s * t / loops,                # ~ n_dot t / K for a K-loop gate
        "scattering": scattering_per_s * t,
        "off_resonant": (omega_rabi_2pi_hz / omega_z_2pi_hz) ** 2,
        "gate_time_s": t,
    }
