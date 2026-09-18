"""A correlation that no local hidden-variable model can push above 2.

Physics
-------
S = |E(a,b) - E(a,b') + E(a',b) + E(a',b')| <= 2 locally [bell1964] [clauser1969]; quantum maximum
2 sqrt 2 (Tsirelson) [cirelson1980] at settings a=0, a'=pi/2, b=pi/4, b'=3pi/4 (spin angles) for |Phi+>.
For a Werner state of fully entangled fraction f: S = 2 sqrt 2 (4f - 1)/3. Settings are drawn from a
declared EntropySource (INV-7).
"""
from __future__ import annotations

import math

import numpy as np

from qll.hardware.randomness import EntropySource, NumpyPRNG

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
OPTIMAL = {"a": 0.0, "a2": math.pi / 2, "b": math.pi / 4, "b2": 3 * math.pi / 4}


def _obs(theta: float) -> np.ndarray:
    return math.cos(theta) * _Z + math.sin(theta) * _X


def correlation(rho: np.ndarray, ta: float, tb: float) -> float:
    return float(np.real(np.trace(rho @ np.kron(_obs(ta), _obs(tb)))))


def chsh_value(rho: np.ndarray, settings: dict[str, float] = OPTIMAL) -> float:
    a, a2, b, b2 = settings["a"], settings["a2"], settings["b"], settings["b2"]
    return abs(correlation(rho, a, b) - correlation(rho, a, b2) + correlation(rho, a2, b) + correlation(rho, a2, b2))


def chsh_werner_analytic(f: float) -> float:
    return 2 * math.sqrt(2) * (4 * f - 1) / 3


def chsh_sampled_stim(n_rounds: int, entropy: EntropySource | None = None, allow_pseudo: bool = False, seed: int = 0) -> tuple[float, float]:
    """Sample a CHSH experiment on |Phi+> in Stim with settings drawn from ``entropy``.

    Returns (S, standard error). Measurement angles that are multiples of pi/4 are not Clifford, so
    each round rotates the pair by an exact single-qubit rotation via a tableau on the state vector
    instead: we use Stim for the Bell-state preparation and readout in rotated bases implemented as
    S/H sequences for the 0, pi/2 settings and analytic post-processing for pi/4 settings is not
    possible; therefore this sampler uses Stim's TableauSimulator to prepare and NumPy for the
    non-Clifford measurement statistics. Rounds are still independent Bernoulli draws with the
    exact quantum probabilities.
    """
    if entropy is None:
        entropy = NumpyPRNG(seed)
    if not entropy.quantum and not allow_pseudo:
        raise ValueError("settings must come from a quantum EntropySource (pass allow_pseudo=True to override)")
    import stim

    sim = stim.TableauSimulator(seed=seed)
    sim.h(0); sim.cx(0, 1)
    vec = sim.state_vector()
    rho = np.outer(vec, vec.conj())
    sa, sb = entropy.bits(n_rounds), entropy.bits(n_rounds)
    rng = np.random.default_rng(seed)
    sums = {k: [] for k in ((0, 0), (0, 1), (1, 0), (1, 1))}
    for r in range(n_rounds):
        ta = OPTIMAL["a2"] if sa[r] else OPTIMAL["a"]
        tb = OPTIMAL["b2"] if sb[r] else OPTIMAL["b"]
        e = correlation(rho, ta, tb)
        outcome = 1 if rng.random() < (1 + e) / 2 else -1
        sums[(int(sa[r]), int(sb[r]))].append(outcome)
    E = {k: (np.mean(v) if v else 0.0) for k, v in sums.items()}
    S = abs(E[(0, 0)] - E[(0, 1)] + E[(1, 0)] + E[(1, 1)])
    err = math.sqrt(sum((1 - E[k] ** 2) / max(1, len(sums[k])) for k in sums))
    return float(S), float(err)
