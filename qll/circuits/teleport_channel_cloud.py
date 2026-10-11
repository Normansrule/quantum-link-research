"""Teleportation as a quantum channel (milestone M4.7): process tomography of the qubit Bob receives, on a cloud
processor, with the same estimator and certificate as the two-room channel (qll/link/channel_tomography.py).

Physics
-------
Teleportation with the two classical bits implements a channel from Alice's input to Bob's qubit [bennett1993]. On
a noiseless processor it is the identity. With a two-qubit depolarizing error p2 after every CX
(teleport_cloud.noise_model_depolarizing) the feed-forward version is depolarizing with Bloch shrink (1 - p2)^2
(teleport_cloud.expected_feedforward_fidelity); the deferred version has one more noisy CX, so (1 - p2)^3. Without
the bits Bob holds I/2 for every input: a completely depolarizing, entanglement-breaking channel [horodecki2003eb].
Tomography sends the inputs H, V, D, A, R, L (the cardinal states |0>, |1>, |+>, |->, |+i>, |-i>) and measures Bob's
qubit in X, Y, and Z [chuang1997]. So entanglement plus two bits per qubit makes a quantum channel, and the
classical bits are an essential part of it, as no-signalling requires.
"""
from __future__ import annotations

from qll.circuits.teleport_cloud import MODES, _prepare

POLARIZATION = {"H": "0", "V": "1", "D": "+", "A": "-", "R": "+i", "L": "-i"}
BASES = ("X", "Y", "Z")


def circuit(state: str, basis: str, mode: str = "feedforward"):
    """Teleport a cardinal state (named by its polarization) and measure Bob's qubit in a basis; c[2] is Bob's bit."""
    if state not in POLARIZATION or basis not in BASES or mode not in MODES:
        raise ValueError(f"state in {tuple(POLARIZATION)}, basis in {BASES}, mode in {MODES}")
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    q, c = QuantumRegister(3, "q"), ClassicalRegister(3, "c")
    qc = QuantumCircuit(q, c, name=f"teleport_channel_{state}_{basis}_{mode}")
    _prepare(qc, 0, POLARIZATION[state])
    qc.h(1); qc.cx(1, 2)
    qc.barrier()
    qc.cx(0, 1); qc.h(0)
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
    if basis == "X":
        qc.h(2)
    elif basis == "Y":
        qc.sdg(2); qc.h(2)
    qc.measure(2, c[2])
    return qc


def circuits(mode: str = "feedforward", inputs=tuple(POLARIZATION), bases=BASES):
    keys = [(s, b) for s in inputs for b in bases]
    return keys, [circuit(s, b, mode) for s, b in keys]


def counts_to_tomography(keys, counts_list) -> dict:
    """{(input, basis): (n0, n1)} from Bob's bit, the first character of each Qiskit key."""
    out = {}
    for key, counts in zip(keys, counts_list):
        n0 = sum(v for k, v in counts.items() if k.replace(" ", "")[0] == "0")
        out[key] = (n0, sum(counts.values()) - n0)
    return out
