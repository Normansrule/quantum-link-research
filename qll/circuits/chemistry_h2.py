"""The hydrogen molecule as a two-qubit Hamiltonian: the smallest chemistry a quantum computer can do.

Physics
-------
In the minimal (STO-3G) basis with parity mapping and symmetry reduction, H2 at bond length R is a two-qubit
Hamiltonian H = g0 I + g1 Z0 + g2 Z1 + g3 Z0Z1 + g4 X0X1 + g5 Y0Y1 [omalley2016]. The coefficients at R = 0.7414 A
(experimental equilibrium) are tabulated; exact diagonalisation gives the ground-state energy -1.137 Ha, the number a
VQE must reproduce [peruzzo2014] [omalley2016]. Resource counts for larger molecules grow as O(N^4) Pauli terms in the
naive Jordan-Wigner mapping, which is the starting point of the resource estimates in learn/01/07.
"""
from __future__ import annotations

import numpy as np

# O'Malley et al. 2016, Table 1, R = 0.7414 Angstrom (g0..g5 in Hartree, electronic part); TODO: verify against the table.
H2_COEFFS_0_74 = {"g0": -0.4804, "g1": 0.3435, "g2": -0.4347, "g3": 0.5716, "g4": 0.0910, "g5": 0.0910}
NUCLEAR_REPULSION_0_74_HA = 1.0 / (0.7414 / 0.529177)   # 1/R in atomic units = 0.7137 Ha
EXPERIMENTAL_TOTAL_ENERGY_HA = -1.137

_I = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def h2_hamiltonian(g: dict[str, float] = H2_COEFFS_0_74) -> np.ndarray:
    return (g["g0"] * np.kron(_I, _I) + g["g1"] * np.kron(_Z, _I) + g["g2"] * np.kron(_I, _Z)
            + g["g3"] * np.kron(_Z, _Z) + g["g4"] * np.kron(_X, _X) + g["g5"] * np.kron(_Y, _Y))


def ground_energy_hartree(g: dict[str, float] = H2_COEFFS_0_74, include_nuclear: bool = True) -> float:
    """Total ground-state energy: electronic (exact diagonalisation) plus nuclear repulsion; -1.137 Ha at equilibrium."""
    e = float(np.linalg.eigvalsh(h2_hamiltonian(g))[0])
    return e + NUCLEAR_REPULSION_0_74_HA if include_nuclear else e


def vqe_ansatz_energy(theta: float, g: dict[str, float] = H2_COEFFS_0_74) -> float:
    """Energy of the one-parameter unitary-coupled-cluster ansatz |psi> = cos(theta)|01> + sin(theta)|10> (parity mapping)."""
    psi = np.zeros(4, dtype=complex)
    psi[1] = np.cos(theta); psi[2] = np.sin(theta)
    return float(np.real(psi.conj() @ h2_hamiltonian(g) @ psi))


def pauli_terms_jordan_wigner(n_spin_orbitals: int) -> int:
    """Order-of-magnitude count of Pauli terms in a second-quantised electronic Hamiltonian: ~ N^4 / 8 [mcardle2020]."""
    return n_spin_orbitals**4 // 8
