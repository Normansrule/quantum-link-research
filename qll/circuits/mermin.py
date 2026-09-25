"""Multipartite nonlocality: the Mermin inequality for GHZ states.

Physics
-------
For three qubits, M = <XYY> + <YXY> + <YYX> - <XXX> obeys |M| <= 2 for any local model; the GHZ state
(|000> + |111>)/sqrt2 gives |M| = 4 with certainty (M = -4 for this phase convention; the +i GHZ gives +4) [mermin1990] [greenberger1990]. The n-qubit Mermin-Klyshko
inequality grows as 2^{(n-1)/2} relative to the local bound, an exponential violation, which is what makes
multipartite entanglement useful for conference key agreement and clock networks [komar2014].
"""
from __future__ import annotations

import itertools

import numpy as np

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
LOCAL_BOUND_3 = 2.0
QUANTUM_MAX_3 = 4.0


def _kron(*ops: np.ndarray) -> np.ndarray:
    out = ops[0]
    for o in ops[1:]:
        out = np.kron(out, o)
    return out


def mermin_value(state: np.ndarray) -> float:
    """M = <XYY> + <YXY> + <YYX> - <XXX> for a three-qubit pure state or density matrix."""
    s = np.asarray(state, dtype=complex)
    rho = np.outer(s, s.conj()) if s.ndim == 1 else s
    terms = [(_X, _Y, _Y), (_Y, _X, _Y), (_Y, _Y, _X)]
    val = sum(np.real(np.trace(rho @ _kron(*t))) for t in terms) - np.real(np.trace(rho @ _kron(_X, _X, _X)))
    return float(val)


def mermin_sampled_stim(n_rounds: int, seed: int = 0) -> float:
    """Sample each of the four settings on a Stim GHZ state and estimate M (all settings are Clifford here)."""
    import stim

    def run(basis: str) -> float:
        c = stim.Circuit()
        c.append("H", [0]); c.append("CX", [0, 1]); c.append("CX", [0, 2])
        for q, b in enumerate(basis):
            if b == "X":
                c.append("H", [q])
            else:                     # Y basis: S^dagger then H
                c.append("S_DAG", [q]); c.append("H", [q])
        c.append("M", [0, 1, 2])
        m = c.compile_sampler(seed=seed).sample(n_rounds)
        parity = 1 - 2 * (m.sum(axis=1) % 2)
        return float(parity.mean())

    return run("XYY") + run("YXY") + run("YYX") - run("XXX")
