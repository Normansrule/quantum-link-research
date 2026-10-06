"""Can the way one half of an entangled pair collapses carry a message to the other half? The experiment that asks,
the statistics that answer, and the controls that show the analysis would notice a real channel.

Physics
-------
Alice and Bob share a two-qubit state rho_AB. Whatever Alice does to her half (apply a unitary, measure in any basis
without telling Bob the outcome, or do nothing) is a quantum instrument {K_k} on A with sum_k K_k^dag K_k = I.
Bob's state afterwards is

    rho_B' = Tr_A[ sum_k (K_k (x) I) rho_AB (K_k (x) I)^dag ] = Tr_A[ (sum_k K_k^dag K_k (x) I) rho_AB ] = Tr_A rho_AB,

by cyclicity of the trace over A. Every statistic Bob can collect is therefore independent of Alice's choice: the
no-signalling theorem [ghirardi1980] [nielsen2010]. The outcomes are correlated, but the correlation is visible only
when the two records are compared, which needs a classical channel no faster than light. Teleportation needs two
classical bits per qubit [bennett1993], and superdense coding needs the encoded qubit itself to travel [bennett1992].

For polarization-entangled |Phi+> with visibility V and linear analyzers at alpha (Alice) and beta (Bob) [aspect1982]:

    P(a, b) = [1 + (-1)^(a xor b) V cos 2(alpha - beta)] / 4,        P_B(b) = sum_a P(a, b) = 1/2.

The "collapse code" encodes message bit x in Alice's action (scheme "basis": measure at 0 or 45 degrees; "measure":
measure or do nothing; "flip": apply X or nothing) and lets Bob, who never hears from Alice, try to read x from his
own outcomes b. Two controls bracket it. The classical control is teleportation of |x>: with Alice's two bits Bob
reads x exactly; without them his result is x xor m with m a uniformly random bit. The leak control lets Alice's
action reach Bob's qubit physically, as crosstalk on a shared chip would: with probability `leak` Bob's qubit is reset
to |0> when x = 1. A unitary leak would not show at all, because Bob's reduced state is I/2 and every unitary
leaves I/2 unchanged; only a dissipative or readout disturbance can bias his marginal.

Statistics
----------
The data are a 2 x 2 table n[x, b]. Independence of x and b is tested with the likelihood-ratio (G) statistic,
chi-square with one degree of freedom [casella2002]. The bias delta = P(b=1|x=1) - P(b=1|x=0) is estimated with
Clopper-Pearson intervals on each conditional [clopper1934]. Because mutual information is convex in the channel for
a fixed input distribution [cover2006], its maximum over the box of plausible channels sits at a corner, so

    I_upper = max over the four corners of I(X; B), with P(x) = 1/2,

is an upper confidence bound on the information per use that Bob could extract, at the joint level 1 - alpha. The
number of uses per message value needed to detect a bias delta at significance alpha with power 1 - beta is, from the
normal approximation to the difference of two proportions near 1/2 [casella2002],

    n = (z_{1 - alpha/2} + z_{1 - beta})^2 [p0 (1 - p0) + p1 (1 - p1)] / delta^2  ~  (z_{1 - alpha/2} + z_{1 - beta})^2 / (2 delta^2).

A null result is not "nothing happened": it is a measured upper bound on the information per use, which shrinks
as 1/n. A positive result on a shared chip is a crosstalk measurement, never a faster-than-light channel.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats

SCHEMES = ("basis", "measure", "flip")
_I2 = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)


# ---------------------------------------------------------------------------------------------------- exact physics
def projectors(theta: float) -> list[np.ndarray]:
    """Linear-polarizer measurement at angle theta: pass (outcome 0) and block (outcome 1)."""
    v = np.array([np.cos(theta), np.sin(theta)], dtype=complex)
    p0 = np.outer(v, v.conj())
    return [p0, _I2 - p0]


def instrument(scheme: str, x: int) -> list[np.ndarray]:
    """Alice's Kraus operators for message bit x under a scheme; each list satisfies sum K^dag K = I."""
    if scheme not in SCHEMES:
        raise ValueError(f"scheme must be one of {SCHEMES}")
    if scheme == "basis":
        return projectors(0.0 if x == 0 else np.pi / 4)
    if scheme == "measure":
        return projectors(0.0) if x else [_I2]
    return [_X] if x else [_I2]


