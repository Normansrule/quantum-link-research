"""Compress the reconciled key so that an eavesdropper's information becomes negligible.

Physics
-------
Two-universal hashing (Toeplitz matrix over GF(2)) maps n bits with min-entropy H_min to
l = H_min - leak_EC - 2 log2(1/eps) secret bits, with Eve's information bounded by eps
[bennett1995pa] [renner2005]. For BB84 in the asymptotic limit H_min = n (1 - h2(Q)) so
l = n (1 - 2 h2(Q)) - 2 log2(1/eps), recovering the Shor-Preskill rate [shor2000].
"""
from __future__ import annotations

import math

import numpy as np

from qll.qkd.binary_entropy import h2


def final_key_length(n_sifted: int, qber: float, leak_ec_bits: float, eps: float = 1e-10) -> int:
    l = n_sifted * (1 - h2(qber)) - leak_ec_bits - 2 * math.log2(1 / eps)
    return max(0, int(math.floor(l)))


def toeplitz_hash(key: np.ndarray, out_len: int, seed: int = 0) -> np.ndarray:
    """Apply a random Toeplitz matrix (two-universal family) to a bit vector."""
    k = np.asarray(key, dtype=np.int8)
    n = len(k)
    if out_len <= 0:
        return np.zeros(0, dtype=np.int8)
    rng = np.random.default_rng(seed)
    diag = rng.integers(0, 2, size=n + out_len - 1, dtype=np.int8)   # first column + first row
    out = np.zeros(out_len, dtype=np.int8)
    for i in range(out_len):
        row = diag[i : i + n][::-1]
        out[i] = int(np.dot(row, k) % 2)
    return out
