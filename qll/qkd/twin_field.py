"""Single-photon interference at a midpoint gives a rate scaling as sqrt(eta), beating PLOB.

Physics
-------
Alice and Bob send phase-locked weak coherent pulses to Charlie; a single click heralds a key bit whose
value depends on the relative phase. The gain is ~ 2 mu sqrt(eta) (one photon from either side) instead of
mu eta, so R ~ sqrt(eta) [lucamarini2018]; the repeaterless bound -log2(1 - eta) ~ 1.44 eta is beaten beyond
a crossover of a few hundred km of fiber. Demonstrated over 830 km (2022) and 1000 km (2023) [wang2022tf]
[liu2023tf]. Model: R = sqrt(eta) * mu * c_tf with c_tf the protocol prefactor (order 0.1) [lucamarini2018].
"""
from __future__ import annotations

import math


def twin_field_rate_per_pulse(eta_total: float, mu: float = 0.1, prefactor: float = 0.1) -> float:
    return prefactor * mu * math.sqrt(eta_total)


def crossover_transmittance(mu: float = 0.1, prefactor: float = 0.1) -> float:
    """Transmittance below which the TF rate exceeds the PLOB bound 1.44 eta (small-eta form)."""
    return (prefactor * mu / (1 / math.log(2))) ** 2
