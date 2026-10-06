"""Measurement-only teleportation with Majorana zero modes, as proposed by Crogman, Dang, and Erenso (2025), in an exact
fermionic model: six Majorana operators on three fermion modes, parity projections, and the corrections, so every
step of the protocol and every theorem of the paper's appendix can be checked numerically.

Model
-----
Three qubits A, B, C, each the occupation of one fermion mode c_j = (gamma_{2j-1} + i gamma_{2j}) / 2, with
{gamma_j, gamma_k} = 2 delta_jk [kitaev2001]. The operators are built by the Jordan-Wigner transformation, so the Fock
basis |n_A n_B n_C> is the computational basis. With this definition i gamma_1 gamma_2 = 2n - 1, so the logical Z
(+1 on the empty mode) is Z = -i gamma_1 gamma_2 = 1 - 2n.

Protocol [crogman2025]: A holds |psi>, B and C share |Phi+> = (|00> + |11>)/sqrt(2). Alice measures joint parities
across A and B, sends the outcomes, and Bob applies a parity-preserving correction on C.
    "paper_one_bit"   the four steps of the paper's Section 4: measure P23 = i gamma_2 gamma_3 (one bit), then apply
                      X_C = i gamma_4 gamma_5 if p = -1 (its Equations 9 to 12);
    "one_bit_best"    the same single measurement with the best unitary correction for each outcome: one parity bit
                      leaves Bob holding the X component of |psi> with a sign only the bit reveals, so the best
                      correction is Z_C for p = +1 (in this model's conventions), and the Y and Z components are lost;
    "two_bit"         the two commuting parities P23 and P14 = i gamma_1 gamma_4 (a full Bell measurement of A and B,
                      as in the paper's Theorem A4), with the Majorana-bilinear corrections found in CORRECTIONS.
Results (tests/test_majorana_teleport.py): the two-bit protocol teleports exactly; one parity measurement and one bit
cannot exceed the classical average fidelity of 2/3, and the literal one-bit correction gives 1/2. That is the
two-classical-bits-per-qubit requirement of teleportation [bennett1993] seen in Majorana language. Without any
feed-forward, Bob's state is I/2 for every input (no signalling), so the information is carried by the classical
bits. Under Jordan-Wigner, P23 = -X_A X_B and P14 = Y_A Y_B: the protocol is standard teleportation in a fermionic
encoding; the topological protection is a property of the hardware that stores the modes, not of the protocol.

Two modelling notes. A qubit made of one pair of modes cannot hold a superposition of fermion parities in an
isolated system (parity superselection [bravyi2002]); hardware therefore uses four modes per qubit at fixed total
parity [karzig2017]. The model works in the full Fock space, as the paper's algebra does. Average fidelities of qubit
channels are computed from their Bloch maps [nielsen2002].
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np

N_MODES = 3
SCHEMES = ("paper_one_bit", "one_bit_best", "two_bit")
_I2 = np.eye(2, dtype=complex)
_Z = np.diag([1.0, -1.0]).astype(complex)
_A = np.array([[0, 1], [0, 0]], dtype=complex)          # annihilation: a|1> = |0>
PAULI = (np.array([[0, 1], [1, 0]], complex), np.array([[0, -1j], [1j, 0]]), np.diag([1.0, -1.0]).astype(complex))


def _kron(*ms):
    out = np.eye(1, dtype=complex)
    for m in ms:
        out = np.kron(out, m)
    return out


def majoranas(n_modes: int = N_MODES) -> dict[int, np.ndarray]:
    """gamma_1 ... gamma_{2n} by Jordan-Wigner: c_j = Z x ... x Z x a x I x ... x I."""
    g = {}
    for j in range(n_modes):
        c = _kron(*([_Z] * j + [_A] + [_I2] * (n_modes - j - 1)))
        g[2 * j + 1] = c + c.conj().T
        g[2 * j + 2] = -1j * (c - c.conj().T)
    return g


G = majoranas()
DIM = 2 ** N_MODES
ID = np.eye(DIM, dtype=complex)


def bilinear(i: int, j: int) -> np.ndarray:
    """The Hermitian parity operator i gamma_i gamma_j (eigenvalues +1 and -1)."""
    return 1j * G[i] @ G[j]


def logical_z(mode: int) -> np.ndarray:
    """Z of qubit `mode` (0 = A, 1 = B, 2 = C): -i gamma_{2m+1} gamma_{2m+2} = 1 - 2 n_m."""
    return -bilinear(2 * mode + 1, 2 * mode + 2)


def projector(op: np.ndarray, outcome: int) -> np.ndarray:
    return (ID + outcome * op) / 2


def ket(bits) -> np.ndarray:
    v = np.zeros(DIM, complex)
    v[int("".join(map(str, bits)), 2)] = 1
    return v


def initial_state(psi) -> np.ndarray:
    """|psi>_A (x) |Phi+>_BC in the occupation basis."""
    psi = np.asarray(psi, complex) / np.linalg.norm(psi)
    phi = lambda a: (ket([a, 0, 0]) + ket([a, 1, 1])) / np.sqrt(2)
    return psi[0] * phi(0) + psi[1] * phi(1)


def reduced(rho: np.ndarray, keep: str) -> np.ndarray:
    r = rho.reshape(2, 2, 2, 2, 2, 2)
    return {"A": np.einsum("abcdbc->ad", r), "B": np.einsum("abcaec->be", r), "C": np.einsum("abcabd->cd", r)}[keep]


P23 = bilinear(2, 3)
P14 = bilinear(1, 4)
X_C_PAPER = bilinear(4, 5)                                # the paper's Equation 12
CORRECTIONS = {(1, 1): bilinear(5, 6), (1, -1): bilinear(3, 6), (-1, 1): bilinear(3, 5), (-1, -1): ID}


def _outcomes(scheme: str):
    if scheme == "two_bit":
        return {(p, q): projector(P23, p) @ projector(P14, q) for p in (1, -1) for q in (1, -1)}
    return {(p,): projector(P23, p) for p in (1, -1)}


def bob_conditional(psi, scheme: str) -> dict:
    """For each outcome: (probability, Bob's normalized state before correction)."""
    s = initial_state(psi)
    rho = np.outer(s, s.conj())
    out = {}
    for key, Pi in _outcomes(scheme).items():
        r = Pi @ rho @ Pi
        pr = float(np.real(np.trace(r)))
        out[key] = (pr, r / pr)
    return out


def bloch_map(scheme: str, key) -> tuple[np.ndarray, np.ndarray]:
    """The affine Bloch map v -> T v + t of Bob's state (before correction) for one outcome."""
    vec = lambda rho: np.array([np.real(np.trace(rho @ P)) for P in PAULI])
    states = {"0": [1, 0], "1": [0, 1], "+": [1 / np.sqrt(2), 1 / np.sqrt(2)], "+i": [1 / np.sqrt(2), 1j / np.sqrt(2)]}
    v = {k: vec(reduced(bob_conditional(s, scheme)[key][1], "C")) for k, s in states.items()}
    t = (v["0"] + v["1"]) / 2
    return np.column_stack([v["+"] - t, v["+i"] - t, (v["0"] - v["1"]) / 2]), t


def best_average_fidelity(T: np.ndarray) -> float:
    """Average fidelity after the best unitary correction: 1/2 + max_R tr(R^T T)/6 over rotations R [nielsen2002]."""
    U, _, Vt = np.linalg.svd(T)
    R = U @ np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))]) @ Vt
    return 0.5 + float(np.trace(R.T @ T)) / 6


