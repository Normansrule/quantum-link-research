"""Key delivery to authorized external systems: accepted key only, each key used once, by identifier.

Interface
---------
Modelled on the three calls of the ETSI GS QKD 014 key-delivery interface [etsi2019qkd014]: `status`, `get_key`
(the initiating application at one site receives keys and their identifiers), and `get_key_with_ids` (the peer
application at the other site retrieves the same keys by identifier). A site holds one store per peer site, so adding
Site C creates new stores without touching the A-B pair (SN-13).

One-time ownership (audit S03). Only sessions the protocol accepted deposit key material, and every transition is
irreversible:
  - a deposit names the reproducible experiment identifier (the run id derived from the configuration) and a unique
    execution identifier for this acquisition; key identifiers are derived from both, and an execution can deposit
    only once;
  - the SHA-256 digest of every key ever deposited is remembered (the material itself is not), so identical material
    is refused whether it is still stored or was already handed out: renaming identical material is not a new key;
  - a handed-out identifier is tombstoned and can never be issued again;
  - requests are validated (positive integer counts, string identifiers, no duplicates) and atomic: either every key
    requested is delivered or nothing changes, including the counters; one lock serializes deposits and deliveries,
    so concurrent callers can never receive the same key.
Keys at rest in this simulation are ordinary Python bytes: protecting them (memory protection, zeroization, hardware
security modules) is a deployment concern recorded in systems/see510/09_limitations_and_hardware.md.
"""
from __future__ import annotations

import hashlib
import threading
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field

import numpy as np


class KeyUnavailable(RuntimeError):
    """No accepted key is available (or the identifier is unknown or already used): fail closed."""


class Unauthorized(RuntimeError):
    """The calling application is not authorized for this store."""


class KeyReuse(RuntimeError):
    """A deposit would make one-time key material available again (same execution, or identical material)."""


@dataclass
class KeyStore:
    site: str
    peer: str
    key_size_bits: int = 256
    authorized: set = field(default_factory=set)
    _keys: OrderedDict = field(default_factory=OrderedDict)
    delivered: int = 0
    _consumed: set = field(default_factory=set)            # identifiers already handed out (tombstones)
    _digests: set = field(default_factory=set)             # SHA-256 of every key ever deposited
    _executions: set = field(default_factory=set)          # execution identifiers already deposited
    ledger: list = field(default_factory=list)             # (identifier, application, purpose) per delivery
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def deposit(self, session_id: str, key_bits: np.ndarray, execution_id: str) -> list[str]:
        with self._lock:
            return self._deposit(session_id, key_bits, execution_id)

    def _deposit(self, session_id: str, key_bits: np.ndarray, execution_id: str) -> list[str]:
        """Cut accepted key material into keys of key_size_bits. Identifiers derive from the experiment and execution
        identifiers, so both sites, depositing the same accepted material from the same execution, get the same ones."""
        if not isinstance(execution_id, str) or not execution_id:
            raise ValueError("a unique, non-empty execution identifier is required")
        if execution_id in self._executions:
            raise KeyReuse(f"execution {execution_id} already deposited at site {self.site}")
        bits = np.asarray(key_bits)
        if bits.ndim != 1 or (bits.size and not np.isin(bits, (0, 1)).all()):
            raise ValueError("key material must be a one-dimensional array of bits")
        bits = bits.astype(np.uint8)
        chunks = [np.packbits(bits[i * self.key_size_bits:(i + 1) * self.key_size_bits]).tobytes() for i in range(len(bits) // self.key_size_bits)]
        digests = [hashlib.sha256(c).digest() for c in chunks]
        if len(set(digests)) != len(digests) or any(d in self._digests for d in digests):
            raise KeyReuse(f"identical key material was already deposited at site {self.site}")
        ids = []
        for i, (chunk, d) in enumerate(zip(chunks, digests)):
            kid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"qll-link/{session_id}/{execution_id}/{i}"))
            self._keys[kid] = chunk
            self._digests.add(d)
            ids.append(kid)
        self._executions.add(execution_id)
        return ids

    def _check(self, app: str) -> None:
        if app not in self.authorized:
            raise Unauthorized(f"application '{app}' is not authorized at site {self.site}")

    def status(self) -> dict:
        return {"site": self.site, "peer": self.peer, "key_size_bits": self.key_size_bits,
                "stored_key_count": len(self._keys), "delivered": self.delivered, "consumed_ids": len(self._consumed)}

    def _deliver(self, app: str, ids: list[str], purpose: str) -> list[tuple[str, bytes]]:
        out = [(k, self._keys.pop(k)) for k in ids]                # all checks passed: commit
        self._consumed.update(ids)
        self.delivered += len(ids)
        self.ledger.extend((k, app, purpose) for k in ids)
        return out

    def get_key(self, app: str, number: int = 1, purpose: str = "") -> list[tuple[str, bytes]]:
        with self._lock:
            return self._get_key(app, number, purpose)

    def _get_key(self, app: str, number: int, purpose: str) -> list[tuple[str, bytes]]:
        self._check(app)
        if isinstance(number, bool) or not isinstance(number, (int, np.integer)) or number < 1:
            raise ValueError(f"number must be a positive integer, got {number!r}")
        if number > len(self._keys):
            raise KeyUnavailable(f"{number} keys requested, {len(self._keys)} available at site {self.site}")
        return self._deliver(app, list(self._keys)[:number], purpose)

    def get_key_with_ids(self, app: str, ids: list[str], purpose: str = "") -> list[tuple[str, bytes]]:
        with self._lock:
            return self._get_key_with_ids(app, ids, purpose)

    def _get_key_with_ids(self, app: str, ids: list[str], purpose: str) -> list[tuple[str, bytes]]:
        self._check(app)
        if not isinstance(ids, (list, tuple)) or not ids or not all(isinstance(k, str) for k in ids):
            raise ValueError("ids must be a non-empty list of key identifiers")
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate key identifiers in one request")
        missing = [k for k in ids if k not in self._keys]
        if missing:
            raise KeyUnavailable(f"unknown or already used key identifiers at site {self.site}: {missing}")
        return self._deliver(app, list(ids), purpose)


@dataclass
class SiteKeyManager:
    """All of one site's stores, one per peer site."""
    site: str
    stores: dict = field(default_factory=dict)

    def store_for(self, peer: str, key_size_bits: int = 256) -> KeyStore:
        if peer not in self.stores:
            self.stores[peer] = KeyStore(self.site, peer, key_size_bits)
        return self.stores[peer]
