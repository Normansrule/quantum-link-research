"""Site A: random bits, random bases, and the single-photon states it sends (BB84 preparation).

Model
-----
Each pulse carries one bit a in one basis s (0 = rectilinear Z, 1 = diagonal X), both uniform and independent
[bennett1984]. The simulation draws them from a seeded PCG64 generator so runs reproduce exactly; a deployed Site A
needs a certified random source (a quantum RNG, or a DRBG per NIST SP 800-90A) instead [nist2015sp800-90a].
Sources: "single_photon" (ideal: exactly one photon per pulse), "weak_coherent" (an attenuated laser: the photon
number of each pulse is Poisson with mean mu, so a fraction 1 - e^-mu (1 + mu) of pulses carry two or more photons,
which photon-number splitting can exploit [brassard2000]), and "weak_coherent_decoy" (the same laser at a signal, a
weak decoy, and a vacuum intensity chosen at random per pulse, so that the attack shows up in the statistics
[hwang2003] [lo2005]).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


SIGNAL, DECOY, VACUUM = 0, 1, 2


@dataclass(frozen=True)
class PreparedStates:
    bits: np.ndarray        # int8, 0 or 1
    bases: np.ndarray       # int8, 0 = Z, 1 = X
    photons: np.ndarray | None = None     # photons per pulse (weak-coherent sources); None means exactly one
    intensity: np.ndarray | None = None   # intensity class per pulse: 0 signal, 1 decoy, 2 vacuum


class SiteA:
    def __init__(self, rng: np.random.Generator):
        self.rng = rng

    def prepare(self, n: int, c=None) -> PreparedStates:
        bits, bases = self.rng.integers(0, 2, n, dtype=np.int8), self.rng.integers(0, 2, n, dtype=np.int8)
        if c is None or c.source_model == "single_photon":
            return PreparedStates(bits, bases)
        # an attenuated laser: Poisson photon numbers [gisin2002]; with decoys, a random intensity per pulse [hwang2003]
        if c.source_model == "weak_coherent":
            return PreparedStates(bits, bases, self.rng.poisson(c.mu_signal, n).astype(np.int64))
        cls = self.rng.choice(3, n, p=[c.p_signal, c.p_decoy, 1 - c.p_signal - c.p_decoy]).astype(np.int8)
        mean = np.array([c.mu_signal, c.mu_decoy, 0.0])[cls]
        return PreparedStates(bits, bases, self.rng.poisson(mean).astype(np.int64), cls)
