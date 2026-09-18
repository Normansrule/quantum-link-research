"""Prepare-and-measure QKD with two conjugate bases.

Physics
-------
Alice sends |0>,|1> (Z) or |+>,|-> (X) at random; Bob measures in a random basis; sifting keeps the
matched half; QBER Q from channel errors plus background; secret fraction 1 - 2 h2(Q) [bennett1984]
[shor2000]. An intercept-resend attacker in a random basis induces Q = 25% [nielsen2010]. All basis
announcements, error estimation, reconciliation, and amplification are ClassicalMessages, so a
session at distance d takes at least the light time to complete (INV-1).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qll.channels.light_time_delay import one_way_delay_s
from qll.hardware.randomness import EntropySource, NumpyPRNG
from qll.qkd.error_correction import reconcile
from qll.qkd.key_rate import bb84_rate_per_sifted_bit
from qll.qkd.privacy_amplification import final_key_length, toeplitz_hash
from qll.qkd.sifting import sift


@dataclass(frozen=True)
class Bb84Result:
    n_sent: int
    n_sifted: int
    qber: float
    secret_bits: int
    secret_fraction_per_sifted: float
    classical_time_s: float
    key: np.ndarray


def run_bb84(n_pulses: int, channel_error: float = 0.0, transmittance: float = 1.0, intercept_resend: bool = False,
             distance_m: float = 0.0, entropy: EntropySource | None = None, allow_pseudo: bool = False,
             ec_scheme: str = "ldpc", seed: int = 0) -> Bb84Result:
    entropy = entropy or NumpyPRNG(seed)
    if not entropy.quantum and not allow_pseudo:
        raise ValueError("basis choice must come from a quantum EntropySource (or pass allow_pseudo=True)")
    rng = np.random.default_rng(seed)
    a_bits, a_bases, b_bases = entropy.bits(n_pulses), entropy.bits(n_pulses), entropy.bits(n_pulses)
    arrived = rng.random(n_pulses) < transmittance
    # Eve: measure in a random basis and resend her result
    if intercept_resend:
        e_bases = rng.integers(0, 2, n_pulses, dtype=np.int8)
        e_bits = np.where(e_bases == a_bases, a_bits, rng.integers(0, 2, n_pulses, dtype=np.int8))
        sent_bits, sent_bases = e_bits, e_bases
    else:
        sent_bits, sent_bases = a_bits, a_bases
    # Bob: correct result if bases match the *sent* basis, else random; plus channel errors
    b_bits = np.where(b_bases == sent_bases, sent_bits, rng.integers(0, 2, n_pulses, dtype=np.int8))
    b_bits = np.where(rng.random(n_pulses) < channel_error, 1 - b_bits, b_bits)
    s = sift(a_bases, b_bases, distance_m)
    keep = s.keep & arrived
    ka, kb = a_bits[keep], b_bits[keep]
    n_sifted = int(keep.sum())
    qber = float(np.mean(ka != kb)) if n_sifted else 0.5
    rec = reconcile(ka, kb, qber, ec_scheme, distance_m=distance_m)
    l = final_key_length(n_sifted, qber, rec.leaked_bits)
    key = toeplitz_hash(rec.corrected_key, l, seed)
    t_classical = 2 * one_way_delay_s(distance_m) + rec.classical_time_s   # sift exchange + reconciliation
    return Bb84Result(n_pulses, n_sifted, qber, l, bb84_rate_per_sifted_bit(qber), t_classical, key)
