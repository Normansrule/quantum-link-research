"""A declared entropy source for every basis choice (invariant INV-7).

Physics
-------
Bell tests and QKD assume the measurement settings are unpredictable to the devices and to any
adversary (freedom of choice) [brunner2014] [bigbell2018]. A pseudo-random generator does not satisfy
this in principle, so every consumer must be handed an EntropySource object that states what it is;
protocols refuse a non-quantum source unless allow_pseudo=True. A CHSH value S certifies min-entropy
H_min >= 1 - log2(1 + sqrt(2 - S^2/4)) bits per round for the outcomes [pironio2010].
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

import numpy as np


class EntropySource(Protocol):
    quantum: bool

    def bits(self, n: int) -> np.ndarray: ...
    def min_entropy_per_bit(self) -> float: ...


@dataclass
class NumpyPRNG:
    """Pseudo-random; labelled non-quantum so protocols must opt in explicitly."""
    seed: int = 0
    quantum: bool = False

    def __post_init__(self) -> None:
        self._rng = np.random.default_rng(self.seed)

    def bits(self, n: int) -> np.ndarray:
        return self._rng.integers(0, 2, size=n, dtype=np.int8)

    def min_entropy_per_bit(self) -> float:
        return 0.0


@dataclass
class SerialQrng:
    """Bits read from a hardware QRNG (e.g. the owner's diode-noise FPGA board) over a serial port.

    Falls back to reading a file of raw bytes when ``port`` is a path, so tests can run without hardware.
    """
    port: str
    baud: int = 115200
    quantum: bool = True
    _claimed_min_entropy: float = 0.9

    def bits(self, n: int) -> np.ndarray:
        nbytes = (n + 7) // 8
        try:
            import serial  # type: ignore
            with serial.Serial(self.port, self.baud, timeout=2) as s:
                raw = s.read(nbytes)
        except Exception:
            with open(self.port, "rb") as fh:
                raw = fh.read(nbytes)
        if len(raw) < nbytes:
            raise RuntimeError("QRNG delivered too few bytes")
        return np.unpackbits(np.frombuffer(raw, dtype=np.uint8))[:n].astype(np.int8)

    def min_entropy_per_bit(self) -> float:
        return self._claimed_min_entropy


def min_entropy_from_chsh(S: float) -> float:
    """Device-independent min-entropy bound per round from a CHSH value S in (2, 2*sqrt(2)] [pironio2010]."""
    S = min(max(S, 2.0), 2 * math.sqrt(2))
    return 1 - math.log2(1 + math.sqrt(max(0.0, 2 - S**2 / 4)))


def health_check(bits: np.ndarray) -> dict[str, float]:
    """NIST SP 800-90B-style quick checks: bias and longest run [nist800-90b]."""
    b = np.asarray(bits, dtype=np.int8)
    p1 = float(b.mean())
    runs = 1 + int(np.sum(b[1:] != b[:-1]))
    longest = int(max(len(list(g)) for _, g in __import__("itertools").groupby(b.tolist())))
    return {"bias": abs(p1 - 0.5), "runs_per_bit": runs / len(b), "longest_run": longest}