def bob_state_after(rho_ab: np.ndarray, kraus_a: list[np.ndarray]) -> np.ndarray:
    """Bob's reduced density matrix after Alice applies an instrument and keeps any outcome to herself."""
    rho = sum(np.kron(k, _I2) @ rho_ab @ np.kron(k, _I2).conj().T for k in kraus_a)
    return np.einsum("abac->bc", rho.reshape(2, 2, 2, 2))


def joint_probability(a: int, b: int, alpha: float, beta: float, visibility: float = 1.0) -> float:
    """P(a, b) for |Phi+> polarization pairs with analyzers at alpha and beta."""
    return 0.25 * (1.0 + (-1) ** (a ^ b) * visibility * np.cos(2.0 * (alpha - beta)))


# ---------------------------------------------------------------------------------------------- the collapse code
@dataclass
class CollapseRun:
    message: np.ndarray          # Alice's bits, one per symbol (time slot)
    x: np.ndarray                # the bit behind every pair
    symbol: np.ndarray           # the time slot of every pair
    a: np.ndarray                # Alice's outcomes (-1 where she did not measure)
    b: np.ndarray                # Bob's outcomes
    scheme: str
    leak: float


def simulate(message, shots_per_bit: int, scheme: str = "basis", visibility: float = 0.97, leak: float = 0.0,
             seed: int = 0) -> CollapseRun:
    """Monte Carlo of the collapse code with pairs from a source of the given visibility. Symbol i occupies time slot
    i and uses `shots_per_bit` pairs, as a Morse-like code would; Bob always measures at 0 degrees. A random message
    keeps slow drift from lining up with the bits."""
    if scheme not in SCHEMES:
        raise ValueError(f"scheme must be one of {SCHEMES}")
    if not 0.0 <= leak <= 1.0 or not 0.0 <= visibility <= 1.0:
        raise ValueError("leak and visibility must lie in [0, 1]")
    rng = np.random.default_rng(seed)
    message = np.asarray(message, dtype=np.int8)
    x = np.repeat(message, shots_per_bit)
    symbol = np.repeat(np.arange(message.size), shots_per_bit)
    n = x.size
    a = np.full(n, -1, dtype=np.int8)
    b = np.empty(n, dtype=np.int8)
    measured = np.ones(n, bool) if scheme == "basis" else (x == 1) if scheme == "measure" else np.zeros(n, bool)
    alpha = np.where((scheme == "basis") & (x == 1), np.pi / 4, 0.0)
    # Alice's outcome first (marginal 1/2), then Bob's conditional: P(b = a) = [1 + V cos 2(alpha - beta)] / 2
    a_out = rng.integers(0, 2, n, dtype=np.int8)
    same = rng.random(n) < 0.5 * (1.0 + visibility * np.cos(2.0 * alpha))
    b_meas = np.where(same, a_out, 1 - a_out).astype(np.int8)
    # unmeasured: Bob's Z outcome on |Phi+> (or X(x)I |Phi+>, which flips nothing in his marginal) is a fair coin
    b_free = rng.integers(0, 2, n, dtype=np.int8)
    b[:] = np.where(measured, b_meas, b_free)
    a[measured] = a_out[measured]
    if leak > 0:                                     # physical disturbance of Bob's qubit when x = 1 (reset to |0>)
        hit = (x == 1) & (rng.random(n) < leak)
        b[hit] = 0
    return CollapseRun(message, x, symbol, a, b, scheme, leak)


