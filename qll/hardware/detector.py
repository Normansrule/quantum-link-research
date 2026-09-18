"""A single-photon detector is an efficiency, a dark-count rate, a dead time, and a jitter.

Physics
-------
Click probability for n incident photons: 1 - (1 - eta)^n, plus dark counts p_d = 1 - exp(-N_d tau)
in a gate tau [hadfield2009] [eisaman2011]. Representative parameters (2020s): Si SPAD (Excelitas
SPCM-AQRH) eta ~0.7 at 650-810 nm, N_d ~ 25-250 /s, dead time ~22 ns, jitter ~350 ps; InGaAs SPAD
eta ~0.2-0.3 at 1550 nm, N_d ~ 1e3 /s gated; SNSPD eta > 0.9, N_d < 10 /s, jitter < 50 ps at 1-4 K.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Detector:
    efficiency: float
    dark_rate_hz: float
    dead_time_s: float
    jitter_s: float
    name: str = "detector"

    def p_click(self, n_photons: int, gate_s: float) -> float:
        p_sig = 1 - (1 - self.efficiency) ** n_photons
        p_dark = 1 - math.exp(-self.dark_rate_hz * gate_s)
        return 1 - (1 - p_sig) * (1 - p_dark)

    def max_count_rate_hz(self) -> float:
        return 1.0 / self.dead_time_s


SI_SPAD = Detector(0.70, 100.0, 22e-9, 350e-12, "Si SPAD (SPCM-AQRH class)")
INGAAS_SPAD = Detector(0.25, 1e3, 1e-6, 200e-12, "InGaAs SPAD, gated")
SNSPD = Detector(0.93, 5.0, 40e-9, 30e-12, "SNSPD at 1-4 K")
