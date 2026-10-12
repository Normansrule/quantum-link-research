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

import numpy as np

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


class PoolExhausted(RuntimeError):
    """The authentication pool cannot supply the key a session needs; the session must not be accepted."""


def _check_bits(n_bits) -> int:
    if isinstance(n_bits, bool) or not isinstance(n_bits, (int, np.integer)) or n_bits <= 0:
        raise ValueError(f"bit counts must be positive integers, got {n_bits!r}")
    return int(n_bits)


@dataclass
class SimulatedAuthKeyPool:
    """SIMULATION LEDGER, NOT SECRET MATERIAL (audit S01). Hash keys and pads are drawn from SHA-256 of a seed and a
    counter, which makes sessions reproducible but derives every value from a seed anyone with the configuration can
    recompute. `refill` adds to a balance; it does not add entropy. Use it to account for key consumption in simulations;
    never as the authentication key of a real link (use SecretAuthKeyPool)."""
    bits: int                                  # pad material available, in bits (an accounting balance)
    seed: bytes                                # reproducible stand-in for pre-shared and replenished material
    hash_key_bits_per_session: int = TAG_BITS  # conservative: charge a fresh hash key every session
    consumed: int = 0
    _counter: int = 0
    simulated: bool = field(default=True, init=False)

    def _draw(self) -> int:
        self._counter += 1
        v = int.from_bytes(hashlib.sha256(self.seed + self._counter.to_bytes(8, "big")).digest()[:16], "big") % P127
        return v or 1

    def take(self, n_bits: int) -> int:
        n_bits = _check_bits(n_bits)
        if n_bits > self.bits:
            raise PoolExhausted(f"authentication key pool exhausted: {n_bits} bits needed, {self.bits} left")
        self.bits -= n_bits
        self.consumed += n_bits
        return self._draw()

    def session_keys(self) -> tuple[int, int, int]:
        """A hash key and the two pads one session needs."""
        k = self.take(self.hash_key_bits_per_session)
        return k, self.take(TAG_BITS), self.take(TAG_BITS)

    def refill(self, n_bits: int) -> None:
        """Ledger only: record that n_bits of accepted key were set aside for authentication."""
        self.bits += _check_bits(n_bits)

    def replenish(self, key_bits, provenance: str = "") -> None:
        """Same interface as SecretAuthKeyPool.replenish; in the simulation ledger only the count is recorded."""
        self.refill(len(key_bits))

    @staticmethod
    def session_cost_bits(hash_key_bits: int = TAG_BITS) -> int:
        return hash_key_bits + 2 * TAG_BITS


AuthKeyPool = SimulatedAuthKeyPool          # the name existing simulation code uses; it is the ledger, not live key


@dataclass(repr=False)
class SecretAuthKeyPool:
    """Authentication key from actual secret bytes, each consumed once (audit S01). It is filled with pre-shared key
    material and replenished only with accepted, authenticated key bytes from a session, each recorded with its
    provenance; every hash key and pad is cut from the front of the unused material, and consumed bytes are never
    handed out again. Values are 16-byte strings masked to 127 bits and reduced mod p = 2^127 - 1, a deviation from
    uniform of at most 2^-126 per value. The hash key is charged per session here, as in the simulation ledger, so no
    hash key is reused across sessions. The repr never shows material. This class enforces ownership and accounting;
    whether the material is secret depends on where it came from, which the provenance records."""
    material: bytearray = field(default_factory=bytearray)
    hash_key_bits_per_session: int = TAG_BITS
    consumed: int = 0
    provenance: list = field(default_factory=list)
    simulated: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.material, (bytes, bytearray)):
            raise TypeError("SecretAuthKeyPool needs key material as bytes")
        self.material = bytearray(self.material)
        if self.material:
            self.provenance.append(("pre-shared", len(self.material) * 8))

    def __repr__(self) -> str:
        return f"SecretAuthKeyPool(<{len(self.material) * 8} bits unused, {self.consumed} consumed>)"

    @property
    def bits(self) -> int:
        return len(self.material) * 8

    def take(self, n_bits: int) -> int:
        n_bits = _check_bits(n_bits)
        n_bytes = -(-n_bits // 8)
        if n_bytes > len(self.material):
            raise PoolExhausted(f"authentication key pool exhausted: {n_bits} bits needed, {self.bits} left")
        chunk = bytes(self.material[:n_bytes])
        del self.material[:n_bytes]                              # consumed: never handed out again
        self.consumed += n_bytes * 8
        v = (int.from_bytes(chunk, "big") & ((1 << 127) - 1)) % P127
        return v or 1

    def session_keys(self) -> tuple[int, int, int]:
        k = self.take(self.hash_key_bits_per_session)
        return k, self.take(TAG_BITS), self.take(TAG_BITS)

    def replenish(self, key_bits, provenance: str) -> None:
        """Append accepted key (an array of bits, or bytes) with where it came from; whole bytes only."""
        if not provenance:
            raise ValueError("replenishment must record its provenance (the accepted session it came from)")
        if isinstance(key_bits, (bytes, bytearray)):
            data = bytes(key_bits)
        else:
            b = np.asarray(key_bits)
            if b.ndim != 1 or (b.size and not np.isin(b, (0, 1)).all()):
                raise ValueError("key material must be a one-dimensional array of bits")
            data = np.packbits(b[: len(b) // 8 * 8].astype(np.uint8)).tobytes()
        if not data:
            raise ValueError("no whole bytes of key to add")
        self.material.extend(data)
        self.provenance.append((provenance, len(data) * 8))

    @staticmethod
    def session_cost_bits(hash_key_bits: int = TAG_BITS) -> int:
        return hash_key_bits + 2 * TAG_BITS
