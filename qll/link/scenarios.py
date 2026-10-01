"""The test scenarios of the handoff (systems/see510/06_test_cases.md) and the validation checks against the
closed-form models.

Scenarios: 1 baseline; 2 increasing distance (with a block-size sensitivity); 3 interception (and classical
tampering); 4 high loss from an inserted attenuator; 5 random channel error compared with an adversary producing the
same error rate; 6 reproducibility. The demonstration delivers accepted keys to the external application and shows it
failing closed. Every function returns plain records, so the runner, the plots, and the tests share one source.
"""
from __future__ import annotations

import math

import numpy as np

from qll.link import models
from qll.link.config import LinkConfig
from qll.link.demo_app import DemoApp
from qll.link.key_store import KeyUnavailable, SiteKeyManager
from qll.link.monitor import SessionMetrics
from qll.link.protocol_bb84 import SessionResult, run_session

SEEDS = (11, 12, 13)
DISTANCES_KM = (0, 1, 5, 10, 25, 50, 75, 100, 125)
EVE_FRACTIONS = (0.0, 0.05, 0.1, 0.25, 0.5, 1.0)
EXTRA_LOSS_DB = (0, 5, 10, 15, 20, 25, 30, 35, 40)
MISALIGNMENT = (0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15)


def baseline(base: LinkConfig | None = None) -> list[SessionResult]:
    base = (base or LinkConfig()).with_(scenario="1_baseline")
    return [run_session(base.with_(seed=s)) for s in SEEDS]


def distance(base: LinkConfig | None = None, distances=DISTANCES_KM, seeds=SEEDS, long_block: int = 10_000_000) -> list[SessionResult]:
    base = (base or LinkConfig()).with_(scenario="2_distance")
    out = [run_session(base.with_(distance_km=float(d), seed=s)) for d in distances for s in seeds]
    big = base.with_(scenario="2_distance_long_block", n_pulses=long_block)
    out += [run_session(big.with_(distance_km=float(d), seed=seeds[0])) for d in distances if d >= 50]
    return out


def interception(base: LinkConfig | None = None, fractions=EVE_FRACTIONS, seeds=SEEDS) -> list[SessionResult]:
    base = (base or LinkConfig()).with_(scenario="3_interception")
    out = [run_session(base.with_(eve_fraction=f, seed=s)) for f in fractions for s in seeds]
    out.append(run_session(base.with_(scenario="3_classical_tampering", tamper_classical=True, seed=seeds[0])))
    return out


def high_loss(base: LinkConfig | None = None, losses=EXTRA_LOSS_DB) -> list[SessionResult]:
    base = (base or LinkConfig()).with_(scenario="4_high_loss")
    return [run_session(base.with_(extra_loss_db=float(x), seed=SEEDS[0])) for x in losses]


def noise_vs_adversary(base: LinkConfig | None = None, errors=MISALIGNMENT) -> list[tuple[SessionResult, SessionResult]]:
    """Each misalignment error e is paired with an adversary on a clean (1 % misalignment) channel tuned to the same
    expected error rate, f = 4 (e - e0) / (1 - 2 e0); returns (noise, adversary) pairs."""
    base = (base or LinkConfig()).with_(scenario="5_noise_vs_adversary")
    e0 = base.misalignment_error
    pairs = []
    for e in errors:
        noise = run_session(base.with_(misalignment_error=e, seed=SEEDS[0]))
        f = 4 * (e - e0) / (1 - 2 * e0)
        adv = run_session(base.with_(eve_fraction=f, seed=SEEDS[0])) if 0 <= f <= 1 else None
        pairs.append((noise, adv))
    return pairs


def reproducibility(base: LinkConfig | None = None) -> dict:
    base = (base or LinkConfig()).with_(scenario="6_reproducibility", seed=SEEDS[0])
    r1, r2, r3 = run_session(base), run_session(base), run_session(base.with_(seed=SEEDS[1]))
    strip = lambda m: {k: v for k, v in m.to_dict(with_events=False).items() if k not in ("execution_time_s", "timestamp_utc")}
    return {"same_metrics": strip(r1.metrics) == strip(r2.metrics), "same_keys": bool(np.array_equal(r1.key_a, r2.key_a)),
            "same_run_id": r1.metrics.run_id == r2.metrics.run_id, "other_seed_differs": not np.array_equal(r1.key_a, r3.key_a),
            "runs": [r1, r2, r3]}


