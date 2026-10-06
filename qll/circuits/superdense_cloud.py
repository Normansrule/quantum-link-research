"""Superdense coding as a cloud-processor experiment (mission milestone M4.2): two classical bits per transmitted
qubit, and the control in which the qubit is not sent.

Physics
-------
Alice and Bob share |Phi+>. Alice encodes (i, j) by applying Z^i X^j to her qubit and sends it; Bob's Bell
measurement (CX, then H on Alice's qubit, then read both) returns (i, j) exactly [bennett1992]. The Holevo bound
caps the classical information one qubit can carry at one bit, and at two bits with prior entanglement, so
superdense coding is optimal [holevo1973]. In the control, Alice encodes but keeps her qubit; Bob reads only his own,
whose state is I/2 whatever she did, so his best guess of the two bits succeeds a quarter of the time and the
information per use is zero (the same no-signalling fact as P11).

Bob's qubit is 1 and Alice's is 0. Classical bits: c[0] = decoded i (or unused), c[1] = decoded j (or Bob's lone
reading in the control).
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np

MODES = ("send_qubit", "keep_qubit")
MESSAGES = tuple(itertools.product((0, 1), repeat=2))


def circuit(bits: tuple[int, int], mode: str = "send_qubit"):
    if mode not in MODES or tuple(bits) not in MESSAGES:
        raise ValueError(f"mode in {MODES}, bits in {MESSAGES}")
    from qiskit import QuantumCircuit

    i, j = bits
    qc = QuantumCircuit(2, 2, name=f"superdense_{i}{j}_{mode}")
    qc.h(0); qc.cx(0, 1)
    qc.barrier()
    if j:
        qc.x(0)
    if i:
        qc.z(0)
    qc.barrier()
    if mode == "send_qubit":                        # Alice's qubit reaches Bob: Bell measurement on both
        qc.cx(0, 1); qc.h(0)
        qc.measure(0, 0); qc.measure(1, 1)
    else:                                           # Alice keeps her qubit: Bob reads his own alone
        qc.measure(1, 1)
    return qc


def circuits(mode: str = "send_qubit"):
    return [circuit(m, mode) for m in MESSAGES]


@dataclass
class SuperdenseVerdict:
    mode: str
    confusion: np.ndarray            # rows: sent (i, j); columns: decoded (i, j)
    success: float
    bits_per_use: float              # plug-in mutual information with a uniform message

    def row(self) -> dict:
        return {"mode": self.mode, "success": self.success, "bits_per_use": self.bits_per_use}


def _decode(key: str, mode: str) -> int:
    k = key.replace(" ", "")
    c1, c0 = int(k[0]), int(k[1])                   # Qiskit prints c[1] first
    if mode == "send_qubit":
        return 2 * c0 + c1                          # (i, j) = (c[0], c[1]) as an index into MESSAGES
    return c1                                       # Bob's best guess from one bit: (0, c[1])


def analyze(counts_list, mode: str) -> SuperdenseVerdict:
    conf = np.zeros((4, 4))
    for row, counts in enumerate(counts_list):
        for key, v in counts.items():
            conf[row, _decode(key, mode)] += v
    p = conf / conf.sum(axis=1, keepdims=True)
    success = float(np.trace(p) / 4)
    py = p.mean(axis=0)
    h = lambda q: float(-np.sum(q[q > 0] * np.log2(q[q > 0])))
    mi = h(py) - float(np.mean([h(r) for r in p]))
    return SuperdenseVerdict(mode, conf, success, mi)
