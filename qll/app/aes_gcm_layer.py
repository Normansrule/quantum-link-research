"""Authenticated encryption of message bodies with AES-256-GCM.

Cryptography
------------
AES-GCM provides confidentiality and integrity with a 96-bit nonce that must never repeat under one key
[nist2007sp800-38d]. Over a 20-minute-latency link with retransmissions, nonce reuse is the realistic failure
mode, so nonces are a monotonic counter bound to the key, and a key is retired after a fixed message budget.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MESSAGE_BUDGET_PER_KEY = 2**20


@dataclass
class KeyedChannel:
    key: bytes
    key_id: int
    counter: int = 0
    retired: bool = False
    _used: set = field(default_factory=set)

    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> tuple[int, bytes, bytes]:
        if self.retired or self.counter >= MESSAGE_BUDGET_PER_KEY:
            self.retired = True
            raise RuntimeError("key retired: message budget exhausted")
        nonce = self.key_id.to_bytes(4, "big") + self.counter.to_bytes(8, "big")
        self.counter += 1
        return self.counter - 1, nonce, AESGCM(self.key).encrypt(nonce, plaintext, aad)

    def decrypt(self, nonce: bytes, ciphertext: bytes, aad: bytes = b"") -> bytes:
        if nonce in self._used:
            raise RuntimeError("replay: nonce already accepted")
        pt = AESGCM(self.key).decrypt(nonce, ciphertext, aad)   # raises InvalidTag on tampering
        self._used.add(nonce)
        return pt
