"""The Scalable Two-Node Fiber-Optic Quantum Communication Link (systems/see510): every module against a case with a
known answer, the decisions of the protocol, the key-delivery interface, and the reproducibility of the evidence."""
import csv
import math
from pathlib import Path

import numpy as np
import pytest

from qll.link import models
from qll.link.adversary import InterceptResend
from qll.link.classical_channel import AuthenticatedChannel, AuthenticationFailure
from qll.link.config import LinkConfig
from qll.link.demo_app import DemoApp
from qll.link.key_store import KeyUnavailable, SiteKeyManager, Unauthorized
from qll.link.protocol_bb84 import auth_key_for, run_session
from qll.link.reconciliation import reconcile, verify
from qll.link.scenarios import noise_vs_adversary, reproducibility, validation_checks
from qll.link.site_a import SiteA
from qll.qkd.binary_entropy import h2
from qll.qkd.privacy_amplification import toeplitz_hash

pytestmark = pytest.mark.phase3
SMALL = LinkConfig(n_pulses=300_000)
ROOT = Path(__file__).resolve().parents[1]


def test_config_validates_and_identifies_runs():
    assert SMALL.run_id() == LinkConfig(n_pulses=300_000).run_id() != SMALL.with_(seed=1).run_id()
    assert LinkConfig.from_dict(SMALL.to_dict()) == SMALL
    for bad in ({"detector_efficiency": 1.5}, {"distance_km": -1}, {"source_model": "weak_coherent"}, {"misalignment_error": 0.7}):
        with pytest.raises(ValueError):
            LinkConfig(**bad)
    with pytest.raises(ValueError):
        LinkConfig.from_dict({"distanse_km": 3})
    with pytest.raises(TypeError):
        LinkConfig(distance_km=1 + 0j)


def test_closed_form_models():
    c = LinkConfig(distance_km=50, extra_loss_db=3)
    assert models.channel_loss_db(c) == pytest.approx(13.0)
    assert models.channel_transmittance(c) == pytest.approx(10 ** -1.3)
    mu, pb = models.signal_click_prob(c), models.background_click_prob(c)
    assert models.detection_prob(c) == pytest.approx(mu + (1 - mu) * pb)
    clean = LinkConfig(dark_count_prob=0.0, misalignment_error=0.0)
    assert models.expected_qber(clean.with_(eve_fraction=1.0)) == pytest.approx(0.25)
    assert models.expected_qber(clean.with_(eve_fraction=0.4)) == pytest.approx(0.10)
    assert models.asymptotic_secret_fraction(0.11) == pytest.approx(0.0, abs=0.003)
    assert 200 < models.max_distance_km(LinkConfig()) < 260
    assert models.hoeffding_margin(1000, 1e-10) == pytest.approx(math.sqrt(math.log(1e10) / 2000))


def test_adversary_guesses_the_wrong_basis_half_the_time():
    rng = np.random.default_rng(5)
    s = SiteA(rng).prepare(200_000)
    out, rec = InterceptResend(1.0, np.random.default_rng(6)).act(s)
    assert rec.n_touched == 200_000 and rec.wrong_basis / 200_000 == pytest.approx(0.5, abs=0.005)
    right = rec.bases == s.bases
    assert np.array_equal(out.bits[right], s.bits[right])                    # right basis: she learns and resends the bit


def test_classical_channel_authenticates_and_records():
    ch = AuthenticatedChannel(b"k" * 32)
    assert ch.send("A", "hello", {"x": 1}) == {"x": 1} and ch.n_messages == 1 and ch.bytes_sent > 0
    bad = AuthenticatedChannel(b"k" * 32, tamper_kind="hello")
    with pytest.raises(AuthenticationFailure):
        bad.send("A", "hello", {"x": 1})