@dataclass
class Teleport:
    scheme: str
    outcomes: dict             # key -> (probability, fidelity after correction)
    average: float
    bits_sent: int


def teleport(psi, scheme: str = "two_bit") -> Teleport:
    if scheme not in SCHEMES:
        raise ValueError(f"scheme must be one of {SCHEMES}")
    psi = np.asarray(psi, complex) / np.linalg.norm(psi)
    res, avg = {}, 0.0
    for key, (pr, r) in bob_conditional(psi, scheme).items():
        if scheme == "two_bit":
            U = CORRECTIONS[key]
            f = float(np.real(psi.conj() @ reduced(U @ r @ U.conj().T, "C") @ psi))
        else:
            if scheme == "paper_one_bit":
                U = ID if key[0] == 1 else X_C_PAPER
            else:                                              # the optimum (tests check it against best_average_fidelity)
                U = logical_z(2) if key[0] == 1 else ID
            f = float(np.real(psi.conj() @ reduced(U @ r @ U.conj().T, "C") @ psi))
        res[key] = (pr, f)
        avg += pr * f
    return Teleport(scheme, res, avg, 2 if scheme == "two_bit" else 1)


def average_fidelity(scheme: str) -> float:
    """Average over all pure inputs (the outcome probabilities are input-independent: 1/2 or 1/4 each)."""
    r = 1 / np.sqrt(2)                                          # the six cardinal states: a 2-design [dankert2009]
    cardinal = ([1, 0], [0, 1], [r, r], [r, -r], [r, 1j * r], [r, -1j * r])
    return float(np.mean([teleport(v, scheme).average for v in cardinal]))


def no_feedforward_state(psi) -> np.ndarray:
    """Bob's state averaged over Alice's outcomes, with no classical bits: I/2 for every input."""
    s = initial_state(psi)
    return reduced(np.outer(s, s.conj()), "C")


def luders(rho: np.ndarray, op: np.ndarray) -> np.ndarray:
    """Non-selective ideal measurement of a parity operator (the Lueders instrument)."""
    p, m = projector(op, 1), projector(op, -1)
    return p @ rho @ p + m @ rho @ m


def von_neumann(rho: np.ndarray) -> float:
    w = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    w = w[w > 1e-12]
    return float(-np.sum(w * np.log2(w)))


def parity_even_operators_on(modes: tuple[int, ...]) -> list[np.ndarray]:
    """All products of an even number of the given Majorana operators (the physically allowed operators there)."""
    ops = [ID]
    for r in range(2, len(modes) + 1, 2):
        for combo in itertools.combinations(modes, r):
            m = ID.copy()
            for k in combo:
                m = m @ G[k]
            ops.append(m)
    return ops
