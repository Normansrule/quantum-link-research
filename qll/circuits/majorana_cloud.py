"""Majorana measurement-only teleportation emulated on a qubit processor (mission milestone M4.6, protocol P13),
after Huang et al. (2021), who emulated a Majorana teleportation protocol on a superconducting processor [huang2021].

Mapping
-------
With the Jordan-Wigner transformation of qll/circuits/majorana_teleport.py (qubit A first), the six Majorana
operators are
    gamma_1 = X_A,   gamma_2 = Y_A,   gamma_3 = Z_A X_B,   gamma_4 = Z_A Y_B,   gamma_5 = Z_A Z_B X_C,   gamma_6 = Z_A Z_B Y_C,
so the protocol's parities are Pauli products: P23 = i gamma_2 gamma_3 = -X_A X_B and P14 = i gamma_1 gamma_4 = Y_A Y_B
(checked against the fermionic matrices in tests/test_majorana_teleport.py). Measuring both is a Bell measurement of
A and B; measuring P23 alone reads one bit. Qubits: 0 = A (input), 1 = B, 2 = C (Bob). Classical bits follow
qll/circuits/teleport_cloud.py: c[2] = 0 means Bob's qubit was found in the input state, so the same analysis applies.

Modes and the average fidelities the fermionic model predicts:
    "two_bit"        both parities, Pauli corrections                         1
    "one_bit"        P23 only, best correction (Z_C when p = +1)                2/3, the classical limit
    "paper_one_bit"  P23 only, the paper's correction (X_C when p = -1)          1/2
    "no_bits"        both parities measured, nothing sent                       1/2
This emulates the protocol's logic; it says nothing about topological protection, which belongs to the hardware.
"""
from __future__ import annotations

from qll.circuits.teleport_cloud import CARDINAL, _prepare

MODES = ("two_bit", "one_bit", "paper_one_bit", "no_bits")
EXPECTED = {"two_bit": 1.0, "one_bit": 2 / 3, "paper_one_bit": 0.5, "no_bits": 0.5}
JW = {1: "XII", 2: "YII", 3: "ZXI", 4: "ZYI", 5: "ZZX", 6: "ZZY"}       # qubit A, B, C from left to right


def circuit(state: str, mode: str = "two_bit"):
    if state not in CARDINAL or mode not in MODES:
        raise ValueError(f"state in {CARDINAL}, mode in {MODES}")
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    q, c = QuantumRegister(3, "q"), ClassicalRegister(3, "c")
    qc = QuantumCircuit(q, c, name=f"majorana_{state}_{mode}")
    _prepare(qc, 0, state)
    qc.h(1); qc.cx(1, 2)                                   # |Phi+> on B and C
    qc.barrier()
    if mode in ("two_bit", "no_bits"):                     # read X_A X_B (c[0]) and Z_A Z_B (c[1]); Y_A Y_B = -XX ZZ
        qc.cx(0, 1); qc.h(0)
        qc.measure(0, c[0]); qc.measure(1, c[1])
        if mode == "two_bit":
            with qc.if_test((c[1], 1)):
                qc.x(2)
            with qc.if_test((c[0], 1)):
                qc.z(2)
    else:                                                  # read X_A X_B only: c[1] = parity bit, P23 = -(-1)^c[1]
        qc.h(0); qc.h(1); qc.cx(0, 1)
        qc.measure(1, c[1])
        if mode == "one_bit":
            with qc.if_test((c[1], 1)):                    # p = +1
                qc.z(2)
        else:
            with qc.if_test((c[1], 0)):                    # p = -1
                qc.x(2)
    qc.barrier()
    _prepare(qc, 2, state, inverse=True)
    qc.measure(2, c[2])
    return qc


def circuits(mode: str = "two_bit"):
    return [circuit(s, mode) for s in CARDINAL]
