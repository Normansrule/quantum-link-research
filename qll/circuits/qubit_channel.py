"""A qubit quantum channel, described the way an experiment measures it, and what it can carry.

Representations
---------------
Any qubit channel E (completely positive, trace preserving [kraus1983]) is fixed by its Pauli transfer matrix
    R_ij = (1/2) Tr[ sigma_i E(sigma_j) ],   i, j in {I, X, Y, Z},
whose lower-right 3 x 3 block T and first column t give the affine Bloch map r -> T r + t [nielsen2010 ch. 8].
Its Choi state, the output of one half of |Phi+> sent through E, is
    J = (id (x) E)(|Phi+><Phi+|) = (1/4) sum_ij R_ij sigma_j^T (x) sigma_i,
because |Phi+><Phi+| = (1/4) sum_j sigma_j^T (x) sigma_j.

Figures of merit
----------------
    entanglement fidelity   F_e = <Phi+|J|Phi+> = (1 + Tr T) / 4,
    average fidelity        F = (2 F_e + 1) / 3                                    [nielsen2002]
    basis error             e_a = (1 - T_aa) / 2   (averaged over the two eigenstates of axis a).
In the process (chi) matrix, e_z = chi_XX + chi_YY and e_x = chi_ZZ + chi_YY, and F_e = chi_II = 1 - chi_XX - chi_YY
- chi_ZZ, so for every qubit channel
    F_e >= 1 - e_z - e_x,
which turns the two error rates a BB84 link already measures into a bound on how well the channel preserves
entanglement. A channel is entanglement breaking (it could be replaced by measure-and-prepare, a classical relay)
exactly when J is separable [horodecki2003eb], which for two qubits is when J has a positive partial transpose
[horodecki1996sep]. Every entanglement-breaking qubit channel has F_e <= 1/2 and F <= 2/3, so F_e > 1/2 certifies
that the channel is quantum.

Capacities (bits or qubits per channel use)
-------------------------------------------
    classical (Holevo), unital channels   C = 1 - h((1 + s_max)/2), s_max the largest singular value of T  [king2002]
    entanglement-assisted                 C_E = max_rho I(R; B), = 2 - S(J) for unital channels             [bennett2002]
    quantum, one shot                     Q1 = max_rho [S(B) - S(RB)] (coherent information), a lower bound on
                                          Q [devetak2005q]; = 1 - S(J) at rho = I/2 is the hashing bound for
                                          Pauli channels [bennett1996mixed]; exact for degradable channels such as
                                          amplitude damping with gamma <= 1/2: Q = max_p h((1-gamma)p) - h(gamma p)
                                          [giovannetti2005]
    erasure with probability eps          Q = max(0, 1 - 2 eps) one way, 1 - eps with classical feedback,
                                          C = 1 - eps, C_E = 2(1 - eps)                                       [bennett1997erasure]
    private, from BB84 error rates        P >= 1 - h(e_z) - h(e_x)                                            [shor2000]
A lost polarization photon gives no click, so photon loss is a heralded erasure: below 50 % transmission a
one-way link carries no qubits at all, while heralding over a classical channel recovers a rate proportional to
the transmission. Quantum channels and classical channels work together; neither replaces the other.
"""
from __future__ import annotations

import math

import numpy as np

from qll.circuits.noise._kraus_base import KrausChannel

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = (I2, X, Y, Z)
PHI_PLUS = np.array([1, 0, 0, 1], dtype=complex) / math.sqrt(2)


def h2(x: float) -> float:
    """Binary entropy in bits [cover2006]; kept here so the circuits layer does not import the QKD layer."""
    return 0.0 if x <= 0 or x >= 1 else float(-x * math.log2(x) - (1 - x) * math.log2(1 - x))


# ------------------------------------------------------------------------------------------- representations
def ptm(channel: KrausChannel) -> np.ndarray:
    """Pauli transfer matrix of a Kraus channel."""
    return np.array([[0.5 * np.real(np.trace(si @ channel.apply(sj))) for sj in PAULI] for si in PAULI])


def ptm_from_affine(T: np.ndarray, t: np.ndarray) -> np.ndarray:
    R = np.zeros((4, 4))
    R[0, 0] = 1.0
    R[1:, 0] = t
    R[1:, 1:] = T
    return R


def pauli_channel(px: float, py: float, pz: float) -> np.ndarray:
    """rho -> (1 - px - py - pz) rho + px X rho X + py Y rho Y + pz Z rho Z."""
    p0 = 1 - px - py - pz
    if min(p0, px, py, pz) < -1e-15:
        raise ValueError("Pauli probabilities must be non-negative and sum to at most 1")
    return np.diag([1.0, p0 + px - py - pz, p0 - px + py - pz, p0 - px - py + pz])


def depolarizing_ptm(p: float) -> np.ndarray:
    """rho -> (1 - p) rho + p I/2: the Bloch vector shrinks by 1 - p."""
    return np.diag([1.0, 1 - p, 1 - p, 1 - p])


def rotation_ptm(theta: float, axis=(0.0, 0.0, 1.0)) -> np.ndarray:
    """A unitary rotation of the Bloch sphere by theta about `axis` (polarization drift in a fiber)."""
    n = np.asarray(axis, float) / np.linalg.norm(axis)
    K = np.array([[0, -n[2], n[1]], [n[2], 0, -n[0]], [-n[1], n[0], 0]])
    Rot = np.eye(3) + math.sin(theta) * K + (1 - math.cos(theta)) * K @ K
    return ptm_from_affine(Rot, np.zeros(3))


