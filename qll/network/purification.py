"""Trade several noisy pairs for one better pair using only local operations and classical communication.

Physics
-------
BBPSSW recurrence on two Werner pairs of fidelity F (bilateral CNOT, measure targets, keep on agreement)
[bennett1996]:
    F' = [F^2 + ((1-F)/3)^2] / p_succ,   p_succ = F^2 + 2F(1-F)/3 + 5((1-F)/3)^2.
F' > F iff F > 1/2; fixed points at 1/2 (unstable) and 1 (stable). DEJMPS acts on Bell-diagonal states
with rotations first and converges faster [deutsch1996]. Each round consumes two pairs, succeeds with
probability p_succ, and costs one classical round trip (a ClassicalMessage each way) to compare outcomes
(INV-1); at Mars distance each round is 6-45 minutes.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.channels.light_time_delay import ClassicalMessage, round_trip_delay_s

_I = np.eye(2, dtype=complex)


def bbpssw_step(F: float) -> tuple[float, float]:
    """Return (F', p_succ) for BBPSSW on two Werner pairs of fidelity F [bennett1996]."""
    q = (1 - F) / 3
    p = F**2 + 2 * F * q + 5 * q**2
    return (F**2 + q**2) / p, p


def bbpssw_rounds_to_target(F0: float, F_target: float, max_rounds: int = 50) -> tuple[int, float, float]:
    """Rounds needed to reach F_target, the final fidelity, and the expected number of input pairs consumed."""
    if F0 <= 0.5:
        raise ValueError("purification needs F > 1/2")
    F, pairs, rounds = F0, 1.0, 0
    while F < F_target and rounds < max_rounds:
        F2, p = bbpssw_step(F)
        pairs = 2 * pairs / p
        F, rounds = F2, rounds + 1
    return rounds, F, pairs


@dataclass(frozen=True)
class PurificationRecord:
    fidelity: float
    rounds: int
    expected_pairs_consumed: float
    classical_time_s: float
    messages: tuple[ClassicalMessage, ...]


def purify_werner(F0: float, F_target: float, distance_m: float = 0.0) -> PurificationRecord:
    rounds, F, pairs = bbpssw_rounds_to_target(F0, F_target)
    rt = round_trip_delay_s(distance_m)
    msgs = tuple(ClassicalMessage(payload=(k,), sent_at_s=k * rt, distance_m=distance_m) for k in range(rounds))
    return PurificationRecord(F, rounds, pairs, rounds * rt, msgs)


def bbpssw_numeric(rho_a: np.ndarray, rho_b: np.ndarray) -> tuple[np.ndarray, float]:
    """Exact BBPSSW on two arbitrary 4x4 pair states (qubits A1B1, A2B2): bilateral CNOT A1->A2, B1->B2,
    measure A2, B2 in Z, keep on equal outcomes. Returns (post-selected pair A1B1, success probability)."""
    cnot = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)
    rho = np.kron(rho_a, rho_b)                       # order A1 B1 A2 B2
    # reorder to (A1 A2 B1 B2) to apply CNOTs on (A1,A2) and (B1,B2)
    perm = [0, 2, 1, 3]
    r = rho.reshape([2] * 8).transpose(perm + [4 + p for p in perm]).reshape(16, 16)
    U = np.kron(cnot, cnot)
    r = U @ r @ U.conj().T
    P0 = np.diag([1, 0]).astype(complex); P1 = np.diag([0, 1]).astype(complex)
    out, p_tot = np.zeros((4, 4), dtype=complex), 0.0
    for Pa, Pb in ((P0, P0), (P1, P1)):
        Pfull = np.kron(np.kron(_I, Pa), np.kron(_I, Pb))   # measure A2 (index 1) and B2 (index 3)
        t = Pfull @ r @ Pfull
        t4 = t.reshape([2] * 8)
        red = np.einsum("aibjAiBj->abAB", t4)                 # trace out A2, B2
        p_tot += float(np.real(np.trace(red.reshape(4, 4))))
        out += red.reshape(4, 4)
    return out / p_tot, p_tot


# ---------------------------------------------------------------------------------------------------------
# DEJMPS [deutsch1996]: Alice applies R_x(pi/2), Bob R_x(-pi/2) to their qubits of both pairs, then the same
# bilateral CNOT + agreement post-selection as BBPSSW. On Bell-diagonal states (weights p_phi+, p_phi-, p_psi+,
# p_psi-) the map is
#   p'_A = (A^2 + B^2)/N,  p'_B = 2 C D / N,  p'_C = (C^2 + D^2)/N,  p'_D = 2 A B / N,  N = (A+B)^2 + (C+D)^2,
# in Deutsch's labelling (A the target). In this repository's Bell labels the numeric protocol puts the 2AB weight
# on phi- rather than psi- (a relabelling by the rotation), which the next round's rotation undoes; the target fidelity
# and success probability agree round by round with the map, which the tests check by iterating both,
# which converges faster than BBPSSW because it does not first twirl to a Werner state.
# ---------------------------------------------------------------------------------------------------------
def dejmps_step(p: tuple[float, float, float, float]) -> tuple[tuple[float, float, float, float], float]:
    """One DEJMPS round on two identical Bell-diagonal pairs with weights (phi+, phi-, psi+, psi-)."""
    a, b, c, d = p
    N = (a + b) ** 2 + (c + d) ** 2
    return ((a * a + b * b) / N, 2 * c * d / N, (c * c + d * d) / N, 2 * a * b / N), N


def dejmps_numeric(rho_a: np.ndarray, rho_b: np.ndarray) -> tuple[np.ndarray, float]:
    """Exact DEJMPS on two arbitrary 4x4 pair states: the R_x(±π/2) rotations followed by BBPSSW's circuit."""
    rx = lambda th: np.array([[np.cos(th / 2), -1j * np.sin(th / 2)], [-1j * np.sin(th / 2), np.cos(th / 2)]])
    U = np.kron(rx(np.pi / 2), rx(-np.pi / 2))          # Alice, Bob
    ra = U @ rho_a @ U.conj().T
    rb = U @ rho_b @ U.conj().T
    return bbpssw_numeric(ra, rb)


def bell_diagonal_weights(rho: np.ndarray) -> tuple[float, float, float, float]:
    from qll.circuits.bell import bell_state
    return tuple(float(np.real(bell_state(k).conj() @ rho @ bell_state(k))) for k in ("phi+", "phi-", "psi+", "psi-"))


def dejmps_rounds_to_target(p0: tuple[float, float, float, float], F_target: float, max_rounds: int = 50) -> tuple[int, float, float]:
    p, pairs, rounds = p0, 1.0, 0
    while p[0] < F_target and rounds < max_rounds:
        p, N = dejmps_step(p)
        pairs = 2 * pairs / N
        rounds += 1
    return rounds, p[0], pairs
