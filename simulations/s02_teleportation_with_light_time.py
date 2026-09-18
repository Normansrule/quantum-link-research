"""S02 — Teleportation fidelity with a light-time-delayed classical channel (Flagship F3, stage S1).

Physics: the Bell pair is created at t = 0; Bob's half sits in a memory with T2 while Alice's two bits
travel d/c. Bob applies the correction only when the ClassicalMessage arrives. The memory is modelled
as depolarization of Bob's qubit with probability 1 − exp(−t/T2), so the resource singlet fraction is
f(t) = 1/4 + 3/4·exp(−t/T2) and the average teleportation fidelity is F = (2f + 1)/3 (Horodecki 1999).
Reference: Bennett et al. (1993); Massar & Popescu (1995).
"""
from __future__ import annotations

import math

import numpy as np

from qll.channels.light_time_delay import ClassicalMessage, NotYetArrived, one_way_delay_s
from qll.constants.astro import EARTH_MARS_MAX_M, EARTH_MARS_MIN_M


def teleport_fidelity_aer(delay_s: float, T2_s: float, shots: int = 4000, seed: int = 3) -> float:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import DensityMatrix, Statevector, state_fidelity
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    p_mem = 1 - math.exp(-delay_s / T2_s)
    noise = NoiseModel()
    if p_mem > 0:
        noise.add_all_qubit_quantum_error(depolarizing_error(p_mem, 1), ["id"])
    sim = AerSimulator(method="density_matrix", noise_model=noise, seed_simulator=seed)
    # six cardinal input states
    inputs = [("0", lambda qc: None), ("1", lambda qc: qc.x(0)), ("+", lambda qc: qc.h(0)),
              ("-", lambda qc: (qc.x(0), qc.h(0))), ("+i", lambda qc: (qc.h(0), qc.s(0))), ("-i", lambda qc: (qc.h(0), qc.sdg(0)))]
    fids = []
    for _, prep in inputs:
        qc = QuantumCircuit(3, 2)
        prep(qc)
        qc.h(1); qc.cx(1, 2)                 # Bell pair between Alice (1) and Bob (2)
        qc.id(2)                             # Bob's memory waits: noise applies here
        qc.cx(0, 1); qc.h(0); qc.measure([0, 1], [0, 1])   # Alice's Bell measurement → bits
        with qc.if_test((1, 1)):
            qc.x(2)
        with qc.if_test((0, 1)):
            qc.z(2)
        qc.save_density_matrix([2], label="bob")
        # the classical channel: bits exist at t=0 but may only be used at t = d/c
        msg = ClassicalMessage(payload=(0, 0), sent_at_s=0.0, distance_m=delay_s * 299792458.0)
        if delay_s > 0:
            try:
                msg.receive(now_s=0.0)
                raise RuntimeError("guard failed: bits usable before arrival")
            except NotYetArrived:
                pass
        msg.receive(now_s=msg.earliest_arrival_s)   # allowed only now
        rho = DensityMatrix(sim.run(qc, shots=shots).result().data()["bob"])
        target = QuantumCircuit(1); prep(target)
        fids.append(state_fidelity(rho, Statevector(target)))
    return float(np.mean(fids))


def main() -> None:
    from _common import report, save
    import matplotlib.pyplot as plt

    T2 = 3600.0  # a one-hour memory
    delays = np.logspace(-1, 4.2, 14)
    F = [teleport_fidelity_aer(d, T2) for d in delays]
    lo, hi = one_way_delay_s(EARTH_MARS_MIN_M), one_way_delay_s(EARTH_MARS_MAX_M)
    report("S02 teleportation vs classical delay (T2 = 1 h)", [
        ("F at 1 s delay", f"{F[0]:.3f}"), ("F at Mars minimum one-way (%.0f s)" % lo, f"{teleport_fidelity_aer(lo, T2):.3f}"),
        ("F at Mars maximum one-way (%.0f s)" % hi, f"{teleport_fidelity_aer(hi, T2):.3f}"),
        ("delay where F = 2/3 (analytic: T2·ln 3)", f"{T2*math.log(3):.0f} s")])
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.semilogx(delays, F, "o-", lw=2, label="Aer, six-state average")
    ax.semilogx(delays, (2 * (0.25 + 0.75 * np.exp(-delays / T2)) + 1) / 3, "--", label="(2f(t)+1)/3")
    ax.axhline(2 / 3, color="k", ls=":"); ax.text(0.12, 0.675, "classical limit 2/3", fontsize=8)
    ax.axvspan(lo, hi, color="C3", alpha=0.12); ax.text(math.sqrt(lo * hi), 0.9, "Mars one-way", ha="center", fontsize=8, color="C3")
    ax.set(xlabel="classical delay before correction (s)", ylabel="teleportation fidelity", ylim=(0.4, 1.02), title="S02: the bits arrive late; the memory decays meanwhile")
    ax.legend(loc="lower left"); save(fig, "teleport_delay")


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent)); main()
