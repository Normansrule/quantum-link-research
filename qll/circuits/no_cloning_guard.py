"""No public function in qll.circuits returns two copies of an unknown input state.

Physics
-------
No unitary maps |psi>|0> to |psi>|psi> for all |psi> [wootters1982] [dieks1982]; the best universal
cloner reaches fidelity 5/6 [buzek1996]. The test module drives every public callable with a random
input and checks that no output contains the input twice; this module supplies the demonstration
that a naive "cloning circuit" (CNOT onto |0>) fails on a superposition.
"""
from __future__ import annotations

import numpy as np

from qll.circuits.fidelity import fidelity

BUZEK_HILLERY_BOUND = 5 / 6


def naive_cnot_clone(psi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """CNOT from psi onto |0>; returns the two reduced single-qubit states."""
    psi = np.asarray(psi, dtype=complex) / np.linalg.norm(psi)
    cnot = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)
    out = cnot @ np.kron(psi, np.array([1, 0], dtype=complex))
    rho = np.outer(out, out.conj()).reshape(2, 2, 2, 2)
    return np.einsum("ijkj->ik", rho), np.einsum("jijk->ik", rho)


def clone_fidelities(psi: np.ndarray) -> tuple[float, float]:
    a, b = naive_cnot_clone(psi)
    return fidelity(psi, a), fidelity(psi, b)
