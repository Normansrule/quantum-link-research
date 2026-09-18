"""Energy relaxation toward |0> at rate 1/T1 (zero-temperature limit of thermal.py).

Physics
-------
gamma = 1 - exp(-t/T1); E0 = [[1,0],[0,sqrt(1-gamma)]], E1 = [[0,sqrt(gamma)],[0,0]] [nielsen2010 §8.3.5].
Lindblad form: L = sqrt(1/T1) sigma_-; the Kraus map at time t equals the Lindblad solution at t
(cross-checked in tests with QuTiP). The finite-temperature version is
thermal.generalized_amplitude_damping_kraus.
"""
from __future__ import annotations

import math

import numpy as np

from qll.circuits.noise._kraus_base import KrausChannel


def amplitude_damping(gamma: float) -> KrausChannel:
    if not 0.0 <= gamma <= 1.0:
        raise ValueError("gamma must lie in [0, 1]")
    e0 = np.array([[1, 0], [0, math.sqrt(1 - gamma)]], dtype=complex)
    e1 = np.array([[0, math.sqrt(gamma)], [0, 0]], dtype=complex)
    return KrausChannel((e0, e1), "amplitude_damping", "nielsen2010")


def gamma_from_time(t: float, T1: float) -> float:
    return 1 - math.exp(-t / T1)


def lindblad_solution(rho0: np.ndarray, t: float, T1: float):
    """QuTiP master-equation solution for cross-checking the Kraus map."""
    import qutip as qt

    L = [np.sqrt(1 / T1) * qt.Qobj([[0, 1], [0, 0]])]  # sigma_- = |0><1|
    res = qt.mesolve(0 * qt.qeye(2), qt.Qobj(rho0), [0, t], L)
    return res.states[-1].full()
