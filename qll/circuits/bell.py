"""The four maximally entangled two-qubit states.

Physics
-------
|Phi+-> = (|00> +- |11>)/sqrt2, |Psi+-> = (|01> +- |10>)/sqrt2. Each has Schmidt coefficients
(1/sqrt2, 1/sqrt2), reduced state I/2, and concurrence 1 [nielsen2010] [wootters1998]. The circuit is
H on qubit 0 then CNOT(0,1), with X on qubit 1 for Psi and Z on qubit 0 for the minus sign.
Werner state: rho_W = f |B><B| + (1-f)/3 (I - |B><B|) for a Bell state |B| [werner1989]: entangled iff f > 1/2.
"""
from __future__ import annotations

from typing import Literal

import numpy as np

Kind = Literal["phi+", "phi-", "psi+", "psi-"]
_ZERO = np.array([1, 0], dtype=complex)
_ONE = np.array([0, 1], dtype=complex)


def bell_state(kind: Kind = "phi+") -> np.ndarray:
    a = np.kron(_ZERO, _ZERO) if kind.startswith("phi") else np.kron(_ZERO, _ONE)
    b = np.kron(_ONE, _ONE) if kind.startswith("phi") else np.kron(_ONE, _ZERO)
    sign = 1 if kind.endswith("+") else -1
    return (a + sign * b) / np.sqrt(2)


def bell_circuit(kind: Kind = "phi+"):
    """Qiskit circuit preparing the requested Bell state on qubits (0, 1)."""
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(2, name=f"bell_{kind}")
    if kind.startswith("psi"):
        qc.x(1)
    qc.h(0)
    qc.cx(0, 1)
    if kind.endswith("-"):
        qc.z(0)
    return qc


def bell_stim(kind: Kind = "phi+"):
    """Stim circuit for the same state (Clifford), for large-n sampling."""
    import stim

    c = stim.Circuit()
    if kind.startswith("psi"):
        c.append("X", [1])
    c.append("H", [0])
    c.append("CX", [0, 1])
    if kind.endswith("-"):
        c.append("Z", [0])
    return c


def werner_state(f: float, kind: Kind = "phi+") -> np.ndarray:
    """Werner state with fully-entangled fraction f about the Bell state ``kind`` (4x4 density matrix).

    The teleportation protocol in this repository is written for |Phi+>, so f is the |Phi+> fraction
    by default; the physics (entangled iff f > 1/2, F_tele = (2f+1)/3) is the same for any Bell state.
    """
    if not 0.0 <= f <= 1.0:
        raise ValueError("fully entangled fraction must lie in [0, 1]")
    psi = bell_state(kind)
    proj = np.outer(psi, psi.conj())
    return f * proj + (1 - f) / 3 * (np.eye(4) - proj)


def schmidt_coefficients(state: np.ndarray) -> np.ndarray:
    return np.linalg.svd(np.asarray(state).reshape(2, 2), compute_uv=False)


def concurrence(rho: np.ndarray) -> float:
    """Wootters concurrence of a two-qubit density matrix [wootters1998]."""
    rho = np.asarray(rho, dtype=complex)
    if rho.ndim == 1:
        rho = np.outer(rho, rho.conj())
    sy = np.array([[0, -1j], [1j, 0]])
    yy = np.kron(sy, sy)
    r = rho @ yy @ rho.conj() @ yy
    ev = np.sort(np.sqrt(np.abs(np.linalg.eigvals(r))))[::-1]
    return float(max(0.0, ev[0] - ev[1] - ev[2] - ev[3]))
