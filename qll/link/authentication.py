"""Information-theoretically secure authentication of the classical channel: Wegman-Carter tags from a key pool.

Method
------
A tag is t = (h_k(M) + r) mod p with p = 2^127 - 1. The hash h_k evaluates the message, cut into 15-byte blocks
m_1..m_L and prefixed with its length, as a polynomial at the secret point k:
    h_k(M) = (m_0 k^(L+1) + m_1 k^L + ... + m_L k) mod p,
which is epsilon-almost-delta-universal with epsilon <= (L + 1)/p [stinson1994]. The pad r is fresh one-time key, so
the scheme is the Wegman-Carter construction: an adversary who sees any number of tags, each with its own pad, forges
a new one with probability at most epsilon, whatever her computing power [wegman1981]. The hash key k may be reused
across messages; every tag consumes one pad.

Cascade exchanges hundreds of messages per session, so tagging each would spend more key than a long link makes.
Instead each site tags the whole transcript as it saw it (every message sent and received, in order) at the end of
the session, and the other site checks it against its own view, before any key is accepted ("authenticate before
use"). Only a session that would otherwise be accepted is authenticated, so a rejected session spends nothing and an
adversary cannot drain the pool by forcing rejections. Two pads per session, plus a hash key, are drawn from a pool
that starts with pre-shared key and is topped back up from each accepted session's output, so QKD acts as key growth:
a session is only worth running if it returns more key than it spent.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

P127 = (1 << 127) - 1
BLOCK = 15                                     # bytes per block, so every block value is below p
TAG_BITS = 127


def poly_hash(key: int, message: bytes) -> int:
    """h_k(M) over GF(2^127 - 1), length-prefixed so that messages of different lengths never collide trivially."""
    if not 0 < key < P127:
        raise ValueError("hash key must lie in (0, p)")
    acc = len(message) % P127
    for i in range(0, len(message), BLOCK):
        acc = (acc * key + int.from_bytes(message[i:i + BLOCK], "big") + 1) % P127      # +1 keeps zero blocks distinct
    return (acc * key) % P127


def tag(key: int, pad: int, message: bytes) -> int:
    return (poly_hash(key, message) + pad) % P127


def forgery_bound(message_len_bytes: int) -> float:
    """Probability that any substituted message passes: (L + 1) / p."""
    return (message_len_bytes // BLOCK + 2) / P127


@dataclass
class AuthKeyPool:
    """Shared authentication key held identically at both sites: a reusable hash key and one-time pads."""
    bits: int                                  # pad material available, in bits
    seed: bytes                                # stand-in for the pre-shared and replenished key material
    hash_key_bits_per_session: int = TAG_BITS  # conservative: charge a fresh hash key every session
    consumed: int = 0
    _counter: int = 0

    def _draw(self) -> int:
        self._counter += 1
        v = int.from_bytes(hashlib.sha256(self.seed + self._counter.to_bytes(8, "big")).digest()[:16], "big") % P127
        return v or 1

    def take(self, n_bits: int) -> int:
        if n_bits > self.bits:
            raise RuntimeError(f"authentication key pool exhausted: {n_bits} bits needed, {self.bits} left")
        self.bits -= n_bits
        self.consumed += n_bits
        return self._draw()

    def session_keys(self) -> tuple[int, int, int]:
        """A hash key and the two pads one session needs."""
        k = self.take(self.hash_key_bits_per_session)
        return k, self.take(TAG_BITS), self.take(TAG_BITS)

    def refill(self, n_bits: int) -> None:
        self.bits += n_bits

    @staticmethod
    def session_cost_bits(hash_key_bits: int = TAG_BITS) -> int:
        return hash_key_bits + 2 * TAG_BITS
