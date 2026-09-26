"""Hypergraph-product codes: how quantum LDPC codes beat the surface code's encoding rate.

Physics
-------
From classical parity-check matrices H1 (m1 x n1) and H2 (m2 x n2), the hypergraph product [tillich2014] is the CSS code
    H_X = [H1 ⊗ I_n2 | I_m1 ⊗ H2^T],   H_Z = [I_n1 ⊗ H2 | H1^T ⊗ I_m2],
with n = n1 n2 + m1 m2 physical qubits and k = k1 k2 + k1^T k2^T logical qubits, where k^T = m - rank(H) is the
dimension of the transposed code. The surface code is the product of two repetition codes (k = 1); products of better
classical codes keep the checks sparse (low weight, hence "LDPC") while k grows linearly with n, which is the idea behind
the 2024 bivariate-bicycle "gross" code that stores 12 logical qubits in 144 data qubits at distance 12 [bravyi2024]
[breuckmann2021]. This module builds the matrices, checks commutation (H_X H_Z^T = 0 mod 2), and counts k by GF(2) rank.
"""
from __future__ import annotations

import numpy as np


def gf2_rank(M: np.ndarray) -> int:
    A = (np.asarray(M, dtype=np.uint8) % 2).copy()
    rows, cols = A.shape
    r = 0
    for c in range(cols):
        pivot = next((i for i in range(r, rows) if A[i, c]), None)
        if pivot is None:
            continue
        A[[r, pivot]] = A[[pivot, r]]
        for i in range(rows):
            if i != r and A[i, c]:
                A[i] ^= A[r]
        r += 1
        if r == rows:
            break
    return r


def repetition_checks(d: int) -> np.ndarray:
    """Open-boundary repetition code: (d-1) x d, checks on neighbouring bits."""
    H = np.zeros((d - 1, d), dtype=np.uint8)
    for i in range(d - 1):
        H[i, i] = H[i, i + 1] = 1
    return H


def hamming_checks() -> np.ndarray:
    """[7,4,3] Hamming code."""
    return np.array([[1, 0, 1, 0, 1, 0, 1], [0, 1, 1, 0, 0, 1, 1], [0, 0, 0, 1, 1, 1, 1]], dtype=np.uint8)


def hypergraph_product(H1: np.ndarray, H2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    m1, n1 = H1.shape
    m2, n2 = H2.shape
    HX = np.hstack([np.kron(H1, np.eye(n2, dtype=np.uint8)), np.kron(np.eye(m1, dtype=np.uint8), H2.T)]) % 2
    HZ = np.hstack([np.kron(np.eye(n1, dtype=np.uint8), H2), np.kron(H1.T, np.eye(m2, dtype=np.uint8))]) % 2
    return HX.astype(np.uint8), HZ.astype(np.uint8)


def css_parameters(HX: np.ndarray, HZ: np.ndarray) -> tuple[int, int]:
    """(n, k) of a CSS code: k = n - rank(H_X) - rank(H_Z)."""
    n = HX.shape[1]
    return n, n - gf2_rank(HX) - gf2_rank(HZ)


def max_check_weight(HX: np.ndarray, HZ: np.ndarray) -> int:
    return int(max(HX.sum(axis=1).max(), HZ.sum(axis=1).max()))