def teleport_bits(message, shots_per_bit: int, with_classical_bits: bool, seed: int = 0):
    """Classical control: Alice teleports |x> [bennett1993]. Before correction Bob holds X^m2 Z^m1 |x>, so his Z
    reading is x xor m2 with m2 a uniform bit; with the two bits he applies the correction and reads x.
    Returns (x, symbol, b) per use."""
    rng = np.random.default_rng(seed)
    message = np.asarray(message, dtype=np.int8)
    x = np.repeat(message, shots_per_bit)
    symbol = np.repeat(np.arange(message.size), shots_per_bit)
    m2 = rng.integers(0, 2, x.size, dtype=np.int8)
    b = x.copy() if with_classical_bits else (x ^ m2)
    return x, symbol, b


# --------------------------------------------------------------------------------------------------------- analysis
def h2(p: float) -> float:
    p = float(np.clip(p, 0.0, 1.0))
    return 0.0 if p in (0.0, 1.0) else float(-p * np.log2(p) - (1 - p) * np.log2(1 - p))


def mutual_information(p0: float, p1: float) -> float:
    """I(X; B) in bits for a uniform binary X and P(b = 1 | x) = p_x."""
    return h2(0.5 * (p0 + p1)) - 0.5 * (h2(p0) + h2(p1))


