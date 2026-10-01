"""Site A: random bits, random bases, and the single-photon states it sends (BB84 preparation).

Model
-----
Each pulse carries one bit a in one basis s (0 = rectilinear Z, 1 = diagonal X), both uniform and independent
[bennett1984]. The simulation draws them from a seeded PCG64 generator so runs reproduce exactly; a deployed Site A
needs a certified random source (a quantum RNG, or a DRBG per NIST SP 800-90A) instead [nist2015sp800-90a]. The
source is ideal: exactly one photon per pulse, so photon-number-splitting attacks [brassard2000] are outside the model.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PreparedStates:
    bits: np.ndarray        # int8, 0 or 1
    bases: np.ndarray       # int8, 0 = Z, 1 = X


class SiteA:
    def __init__(self, rng: np.random.Generator):
        self.rng = rng

    def prepare(self, n: int) -> PreparedStates:
        return PreparedStates(self.rng.integers(0, 2, n, dtype=np.int8), self.rng.integers(0, 2, n, dtype=np.int8))
