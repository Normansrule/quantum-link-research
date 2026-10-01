"""Compact, exact encoding of bit arrays inside classical messages (packed bits in base64)."""
from __future__ import annotations

import base64

import numpy as np


def pack(bits: np.ndarray) -> dict:
    a = np.asarray(bits, dtype=np.uint8)
    return {"n": int(len(a)), "b64": base64.b64encode(np.packbits(a).tobytes()).decode()}


def unpack(d: dict) -> np.ndarray:
    raw = np.frombuffer(base64.b64decode(d["b64"]), dtype=np.uint8)
    return np.unpackbits(raw)[: d["n"]].astype(np.int8)


def pack_indices(idx: np.ndarray) -> dict:
    return {"b64": base64.b64encode(np.asarray(idx, dtype=np.uint32).tobytes()).decode()}


def unpack_indices(d: dict) -> np.ndarray:
    return np.frombuffer(base64.b64decode(d["b64"]), dtype=np.uint32).astype(np.int64)
