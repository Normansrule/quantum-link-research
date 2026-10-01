"""A controlled, textbook adversary on the quantum channel: intercept-and-resend in a random basis.

Model
-----
On a chosen fraction f of pulses the adversary measures in a uniformly random basis and resends a fresh photon in
her basis with her result; on the rest she does nothing. Where her basis is wrong (probability 1/2) Site B's result
in the original basis is random, so she causes an error on a quarter of the sifted pulses she touched: the error rate
rises by f/4 [bennett1984] [nielsen2010]. She sits at Site A's output, before the fiber's loss, and records exactly
what she did. She is not all-powerful: no collective or coherent attacks, no detector-control attacks, and no
photon-number splitting (the source is ideal). Her presence is inferred only statistically, from the error rate; the
simulation never identifies, locates, or removes her.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.link.site_a import PreparedStates


@dataclass(frozen=True)
class AdversaryRecord:
    fraction: float
    touched: np.ndarray          # bool mask of the pulses she measured and resent
    bases: np.ndarray            # her bases on touched pulses (int8; meaningless elsewhere)
    results: np.ndarray          # her measurement results

    alice_bases: np.ndarray      # Site A's bases, to count her wrong-basis measurements

    @property
    def n_touched(self) -> int:
        return int(self.touched.sum())

    @property
    def wrong_basis(self) -> int:
        return int(np.sum(self.touched & (self.bases != self.alice_bases)))


class InterceptResend:
    def __init__(self, fraction: float, rng: np.random.Generator):
        if not 0.0 <= fraction <= 1.0:
            raise ValueError("fraction must lie in [0, 1]")
        self.fraction, self.rng = fraction, rng

    def act(self, s: PreparedStates) -> tuple[PreparedStates, AdversaryRecord]:
        n = len(s.bits)
        touched = self.rng.random(n) < self.fraction
        e_bases = self.rng.integers(0, 2, n, dtype=np.int8)
        e_bits = np.where(e_bases == s.bases, s.bits, self.rng.integers(0, 2, n, dtype=np.int8)).astype(np.int8)
        out = PreparedStates(np.where(touched, e_bits, s.bits).astype(np.int8), np.where(touched, e_bases, s.bases).astype(np.int8))
        rec = AdversaryRecord(self.fraction, touched, e_bases, e_bits, s.bases)
        return out, rec
