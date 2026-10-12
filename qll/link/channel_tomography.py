"""Process tomography of the two-room channel with the P10 bench plus two quarter-wave plates (protocol P14), and
the certificate that the channel is quantum.

Data
----
Each click is one row `input, basis, outcome`: the polarization Alice sent (H, V, D, A, R, L, as the Bloch
vectors +z, -z, +x, -x, +y, -y), the basis Bob's arm measured (Z, X, or Y with the quarter-wave plate flipped into
the X arm), and the outcome (0 for the + eigenstate). A count pair (n0, n1) estimates <sigma_b> = (n0 - n1)/n.

Estimation
----------
The output Bloch component b of input s is t_b + sum_j T_bj s_j, so each b is an ordinary least-squares fit of four
numbers to the inputs measured in that basis; four inputs that span the sphere (for example H, V, D, R) and all
three bases determine the affine map, hence the Pauli transfer matrix (qll/circuits/qubit_channel.py) [chuang1997]
[nielsen2010]. Linear inversion can leave a slightly unphysical estimate at finite counts; `is_physical` reports it.

Certificate
-----------
F_e >= 1 - e_z - e_x holds for every qubit channel, with e_z and e_x the error rates averaged over H, V in Z and
over D, A in X. Each of the four per-state error rates gets a one-sided Clopper-Pearson upper limit at level
alpha/4 [clopper1934], so with probability at least 1 - alpha
    F_e >= 1 - (u_H + u_V)/2 - (u_D + u_A)/2,
and a value above 1/2 rules out every entanglement-breaking (measure-and-resend) channel [horodecki2003eb].
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy import stats

from qll.circuits import qubit_channel as Q

INPUTS = {"H": (0, 0, 1), "V": (0, 0, -1), "D": (1, 0, 0), "A": (-1, 0, 0), "R": (0, 1, 0), "L": (0, -1, 0)}
BASES = {"X": 0, "Y": 1, "Z": 2}
ERROR_OUTCOME = {("H", "Z"): 1, ("V", "Z"): 0, ("D", "X"): 1, ("A", "X"): 0}


def probabilities(R: np.ndarray, state: str, basis: str) -> float:
    """P(outcome 0) for an input state measured in a basis, through the channel R."""
    r = R @ np.array([1.0, *INPUTS[state]])
    return 0.5 * (1 + r[1 + BASES[basis]])


def simulate_counts(R: np.ndarray, shots: int, inputs=("H", "V", "D", "A", "R"), bases=("X", "Y", "Z"), seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    out = {}
    for s in inputs:
        for b in bases:
            n0 = int(rng.binomial(shots, min(1.0, max(0.0, probabilities(R, s, b)))))
            out[(s, b)] = (n0, shots - n0)
    return out


def estimate(counts: dict) -> np.ndarray:
    """Least-squares Pauli transfer matrix from counts {(input, basis): (n0, n1)}."""
    R = np.zeros((4, 4))
    R[0, 0] = 1.0
    for b, k in BASES.items():
        rows = [(s, n0, n1) for (s, bb), (n0, n1) in counts.items() if bb == b and n0 + n1 > 0]
        if len(rows) < 4:
            raise ValueError(f"basis {b}: need at least four inputs that span the sphere")
        A = np.array([[1.0, *INPUTS[s]] for s, _, _ in rows])
        y = np.array([(n0 - n1) / (n0 + n1) for _, n0, n1 in rows])
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        if np.linalg.matrix_rank(A) < 4:
            raise ValueError(f"basis {b}: the inputs do not span the sphere")
        R[1 + k, 0], R[1 + k, 1:] = coef[0], coef[1:]
    return R


def _upper(k: int, n: int, alpha: float) -> float:
    return 1.0 if k == n else float(stats.beta.ppf(1 - alpha, k + 1, n - k))


ASSUMPTIONS = (
    "trusted qubit model: the source prepares the named polarization qubits and the analyzer measures in the named bases",
    "counts are conditional on a click; no-click and double-click events are excluded by the selection rule",
    "fair sampling: which pulses click does not depend on the input state (state-independent loss)",
    "single-photon (qubit) signals; a weak-coherent or bright-light source needs the decoy bound or is only an analogue",
    "Clopper-Pearson intervals at alpha/4 per input, assuming independent trials",
)


def certify(counts: dict, alpha: float = 0.01) -> dict:
    """The entanglement-fidelity lower bound from the H, V (Z) and D, A (X) error counts. This is a witness WITHIN the
    trusted qubit-channel model listed in ASSUMPTIONS (audit P04), returned with the result; it is not device-
    independent certification, a capacity, or a secure key. Missing or empty input classes raise ValueError."""
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0, 1)")
    up, rate = {}, {}
    for (s, b), err in ERROR_OUTCOME.items():
        if (s, b) not in counts:
            raise ValueError(f"insufficient data: no counts for input {s} in basis {b}")
        n0, n1 = counts[(s, b)]
        if min(n0, n1) < 0 or n0 + n1 == 0:
            raise ValueError(f"insufficient data: {n0 + n1} counts for input {s} in basis {b}")
        k, n = (n1 if err == 1 else n0), n0 + n1
        up[s], rate[s] = _upper(k, n, alpha / 4), k / n
    e_z, e_x = (rate["H"] + rate["V"]) / 2, (rate["D"] + rate["A"]) / 2
    ez_u, ex_u = (up["H"] + up["V"]) / 2, (up["D"] + up["A"]) / 2
    bound = Q.certified_entanglement_fidelity(ez_u, ex_u)
    return {"e_z": e_z, "e_x": e_x, "e_z_upper": ez_u, "e_x_upper": ex_u, "fe_estimate": 1 - e_z - e_x,
            "fe_lower": bound, "certified_quantum": bound > 0.5, "confidence": 1 - alpha,
            "scope": "witness within a trusted qubit-channel model", "assumptions": list(ASSUMPTIONS),
            "trials": {f"{s}{b}": sum(counts[(s, b)]) for (s, b) in ERROR_OUTCOME}}


def write_log(path: Path, counts: dict, seed: int = 0) -> Path:
    """One row per click, in a shuffled order, as room B would record them."""
    rows = [(s, b, o) for (s, b), (n0, n1) in counts.items() for o, n in ((0, n0), (1, n1)) for _ in range(n)]
    np.random.default_rng(seed).shuffle(rows)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["input", "basis", "outcome"])
        w.writerows(rows)
    return Path(path)


def read_log(path: Path) -> dict:
    counts: dict = {}
    with open(path, newline="", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        if r.fieldnames != ["input", "basis", "outcome"]:
            raise ValueError("a tomography log has the columns input, basis, outcome")
        for row in r:
            s, b, o = row["input"], row["basis"], int(row["outcome"])
            if s not in INPUTS or b not in BASES or o not in (0, 1):
                raise ValueError(f"bad row {row}")
            n0, n1 = counts.get((s, b), (0, 0))
            counts[(s, b)] = (n0 + (o == 0), n1 + (o == 1))
    return counts
