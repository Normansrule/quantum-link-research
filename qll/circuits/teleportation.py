"""Move an unknown qubit with one Bell pair and two classical bits.

Physics
-------
|psi>_1 |Phi+>_23 = 1/2 sum_ij |beta_ij>_12 X^j Z^i |psi>_3 [bennett1993]. Alice's Bell measurement
yields (i, j); Bob applies Z^i X^j after the bits arrive. Average fidelity with a Werner resource of
singlet fraction f is F = (2f + 1)/3 [horodecki1996]; the classical (measure-and-prepare) limit is 2/3
[massar1995]. Invariants: exactly one pair consumed and exactly two bits sent (INV-3); the output is
sealed until the ClassicalMessage arrives (INV-1).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.channels.light_time_delay import ClassicalMessage, NotYetArrived
from qll.circuits.bell import bell_state
from qll.circuits.bell_measurement import BellMeasurement
from qll.circuits.fidelity import fidelity

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_I = np.eye(2, dtype=complex)


class SealedQubit:
    """Bob's qubit before correction: readable only once the classical message has arrived."""

    def __init__(self, rho_uncorrected: np.ndarray, message: ClassicalMessage) -> None:
        self._rho = rho_uncorrected
        self.message = message

    def open(self, now_s: float) -> np.ndarray:
        i, j = self.message.receive(now_s)          # raises NotYetArrived if too early
        corr = np.linalg.matrix_power(_Z, i) @ np.linalg.matrix_power(_X, j)
        return corr @ self._rho @ corr.conj().T


@dataclass(frozen=True)
class TeleportationRecord:
    output: SealedQubit
    classical_bits: tuple[int, int]
    message: ClassicalMessage
    pairs_consumed: int
    outcome_probability: float


def teleport(psi: np.ndarray, resource: np.ndarray | None = None, distance_m: float = 0.0,
             sent_at_s: float = 0.0, bsm: BellMeasurement = BellMeasurement(), rng: np.random.Generator | None = None) -> TeleportationRecord:
    """Teleport a pure qubit |psi> (2-vector) using ``resource`` (4x4 density matrix, default ideal |Phi+>).

    The Bell measurement outcome is sampled from its Born probabilities; the two bits are placed in a
    ClassicalMessage that cannot be read before distance_m / c.
    """
    rng = rng or np.random.default_rng()
    psi = np.asarray(psi, dtype=complex) / np.linalg.norm(psi)
    if resource is None:
        b = bell_state("phi+")
        resource = np.outer(b, b.conj())
    rho_in = np.outer(psi, psi.conj())
    rho_123 = np.kron(rho_in, resource)                       # qubit order (1, 2, 3)
    probs, posts = {}, {}
    for (i, j), P in bsm.projectors().items():
        P12 = np.kron(P, _I)
        unnorm = P12 @ rho_123 @ P12.conj().T
        p = float(np.real(np.trace(unnorm)))
        probs[(i, j)] = p
        # Bob's reduced state given the outcome: trace out qubits 1, 2
        red = unnorm.reshape(4, 2, 4, 2)
        posts[(i, j)] = np.einsum("aiaj->ij", red) / p if p > 1e-15 else _I / 2
    keys = list(probs)
    (i, j) = keys[rng.choice(len(keys), p=np.array([probs[k] for k in keys]) / sum(probs.values()))]
    msg = ClassicalMessage(payload=(i, j), sent_at_s=sent_at_s, distance_m=distance_m)
    return TeleportationRecord(SealedQubit(posts[(i, j)], msg), (i, j), msg, pairs_consumed=1, outcome_probability=probs[(i, j)])


def average_fidelity(resource: np.ndarray | None = None, n_haar: int = 200, seed: int = 0) -> float:
    """Average teleportation fidelity over Haar-random inputs (bits read at arrival)."""
    rng = np.random.default_rng(seed)
    total = 0.0
    for _ in range(n_haar):
        v = rng.normal(size=2) + 1j * rng.normal(size=2)
        v /= np.linalg.norm(v)
        rec = teleport(v, resource, rng=rng)
        total += fidelity(v, rec.output.open(rec.message.earliest_arrival_s))
    return total / n_haar


def analytic_average_fidelity(singlet_fraction: float) -> float:
    return (2 * singlet_fraction + 1) / 3
