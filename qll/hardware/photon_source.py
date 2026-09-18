"""Photon-number statistics of the sources a link can use.

Physics
-------
SPDC (two-mode squeezed vacuum): P(n pairs) = (1 - x) x^n with x = tanh^2(r); pair probability per
pulse p ~ x for small x; heralded g2(0) ~ 2 p (multi-pair contamination) [kwiat1995] [burnham1970].
Weak coherent pulse: Poisson P(n) = e^-mu mu^n / n!, g2(0) = 1; multiphoton fraction gives the
photon-number-splitting vulnerability that decoy states fix [lo2005].
Single emitter (NV, quantum dot): ideal g2(0) = 0; herald probability per attempt for two-photon
schemes p ~ (eta_zpl eta_coll eta_det)^2 / 2 [barrett2005].
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SpdcSource:
    pair_probability: float           # x = tanh^2 r, per pulse or per coherence time
    rep_rate_hz: float = 80e6
    heralding_efficiency: float = 0.5

    def p_n_pairs(self, n: int) -> float:
        x = self.pair_probability
        return (1 - x) * x**n

    def heralded_g2(self, n_max: int = 60) -> float:
        """Heralded g2(0) with an ideal (non-number-resolving, unit-efficiency) herald: the signal is the
        thermal distribution conditioned on n >= 1; computed numerically, ~2x for small x."""
        x = self.pair_probability
        if x <= 0:
            return 0.0
        ps = [(1 - x) * x**n for n in range(1, n_max)]
        z = sum(ps)
        mean = sum(n * p for n, p in zip(range(1, n_max), ps)) / z
        mean2 = sum(n * (n - 1) * p for n, p in zip(range(1, n_max), ps)) / z
        return mean2 / mean**2

    def pair_rate_hz(self) -> float:
        return self.rep_rate_hz * self.pair_probability


@dataclass(frozen=True)
class WeakCoherentSource:
    mu: float
    rep_rate_hz: float = 1e9

    def p_n(self, n: int) -> float:
        return math.exp(-self.mu) * self.mu**n / math.factorial(n)

    def multiphoton_fraction(self) -> float:
        """Fraction of non-empty pulses that carry more than one photon (PNS-attackable)."""
        p0, p1 = self.p_n(0), self.p_n(1)
        return (1 - p0 - p1) / (1 - p0)

    g2 = 1.0


@dataclass(frozen=True)
class SingleEmitterSource:
    zpl_fraction: float = 0.03
    collection_efficiency: float = 0.1
    detector_efficiency: float = 0.7
    attempt_rate_hz: float = 1e5
    g2 = 0.0

    def photon_efficiency(self) -> float:
        return self.zpl_fraction * self.collection_efficiency * self.detector_efficiency

    def herald_probability_two_photon(self) -> float:
        return 0.5 * self.photon_efficiency() ** 2

    def herald_probability_single_photon(self, alpha: float = 0.1) -> float:
        """Single-click schemes scale linearly with efficiency at the cost of a bright-state fraction alpha."""
        return 2 * alpha * self.photon_efficiency()

    def seconds_per_pair(self, scheme: str = "two_photon") -> float:
        p = self.herald_probability_two_photon() if scheme == "two_photon" else self.herald_probability_single_photon()
        return 1.0 / (p * self.attempt_rate_hz)
