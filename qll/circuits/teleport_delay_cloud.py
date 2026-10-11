"""Teleportation with a delayed classical channel on a cloud processor (milestone M4.3, proposal E01, tier 1 of the
frontier lab): Bob's qubit waits, as it would while the two bits cross a distance, before the corrections arrive.

Physics
-------
Between Alice's Bell measurement and Bob's correction, Bob's qubit idles for the classical channel's transit time t.
On a superconducting processor an idle qubit relaxes with T1 and dephases with T2 [krantz2019]; in Bloch form the
idle channel shrinks x and y by exp(-t/T2) and z by exp(-t/T1), and pulls z toward |0> by 1 - exp(-t/T1)
[nielsen2010]. The corrections X^m1 Z^m0 conjugate that channel, and averaging over the six cardinal states (a qubit
2-design [dankert2009]) cancels the pull, so the average fidelity depends only on the shrink:
    F(t) = 1/2 + (2 exp(-t/T2) + exp(-t/T1)) / 6                                [nielsen2002]
since F = (2 F_e + 1)/3 with F_e = (1 + Tr T)/4. A two-qubit depolarizing error p2 after every CX shrinks the whole
teleported Bloch vector by (1 - p2)^2 in feed-forward mode (teleport_cloud.expected_feedforward_fidelity), and the
shrinks multiply:
    F(t) = 1/2 + (1 - p2)^2 (2 exp(-t/T2) + exp(-t/T1)) / 6.
Teleportation beats every measure-and-prepare strategy only while F > 2/3 [massar1995]; the delay at which F falls
to 2/3 is the longest classical channel the processor's memory survives. Without the bits F = 1/2 at every delay,
which is no-signalling [peres2004]: the delay changes nothing Bob can see until the bits arrive.

Two ways to delay:
    "emulated"  the idle channel inserted as a thermal-relaxation Kraus map (qiskit-aer), for the simulator;
    "hardware"  a real delay instruction on Bob's qubit, so the device's own T1 and T2 do the work.
"""
from __future__ import annotations

import math

from qll.circuits.teleport_cloud import CARDINAL, MODES, _prepare

DELAYS = ("emulated", "hardware")
T1_DEFAULT_US, T2_DEFAULT_US = 200.0, 150.0      # orders of magnitude for a current transmon; replace with calibration data


def bloch_shrink(t_us: float, T1_us: float, T2_us: float) -> tuple[float, float]:
    """(exp(-t/T2), exp(-t/T1)): the transverse and longitudinal shrink of an idle qubit."""
    if t_us < 0 or T1_us <= 0 or T2_us <= 0 or T2_us > 2 * T1_us:
        raise ValueError("need t >= 0, T1 > 0, and 0 < T2 <= 2 T1")
    return math.exp(-t_us / T2_us), math.exp(-t_us / T1_us)


def average_fidelity(t_us: float, T1_us: float = T1_DEFAULT_US, T2_us: float = T2_DEFAULT_US, p2: float = 0.0, mode: str = "feedforward") -> float:
    if mode == "no_bits":
        return 0.5
    e2, e1 = bloch_shrink(t_us, T1_us, T2_us)
    k = (1 - p2) ** (2 if mode == "feedforward" else 3)
    return 0.5 + k * (2 * e2 + e1) / 6


def with_offset(t_us: float, T1_us: float, T2_us: float, k: float) -> float:
    """F(t) = 1/2 + k (2 exp(-t/T2) + exp(-t/T1))/6 with k = 2 (F(0) - 1/2) measured at zero delay, which absorbs gate
    and readout errors on a device so the delay's own effect can be compared with its calibrated T1 and T2."""
    e2, e1 = bloch_shrink(t_us, T1_us, T2_us)
    return 0.5 + k * (2 * e2 + e1) / 6


def crossover_delay_us(T1_us: float = T1_DEFAULT_US, T2_us: float = T2_DEFAULT_US, p2: float = 0.0) -> float:
    """The delay at which the feed-forward fidelity falls to 2/3 (0 if it starts at or below 2/3)."""
    target = 2 / 3
    if average_fidelity(0.0, T1_us, T2_us, p2) <= target:
        return 0.0
    lo, hi = 0.0, 50.0 * max(T1_us, T2_us)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if average_fidelity(mid, T1_us, T2_us, p2) > target else (lo, mid)
    return 0.5 * (lo + hi)


def circuit(state: str, delay_us: float, mode: str = "feedforward", delay: str = "emulated", T1_us: float = T1_DEFAULT_US, T2_us: float = T2_DEFAULT_US):
    """Teleport a cardinal state with Bob's qubit idle for delay_us between Alice's measurement and his correction."""
    if state not in CARDINAL or mode not in MODES or delay not in DELAYS or delay_us < 0:
        raise ValueError(f"state in {CARDINAL}, mode in {MODES}, delay in {DELAYS}, delay_us >= 0")
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    q, c = QuantumRegister(3, "q"), ClassicalRegister(3, "c")
    qc = QuantumCircuit(q, c, name=f"teleport_delay_{state}_{mode}_{delay_us:g}us")
    _prepare(qc, 0, state)
    qc.h(1); qc.cx(1, 2)
    qc.barrier()
    qc.cx(0, 1); qc.h(0)
    if mode != "deferred":
        qc.measure(0, c[0]); qc.measure(1, c[1])
    if delay_us > 0:                                            # the two bits in transit; Bob's qubit waits
        if delay == "hardware":
            qc.delay(delay_us, 2, unit="us")
        else:
            from qiskit_aer.noise import thermal_relaxation_error
            qc.append(thermal_relaxation_error(T1_us, T2_us, delay_us).to_instruction(), [2])
    if mode == "deferred":
        qc.cx(1, 2); qc.cz(0, 2)
        qc.measure(0, c[0]); qc.measure(1, c[1])
    elif mode == "feedforward":
        with qc.if_test((c[1], 1)):
            qc.x(2)
        with qc.if_test((c[0], 1)):
            qc.z(2)
    qc.barrier()
    _prepare(qc, 2, state, inverse=True)
    qc.measure(2, c[2])
    return qc


def circuits(delay_us: float, mode: str = "feedforward", delay: str = "emulated", **kw):
    return [circuit(s, delay_us, mode, delay, **kw) for s in CARDINAL]


def sweep_delays_us(T2_us: float = T2_DEFAULT_US, n: int = 6) -> list[float]:
    """Delays from zero to about two T2, where the fidelity has crossed 2/3: the sweep the runner uses."""
    return [round(2 * T2_us * k / (n - 1), 1) for k in range(n)]
