"""Endpoint scope (audit S05): each run says whether it is a shared-state simulation or an offline analysis of recorded
logs, and the reconciliation is fully determined by its public transcript. Every pass publishes the seed of its
permutation, and replaying the transcript alone reproduces each block parity Alice sent, so Bob needs no shared
array to follow the protocol. Independent live endpoints for the full protocol are not implemented; these tests
keep the labels honest until they are."""
import numpy as np
import pytest

from qll.link.classical_channel import AuthenticatedChannel, AuthenticationFailure
from qll.link.codec import unpack
from qll.link.config import LinkConfig
from qll.link.protocol_bb84 import run_session
from qll.link.reconciliation import _parities, reconcile

pytestmark = pytest.mark.phase3


def _keys(n=4000, q=0.03, seed=7):
    rng = np.random.default_rng(seed)
    a = rng.integers(0, 2, n, dtype=np.int8)
    b = a ^ (rng.random(n) < q).astype(np.int8)
    return a, b


def test_every_permutation_is_rebuilt_from_the_transcript_alone():
    a, b = _keys()
    cc = AuthenticatedChannel(b"k" * 32)
    out = reconcile(a, b, 0.03, 4, np.random.default_rng(1), cc)
    assert np.array_equal(out.key_b, a)
    msgs = [(m.kind, m.payload) for m in cc.transcript]
    seeds = [p for k, p in msgs if k == "permutation_seed"]
    blocks = [p for k, p in msgs if k == "block_parities"]
    assert [s["pass"] for s in seeds] == [0, 1, 2, 3] and seeds[0]["seed"] == 0 and len(blocks) == 4
    n = len(a)
    k1 = int(min(n, max(4, round(0.73 / 0.03))))
    for p, (s, blk) in enumerate(zip(seeds, blocks)):
        perm = np.arange(n) if s["seed"] == 0 else np.random.default_rng(s["seed"]).permutation(n)
        k = min(n, k1 * 2**p)
        lo = np.arange(0, n, k)
        assert np.array_equal(unpack(blk), _parities(a[perm], lo, np.minimum(lo + k, n)))   # public data suffices


def test_a_tampered_seed_is_caught_by_authentication():
    a, b = _keys()
    cc = AuthenticatedChannel(b"k" * 32, tamper_kind="permutation_seed")
    with pytest.raises(AuthenticationFailure):
        reconcile(a, b, 0.03, 4, np.random.default_rng(1), cc)


def test_a_session_states_its_execution_mode():
    r = run_session(LinkConfig(n_pulses=100_000))
    ready = next(e for e in r.metrics.events if e["step"] == "ready")["message"]
    assert "simulation, both sites in one process" in ready and "not separate endpoints" in ready
    assert "execution id" in ready and "simulation ledger (seeded, not secret)" in ready
