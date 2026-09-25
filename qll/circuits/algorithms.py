"""Quantum Fourier transform and phase estimation, small enough to verify exactly.

Physics
-------
QFT_n maps |j> to (1/sqrt(2^n)) sum_k e^{2 pi i jk/2^n} |k> with n(n+1)/2 gates (Hadamards and controlled phases)
[coppersmith1994] [nielsen2010 ch. 5]. Phase estimation reads the eigenphase phi of U|u> = e^{2 pi i phi}|u> to t bits
by applying controlled-U^(2^k) and an inverse QFT; the outcome is the t-bit binary expansion of phi with probability
>= 4/pi^2 when phi is not exactly representable [kitaev1995]. Shor's algorithm is phase estimation of the modular
multiplication operator; this module stops at the phase-estimation primitive, verified against the analytic
Fourier matrix and a known eigenphase.
"""
from __future__ import annotations

import math

import numpy as np


def qft_matrix(n: int) -> np.ndarray:
    N = 2**n
    j, k = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    return np.exp(2j * np.pi * j * k / N) / math.sqrt(N)


def qft_circuit(n: int):
    """Textbook QFT (with the final qubit-order swaps so that the matrix matches qft_matrix in Qiskit's ordering)."""
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(n, name="qft")
    for i in reversed(range(n)):                 # most significant qubit (n-1) first, in Qiskit's little-endian order
        qc.h(i)
        for j in range(i):
            qc.cp(math.pi / 2 ** (i - j), j, i)
    for i in range(n // 2):
        qc.swap(i, n - 1 - i)
    return qc


def phase_estimation(phi: float, t_bits: int, shots: int = 4000, seed: int = 0) -> tuple[float, dict]:
    """Estimate phi in [0,1) for U = diag(1, e^{2 pi i phi}) acting on |1>; returns (best estimate, counts)."""
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    qc = QuantumCircuit(t_bits + 1, t_bits)
    qc.x(t_bits)                                    # eigenstate |1>
    for k in range(t_bits):
        qc.h(k)
        qc.cp(2 * math.pi * phi * 2**k, k, t_bits)  # controlled-U^(2^k)
    qc.compose(qft_circuit(t_bits).inverse(), qubits=range(t_bits), inplace=True)   # inverse QFT on the register
    qc.measure(range(t_bits), range(t_bits))
    counts = AerSimulator(seed_simulator=seed).run(qc, shots=shots).result().get_counts()
    best = max(counts, key=counts.get)
    return int(best, 2) / 2**t_bits, counts
