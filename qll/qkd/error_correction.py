"""Information reconciliation: correct Bob's sifted key to Alice's while leaking as little as possible.

Physics
-------
Any reconciliation of a key with error rate Q must leak at least n h2(Q) bits (Slepian-Wolf); practical
codes leak f * n * h2(Q) with efficiency f ~ 1.05-1.2 (Cascade, interactive, ~4 rounds) or one-way LDPC
[brassard1994] [elkouss2009]. The number of rounds is a latency cost: each Cascade pass is one
round trip of ClassicalMessages, which at Mars distance is 6-45 minutes per pass. This module models
the leak and the round count; it does not implement a production decoder.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.channels.light_time_delay import ClassicalMessage, round_trip_delay_s
from qll.qkd.binary_entropy import h2


@dataclass(frozen=True)
class ReconciliationResult:
    corrected_key: np.ndarray
    leaked_bits: float
    rounds: int
    classical_time_s: float
    messages: tuple[ClassicalMessage, ...]


def reconcile(alice_key: np.ndarray, bob_key: np.ndarray, qber_estimate: float, scheme: str = "ldpc",
              efficiency: float = 1.1, distance_m: float = 0.0) -> ReconciliationResult:
    """Return Bob's key corrected to Alice's (oracle correction), with the leak and latency the scheme costs.

    scheme 'ldpc': one-way, 1 message, leak f*n*h2(Q); 'cascade': interactive, ~4 passes each a round trip.
    """
    a = np.asarray(alice_key, dtype=np.int8)
    n = len(a)
    leak = efficiency * n * h2(max(qber_estimate, 1e-12))
    if scheme == "ldpc":
        rounds = 1
        msgs = (ClassicalMessage(payload=(int(leak),), sent_at_s=0.0, distance_m=distance_m),)
        t = round_trip_delay_s(distance_m) / 2
    elif scheme == "cascade":
        rounds = 4
        msgs = tuple(ClassicalMessage(payload=(k,), sent_at_s=k * round_trip_delay_s(distance_m), distance_m=distance_m) for k in range(rounds))
        t = rounds * round_trip_delay_s(distance_m)
    else:
        raise ValueError("scheme must be 'ldpc' or 'cascade'")
    return ReconciliationResult(a.copy(), float(leak), rounds, float(t), msgs)


def minimum_leak_bits(n: int, qber: float) -> float:
    return n * h2(qber)
