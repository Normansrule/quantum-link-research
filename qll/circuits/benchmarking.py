"""Single-qubit randomized benchmarking (RB) with the 24-element Clifford group in Qiskit Aer.

Physics
-------
Random Clifford sequences of length m followed by the inverting Clifford return the qubit to |0> if the gates are
perfect; with gate-independent noise the survival probability decays as A p^m + B and the average error per
Clifford is r = (1 - p)(1 - 1/d) with d = 2 [magesan2011] [magesan2012]. RB is insensitive to state-preparation and
measurement error (they sit in A and B), which is why it is the standard gate benchmark. For a depolarizing error of
strength eps per Clifford, p = 1 - eps (up to the d/(d+1) convention checked in the tests).
"""
from __future__ import annotations

import math

import numpy as np


def single_qubit_cliffords():
    """The 24 single-qubit Cliffords as Qiskit gate-name sequences (a standard generating set)."""
    return [
        [], ["x"], ["y"], ["z"], ["h"], ["s"], ["sdg"], ["h", "s"], ["h", "sdg"], ["s", "h"], ["sdg", "h"],
        ["h", "x"], ["h", "y"], ["h", "z"], ["s", "x"], ["s", "y"], ["s", "z"], ["sdg", "x"], ["sdg", "y"],
        ["h", "s", "h"], ["h", "sdg", "h"], ["s", "h", "s"], ["sdg", "h", "sdg"], ["s", "h", "sdg"],
    ]


def rb_survival(lengths: list[int], p_error: float, shots: int = 2000, n_seq: int = 8, seed: int = 0) -> list[float]:
    """Survival probability vs sequence length with a depolarizing error of strength p_error on every gate."""
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Clifford
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, depolarizing_error

    rng = np.random.default_rng(seed)
    cliffs = single_qubit_cliffords()
    noise = NoiseModel()
    if p_error > 0:
        noise.add_all_qubit_quantum_error(depolarizing_error(p_error, 1), ["x", "y", "z", "h", "s", "sdg"])
    sim = AerSimulator(noise_model=noise, seed_simulator=seed)
    out = []
    for m in lengths:
        surv = []
        for _ in range(n_seq):
            qc = QuantumCircuit(1, 1)
            acc = QuantumCircuit(1)
            for _ in range(m):
                seq = cliffs[rng.integers(len(cliffs))]
                for g in seq:
                    getattr(qc, g)(0); getattr(acc, g)(0)
            inv = Clifford(acc).adjoint().to_circuit()
            qc.compose(inv, inplace=True)
            qc.measure(0, 0)
            counts = sim.run(qc, shots=shots).result().get_counts()
            surv.append(counts.get("0", 0) / shots)
        out.append(float(np.mean(surv)))
    return out


def fit_decay(lengths: list[int], survival: list[float]) -> tuple[float, float, float]:
    """Fit A p^m + B; returns (p, A, B)."""
    from scipy.optimize import curve_fit

    f = lambda m, A, p, B: A * p**m + B
    popt, _ = curve_fit(f, np.asarray(lengths, float), np.asarray(survival, float), p0=[0.5, 0.98, 0.5], bounds=([0, 0, 0], [1, 1, 1]))
    return float(popt[1]), float(popt[0]), float(popt[2])


def error_per_clifford(p: float, d: int = 2) -> float:
    return (1 - p) * (1 - 1 / d)
