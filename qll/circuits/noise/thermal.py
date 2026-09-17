"""Temperature as a first-class qubit parameter: thermal occupation, T1(T), and the generalized
amplitude-damping (GAD) channel.

Physics
-------
A bosonic mode at angular frequency omega in equilibrium with a bath at temperature T has mean
occupation n = 1/(exp(hbar*omega/(k_B*T)) - 1) [clerk2010]. For a two-level system coupled to
that bath, upward and downward transition rates are proportional to n and n+1, so the
relaxation rate is (2n+1)/T1(0) and the excited-state population is n/(2n+1) [krantz2019].
The Kraus form is the generalized amplitude-damping channel of Nielsen & Chuang §8.3.5
[nielsen2010] with ground weight p_ground = (n+1)/(2n+1).

Why this matters for a link: a 5 GHz superconducting qubit needs ~15 mK to reach n ~ 1e-7
(n ~ 1250 at 300 K), whereas a 1550 nm (193 THz) photon at 300 K has n ~ 4e-14 because
hbar*omega/(k_B T) ~ 31. Optical carriers therefore cross warm channels essentially noise-free;
moving quantum information between the two domains (transduction) is the open problem [lauk2020].
"""
from __future__ import annotations

import numpy as np

from qll.constants.physical import HBAR, K_BOLTZMANN


def bose_einstein_occupation(omega: float, T: float) -> float:
    """Mean thermal occupation of a mode at angular frequency ``omega`` (rad/s) and temperature ``T`` (K).

    Returns exactly 0 at T = 0 [clerk2010].
    """
    if T <= 0.0:
        return 0.0
    x = HBAR * omega / (K_BOLTZMANN * T)
    if x > 700.0:
        return 0.0
    return float(1.0 / np.expm1(x))


def excited_state_population(omega: float, T: float) -> float:
    """Equilibrium excited-state population n/(2n+1) of a two-level system [krantz2019]."""
    n = bose_einstein_occupation(omega, T)
    return n / (2.0 * n + 1.0)


def bath_ground_weight(omega: float, T: float) -> float:
    """Ground-state weight (n+1)/(2n+1) of the thermal bath; equals 1 at T = 0."""
    n = bose_einstein_occupation(omega, T)
    return (n + 1.0) / (2.0 * n + 1.0)


def thermal_t1(T1_zero: float, omega: float, T: float) -> float:
    """Relaxation time at temperature T: T1(T) = T1(0)/(2n+1) [krantz2019]."""
    n = bose_einstein_occupation(omega, T)
    return T1_zero / (2.0 * n + 1.0)


def generalized_amplitude_damping_kraus(gamma: float, p_ground: float) -> list[np.ndarray]:
    """Kraus operators [E0, E1, E2, E3] of the GAD channel [nielsen2010 §8.3.5].

    ``gamma`` is the damping probability (1 - exp(-t/T1)); ``p_ground`` is the bath ground weight.
    """
    if not (0.0 <= gamma <= 1.0 and 0.0 <= p_ground <= 1.0):
        raise ValueError("gamma and p_ground must lie in [0, 1]")
    sp, sq = np.sqrt(p_ground), np.sqrt(1.0 - p_ground)
    sg, s1g = np.sqrt(gamma), np.sqrt(1.0 - gamma)
    e0 = sp * np.array([[1.0, 0.0], [0.0, s1g]])
    e1 = sp * np.array([[0.0, sg], [0.0, 0.0]])
    e2 = sq * np.array([[s1g, 0.0], [0.0, 1.0]])
    e3 = sq * np.array([[0.0, 0.0], [sg, 0.0]])
    return [e0, e1, e2, e3]
