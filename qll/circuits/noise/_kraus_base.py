"""Every noise process is a list of Kraus operators, and nothing else.

Physics
-------
A physical (completely positive, trace-preserving, CPTP) map has the operator-sum form
rho -> sum_k E_k rho E_k^dagger with sum_k E_k^dagger E_k = I [kraus1983] [nielsen2010 ch. 8].
This module enforces that identity on construction (invariant INV-4) and provides the two
adapters the rest of the repository uses: Qiskit Aer QuantumError objects and QuTiP superoperators.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

TRACE_TOL = 1e-12


@dataclass(frozen=True)
class KrausChannel:
    ops: tuple[np.ndarray, ...]
    name: str = "channel"
    bibkey: str = field(default="nielsen2010")

    def __post_init__(self) -> None:
        d = self.ops[0].shape[0]
        for e in self.ops:
            if e.shape != (d, d):
                raise ValueError("all Kraus operators must be square and of the same dimension")
        total = sum(e.conj().T @ e for e in self.ops)
        if not np.allclose(total, np.eye(d), atol=TRACE_TOL):
            raise ValueError(f"{self.name}: Kraus operators are not trace preserving (max dev {np.max(np.abs(total-np.eye(d))):.2e})")

    @property
    def dim(self) -> int:
        return self.ops[0].shape[0]

    def apply(self, rho: np.ndarray) -> np.ndarray:
        return sum(e @ rho @ e.conj().T for e in self.ops)

    def to_aer(self):
        """Qiskit Aer QuantumError built from the Kraus list."""
        from qiskit_aer.noise import kraus_error

        return kraus_error([np.asarray(e, dtype=complex) for e in self.ops])

    def to_qutip_superop(self):
        """QuTiP superoperator (column-stacking convention) for cross-checks."""
        import qutip as qt

        return qt.kraus_to_super([qt.Qobj(e) for e in self.ops])


def average_gate_fidelity(channel: KrausChannel) -> float:
    """F_avg = (d F_pro + 1)/(d + 1) with process fidelity F_pro = sum_k |Tr E_k|^2 / d^2 [nielsen2002]."""
    d = channel.dim
    f_pro = sum(abs(np.trace(e)) ** 2 for e in channel.ops) / d**2
    return float((d * f_pro + 1) / (d + 1))