def intercept_resend_ptm(f: float) -> np.ndarray:
    """A fraction f of qubits measured in a random BB84 basis (Z or X) and resent: entanglement breaking at f = 1."""
    return np.diag([1.0, 1 - f / 2, 1 - f, 1 - f / 2])


def compose(*Rs: np.ndarray) -> np.ndarray:
    """Channels applied left to right: compose(A, B) is B after A."""
    out = np.eye(4)
    for R in Rs:
        out = R @ out
    return out


def choi(R: np.ndarray) -> np.ndarray:
    """(id (x) E)(|Phi+><Phi+|), reference qubit first."""
    J = np.zeros((4, 4), dtype=complex)
    for j in range(4):
        out = sum(R[i, j] * PAULI[i] for i in range(4))
        J += np.kron(PAULI[j].T, out)
    return J / 4


# --------------------------------------------------------------------------------------------- figures of merit
def entanglement_fidelity(R: np.ndarray) -> float:
    return float((1 + np.trace(R[1:, 1:])) / 4)


def average_fidelity(R: np.ndarray) -> float:
    return (2 * entanglement_fidelity(R) + 1) / 3


def basis_errors(R: np.ndarray) -> dict[str, float]:
    return {a: float((1 - R[k, k]) / 2) for k, a in ((1, "x"), (2, "y"), (3, "z"))}


def certified_entanglement_fidelity(e_z: float, e_x: float) -> float:
    """The lower bound F_e >= 1 - e_z - e_x from two measured error rates."""
    return max(0.0, 1.0 - e_z - e_x)


def is_entanglement_breaking(R: np.ndarray, tol: float = 1e-12) -> bool:
    """Separable Choi state, tested by the partial transpose (exact for two qubits)."""
    J = choi(R).reshape(2, 2, 2, 2).transpose(2, 1, 0, 3).reshape(4, 4)
    return bool(np.min(np.linalg.eigvalsh((J + J.conj().T) / 2)) >= -tol)


def is_physical(R: np.ndarray, tol: float = 1e-9) -> bool:
    """Completely positive (Choi state positive) and trace preserving (first row (1, 0, 0, 0))."""
    J = choi(R)
    return bool(np.min(np.linalg.eigvalsh((J + J.conj().T) / 2)) >= -tol and np.allclose(R[0], [1, 0, 0, 0], atol=tol))


# -------------------------------------------------------------------------------------------------- capacities
def entropy(rho: np.ndarray) -> float:
    w = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    w = w[w > 1e-15]
    return float(-np.sum(w * np.log2(w)))


def apply(R: np.ndarray, rho: np.ndarray) -> np.ndarray:
    r = np.array([1.0] + [np.real(np.trace(rho @ P)) for P in PAULI[1:]])
    out = R @ r
    return 0.5 * sum(out[i] * PAULI[i] for i in range(4))


def _purified_output(R: np.ndarray, rho: np.ndarray) -> np.ndarray:
    """omega_RB = 2 (sqrt(rho)^T (x) I) J (sqrt(rho)^T (x) I)^dagger: the channel applied to one half of a purification."""
    w, V = np.linalg.eigh(rho)
    s = V @ np.diag(np.sqrt(np.clip(w, 0, None))) @ V.conj().T
    M = np.kron(s.T, I2)
    return 2 * M @ choi(R) @ M.conj().T


def coherent_information(R: np.ndarray, rho: np.ndarray) -> float:
    om = _purified_output(R, rho)
    return entropy(apply(R, rho)) - entropy(om)


def mutual_information(R: np.ndarray, rho: np.ndarray) -> float:
    om = _purified_output(R, rho)
    return entropy(rho) + entropy(apply(R, rho)) - entropy(om)


def _inputs(n: int = 201):
    """Diagonal inputs diag(p, 1 - p) in the z basis, the optimum for channels covariant about z."""
    return [np.diag([p, 1 - p]).astype(complex) for p in np.linspace(0, 1, n)]


def quantum_capacity_lower(R: np.ndarray) -> float:
    """max(0, single-shot coherent information) over diagonal inputs."""
    return max(0.0, max(coherent_information(R, rho) for rho in _inputs()))


def hashing_bound(R: np.ndarray) -> float:
    return max(0.0, coherent_information(R, I2 / 2))


def entanglement_assisted_capacity(R: np.ndarray) -> float:
    return max(mutual_information(R, rho) for rho in _inputs())


def holevo_capacity_unital(R: np.ndarray) -> float:
    if not np.allclose(R[1:, 0], 0, atol=1e-12):
        raise ValueError("the closed form holds for unital channels (t = 0)")
    s = float(np.max(np.linalg.svd(R[1:, 1:], compute_uv=False)))
    return 1 - h2((1 + min(s, 1.0)) / 2)


def amplitude_damping_quantum_capacity(gamma: float, n: int = 20001) -> float:
    if gamma >= 0.5:
        return 0.0
    p = np.linspace(0, 1, n)
    h = lambda x: np.where((x > 0) & (x < 1), -x * np.log2(np.clip(x, 1e-300, 1)) - (1 - x) * np.log2(np.clip(1 - x, 1e-300, 1)), 0.0)
    return float(np.max(h((1 - gamma) * p) - h(gamma * p)))


def erasure_capacities(eps: float) -> dict[str, float]:
    return {"quantum_one_way": max(0.0, 1 - 2 * eps), "quantum_two_way": 1 - eps, "classical": 1 - eps, "entanglement_assisted": 2 * (1 - eps)}


def private_capacity_bb84(e_z: float, e_x: float) -> float:
    return max(0.0, 1 - h2(e_z) - h2(e_x))
