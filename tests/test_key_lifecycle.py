"""Key and authentication lifecycle (audit S01-S03): a simulation ledger is not secret material; a secret pool consumes
actual bytes once and is replenished only with recorded accepted key; the authenticated channel fails closed and
stays failed, and its verified transcript cannot change; one-time key material cannot be issued twice, and requests
are validated and atomic."""
import os

import numpy as np
import pytest

from qll.link.authentication import TAG_BITS, AuthKeyPool, PoolExhausted, SecretAuthKeyPool, SimulatedAuthKeyPool
from qll.link.classical_channel import FAILED, OPEN, VERIFIED, AuthenticatedChannel, AuthenticationFailure, ChannelClosed
from qll.link.config import LinkConfig
from qll.link.key_store import KeyReuse, KeyStore, KeyUnavailable
from qll.link.protocol_bb84 import run_session

pytestmark = pytest.mark.phase3


# ---------------------------------------------------------------------------------------------------- S01 pools
def test_the_simulation_ledger_is_labelled_and_validates_counts():
    p = SimulatedAuthKeyPool(1024, b"seed")
    assert p.simulated and AuthKeyPool is SimulatedAuthKeyPool
    for bad in (0, -5, True, 1.5):
        with pytest.raises(ValueError):
            p.take(bad)
        with pytest.raises(ValueError):
            p.refill(bad)
    assert p.bits == 1024 and p.consumed == 0                                   # nothing changed on a rejected request


def test_secret_pool_consumes_actual_bytes_once():
    material = os.urandom(64)
    p = SecretAuthKeyPool(bytearray(material))
    assert not p.simulated and p.bits == 512 and "pre-shared" in p.provenance[0]
    k, a, b = p.session_keys()
    assert p.consumed == 3 * 128 and p.bits == 512 - 384
    assert k == (int.from_bytes(material[:16], "big") & ((1 << 127) - 1)) % ((1 << 127) - 1) or k == 1   # cut from the front
    assert len({k, a, b}) == 3
    with pytest.raises(PoolExhausted):
        p.session_keys()
    assert material.hex() not in repr(p) and "unused" in repr(p)


def test_secret_pool_replenishment_needs_real_bits_and_provenance():
    p = SecretAuthKeyPool(bytearray())
    with pytest.raises(ValueError):
        p.replenish(np.array([1, 0, 1, 1, 0, 0, 1, 0]), provenance="")
    with pytest.raises(ValueError):
        p.replenish(np.array([0.5, 1.0]), provenance="run/exec")
    p.replenish(np.array([1, 0, 1, 1, 0, 0, 1, 0, 1, 1]), provenance="run/exec")   # 10 bits: one whole byte kept
    assert p.bits == 8 and p.material == bytearray(b"\xb2") and p.provenance[-1] == ("run/exec", 8)
    with pytest.raises(TypeError):
        SecretAuthKeyPool("not bytes")


def test_a_session_with_a_secret_pool_replenishes_it_with_its_own_key():
    c = LinkConfig(n_pulses=200_000, auth_mode="wegman_carter", auth_pool_bits=1024)
    pool = SecretAuthKeyPool(bytearray(os.urandom(128)))
    r = run_session(c, pool=pool)
    assert r.metrics.accepted and r.metrics.auth_bits_refilled % 8 == 0 and r.metrics.auth_bits_refilled > 0
    assert pool.provenance[-1][0].startswith(r.metrics.run_id + "/") and pool.provenance[-1][1] == r.metrics.auth_bits_refilled


# ---------------------------------------------------------------------------------------------------- S02 channel
def _wc(pool):
    return AuthenticatedChannel(b"k" * 32, mode="wegman_carter", pool=pool)


def test_failure_is_sticky():
    cc = AuthenticatedChannel(b"k" * 32, mode="wegman_carter", pool=SimulatedAuthKeyPool(4096, b"s"), tamper_kind="bases")
    cc.send("A", "bases", {"x": 1})
    with pytest.raises(AuthenticationFailure):
        cc.finalize()
    assert cc.state == FAILED
    with pytest.raises(AuthenticationFailure):
        cc.finalize()                                                          # a retry cannot turn failure into success
    with pytest.raises(ChannelClosed):
        cc.require_verified(cc.transcript_digest)


