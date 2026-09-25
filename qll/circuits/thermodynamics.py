"""Landauer's bound and what erasing a qubit costs at a dilution refrigerator.

Physics
-------
Erasing one bit of information dissipates at least k_B T ln 2 of heat [landauer1961]; at 300 K that is 2.9e-21 J, at
10 mK 9.6e-26 J. A quantum processor resetting N qubits at rate f dissipates at least N f k_B T ln 2 into its coldest
stage, which is negligible against the microwatts available (qll.hardware.cryo_wiring); the actual reset cost is set by
the reset mechanism (measurement + feedback, or a leaky resonator), orders of magnitude above the bound. Measurement
itself is free of Landauer cost; the erasure of the record is not [bennett1982].
"""
from __future__ import annotations

import math

K_B = 1.380649e-23


def landauer_energy_j(T_kelvin: float) -> float:
    return K_B * T_kelvin * math.log(2)


def reset_power_bound_w(n_qubits: int, rate_hz: float, T_kelvin: float) -> float:
    return n_qubits * rate_hz * landauer_energy_j(T_kelvin)
