"""Classical information takes at least d/c. This module is the ONLY permitted source of
classical latency in the repository.

Physics
-------
The no-communication theorem forbids using entanglement alone to signal [ghirardi1980]
[peres2004]; every teleportation, swap herald, and key-reconciliation message therefore
arrives no earlier than d/c after it is sent. Earth-Mars one-way delays span about 3 to 22
minutes.
"""
from __future__ import annotations

from dataclasses import dataclass

from qll.constants.physical import C_LIGHT


def one_way_delay_s(distance_m: float) -> float:
    """d/c in seconds."""
    if distance_m < 0.0:
        raise ValueError("distance must be non-negative")
    return distance_m / C_LIGHT


def round_trip_delay_s(distance_m: float) -> float:
    """2d/c in seconds."""
    return 2.0 * one_way_delay_s(distance_m)


class NotYetArrived(RuntimeError):
    """Raised when a classical message is read before its light-time arrival."""


@dataclass(frozen=True)
class ClassicalMessage:
    """A classical message with a physically enforced earliest arrival time."""

    payload: tuple[int, ...]
    sent_at_s: float
    distance_m: float

    @property
    def earliest_arrival_s(self) -> float:
        return self.sent_at_s + one_way_delay_s(self.distance_m)

    def receive(self, now_s: float) -> tuple[int, ...]:
        if now_s < self.earliest_arrival_s:
            raise NotYetArrived(
                f"message arrives at t={self.earliest_arrival_s:.3f} s; now is {now_s:.3f} s"
            )
        return self.payload