def test_exhausted_pool_fails_the_channel():
    cc = _wc(SimulatedAuthKeyPool(10, b"s"))
    cc.send("A", "x", {"a": 1})
    with pytest.raises(AuthenticationFailure):
        cc.finalize()
    assert cc.state == FAILED


def test_verified_transcript_is_sealed_and_bound_to_its_digest():
    cc = _wc(SimulatedAuthKeyPool(4096, b"s"))
    assert cc.state == OPEN
    cc.send("A", "x", {"a": 1}); cc.send("B", "y", {"b": 2})
    d = cc.finalize()
    assert cc.state == VERIFIED and cc.finalize() == d
    with pytest.raises(ChannelClosed):
        cc.send("A", "late", {"c": 3})                                        # no message after closure
    cc.require_verified(d)
    with pytest.raises(ChannelClosed):
        cc.require_verified("0" * 64)


def test_hmac_mode_fails_at_once_and_stays_failed():
    cc = AuthenticatedChannel(b"k" * 32, mode="hmac", tamper_kind="x")
    with pytest.raises(AuthenticationFailure):
        cc.send("A", "x", {"a": 1})
    with pytest.raises(ChannelClosed):
        cc.send("A", "y", {"a": 2})
    with pytest.raises(AuthenticationFailure):
        cc.finalize()


# ---------------------------------------------------------------------------------------------------- S03 store
def _store():
    s = KeyStore("A", "B", key_size_bits=8, authorized={"app"})
    return s


def test_consumed_key_cannot_come_back():
    s = _store()
    bits = np.array([1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0])
    ids = s.deposit("run1", bits, "exec-1")
    s.get_key("app", 2)
    with pytest.raises(KeyReuse):
        s.deposit("run1", bits, "exec-1")                                     # same execution
    with pytest.raises(KeyReuse):
        s.deposit("run1", bits, "exec-2")                                     # identical material under a new execution
    with pytest.raises(KeyUnavailable):
        s.get_key_with_ids("app", [ids[0]])
    assert s.status()["consumed_ids"] == 2 and s.delivered == 2


def test_requests_are_validated_and_atomic():
    s = _store()
    ids = s.deposit("run1", np.array([1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1]), "e")
    before = (s.delivered, s.status()["stored_key_count"])
    for bad in (0, -1, True, 1.0):
        with pytest.raises(ValueError):
            s.get_key("app", bad)
    with pytest.raises(ValueError):
        s.get_key_with_ids("app", [ids[0], ids[0]])                           # duplicate identifiers in one request
    with pytest.raises(KeyUnavailable):
        s.get_key_with_ids("app", [ids[0], "no-such-id"])                     # partly unknown: nothing delivered
    with pytest.raises(KeyUnavailable):
        s.get_key("app", 3)
    assert (s.delivered, s.status()["stored_key_count"]) == before
    out = s.get_key_with_ids("app", ids, purpose="test message")
    assert len(out) == 2 and s.ledger[-1] == (ids[1], "app", "test message")


def test_deposit_rejects_non_bits_and_requires_an_execution_id():
    s = _store()
    with pytest.raises(ValueError):
        s.deposit("run", np.array([0, 2, 1, 0, 1, 0, 1, 0]), "e")
    with pytest.raises(ValueError):
        s.deposit("run", np.zeros(8, dtype=int), "")
    assert TAG_BITS == 127


def test_concurrent_requests_never_share_a_key():
    import threading

    s = KeyStore("A", "B", key_size_bits=64, authorized={"app"})
    s.deposit("run", np.random.default_rng(3).integers(0, 2, 64 * 200), "exec")   # 200 distinct 64-bit keys
    n = s.status()["stored_key_count"]
    assert n == 200
    got, refused = [], []

    def worker():
        for _ in range(40):
            try:
                got.extend(k for k, _ in s.get_key("app", 1))
            except KeyUnavailable:
                refused.append(1)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(got) == len(set(got)) == n and len(refused) == 8 * 40 - n and s.delivered == n
