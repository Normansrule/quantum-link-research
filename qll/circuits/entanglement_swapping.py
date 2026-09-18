"""A Bell measurement on two halves of two pairs entangles the two remaining halves.

Physics
-------
|Phi+>_12 |Phi+>_34 = 1/2 sum_k |beta_k>_23 |beta_k>_14 [zukowski1993]. For two Werner inputs of
fully entangled fraction F the swapped pair (after the heralded Pauli frame update) has
F' = F^2 + (1 - F)^2 / 3 [briegel1998, Eq. 6 with symmetric inputs]. The herald is a ClassicalMessage.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.channels.light_time_delay import ClassicalMessage
from qll.circuits.bell import bell_state
from qll.circuits.bell_measurement import BellMeasurement

_I = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


@dataclass(frozen=True)
class SwapRecord:
    pair_out: np.ndarray
    herald_bits: tuple[int, int]
    message: ClassicalMessage
    probability: float


def swap(pair_a: np.ndarray, pair_b: np.ndarray, distance_m: float = 0.0, bsm: BellMeasurement = BellMeasurement(),
         rng: np.random.Generator | None = None) -> SwapRecord:
    """Swap two 4x4 pair states (qubits 1,2) and (3,4); BSM on (2,3); returns the (1,4) pair with corrections applied."""
    rng = rng or np.random.default_rng()
    rho = np.kron(pair_a, pair_b).reshape([2] * 8)   # indices: 1 2 3 4 | 1' 2' 3' 4'
    recs = []
    for (i, j), P in bsm.projectors().items():
        P4 = P.reshape(2, 2, 2, 2)                     # <bc|P|BC> as P4[b, c, B, C]
        t = np.einsum("bcxy,axydAXYD->abcdAXYD", P4, rho)          # P on the ket side of qubits 2,3
        t = np.einsum("BCXY,abcdAXYD->abcdABCD", P4.conj(), t)     # P^dagger on the bra side
        p = float(np.real(np.einsum("abcdabcd->", t)))
        red = np.einsum("abcdAbcD->adAD", t).reshape(4, 4) / p if p > 1e-15 else np.eye(4) / 4
        corr = np.kron(_I, np.linalg.matrix_power(_Z, i) @ np.linalg.matrix_power(_X, j))
        recs.append(((i, j), p, corr @ red @ corr.conj().T))
    probs = np.array([r[1] for r in recs]); probs /= probs.sum()
    k = rng.choice(4, p=probs)
    (i, j), p, out = recs[k]
    return SwapRecord(out, (i, j), ClassicalMessage(payload=(i, j), sent_at_s=0.0, distance_m=distance_m), p)


def swapped_fraction_analytic(F: float) -> float:
    return F**2 + (1 - F) ** 2 / 3
