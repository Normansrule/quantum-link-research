"""The Earth-Mars key ledger: a synodic period of daily secret key from the link budget, and the key bank that lets
the messenger spend it evenly.

Method
------
The daily key s_t is the budget's BBM92 key per day [mars_budget.py], evaluated on each day of one synodic period
(780 days, [ephemeris.py]); it is periodic to within the ephemeris's slow drift. The bank that carries a constant daily
demand d without refusal is the sequent-peak capacity of (s_t, d) [key_bank.py] [loucks2017]. Two ways to spend it are
compared: a one-time pad, one key bit per message bit [vernam1926] [shannon1949], and hybrid session keys of 256 bits.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.app.key_bank import AES_KEY_BITS, max_demand_for_capacity, sequent_peak, simulate, sustainable_demand
from qll.space.ephemeris import SYNODIC_PERIOD_DAYS
from qll.systems.mars_budget import MarsLinkDesign, budget

CYCLE_DAYS = int(round(SYNODIC_PERIOD_DAYS))


def daily_key_bits(d: MarsLinkDesign, t0_days: float = 0.0, days: int = CYCLE_DAYS) -> np.ndarray:
    """BBM92 key bits made on each day of `days` days starting at t0_days after J2000."""
    return np.array([budget(d, t0_days + i).key_bits_per_day for i in range(days)])


def longest_gap_days(key: np.ndarray) -> int:
    """Longest run of days without key, counted around the end of the record (the record is periodic)."""
    z = np.concatenate([key, key]) <= 0
    best = run = 0
    for v in z:
        run = run + 1 if v else 0
        best = max(best, run)
    return min(best, len(key))


@dataclass(frozen=True)
class Ledger:
    key_bits: np.ndarray            # per day over one synodic period
    demand_bits_per_day: float
    capacity_bits: float            # sequent-peak bank for that demand
    refused_days_without_bank: int  # days on which the day's own key falls short of the demand

    @property
    def sustainable_bits_per_day(self) -> float:
        return sustainable_demand(self.key_bits)

    @property
    def days_with_key(self) -> int:
        return int(np.sum(self.key_bits > 0))

    @property
    def gap_days(self) -> int:
        return longest_gap_days(self.key_bits)

    @property
    def otp_bytes_per_day(self) -> float:
        return self.demand_bits_per_day / 8

    @property
    def sessions_per_day(self) -> float:
        return self.demand_bits_per_day / AES_KEY_BITS


def ledger(d: MarsLinkDesign, demand_bits_per_day: float, key_bits: np.ndarray | None = None) -> Ledger:
    """Size the key bank for a constant daily demand; raises if no bank can carry it."""
    k = daily_key_bits(d) if key_bits is None else np.asarray(key_bits, dtype=float)
    if demand_bits_per_day > sustainable_demand(k):
        raise ValueError(f"demand exceeds the mean key supply of {sustainable_demand(k):.3g} bits per day")
    K = sequent_peak(k, demand_bits_per_day)
    no_bank = simulate(k, demand_bits_per_day, 0.0, 0.0).refused_days
    return Ledger(k, float(demand_bits_per_day), K, no_bank)


def demand_for_capacity(d: MarsLinkDesign, capacity_bits: float, key_bits: np.ndarray | None = None) -> float:
    """Largest constant daily demand a bank of capacity_bits carries through every day of the period."""
    k = daily_key_bits(d) if key_bits is None else np.asarray(key_bits, dtype=float)
    return max_demand_for_capacity(k, capacity_bits)
