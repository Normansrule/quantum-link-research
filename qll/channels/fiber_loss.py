"""Exponential attenuation of light in optical fiber.

Physics
-------
Power transmittance over length L (km) at attenuation alpha (dB/km) is
eta = 10**(-alpha*L/10). The attenuation length L_att = 10/(alpha*ln10) is the distance over
which eta falls to 1/e; at 0.2 dB/km (telecom C-band) it is about 21.7 km [pirandola2017].
"""
from __future__ import annotations

import math

ALPHA_TELECOM_DB_PER_KM: float = 0.2  # 1550 nm, standard single-mode fiber [pirandola2017]


def transmittance(L_km: float, alpha_db_per_km: float = ALPHA_TELECOM_DB_PER_KM) -> float:
    """Power transmittance 10**(-alpha*L/10) [pirandola2017]."""
    if L_km < 0.0 or alpha_db_per_km < 0.0:
        raise ValueError("length and attenuation must be non-negative")
    return 10.0 ** (-alpha_db_per_km * L_km / 10.0)


def attenuation_length_km(alpha_db_per_km: float = ALPHA_TELECOM_DB_PER_KM) -> float:
    """1/e length 10/(alpha*ln 10) in km [pirandola2017]."""
    return 10.0 / (alpha_db_per_km * math.log(10.0))
