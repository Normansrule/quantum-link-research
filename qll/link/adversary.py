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


class PhotonNumberSplitting:
    """Photon-number splitting on a weak-coherent source [brassard2000].

    The adversary measures each pulse's photon number without disturbing its polarization. From a pulse with two or
    more photons she keeps one in a memory and forwards the rest to Site B over her own lossless line; after the bases
    are announced she measures her photon in the right basis and knows the bit, causing no errors. Single-photon
    pulses she blocks with the probability b that makes Site B's signal gain equal an honest channel's, so loss and
    error rate look normal (if multi-photon pulses alone already exceed that gain, she also drops some of them). She
    cannot tell signal pulses from decoy pulses, which carry the same states at a different mean photon number, so the
    same strategy changes the decoy class's gain differently: that is what the decoy-state estimate detects [hwang2003].
    She is given perfect equipment: lossless line, ideal memory, knowledge of mu, the channel, and Site B's efficiency.
    """

    def __init__(self, fraction: float, rng: np.random.Generator, mu: float, honest_t: float, eta_b: float):
        if not 0.0 <= fraction <= 1.0:
            raise ValueError("fraction must lie in [0, 1]")
        self.fraction, self.rng = fraction, rng
        n = np.arange(40)
        logp = -mu + n * np.log(mu) - np.array([sum(np.log(np.arange(1, k + 1))) for k in n])
        pn = np.exp(logp)
        target = 1 - np.exp(-mu * honest_t * eta_b)                       # honest signal gain at Site B (before background)
        g1 = pn[1] * eta_b                                                # gain if every single-photon pulse is forwarded
        gm = float(np.sum(pn[2:] * (1 - (1 - eta_b) ** (n[2:] - 1))))     # gain from forwarding n - 1 photons of the rest
        if gm >= target:
            self.block_single, self.forward_multi = 1.0, target / gm
        else:
            self.block_single, self.forward_multi = min(1.0, max(0.0, 1 - (target - gm) / g1)), 1.0

    def act(self, s: PreparedStates):
        n = len(s.bits)
        attacked = self.rng.random(n) < self.fraction
        u = self.rng.random(n)
        multi = s.photons >= 2
        single = s.photons == 1
        keep_multi = attacked & multi & (u < self.forward_multi)
        photons = s.photons.copy()
        photons[attacked & single & (u < self.block_single)] = 0          # blocked
        photons[attacked & multi & ~keep_multi] = 0                       # dropped (only if multi alone exceed the gain)
        photons[keep_multi] -= 1                                          # one photon split off and stored
        out = PreparedStates(s.bits, s.bases, photons, s.intensity)
        # she learns the bit of every stored photon once the basis is announced
        rec = AdversaryRecord(self.fraction, keep_multi, s.bases.copy(), s.bits.copy(), s.bases)
        return out, rec, attacked                                         # attacked pulses bypass the fiber's loss
