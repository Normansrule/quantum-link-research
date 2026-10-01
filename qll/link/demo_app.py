"""The external secure-communication demonstration: two applications protect test messages with delivered keys.

Design
------
The application at Site A asks its key store for a key (get_key), encrypts a message with AES-256-GCM under it
[nist2007sp800-38d] using the repository's KeyedChannel (counter nonces, replay rejection), and sends the key
identifier, nonce, and ciphertext over an ordinary, unauthenticated network: GCM's tag protects integrity. The
application at Site B retrieves the same key by identifier (get_key_with_ids) and decrypts. Each key protects one
message and is then discarded. With no accepted key available the application refuses to send (fail closed), never
falling back to an unkeyed or weaker channel. Only non-sensitive test data are used. AES-256 under a QKD key is
computationally secure; the information-theoretically secure alternative, a one-time pad, would consume one key bit
per message bit (learn 03/22).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from qll.app.aes_gcm_layer import KeyedChannel
from qll.link.key_store import KeyStore, KeyUnavailable


@dataclass(frozen=True)
class Envelope:
    key_id: str
    nonce: bytes
    ciphertext: bytes


@dataclass
class DemoApp:
    name: str
    store: KeyStore
    log: list = field(default_factory=list)

    def send(self, plaintext: bytes) -> Envelope:
        try:
            (kid, key), = self.store.get_key(self.name, 1)
        except KeyUnavailable as err:
            self.log.append(("refused", str(err)))
            raise
        _, nonce, ct = KeyedChannel(key, 1).encrypt(plaintext, aad=kid.encode())
        self.log.append(("sent", kid))
        return Envelope(kid, nonce, ct)

    def receive(self, env: Envelope) -> bytes:
        (kid, key), = self.store.get_key_with_ids(self.name, [env.key_id])
        pt = KeyedChannel(key, 1).decrypt(env.nonce, env.ciphertext, aad=kid.encode())
        self.log.append(("received", kid))
        return pt
