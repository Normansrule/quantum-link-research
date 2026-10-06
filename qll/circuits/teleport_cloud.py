"""Teleportation as a cloud-processor experiment (mission milestone M4.1): with the two classical bits, without them,
and with the corrections deferred, measured on the six cardinal states.

Physics
-------
Qubit 0 holds the input |psi>, qubits 1 and 2 share |Phi+>. Alice's Bell measurement on qubits 0 and 1 gives two
bits (m0, m1), and Bob's qubit is then X^m1 Z^m0 |psi> up to a global phase [bennett1993]. With the bits Bob applies
X^m1 then Z^m0 and holds |psi>; without them his qubit, averaged over the outcomes, is I/2, so his fidelity with
|psi> is exactly 1/2, the no-signalling value. A measure-and-prepare strategy, which uses no entanglement, cannot
average above 2/3 [massar1995]; with a Werner resource of singlet fraction f the average is (2f + 1)/3
[horodecki1996]. The six cardinal states form a 2-design on a qubit, so their mean fidelity equals the average over
all pure inputs [dankert2009].

Three modes:
    "feedforward"  mid-circuit measurement and classically controlled X and Z: the two bits are real classical data
                   carried to Bob's qubit (on a chip, over wires, at light speed or slower);
    "deferred"     the corrections as controlled gates before measurement: identical statistics by the principle of
                   deferred measurement [nielsen2010], for devices without feed-forward, but no classical channel;
    "no_bits"      Alice measures and Bob does nothing: the control that must give 1/2.

Fidelity is measured by undoing the preparation on Bob's qubit and reading it: P(0) = |<psi|rho_B|psi>|.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats

MODES = ("feedforward", "deferred", "no_bits")
CARDINAL = ("0", "1", "+", "-", "+i", "-i")
CLASSICAL_LIMIT = 2 / 3


def _prepare(qc, q: int, state: str, inverse: bool = False) -> None:
    gates = {"0": [], "1": ["x"], "+": ["h"], "-": ["x", "h"], "+i": ["h", "s"], "-i": ["h", "sdg"]}[state]
    if inverse:
        gates = [{"s": "sdg", "sdg": "s"}.get(g, g) for g in reversed(gates)]
    for g in gates:
        getattr(qc, g)(q)


def circuit(state: str, mode: str = "feedforward"):
    """One teleportation of a cardinal state. Classical bits: c[0] = m0, c[1] = m1 (Alice), c[2] = Bob's check
    (0 means Bob's qubit was found in |psi>)."""
    if state not in CARDINAL or mode not in MODES:
        raise ValueError(f"state in {CARDINAL}, mode in {MODES}")
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    q, c = QuantumRegister(3, "q"), ClassicalRegister(3, "c")
    qc = QuantumCircuit(q, c, name=f"teleport_{state}_{mode}")
    _prepare(qc, 0, state)
    qc.h(1); qc.cx(1, 2)                            # the shared pair
    qc.barrier()
    qc.cx(0, 1); qc.h(0)                            # Alice's Bell-basis rotation
    if mode == "deferred":
        qc.cx(1, 2); qc.cz(0, 2)
        qc.measure(0, c[0]); qc.measure(1, c[1])
    else:
        qc.measure(0, c[0]); qc.measure(1, c[1])
        if mode == "feedforward":
            with qc.if_test((c[1], 1)):
                qc.x(2)
            with qc.if_test((c[0], 1)):
                qc.z(2)
    qc.barrier()
    _prepare(qc, 2, state, inverse=True)
    qc.measure(2, c[2])
    return qc


def circuits(mode: str = "feedforward"):
    return [circuit(s, mode) for s in CARDINAL]


@dataclass
class TeleportVerdict:
    mode: str
    per_state: dict[str, float]
    average: float
    interval: tuple[float, float]       # Clopper-Pearson on the pooled success count
    shots: int
    beats_classical: bool               # the whole interval lies above 2/3

    def row(self) -> dict:
        return {"mode": self.mode, "average_fidelity": self.average, "ci_low": self.interval[0], "ci_high": self.interval[1],
                "shots": self.shots, "beats_classical_limit": self.beats_classical, **{f"F({k})": v for k, v in self.per_state.items()}}


def analyze(counts_list, mode: str, level: float = 0.99) -> TeleportVerdict:
    """Counts for the six cardinal states, in CARDINAL order."""
    per, ok, tot = {}, 0, 0
    for s, counts in zip(CARDINAL, counts_list):
        n = sum(counts.values())
        k = sum(v for key, v in counts.items() if key.replace(" ", "")[0] == "0")      # c[2] is the first character
        per[s] = k / n; ok += k; tot += n
    alpha = 1 - level
    lo = float(stats.beta.ppf(alpha / 2, ok, tot - ok + 1)) if ok else 0.0
    hi = float(stats.beta.ppf(1 - alpha / 2, ok + 1, tot - ok)) if ok < tot else 1.0
    return TeleportVerdict(mode, per, ok / tot, (lo, hi), tot, lo > CLASSICAL_LIMIT)


def werner_average_fidelity(f: float) -> float:
    return (2 * f + 1) / 3


def noise_model_depolarizing(p2: float):
    """Aer noise: after every CX, a two-qubit depolarizing channel rho -> (1 - p2) rho + p2 I/4."""
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ["cx"])
    return nm


def expected_feedforward_fidelity(p2: float) -> float:
    """Average fidelity in "feedforward" mode under noise_model_depolarizing(p2). The pair's CX turns |Phi+> into a
    Werner state with singlet fraction f = 1 - 3 p2/4, which alone gives (2f + 1)/3 = (1 + (1 - p2))/2. Alice's CX
    replaces her two qubits by I/4 with probability p2, after which Bob holds I/2. Both shrink the teleported Bloch
    vector, so F = (1 + (1 - p2)^2) / 2."""
    return 0.5 * (1.0 + (1.0 - p2) ** 2)