def clopper_pearson(k: int, n: int, alpha: float) -> tuple[float, float]:
    lo = 0.0 if k == 0 else float(stats.beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(stats.beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


@dataclass
class Verdict:
    table: np.ndarray            # n[x, b]
    p1_given_x: tuple[float, float]
    bias: float
    bias_interval: tuple[float, float]
    g_statistic: float
    p_value: float
    mi_estimate: float
    mi_upper: float
    level: float

    @property
    def signalling_detected(self) -> bool:
        return self.p_value < 1.0 - self.level


def decode(b, symbol, message, train_fraction: float = 0.5) -> float:
    """Bob's best effort without Alice's help: learn, from a known preamble (the first `train_fraction` of the
    symbols), the mean of his outcomes in slots carrying 0 and carrying 1; then decode every later slot by the nearer
    mean. Returns the bit error rate on the slots he did not train on (0.5 means he learns nothing)."""
    b, symbol, message = np.asarray(b), np.asarray(symbol), np.asarray(message)
    means = np.bincount(symbol, weights=b, minlength=message.size) / np.maximum(np.bincount(symbol, minlength=message.size), 1)
    k = max(2, int(train_fraction * message.size))
    train, test = np.arange(k), np.arange(k, message.size)
    if test.size == 0 or len(set(message[train].tolist())) < 2:
        raise ValueError("the preamble must contain both bit values and leave slots to decode")
    m0, m1 = means[train][message[train] == 0].mean(), means[train][message[train] == 1].mean()
    guess = (np.abs(means[test] - m1) < np.abs(means[test] - m0)).astype(int)
    return float(np.mean(guess != message[test]))


def analyze(x, b, level: float = 0.99) -> Verdict:
    """Test whether Bob's outcomes depend on Alice's bit and bound the information per use."""
    x, b = np.asarray(x), np.asarray(b)
    table = np.array([[np.sum((x == i) & (b == j)) for j in (0, 1)] for i in (0, 1)], dtype=float)
    n0, n1 = table.sum(axis=1)
    if min(n0, n1) == 0:
        raise ValueError("both message values must occur")
    p0, p1 = table[0, 1] / n0, table[1, 1] / n1
    expected = np.outer(table.sum(axis=1), table.sum(axis=0)) / table.sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        g = 2.0 * np.nansum(np.where(table > 0, table * np.log(table / expected), 0.0))
    alpha_each = (1.0 - level) / 2                  # Bonferroni over the two conditionals
    lo0, hi0 = clopper_pearson(int(table[0, 1]), int(n0), alpha_each)
    lo1, hi1 = clopper_pearson(int(table[1, 1]), int(n1), alpha_each)
    mi_upper = max(mutual_information(q0, q1) for q0 in (lo0, hi0) for q1 in (lo1, hi1))
    return Verdict(table, (p0, p1), p1 - p0, (lo1 - hi0, hi1 - lo0), float(g), float(stats.chi2.sf(g, 1)),
                   mutual_information(p0, p1), mi_upper, level)


def uses_to_detect(delta: float, alpha: float = 0.01, power: float = 0.9, p: float = 0.5) -> int:
    """Pairs per message value needed to detect a bias delta in Bob's marginal (two-sided test)."""
    if not 0 < abs(delta) < 1:
        raise ValueError("delta must lie in (0, 1)")
    z = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    p0, p1 = p - delta / 2, p + delta / 2
    return int(np.ceil(z ** 2 * (p0 * (1 - p0) + p1 * (1 - p1)) / delta ** 2))


# ---------------------------------------------------------------------------------- circuits for a cloud processor
def circuit(scheme: str, x: int, leak: float = 0.0):
    """One shot's circuit: Bell pair on (0 = Alice, 1 = Bob), Alice's action for bit x, then Bob's Z measurement.
    Classical bit 0 holds Alice's outcome (if she measured), bit 1 Bob's. `leak` > 0 inserts an amplitude-damping
    channel on Bob's qubit when x = 1 (simulation only), the positive control."""
    if scheme not in SCHEMES:
        raise ValueError(f"scheme must be one of {SCHEMES}")
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Kraus

    qc = QuantumCircuit(2, 2, name=f"collapse_{scheme}_{x}")
    qc.h(0); qc.cx(0, 1)
    qc.barrier()
    if scheme == "basis":
        if x:
            qc.ry(-np.pi / 2, 0)                     # analyzer at 45 degrees: rotate that axis onto Z, then measure Z
        qc.measure(0, 0)
    elif scheme == "measure" and x:
        qc.measure(0, 0)
    elif scheme == "flip" and x:
        qc.x(0)
    if leak > 0 and x:
        k0 = np.array([[1, 0], [0, np.sqrt(1 - leak)]]); k1 = np.array([[0, np.sqrt(leak)], [0, 0]])
        qc.append(Kraus([k0, k1]), [1])
    qc.barrier()
    qc.measure(1, 1)
    return qc


def counts_to_outcomes(counts_by_bit: dict[int, dict[str, int]], seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Turn {x: {bitstring: count}} (Qiskit order: 'b a', clbit 1 first) into per-shot arrays x and b, shuffled."""
    xs, bs = [], []
    for x, counts in counts_by_bit.items():
        for key, c in counts.items():
            bit_b = int(key.replace(" ", "")[0])
            xs += [int(x)] * c; bs += [bit_b] * c
    order = np.random.default_rng(seed).permutation(len(xs))
    return np.asarray(xs, dtype=np.int8)[order], np.asarray(bs, dtype=np.int8)[order]


def run_aer(scheme: str, shots: int, leak: float = 0.0, seed: int = 0, noise_model=None) -> dict[int, dict[str, int]]:
    """Run both message values in Qiskit Aer; returns counts per value."""
    from qiskit_aer import AerSimulator

    sim = AerSimulator(seed_simulator=seed, noise_model=noise_model)
    return {x: sim.run(circuit(scheme, x, leak), shots=shots).result().get_counts() for x in (0, 1)}


def run_on_backend(backend, scheme: str, shots: int, layout: tuple[int, int], repeats: int = 1, seed: int = 0):
    """Hardware run through qll.circuits.cloud_run on any backend (a real device, or a fake one for rehearsal).
    `layout` = (Alice's physical qubit, Bob's). Circuits for x = 0 and x = 1 alternate in one job, repeated, so drift
    affects both equally. Returns {x: counts}."""
    from qll.circuits.cloud_run import run_backend

    circs = [circuit(scheme, x) for _ in range(repeats) for x in (0, 1)]
    out: dict[int, dict[str, int]] = {0: {}, 1: {}}
    for i, counts in enumerate(run_backend(backend, circs, shots, list(layout), seed)):
        for key, v in counts.items():
            out[i % 2][key] = out[i % 2].get(key, 0) + v
    return out
