"""The groups qubits live in: Pauli and Clifford groups, counted by closure.

Physics
-------
The n-qubit Pauli group modulo phase has 4^n elements; the Clifford group (unitaries mapping Paulis to Paulis) modulo
phase has 24 elements for one qubit and 11 520 for two [gottesman1998] [ozols2008]. Cliffords are exactly what Stim
simulates efficiently (Gottesman–Knill), and a uniformly random Clifford is what randomized benchmarking draws. This
module generates the single-qubit group from H and S by closure of the 2x2 matrices up to global phase, and counts the
two-qubit group by enumerating Stim tableaus.
"""
from __future__ import annotations

import numpy as np

H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
S = np.array([[1, 0], [0, 1j]], dtype=complex)


def _canon(U: np.ndarray) -> tuple:
    """Remove the global phase: make the first non-zero entry real positive, round for hashing."""
    flat = U.flatten()
    k = next(i for i, x in enumerate(flat) if abs(x) > 1e-9)
    V = U * (abs(flat[k]) / flat[k])
    return tuple(np.round(V.flatten(), 9))


def single_qubit_clifford_group() -> list[np.ndarray]:
    seen = {_canon(np.eye(2, dtype=complex)): np.eye(2, dtype=complex)}
    frontier = [np.eye(2, dtype=complex)]
    while frontier:
        nxt = []
        for U in frontier:
            for G in (H, S):
                V = G @ U
                key = _canon(V)
                if key not in seen:
                    seen[key] = V
                    nxt.append(V)
        frontier = nxt
    return list(seen.values())


def two_qubit_clifford_count() -> int:
    """Count unsigned 2-qubit Clifford tableaus with Stim (each is a Clifford modulo Pauli frame), times 4^2 Paulis."""
    import stim

    unsigned = sum(1 for _ in stim.Tableau.iter_all(2, unsigned=True))
    return unsigned * 16


def pauli_group_size_mod_phase(n: int) -> int:
    return 4**n
