"""Genuine n-party entanglement that a single measurement can destroy.

Physics
-------
|GHZ_n> = (|0...0> + |1...1>)/sqrt2 [greenberger1989]. Every Z-basis sample is all-0 or all-1; tracing
out one qubit leaves a separable mixture (I/2 ⊗ ... structure), so GHZ entanglement is fragile.
Clifford, hence Stim samples it for n up to 10^4 [gidney2021stim].
"""
from __future__ import annotations

import numpy as np


def ghz_circuit(n: int):
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(n, name=f"ghz{n}")
    qc.h(0)
    for k in range(1, n):
        qc.cx(0, k)
    return qc


def ghz_stim(n: int):
    import stim

    c = stim.Circuit()
    c.append("H", [0])
    for k in range(1, n):
        c.append("CX", [0, k])
    c.append("M", list(range(n)))
    return c


def sample_ghz(n: int, shots: int, seed: int = 0) -> np.ndarray:
    return ghz_stim(n).compile_sampler(seed=seed).sample(shots)


def ghz_state(n: int) -> np.ndarray:
    v = np.zeros(2**n, dtype=complex)
    v[0] = v[-1] = 1 / np.sqrt(2)
    return v
