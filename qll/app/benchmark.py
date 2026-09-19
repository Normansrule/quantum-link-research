"""The three honest numbers: pairs (or key) per day, secret bits per day, and message latency at a target fidelity.

Method
------
Throughput can look terrestrial (pre-shared keys, pre-distributed entanglement); round-trip latency never can.
Given a key rate and a message rate, the benchmark simulates a conversation over the light-time channel and
reports: the fraction of messages sent without refusal, the mean one-way latency, the round-trip time, and the
minimum key buffer that prevents any refusal (REQ-APP-001 sizing), plus pairs and secret bits per day.
"""
from __future__ import annotations

from dataclasses import dataclass

from qll.app.messenger import KeyBuffer, KeyExhausted, Messenger
from qll.channels.light_time_delay import one_way_delay_s, round_trip_delay_s


@dataclass(frozen=True)
class BenchmarkResult:
    distance_m: float
    one_way_s: float
    round_trip_s: float
    messages_attempted: int
    messages_sent: int
    refusals: int
    key_bits_per_day: float
    pairs_per_day: float


def run_conversation(distance_m: float, key_rate_bps: float, buffer_bytes: int, messages: int, interval_s: float,
                     bytes_per_session: int = 32, pairs_per_s: float = 0.0, initial_fill: bool = True) -> BenchmarkResult:
    kb = KeyBuffer(key_rate_bps, buffer_bytes, level_bytes=buffer_bytes if initial_fill else 0)
    m = Messenger(distance_m, kb, bytes_per_session)
    sent = 0
    for i in range(messages):
        t = i * interval_s
        try:
            ch = m.new_session(t)
            m.send(b"hello", t, ch)
            sent += 1
        except KeyExhausted:
            pass
    return BenchmarkResult(distance_m, one_way_delay_s(distance_m), round_trip_delay_s(distance_m), messages, sent,
                           messages - sent, key_rate_bps * 86400, pairs_per_s * 86400)
