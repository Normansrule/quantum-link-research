"""A store-and-forward messenger over a light-time channel that fails closed when it runs out of key.

Design
------
Every message is encrypted under a hybrid session key (ML-KEM + QKD) and transported as a ClassicalMessage,
so it cannot be read before d/c (INV-1). Keys come from a buffer filled by the QKD/entanglement layer at a
finite rate; when the buffer is empty the messenger REFUSES to send (REQ-APP-001) rather than falling back to
an unkeyed or KEM-only channel. Acknowledgements take another light time, so the sender keeps unacknowledged
messages in flight and the key buffer must cover the round trip: buffer >= key_rate * 2d/c is the sizing rule
this module lets you test. Latency at a target fidelity is reported by benchmark.py.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from qll.app.aes_gcm_layer import KeyedChannel
from qll.app.hybrid_kem import establish, keygen
from qll.channels.light_time_delay import ClassicalMessage, NotYetArrived, one_way_delay_s


class KeyExhausted(RuntimeError):
    """Raised when a message would have to be sent without a fresh key (fail closed)."""


@dataclass
class KeyBuffer:
    """Bytes of QKD key available; refilled at key_rate_bps by the physical layer."""
    key_rate_bps: float
    capacity_bytes: int
    level_bytes: int = 0
    last_t: float = 0.0

    def advance(self, now_s: float) -> None:
        self.level_bytes = min(self.capacity_bytes, self.level_bytes + int(self.key_rate_bps * (now_s - self.last_t) / 8))
        self.last_t = now_s

    def take(self, n: int) -> bytes:
        if self.level_bytes < n:
            raise KeyExhausted(f"need {n} bytes of QKD key, have {self.level_bytes}")
        self.level_bytes -= n
        import os
        return os.urandom(n)   # stands in for the actual sifted key material


@dataclass
class Envelope:
    seq: int
    nonce: bytes
    ciphertext: bytes
    message: ClassicalMessage
    key_id: int


@dataclass
class Messenger:
    distance_m: float
    key_buffer: KeyBuffer
    qkd_bytes_per_session: int = 32
    in_flight: deque = field(default_factory=deque)
    sent: int = 0
    refused: int = 0
    _channels: dict = field(default_factory=dict)
    _ek: bytes = b""
    _dk: bytes = b""

    def __post_init__(self) -> None:
        self._ek, self._dk = keygen()

    def new_session(self, now_s: float) -> KeyedChannel:
        """Establish a hybrid key; fails closed if the QKD buffer cannot supply its share."""
        self.key_buffer.advance(now_s)
        k_qkd = self.key_buffer.take(self.qkd_bytes_per_session)      # raises KeyExhausted
        a, _ = establish(self._ek, self._dk, k_qkd, self.distance_m)
        key_id = len(self._channels)
        ch = KeyedChannel(a.session_key, key_id)
        self._channels[key_id] = ch
        return ch

    def send(self, plaintext: bytes, now_s: float, channel: KeyedChannel) -> Envelope:
        try:
            seq, nonce, ct = channel.encrypt(plaintext, aad=str(self.sent).encode())
        except RuntimeError as e:
            self.refused += 1
            raise KeyExhausted(str(e)) from e
        env = Envelope(seq, nonce, ct, ClassicalMessage(payload=(seq,), sent_at_s=now_s, distance_m=self.distance_m), channel.key_id)
        self.in_flight.append(env)
        self.sent += 1
        return env

    def receive(self, env: Envelope, now_s: float) -> bytes:
        env.message.receive(now_s)                                   # NotYetArrived before d/c
        return self._channels[env.key_id].decrypt(env.nonce, env.ciphertext, aad=str(env.seq).encode())

    def ack_arrival_s(self, env: Envelope) -> float:
        return env.message.earliest_arrival_s + one_way_delay_s(self.distance_m)


def required_buffer_bytes(key_rate_bps: float, distance_m: float, bytes_per_session: int, sessions_per_message: float = 1.0, messages_per_s: float = 1.0) -> float:
    """Sizing rule: enough key to keep sending for one round trip while acknowledgements are in flight."""
    rt = 2 * one_way_delay_s(distance_m)
    return max(0.0, bytes_per_session * sessions_per_message * messages_per_s * rt - key_rate_bps / 8 * rt)
