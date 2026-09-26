"""Quantum volume: the heavy-output test on random square circuits.

Physics
-------
A width-n, depth-n model circuit applies layers of random SU(4) gates on random qubit pairs [cross2019]. Its ideal
output distribution defines the "heavy" outputs (probability above the median); an ideal device lands on them with
probability (1 + ln 2)/2 ≈ 0.85 as n grows, a fully depolarized one with 0.5. A device passes at width n if the heavy-output
probability exceeds 2/3 with confidence; quantum volume is 2^n for the largest n that passes. Here the circuits come from
qiskit.circuit.library.quantum_volume and are run in Aer with a depolarizing error on every two-qubit gate.
"""
from __future__ import annotations

import numpy as np


def heavy_output_probability(n: int, p2: float = 0.0, n_circuits: int = 20, shots: int = 1000, seed: int = 0) -> float:
    from qiskit import transpile
    from qiskit.circuit.library import quantum_volume
    from qiskit.quantum_info import Statevector
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    noise = NoiseModel()
    if p2 > 0:
        noise.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ["cx"])
    sim = AerSimulator(noise_model=noise, seed_simulator=seed)
    hops = []
    for k in range(n_circuits):
        qc = quantum_volume(n, seed=seed + k).decompose()
        ideal = Statevector(qc).probabilities()
        heavy = {i for i, pr in enumerate(ideal) if pr > np.median(ideal)}
        meas = qc.copy(); meas.measure_all()
        counts = sim.run(transpile(meas, basis_gates=["cx", "u"], seed_transpiler=seed), shots=shots).result().get_counts()
        hops.append(sum(c for b, c in counts.items() if int(b, 2) in heavy) / shots)
    return float(np.mean(hops))


def ideal_limit() -> float:
    return (1 + np.log(2)) / 2
