"""Basis reconciliation: keep only the rounds where Alice and Bob used the same basis.

Physics
-------
With two bases chosen uniformly the sifting factor is 1/2; with a biased basis choice (probability
p_Z for the key basis at both ends) the fraction kept is p_Z^2 + (1 - p_Z)^2 and tends to 1
[lo2005efficient]. Announcing bases is a public classical exchange: one ClassicalMessage each way.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.channels.light_time_delay import ClassicalMessage


@dataclass(frozen=True)
class SiftResult:
    keep: np.ndarray            # boolean mask over rounds
    messages: tuple[ClassicalMessage, ClassicalMessage]

    @property
    def fraction(self) -> float:
        return float(self.keep.mean()) if len(self.keep) else 0.0


def sift(alice_bases: np.ndarray, bob_bases: np.ndarray, distance_m: float = 0.0, t0_s: float = 0.0) -> SiftResult:
    a = np.asarray(alice_bases, dtype=np.int8)
    b = np.asarray(bob_bases, dtype=np.int8)
    m_a = ClassicalMessage(payload=tuple(int(x) for x in a), sent_at_s=t0_s, distance_m=distance_m)
    m_b = ClassicalMessage(payload=tuple(int(x) for x in b), sent_at_s=t0_s, distance_m=distance_m)
    return SiftResult(a == b, (m_a, m_b))


def sifting_fraction_biased(p_key_basis: float) -> float:
    return p_key_basis**2 + (1 - p_key_basis) ** 2
