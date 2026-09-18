"""One Bell pair plus one transmitted qubit carries two classical bits (the dual of teleportation).

Physics
-------
Alice encodes (i, j) by applying Z^i X^j to her half of |Phi+>, sends it; Bob's Bell measurement
recovers (i, j) deterministically [bennett1992] [mattle1996]. Capacity is at most 2 bits per qubit
(Holevo bound) [holevo1973]: superdense coding saturates it, which is why the qubit must physically
travel and the 2 classical bits of teleportation cannot be compressed away.
"""
from __future__ import annotations

import numpy as np

from qll.circuits.bell import bell_state
from qll.circuits.bell_measurement import BellMeasurement

_I = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
HOLEVO_CAPACITY_BITS_PER_QUBIT = 2.0


def encode(bits: tuple[int, int]) -> np.ndarray:
    i, j = bits
    U = np.linalg.matrix_power(_Z, i) @ np.linalg.matrix_power(_X, j)
    return np.kron(U, _I) @ bell_state("phi+")


def decode(state: np.ndarray, bsm: BellMeasurement = BellMeasurement()) -> dict[tuple[int, int], float]:
    rho = np.outer(state, state.conj())
    return {k: float(np.real(np.trace(P @ rho))) for k, P in bsm.projectors().items()}
