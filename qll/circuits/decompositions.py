"""Gate decompositions and measurement-based computation.

Physics
-------
Any single-qubit unitary is U = e^{i alpha} R_z(beta) R_y(gamma) R_z(delta) (Euler/ZYZ) [nielsen2010 §4.2]. Any two-qubit
unitary needs at most three CNOTs plus single-qubit gates (KAK decomposition) [vatan2004] [kraus2001]; Qiskit's
TwoQubitBasisDecomposer implements it and reports the CNOT count. The Solovay-Kitaev theorem says any unitary is
approximated to eps by O(log^c(1/eps)) gates from a finite universal set [dawson2006].
Measurement-based (one-way) computation: a linear cluster state |+>-CZ-|+>-CZ-... plus adaptive single-qubit
measurements implements any single-qubit unitary; measuring qubit 1 in the basis {|0> +- e^{i phi}|1>} teleports
its state to qubit 2 as X^m H R_z(phi)|psi> (one-bit teleportation) [raussendorf2001] [nielsen2006]. Entanglement is
consumed and measurement drives the computation, which is the model behind photonic and all-photonic repeaters.
"""
from __future__ import annotations

import math

import numpy as np

_H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def rz(t: float) -> np.ndarray:
    return np.array([[np.exp(-1j * t / 2), 0], [0, np.exp(1j * t / 2)]])


def ry(t: float) -> np.ndarray:
    return np.array([[np.cos(t / 2), -np.sin(t / 2)], [np.sin(t / 2), np.cos(t / 2)]], dtype=complex)


def zyz_angles(U: np.ndarray) -> tuple[float, float, float, float]:
    """(alpha, beta, gamma, delta) with U = e^{i alpha} Rz(beta) Ry(gamma) Rz(delta), via Qiskit's Euler decomposer."""
    from qiskit.synthesis import OneQubitEulerDecomposer

    theta, phi, lam, phase = OneQubitEulerDecomposer("ZYZ").angles_and_phase(np.asarray(U, dtype=complex))
    return phase, phi, theta, lam


def zyz_reconstruct(alpha: float, beta: float, gamma: float, delta: float) -> np.ndarray:
    return np.exp(1j * alpha) * rz(beta) @ ry(gamma) @ rz(delta)


def cnot_count(U4: np.ndarray) -> int:
    """Minimum CNOTs for a two-qubit unitary by Qiskit's KAK-based basis decomposer (0-3)."""
    from qiskit.circuit.library import CXGate
    from qiskit.quantum_info import Operator
    from qiskit.synthesis import TwoQubitBasisDecomposer

    dec = TwoQubitBasisDecomposer(CXGate())
    return dec.num_basis_gates(Operator(np.asarray(U4, dtype=complex)))


def one_bit_teleportation(psi: np.ndarray, phi: float, outcome: int) -> np.ndarray:
    """Cluster-state step: qubit 1 in state psi, CZ with |+> on qubit 2, measure qubit 1 in the phi-rotated X basis;
    qubit 2 becomes X^m H Rz(phi) psi (up to the outcome's byproduct). Returns qubit 2's state (normalised)."""
    psi = np.asarray(psi, dtype=complex) / np.linalg.norm(psi)
    plus = np.array([1, 1], dtype=complex) / math.sqrt(2)
    state = np.kron(psi, plus)
    cz = np.diag([1, 1, 1, -1]).astype(complex)
    state = cz @ state
    # measurement basis on qubit 1: |m_phi> = (|0> + (-1)^m e^{-i phi}|1>)/sqrt2 ... project and trace out
    m0 = np.array([1, (-1) ** outcome * np.exp(-1j * phi)], dtype=complex) / math.sqrt(2)
    out = np.einsum("i,ij->j", m0.conj(), state.reshape(2, 2))   # <m| on qubit 1 leaves qubit 2
    return out / np.linalg.norm(out)


def one_bit_teleportation_expected(psi: np.ndarray, phi: float, outcome: int) -> np.ndarray:
    psi = np.asarray(psi, dtype=complex) / np.linalg.norm(psi)
    out = np.linalg.matrix_power(_X, outcome) @ _H @ rz(phi) @ psi
    return out / np.linalg.norm(out)