@pytest.mark.parametrize("q", [0.01, 0.03, 0.08])
def test_cascade_removes_every_error_close_to_the_shannon_limit(q):
    rng = np.random.default_rng(7)
    a = rng.integers(0, 2, 20_000, dtype=np.int8)
    b = a ^ (rng.random(20_000) < q).astype(np.int8)
    out = reconcile(a, b, q, 4, np.random.default_rng(8), AuthenticatedChannel(b"k" * 32))
    assert np.array_equal(out.key_b, a)
    n_err = int(np.sum(a != b))
    assert out.corrected >= n_err
    shannon = len(a) * h2(n_err / len(a))
    assert shannon <= out.leaked_bits <= 1.6 * shannon                   # at least the Slepian-Wolf limit, Cascade-efficient


def test_verification_catches_a_single_differing_bit():
    a = np.random.default_rng(1).integers(0, 2, 5000, dtype=np.int8)
    b = a.copy(); b[1234] ^= 1
    ch = AuthenticatedChannel(b"k" * 32)
    assert verify(a, a.copy(), 64, 9, ch) and not verify(a, b, 64, 9, ch)


def test_fast_toeplitz_equals_the_matrix_product():
    rng = np.random.default_rng(3)
    n, l = 3000, 1500                                                         # large enough for the FFT path
    k = rng.integers(0, 2, n, dtype=np.int8)
    diag = np.random.default_rng(11).integers(0, 2, size=n + l - 1, dtype=np.int8)
    M = np.array([diag[i:i + n][::-1] for i in range(l)], dtype=np.int64)
    assert np.array_equal(toeplitz_hash(k, l, 11), (M @ k % 2).astype(np.int8))


def test_ideal_session_gives_identical_keys_and_the_accounted_length():
    r = run_session(SMALL.with_(misalignment_error=0.0, dark_count_prob=0.0))
    m = r.metrics
    assert m.qber_true == 0 and m.accepted and np.array_equal(r.key_a, r.key_b)
    expected = math.floor(m.key_block_bits * (1 - h2(m.qber_upper_bound)) - m.ec_leaked_bits - 64 - 2 * math.log2(1e10))
    assert m.final_key_bits == expected == len(r.key_a)
    assert [e["step"] for e in m.events][:3] == ["ready", "transmit", "sift"]


def test_decisions():
    assert run_session(SMALL.with_(eve_fraction=1.0)).metrics.reject_reason == "qber"
    assert run_session(SMALL.with_(tamper_classical=True)).metrics.reject_reason == "auth"
    assert run_session(SMALL.with_(distance_km=150)).metrics.reject_reason == "insufficient"
    m = run_session(SMALL.with_(eve_fraction=0.2)).metrics
    assert m.alert                                                            # the operator is warned
    if m.accepted:
        assert m.pa_removed_bits > m.eve_known_key_bits + m.ec_leaked_bits * 0  # amplification removes more than she knew


def test_noise_and_interception_look_alike_to_these_indicators():
    for noise, adv in noise_vs_adversary(LinkConfig(n_pulses=200_000), errors=(0.04, 0.08)):
        assert abs(noise.metrics.qber_true - adv.metrics.qber_true) < 0.012
        assert noise.metrics.detection_probability == pytest.approx(adv.metrics.detection_probability, rel=0.02)


def test_reproducibility():
    rep = reproducibility(SMALL)
    assert rep["same_metrics"] and rep["same_keys"] and rep["same_run_id"] and rep["other_seed_differs"]


def test_key_delivery_interface_and_new_sites():
    mgr = {s: SiteKeyManager(s) for s in "ABC"}
    r = run_session(SMALL, mgr)
    sa, sb = mgr["A"].store_for("B"), mgr["B"].store_for("A")
    sa.authorized.add("app"); sb.authorized.add("app")
    n = sa.status()["stored_key_count"]
    assert n == r.metrics.final_key_bits // 256 > 0
    (kid, key), = sa.get_key("app", 1)
    assert sb.get_key_with_ids("app", [kid]) == [(kid, key)] and len(key) == 32
    with pytest.raises(KeyUnavailable):
        sb.get_key_with_ids("app", [kid])                                      # a key is never handed out twice
    with pytest.raises(Unauthorized):
        sa.get_key("intruder", 1)
    # adding Site C leaves the A-B stores untouched (SN-13)
    run_session(SMALL.with_(seed=7), mgr, "A", "C")
    assert sa.status()["stored_key_count"] == n - 1 and mgr["A"].store_for("C").status()["stored_key_count"] > 0


