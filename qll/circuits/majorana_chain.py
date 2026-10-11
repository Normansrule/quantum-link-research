"""Scaling the Majorana parity teleportation of Crogman, Dang, and Erenso (2025) from one hop to a chain of N hops
(proposal E20, milestone M4.8), emulated on a qubit processor and set against the paper's error budget.

Physics
-------
A chain of N hops holds the input on mode 0 and N shared pairs on modes (1, 2), (3, 4), ..., (2N - 1, 2N), each in
|Phi+>. Hop h measures the two parities of the holder mode k = 2h and its neighbour k + 1,
    P = i gamma_{2k+2} gamma_{2k+3} = -X_k X_{k+1},      Q = i gamma_{2k+1} gamma_{2k+4} = Y_k Y_{k+1},
because the Jordan-Wigner strings of adjacent modes cancel, so every hop is the same local Bell measurement as the
single hop of P13 (qll/circuits/majorana_cloud.py), checked on the fermionic operators for any position in
tests/test_majorana_chain.py [crogman2025] [huang2021]. Its two parity bits drive Pauli corrections on mode k + 2,
which then holds the state, and the next hop repeats. Every hop needs its own two classical bits [bennett1993];
without them Bob holds I/2 whatever the chain length [peres2004].

Scaling. If one hop acts on the teleported qubit as an isotropic channel that shrinks the Bloch vector by s, the
shrinks multiply, so N hops give
    F_N = (1 + s^N) / 2,
and the chain beats every measure-and-prepare strategy (2/3) [massar1995] only while s^N > 1/3, that is for
N < ln 3 / ln(1/s) hops. On a processor with a two-qubit depolarizing error p2 after every CX, each feed-forward hop
shrinks by s = (1 - p2)^2 (qll/circuits/teleport_cloud.expected_feedforward_fidelity). On Majorana hardware a hop's
fidelity F_hop comes from the error budget (qll/hardware/majorana_error_budget.teleport_fidelity). Taking that
conservative bound as the average fidelity of an isotropic hop (a misread parity bit applies a wrong Pauli
correction) gives s = 2 F_hop - 1 [nielsen2002], which never overstates the chain. Solving
F_N = 2/3 for the readout signal-to-noise ratio turns a target chain length into a device requirement.
"""
from __future__ import annotations

import math

import numpy as np

from qll.circuits.majorana_teleport import majoranas
from qll.circuits.teleport_cloud import CARDINAL, _prepare
from qll.hardware.majorana_error_budget import teleport_fidelity

MODES = ("two_bit", "no_bits")
_P = {"I": np.eye(2, dtype=complex), "X": np.array([[0, 1], [1, 0]], complex), "Y": np.array([[0, -1j], [1j, 0]]), "Z": np.diag([1.0, -1.0]).astype(complex)}


def pauli_string(ops: dict[int, str], n: int) -> np.ndarray:
    out = np.eye(1, dtype=complex)
    for q in range(n):
        out = np.kron(out, _P[ops.get(q, "I")])
    return out


def hop_parities(k: int, n_modes: int) -> tuple[np.ndarray, np.ndarray]:
    """The two parities measured by the hop from mode k to mode k + 1, as fermionic bilinears (1-based gammas)."""
    g = majoranas(n_modes)
    return 1j * g[2 * k + 2] @ g[2 * k + 3], 1j * g[2 * k + 1] @ g[2 * k + 4]


def circuit(state: str, hops: int, mode: str = "two_bit"):
    """Teleport a cardinal state along `hops` hops on 2 hops + 1 qubits in a line; c[2 hops] = 0 means Bob holds it."""
    if state not in CARDINAL or mode not in MODES or hops < 1:
        raise ValueError(f"state in {CARDINAL}, mode in {MODES}, hops >= 1")
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    n = 2 * hops + 1
    q, c = QuantumRegister(n, "q"), ClassicalRegister(n, "c")
    qc = QuantumCircuit(q, c, name=f"majorana_chain_{hops}_{state}_{mode}")
    _prepare(qc, 0, state)
    for h in range(hops):
        qc.h(2 * h + 1); qc.cx(2 * h + 1, 2 * h + 2)        # the hop's pair
    qc.barrier()
    for h in range(hops):
        k = 2 * h                                            # holder; reads X_k X_{k+1} into c[k] and Z_k Z_{k+1} into c[k+1]
        qc.cx(k, k + 1); qc.h(k)
        qc.measure(k, c[k]); qc.measure(k + 1, c[k + 1])
        if mode == "two_bit":
            with qc.if_test((c[k + 1], 1)):
                qc.x(k + 2)
            with qc.if_test((c[k], 1)):
                qc.z(k + 2)
    qc.barrier()
    _prepare(qc, n - 1, state, inverse=True)
    qc.measure(n - 1, c[n - 1])
    return qc


def circuits(hops: int, mode: str = "two_bit"):
    return [circuit(s, hops, mode) for s in CARDINAL]


def chain_fidelity(hops: int, shrink: float) -> float:
    return 0.5 * (1.0 + shrink ** hops)


def expected_fidelity(hops: int, p2: float = 0.0, mode: str = "two_bit") -> float:
    return 0.5 if mode == "no_bits" else chain_fidelity(hops, (1 - p2) ** 2)


def max_hops(shrink: float, offset: float = 1.0) -> int:
    """The longest chain still above 2/3: the largest N with offset * shrink^N > 1/3. The offset k = 2 F_0 - 1 absorbs
    the state preparation and final readout on a device, measured by fitting F_N = (1 + k s^N)/2 over several lengths."""
    if offset * min(shrink, 1.0) <= 1 / 3 and shrink <= 1:
        return 0
    if shrink >= 1:
        return math.inf
    n = math.floor(math.log(3 * offset) / math.log(1 / shrink))
    return n - 1 if offset * shrink ** n <= 1 / 3 else n


def hop_shrink(snr0: float, gap_over_kT: float, poison_prob: float, l_over_xi: float, **kw) -> float:
    return 2 * teleport_fidelity(snr0, gap_over_kT, poison_prob, l_over_xi, **kw) - 1


def required_snr(hops: int, gap_over_kT: float = 5.0, poison_prob: float = 0.001, l_over_xi: float = 6.0, snr_max: float = 50.0,
                 target: float = 2 / 3) -> float:
    """Smallest readout signal-to-noise ratio mu0/sigma at which an N-hop chain stays above `target` (2/3 by default:
    better than any classical strategy); inf if no readout can, because poisoning or hybridization alone caps it."""
    ok = lambda snr: chain_fidelity(hops, hop_shrink(snr, gap_over_kT, poison_prob, l_over_xi)) > target
    if not ok(snr_max):
        return math.inf
    lo, hi = 0.0, snr_max
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if ok(mid) else (mid, hi)
    return hi
