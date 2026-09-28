"""The rotated surface code under bit-flip noise with perfect syndrome measurement (the "code capacity" model), decoded
by minimum-weight perfect matching, with every shot's errors, syndrome, matching, and correction kept for display.

Physics
-------
A distance-d rotated surface code stores one logical qubit in d^2 data qubits on a square grid [fowler2012]. Its
Z-type stabilizers are the plaquettes of a checkerboard (weight 4 inside, weight 2 on the top and bottom edges), and
each detects X errors on its corners: the syndrome is s = H x (mod 2) for the X-error pattern x. Every data qubit
belongs to at most two Z plaquettes, so the syndrome defects are the ends of error strings, and the most likely
correction pairs them up (or with a boundary) by minimum total weight: minimum-weight perfect matching, here by
PyMatching [higgott2023pymatching]. After correcting, the residual x + c has no syndrome; it is either a product of stabilizers
(harmless) or the logical X, a string from the left edge to the right, which is detected by its odd overlap with the
logical Z (a column). Below the code-capacity threshold a larger code fails less; above it, more. The asymptotic
matching threshold for this noise is about 10.3 % [dennis2002] [wang2003]; with d = 9, 15, and 21 the curves here
cross near 9.7 %, the usual finite-size shift for planar codes. With measurement errors (the circuit-level model in
decoders.py) the threshold is lower; this module is the clean textbook case, and the one the QEC lab page animates.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _check_distance(d) -> int:
    if not isinstance(d, (int, np.integer)) or d < 3 or d % 2 == 0:
        raise ValueError("distance must be an odd integer >= 3")
    return int(d)


@dataclass(frozen=True)
class RotatedCode:
    d: int
    H: np.ndarray                    # Z-stabilizer x data-qubit parity-check matrix (uint8)
    plaquettes: tuple                # corners (row, col) of each Z stabilizer, for drawing
    logical_z: np.ndarray            # indicator of the data qubits in the logical Z (column 0)

    @property
    def n(self) -> int:
        return self.d**2

    def qubit(self, r: int, c: int) -> int:
        return r * self.d + c


def rotated_code(d: int) -> RotatedCode:
    """Z plaquettes of the distance-d rotated surface code: faces (a, b) with corners (a..a+1, b..b+1) and a + b even;
    interior faces are weight 4, faces beyond the top and bottom rows are weight 2."""
    d = _check_distance(d)
    rows, plaq = [], []
    for a in range(-1, d):
        for b in range(-1, d):
            if (a + b) % 2:
                continue
            interior = 0 <= a <= d - 2 and 0 <= b <= d - 2
            top_bottom = a in (-1, d - 1) and 0 <= b <= d - 2
            if not (interior or top_bottom):
                continue
            corners = [(r, c) for r in (a, a + 1) for c in (b, b + 1) if 0 <= r < d and 0 <= c < d]
            row = np.zeros(d * d, dtype=np.uint8)
            for r, c in corners:
                row[r * d + c] = 1
            rows.append(row)
            plaq.append(tuple(corners))
    lz = np.zeros(d * d, dtype=np.uint8)
    lz[[r * d for r in range(d)]] = 1
    return RotatedCode(d, np.array(rows), tuple(plaq), lz)


def _matching(code: RotatedCode):
    import pymatching

    return pymatching.Matching(code.H)


def logical_failure_rate(d: int, p: float, shots: int = 20000, seed: int = 0) -> float:
    """Fraction of shots in which matching leaves a logical X error, for independent X errors with probability p."""
    if isinstance(p, (complex, np.complexfloating)) or not 0 <= float(p) <= 1:
        raise ValueError("p must be a real probability")
    code = rotated_code(d)
    rng = np.random.default_rng(seed)
    x = (rng.random((shots, code.n)) < p).astype(np.uint8)
    syn = (x @ code.H.T) % 2
    corr = _matching(code).decode_batch(syn)
    residual = (x ^ corr.astype(np.uint8))
    return float(np.mean((residual @ code.logical_z) % 2))


def sample_shots(d: int, p: float, shots: int, seed: int = 0) -> list[dict]:
    """Shots for display: error qubits, defect plaquettes, matched defect pairs (-1 = boundary), correction qubits,
    and whether a logical error remains."""
    code = rotated_code(d)
    m = _matching(code)
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(shots):
        x = (rng.random(code.n) < p).astype(np.uint8)
        s = (code.H @ x) % 2
        c = m.decode(s).astype(np.uint8)
        pairs = m.decode_to_matched_dets_array(s).tolist() if s.any() else []
        fail = int(((x ^ c) @ code.logical_z) % 2)
        out.append({"errors": np.flatnonzero(x).tolist(), "defects": np.flatnonzero(s).tolist(), "pairs": pairs,
                    "correction": np.flatnonzero(c).tolist(), "logical_error": bool(fail)})
    return out
