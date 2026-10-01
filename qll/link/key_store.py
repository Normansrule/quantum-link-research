"""Key delivery to authorized external systems: accepted key only, each key used once, by identifier.

Interface
---------
Modelled on the three calls of the ETSI GS QKD 014 key-delivery interface [etsi2019qkd014]: `status`, `get_key`
(the initiating application at one site receives keys and their identifiers), and `get_key_with_ids` (the peer
application at the other site retrieves the same keys by identifier). A site holds one store per peer site, so adding
Site C creates new stores without touching the A-B pair (SN-13). Only sessions the protocol accepted deposit key
material; a key leaves the store when it is handed out and can never be handed out again. Keys at rest in this
simulation are ordinary Python bytes: protecting them (memory protection, zeroization, hardware security modules)
is a deployment concern recorded in systems/see510/09_limitations_and_hardware.md.
"""
from __future__ import annotations

import uuid
from collections import OrderedDict
from dataclasses import dataclass, field

import numpy as np


class KeyUnavailable(RuntimeError):
    """No accepted key is available (or the identifier is unknown or already used): fail closed."""


class Unauthorized(RuntimeError):
    """The calling application is not authorized for this store."""


@dataclass
class KeyStore:
    site: str
    peer: str
    key_size_bits: int = 256
    authorized: set = field(default_factory=set)
    _keys: OrderedDict = field(default_factory=OrderedDict)
    delivered: int = 0

    def deposit(self, session_id: str, key_bits: np.ndarray) -> list[str]:
        """Cut accepted key material into keys of key_size_bits; identifiers are derived from the session, so both
        sites, depositing the same accepted material, get the same identifiers."""
        bits = np.asarray(key_bits, dtype=np.uint8)
        ids = []
        for i in range(len(bits) // self.key_size_bits):
            kid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"qll-link/{session_id}/{i}"))
            self._keys[kid] = np.packbits(bits[i * self.key_size_bits:(i + 1) * self.key_size_bits]).tobytes()
            ids.append(kid)
        return ids

    def _check(self, app: str) -> None:
        if app not in self.authorized:
            raise Unauthorized(f"application '{app}' is not authorized at site {self.site}")

    def status(self) -> dict:
        return {"site": self.site, "peer": self.peer, "key_size_bits": self.key_size_bits,
                "stored_key_count": len(self._keys), "delivered": self.delivered}

    def get_key(self, app: str, number: int = 1) -> list[tuple[str, bytes]]:
        self._check(app)
        if number > len(self._keys):
            raise KeyUnavailable(f"{number} keys requested, {len(self._keys)} available at site {self.site}")
        out = [self._keys.popitem(last=False) for _ in range(number)]
        self.delivered += number
        return out

    def get_key_with_ids(self, app: str, ids: list[str]) -> list[tuple[str, bytes]]:
        self._check(app)
        missing = [k for k in ids if k not in self._keys]
        if missing:
            raise KeyUnavailable(f"unknown or already used key identifiers at site {self.site}: {missing}")
        self.delivered += len(ids)
        return [(k, self._keys.pop(k)) for k in ids]


@dataclass
class SiteKeyManager:
    """All of one site's stores, one per peer site."""
    site: str
    stores: dict = field(default_factory=dict)

    def store_for(self, peer: str, key_size_bits: int = 256) -> KeyStore:
        if peer not in self.stores:
            self.stores[peer] = KeyStore(self.site, peer, key_size_bits)
        return self.stores[peer]
