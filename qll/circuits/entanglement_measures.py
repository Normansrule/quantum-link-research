"""Entanglement of mixed states: PPT criterion, negativity, and an entanglement witness.

Physics
-------
Peres-Horodecki: a two-qubit state is entangled iff its partial transpose has a negative eigenvalue [peres1996]
[horodecki1996sep]. Negativity N = (||rho^{T_B}||_1 - 1)/2 is an entanglement monotone; for a Werner state of
fully entangled fraction f, N = max(0, (3f - 1)/2 ... ) computed here numerically and checked against the f > 1/2
threshold. A witness W = 1/2 I - |Phi+><Phi+| has Tr(W rho) < 0 only for entangled states and is measurable with
local settings, which is how experiments certify entanglement without full tomography [guhne2009].
"""
from __future__ import annotations

import numpy as np

from qll.circuits.bell import bell_state


def partial_transpose(rho: np.ndarray) -> np.ndarray:
    r = np.asarray(rho, dtype=complex).reshape(2, 2, 2, 2)          # a b | A B
    return r.transpose(0, 3, 2, 1).reshape(4, 4)                     # transpose the second subsystem


def negativity(rho: np.ndarray) -> float:
    ev = np.linalg.eigvalsh(partial_transpose(rho))
    return float(max(0.0, -ev[ev < 0].sum()))


def is_entangled_ppt(rho: np.ndarray, tol: float = 1e-12) -> bool:
    return bool(np.linalg.eigvalsh(partial_transpose(rho)).min() < -tol)


def witness_value(rho: np.ndarray, kind: str = "phi+") -> float:
    """Tr(W rho) with W = I/2 - |B><B|; negative certifies entanglement (for states near |B>)."""
    b = bell_state(kind)
    W = 0.5 * np.eye(4) - np.outer(b, b.conj())
    return float(np.real(np.trace(W @ rho)))