def demonstration(base: LinkConfig | None = None, messages: int = 5) -> dict:
    """Accepted key reaches the applications; a rejected session deposits nothing; an empty store refuses."""
    base = (base or LinkConfig()).with_(scenario="7_demonstration")
    mgr = {"A": SiteKeyManager("A"), "B": SiteKeyManager("B")}
    good = run_session(base, mgr)
    bad = run_session(base.with_(eve_fraction=1.0, seed=SEEDS[1]), mgr)
    sa, sb = mgr["A"].store_for("B"), mgr["B"].store_for("A")
    sa.authorized.add("demo-A"); sb.authorized.add("demo-B")
    app_a, app_b = DemoApp("demo-A", sa), DemoApp("demo-B", sb)
    roundtrips = []
    for i in range(messages):
        text = f"test message {i}: non-sensitive demonstration data".encode()
        env = app_a.send(text)
        roundtrips.append(app_b.receive(env) == text)
    while sa.status()["stored_key_count"]:
        sa.get_key("demo-A", 1)
    try:
        app_a.send(b"one more")
        refused = False
    except KeyUnavailable:
        refused = True
    return {"accepted_session": good.metrics, "rejected_session": bad.metrics, "keys_from_good": good.metrics.keys_delivered_256,
            "keys_from_bad": bad.metrics.keys_delivered_256, "roundtrips_ok": all(roundtrips), "messages": messages,
            "refused_when_empty": refused, "app_log": app_a.log}


def _within(observed: float, expected: float, sigma: float, k: float = 4.0) -> bool:
    return abs(observed - expected) <= k * sigma + 1e-12


def validation_checks(n_pulses: int = 400_000) -> list[dict]:
    """Controlled cases with known answers (systems/see510/08_validation.md). Each returns expected, observed, pass."""
    rows = []

    def add(name, expected, observed, ok, note=""):
        rows.append({"check": name, "expected": expected, "observed": observed, "pass": bool(ok), "note": note})

    ideal = LinkConfig(scenario="validation", n_pulses=n_pulses, misalignment_error=0.0, dark_count_prob=0.0, seed=101)
    r = run_session(ideal)
    add("V1 ideal channel: no errors, matching keys", "QBER 0, keys equal, accepted",
        f"QBER {r.metrics.qber_true:.4f}, equal {bool(np.array_equal(r.key_a, r.key_b))}, {r.metrics.status}",
        r.metrics.qber_true == 0 and r.metrics.accepted and np.array_equal(r.key_a, r.key_b))
    for d in (0.0, 25.0, 75.0):
        c = LinkConfig(scenario="validation", n_pulses=n_pulses, distance_km=d, seed=102)
        m = run_session(c).metrics
        p = models.detection_prob(c)
        sd = math.sqrt(p * (1 - p) / c.n_pulses)
        add(f"V2 detection probability at {d:g} km", f"{p:.4e}", f"{m.detection_probability:.4e}", _within(m.detection_probability, p, sd), "4 sigma, binomial")
        if m.states_detected:
            frac = m.sifted_bits / m.states_detected
            add(f"V3 sifting fraction at {d:g} km", "0.5", f"{frac:.4f}", _within(frac, 0.5, math.sqrt(0.25 / m.states_detected)), "4 sigma")
        q = models.expected_qber(c)
        if m.sifted_bits:
            add(f"V4 error rate at {d:g} km", f"{q:.4f}", f"{m.qber_true:.4f}", _within(m.qber_true, q, math.sqrt(q * (1 - q) / m.sifted_bits)), "4 sigma, over all sifted bits")
    c = LinkConfig(scenario="validation", n_pulses=n_pulses, eve_fraction=1.0, seed=103)
    r = run_session(c)
    q = models.expected_qber(c)
    add("V5 full intercept-resend: error rate near 25 %, session rejected", f"{q:.4f}, rejected",
        f"{r.metrics.qber_true:.4f}, {r.metrics.status}", _within(r.metrics.qber_true, q, math.sqrt(q * (1 - q) / r.metrics.sifted_bits)) and not r.metrics.accepted)
    rep = reproducibility(LinkConfig(n_pulses=n_pulses))
    add("V6 same configuration and seed reproduce the session", "identical metrics, keys, run id",
        f"metrics {rep['same_metrics']}, keys {rep['same_keys']}, id {rep['same_run_id']}; other seed differs {rep['other_seed_differs']}",
        rep["same_metrics"] and rep["same_keys"] and rep["same_run_id"] and rep["other_seed_differs"])
    r = run_session(LinkConfig(scenario="validation", n_pulses=n_pulses, tamper_classical=True, seed=104))
    add("V7 an altered classical message aborts the session", "rejected (auth)", r.metrics.status, r.metrics.reject_reason == "auth")
    demo = demonstration(LinkConfig(n_pulses=n_pulses))
    add("V8 only accepted key reaches the application, and it works", "keys from accepted session only; decrypts; refuses when empty",
        f"{demo['keys_from_good']} keys delivered, {demo['keys_from_bad']} from the rejected session; round trips {demo['roundtrips_ok']}; refused {demo['refused_when_empty']}",
        demo["keys_from_good"] > 0 and demo["keys_from_bad"] == 0 and demo["roundtrips_ok"] and demo["refused_when_empty"])
    return rows


def metrics_of(results) -> list[SessionMetrics]:
    return [r.metrics for r in results]
