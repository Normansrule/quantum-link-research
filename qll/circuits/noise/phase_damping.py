"""Loss of coherence without energy exchange at rate 1/T_phi, with 1/T2 = 1/(2 T1) + 1/T_phi.

Physics
-------
lambda = 1 - exp(-t/T_phi); E0 = [[1,0],[0,sqrt(1-lambda)]], E1 = [[0,0],[0,sqrt(lambda)]]
[nielsen2010 §8.3.6]. Equivalent to a Z flip with probability (1 - exp(-t/T_phi))/2 ... to first
order; the off-diagonal element decays as exp(-t/T_phi) exactly. Lindblad: L = sqrt(1/(2 T_phi)) Z.
T2 <= 2 T1 always [krantz2019].
"""
from __future__ import annotations

import math

import numpy as np

from qll.circuits.noise._kraus_base import KrausChannel


def phase_damping(lam: float) -> KrausChannel:
    if not 0.0 <= lam <= 1.0:
        raise ValueError("lambda must lie in [0, 1]")
    e0 = np.array([[1, 0], [0, math.sqrt(1 - lam)]], dtype=complex)
    e1 = np.array([[0, 0], [0, math.sqrt(lam)]], dtype=complex)
    return KrausChannel((e0, e1), "phase_damping", "nielsen2010")


def t2_from_t1_tphi(T1: float, T_phi: float) -> float:
    return 1 / (1 / (2 * T1) + 1 / T_phi)


def lambda_from_time(t: float, T_phi: float) -> float:
    """Kraus parameter giving off-diagonal decay exp(-t/T_phi): sqrt(1-lambda) = exp(-t/T_phi)."""
    return 1 - math.exp(-2 * t / T_phi)


def lindblad_solution(rho0: np.ndarray, t: float, T_phi: float):
    import qutip as qt

    L = [np.sqrt(1 / (2 * T_phi)) * qt.sigmaz()]
    res = qt.mesolve(0 * qt.qeye(2), qt.Qobj(rho0), [0, t], L)
    return res.states[-1].full()
