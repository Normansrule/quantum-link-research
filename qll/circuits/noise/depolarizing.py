"""With probability p the qubit is replaced by the maximally mixed state.

Physics
-------
rho -> (1 - p) rho + p I/2, Kraus {sqrt(1-3p/4) I, sqrt(p/4) X, sqrt(p/4) Y, sqrt(p/4) Z}
[nielsen2010 §8.3.4]; average gate fidelity 1 - p/2 [nielsen2002]. A |Phi+> pair with this channel
on each qubit has fully entangled fraction f = (1 - p)^2 + p(1 - p)/2 + p^2/4 ... computed
numerically in tests rather than assumed.
"""
from __future__ import annotations

import numpy as np

from qll.circuits.noise._kraus_base import KrausChannel

_I = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def depolarizing(p: float) -> KrausChannel:
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must lie in [0, 1]")
    return KrausChannel((np.sqrt(1 - 3 * p / 4) * _I, np.sqrt(p / 4) * _X, np.sqrt(p / 4) * _Y, np.sqrt(p / 4) * _Z), "depolarizing", "nielsen2010")


def average_gate_fidelity_analytic(p: float) -> float:
    return 1 - p / 2
