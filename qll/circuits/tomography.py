"""Reconstruct a density matrix from Pauli-basis measurements, then enforce physicality.

Physics
-------
rho = 1/4 sum_ij <sigma_i ⊗ sigma_j> sigma_i ⊗ sigma_j [james2001]. Finite statistics give an
unphysical (non-positive) estimate; project onto the closest positive semidefinite trace-one matrix
by the eigenvalue-clipping algorithm of [smolin2012].
"""
from __future__ import annotations

import itertools

import numpy as np

PAULIS = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


def expectation_values(rho: np.ndarray, n_qubits: int = 2) -> dict[str, float]:
    out = {}
    for labels in itertools.product("IXYZ", repeat=n_qubits):
        op = PAULIS[labels[0]]
        for l in labels[1:]:
            op = np.kron(op, PAULIS[l])
        out["".join(labels)] = float(np.real(np.trace(rho @ op)))
    return out


def sampled_expectations(rho: np.ndarray, shots: int, n_qubits: int = 2, seed: int = 0) -> dict[str, float]:
    """Binomially sampled Pauli expectations, as an experiment would produce."""
    rng = np.random.default_rng(seed)
    exact = expectation_values(rho, n_qubits)
    out = {}
    for k, e in exact.items():
        if set(k) == {"I"}:
            out[k] = 1.0
            continue
        p_plus = (1 + e) / 2
        out[k] = 2 * rng.binomial(shots, p_plus) / shots - 1
    return out


def linear_inversion(expectations: dict[str, float], n_qubits: int = 2) -> np.ndarray:
    d = 2**n_qubits
    rho = np.zeros((d, d), dtype=complex)
    for labels, e in expectations.items():
        op = PAULIS[labels[0]]
        for l in labels[1:]:
            op = np.kron(op, PAULIS[l])
        rho += e * op
    return rho / d


def project_to_physical(rho: np.ndarray) -> np.ndarray:
    """Smolin-Gambetta-Smith projection onto the PSD, trace-one set [smolin2012]."""
    rho = (rho + rho.conj().T) / 2
    w, v = np.linalg.eigh(rho)
    w = w[::-1]; v = v[:, ::-1]
    d = len(w)
    acc, out = 0.0, np.zeros(d)
    for i in range(d - 1, -1, -1):
        if w[i] + acc / (i + 1) >= 0:
            out[: i + 1] = w[: i + 1] + acc / (i + 1)
            break
        acc += w[i]
    return (v * out) @ v.conj().T


def reconstruct(rho_true: np.ndarray, shots: int, n_qubits: int = 2, seed: int = 0) -> np.ndarray:
    return project_to_physical(linear_inversion(sampled_expectations(rho_true, shots, n_qubits, seed), n_qubits))
