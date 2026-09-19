"""Combine a post-quantum key encapsulation with a QKD key: secure if either is secure.

Physics and cryptography
-----------------------
ML-KEM (FIPS 203, Module-Lattice-based Key-Encapsulation Mechanism) is believed secure against quantum
computers under the Module-LWE assumption [nist2024fips203]; QKD keys are information-theoretically secure
under the physics of Phase 3 but need an authenticated classical channel. A hybrid combiner derives the
session key K = KDF(K_kem || K_qkd || context) so that an adversary must break both [bindel2019]. One ML-KEM
exchange costs one classical round trip (encapsulation key out, ciphertext back): 6-45 minutes at Mars, so
keys are established in advance and rotated per policy, never on demand.
"""
from __future__ import annotations

from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from kyber_py.ml_kem import ML_KEM_768

from qll.channels.light_time_delay import ClassicalMessage, round_trip_delay_s


@dataclass(frozen=True)
class HybridKeyRecord:
    session_key: bytes
    kem_ciphertext: bytes
    classical_time_s: float
    messages: tuple[ClassicalMessage, ...]


def combine(k_kem: bytes, k_qkd: bytes, context: bytes = b"qll-hybrid-v1") -> bytes:
    hk = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=context)
    return hk.derive(k_kem + k_qkd)


def keygen() -> tuple[bytes, bytes]:
    return ML_KEM_768.keygen()


def establish(ek: bytes, dk: bytes, k_qkd: bytes, distance_m: float = 0.0) -> tuple[HybridKeyRecord, HybridKeyRecord]:
    """Alice encapsulates to Bob's ek; both derive the same hybrid key. Returns (alice_record, bob_record).

    The encapsulation key travelled Bob -> Alice earlier (one light time); the ciphertext travels Alice -> Bob
    (another); total classical time is one round trip.
    """
    k_kem, ct = ML_KEM_768.encaps(ek)
    msg_ek = ClassicalMessage(payload=(len(ek),), sent_at_s=0.0, distance_m=distance_m)
    msg_ct = ClassicalMessage(payload=(len(ct),), sent_at_s=msg_ek.earliest_arrival_s, distance_m=distance_m)
    k_alice = combine(k_kem, k_qkd)
    k_bob = combine(ML_KEM_768.decaps(dk, ct), k_qkd)
    rt = round_trip_delay_s(distance_m)
    return (HybridKeyRecord(k_alice, ct, rt, (msg_ek, msg_ct)), HybridKeyRecord(k_bob, ct, rt, (msg_ek, msg_ct)))
