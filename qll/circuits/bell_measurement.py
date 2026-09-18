"""Projecting two qubits onto the Bell basis.

Physics
-------
Deterministic BSM (matter qubits): CNOT then H on the first qubit, then measure both; outcome bits
(i, j) label |beta_ij> [nielsen2010 §1.3.7]. Linear-optics BSM: identifies only |Psi+-> and
succeeds with probability <= 1/2 without ancillas [calsamiglia2001]; success requires two-photon
interference with Hong-Ou-Mandel visibility V [hong1987], which we fold into an effective fidelity.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from qll.circuits.bell import bell_state


@dataclass(frozen=True)
class BellMeasurement:
    kind: Literal["deterministic", "linear_optics"] = "deterministic"
    visibility: float = 1.0

    @property
    def success_probability(self) -> float:
        return 1.0 if self.kind == "deterministic" else 0.5

    def projectors(self) -> dict[tuple[int, int], np.ndarray]:
        """Bell-basis projectors keyed by outcome bits (i, j): i from Z-type, j from X-type parity."""
        table = {(0, 0): "phi+", (0, 1): "psi+", (1, 0): "phi-", (1, 1): "psi-"}
        return {k: np.outer(bell_state(v), bell_state(v).conj()) for k, v in table.items()}

    def circuit(self):
        """Qiskit sub-circuit: measures qubits (0,1) in the Bell basis into classical bits (0,1)."""
        from qiskit import QuantumCircuit

        qc = QuantumCircuit(2, 2, name=f"bsm_{self.kind}")
        qc.cx(0, 1)
        qc.h(0)
        qc.measure([0, 1], [0, 1])
        return qc