def test_demo_application_uses_only_accepted_key_and_fails_closed():
    mgr = {s: SiteKeyManager(s) for s in "AB"}
    run_session(SMALL.with_(eve_fraction=1.0), mgr)                             # rejected: deposits nothing
    sa, sb = mgr["A"].store_for("B"), mgr["B"].store_for("A")
    sa.authorized.add("a"); sb.authorized.add("b")
    with pytest.raises(KeyUnavailable):
        DemoApp("a", sa).send(b"hello")
    run_session(SMALL, mgr)
    env = DemoApp("a", sa).send(b"non-sensitive test data")
    assert DemoApp("b", sb).receive(env) == b"non-sensitive test data"


def test_every_validation_check_passes():
    rows = validation_checks(n_pulses=300_000)
    assert len(rows) >= 12 and all(r["pass"] for r in rows), [r for r in rows if not r["pass"]]


def test_committed_evidence_is_reproduced_by_a_fresh_run():
    path = ROOT / "systems" / "see510" / "evidence" / "sessions" / "1_baseline.csv"
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    assert len(rows) == 3
    for row in rows:
        m = run_session(LinkConfig(scenario="1_baseline", seed=int(row["seed"]))).metrics
        assert m.run_id == row["run_id"]
        for f in ("states_detected", "sifted_bits", "sample_errors", "ec_leaked_bits", "final_key_bits"):
            assert getattr(m, f) == int(row[f]), f


def test_auth_key_is_per_seed():
    assert auth_key_for(SMALL) != auth_key_for(SMALL.with_(seed=99)) and len(auth_key_for(SMALL)) == 32


def test_cli(capsys, tmp_path):
    from qll.link.run import main
    main(["session", "--set", "n_pulses=200000", "distance_km=10", "--out", str(tmp_path)])
    out = capsys.readouterr().out
    assert "Simulation Run ID" in out and "Key Accepted" in out
    assert list(tmp_path.glob("baseline/*/summary.txt"))


@pytest.mark.slow
def test_scenarios_command_writes_the_evidence(tmp_path):
    from qll.link.run import main
    main(["scenarios", "--out", str(tmp_path)])
    assert (tmp_path / "README.md").exists() and len(list((tmp_path / "plots").glob("*.svg"))) == 10


def test_crosstalk_acts_as_background():
    quiet = models.expected_qber(LinkConfig(distance_km=50))
    noisy = LinkConfig(distance_km=50, crosstalk_click_prob=1e-4)
    assert models.expected_qber(noisy) > quiet
    m = run_session(noisy.with_(n_pulses=300_000)).metrics
    assert m.detection_probability == pytest.approx(models.detection_prob(noisy), rel=0.05)


def test_docs_cover_every_input_and_need():
    from dataclasses import fields
    doc = (ROOT / "systems" / "see510" / "04_inputs_and_outputs.md").read_text(encoding="utf-8").split("## Measured outputs")[0]
    documented = set(__import__("re").findall(r"^\| `([a-z_0-9]+)` \|", doc, flags=__import__("re").M))
    assert documented == {f.name for f in fields(LinkConfig)}
    rows = list(csv.DictReader((ROOT / "systems" / "see510" / "traceability.csv").read_text(encoding="utf-8").splitlines()))
    assert [r["need"] for r in rows] == [f"SN-{i:02d}" for i in range(1, 16)]
    import ast
    for r in rows:
        assert (ROOT / r["module"]).exists(), r["module"]
        path, fn = r["test"].split("::")
        names = {n.name for n in ast.walk(ast.parse((ROOT / path).read_text(encoding="utf-8"))) if isinstance(n, ast.FunctionDef)}
        assert fn in names, fn
        assert (ROOT / "systems" / "see510" / r["evidence"]).exists(), r["evidence"]
