"""Atomic-frequency-comb (AFC) quantum memory: efficiency, storage time, and multimode capacity.

Physics
-------
An inhomogeneously broadened ensemble (rare-earth ions in a crystal) is spectrally tailored into a comb of teeth
with spacing Delta and finesse F = Delta / gamma (gamma the tooth width). An absorbed photon is re-emitted as an echo
after 1/Delta; with a spin-wave transfer the storage becomes on-demand and is limited by the spin coherence time.
Forward-recall efficiency for optical depth d and comb finesse F (square teeth) [afzelius2009]:
    eta_AFC = (d/F)^2 exp(-d/F) exp(-7/F^2) exp(-d0),
maximised at d/F = 2 to 54 % (forward) and reaching 100 % only with backward recall or a cavity [afzelius2010].
The number of temporal modes stored is ~ F/2 (the ratio of storage time 1/Delta to pulse duration ~1/(F Delta)),
which is why AFC memories multiplex: Sinclair et al. stored 26 spectral x many temporal modes [sinclair2014].
Storage time: 1/Delta for the optical echo (up to ~ 1 ms), the spin-wave lifetime for on-demand storage (seconds
in Eu:YSO, hours for the nuclear-spin coherence itself [zhong2015]; retrieval efficiency at those times is < 5 %).
"""
from __future__ import annotations

import math
from dataclasses import dataclass


def afc_efficiency_forward(d: float, F: float, d0: float = 0.0) -> float:
    """Forward-recall efficiency of an AFC with optical depth d, finesse F, background absorption d0 [afzelius2009]."""
    if F <= 0 or d < 0:
        raise ValueError("finesse must be positive and optical depth non-negative")
    return (d / F) ** 2 * math.exp(-d / F) * math.exp(-7 / F**2) * math.exp(-d0)


def afc_efficiency_backward(d: float, F: float, d0: float = 0.0) -> float:
    """Backward recall (phase-matched by counter-propagating control pulses): eta = (1 - exp(-d/F))^2 exp(-7/F^2) exp(-d0)."""
    return (1 - math.exp(-d / F)) ** 2 * math.exp(-7 / F**2) * math.exp(-d0)


def optimal_optical_depth_forward(F: float) -> float:
    return 2 * F


def temporal_modes(F: float) -> float:
    """Approximate number of temporal modes ~ F/2 [afzelius2009]."""
    return F / 2


@dataclass(frozen=True)
class AfcMemory:
    optical_depth: float
    finesse: float
    tooth_spacing_hz: float
    spin_coherence_s: float
    background_depth: float = 0.0

    @property
    def echo_time_s(self) -> float:
        return 1.0 / self.tooth_spacing_hz

    def efficiency(self, backward: bool = False) -> float:
        f = afc_efficiency_backward if backward else afc_efficiency_forward
        return f(self.optical_depth, self.finesse, self.background_depth)

    def modes(self) -> float:
        return temporal_modes(self.finesse)
