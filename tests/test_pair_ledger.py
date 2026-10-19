"""The pair ledger (qll/network/pair_ledger.py): entanglement is a resource that is created, aged, consumed, and never
resurrected. Swaps and purifications consume their inputs whether they succeed or not, nothing is usable before its
classical messages arrive, decayed pairs expire, and a long randomized run conserves every pair it created. The
closed forms (Werner decay, the swap map, BBPSSW, survival) are checked against independent expressions."""
import math

import numpy as np
import pytest

from qll.channels.light_time_delay import one_way_delay_s
from qll.circuits.entanglement_swapping import swapped_fraction_analytic
from qll.network import pair_ledger as PL
from qll.network.purification import bbpssw_step

pytestmark = pytest.mark.phase4
AB, BC = ("Alice", "Relay"), ("Relay", "Charlie")


class AlwaysSucceed:
    def random(self):
        return 0.0


class AlwaysFail:
    def random(self):
        return 1.0


def test_closed_forms_match_the_repository_physics():
    assert PL.swapped_fidelity(0.95, 0.95) == pytest.approx(swapped_fraction_analytic(0.95))
    w = (4 * 0.95 - 1) / 3                                                             # independently: Werner parameters multiply
    assert PL.swapped_fidelity(0.95, 0.95) == pytest.approx((3 * w * w + 1) / 4) == pytest.approx(0.90333, abs=1e-5)
    # (the October 18 roadmap quotes 0.9042 for this case; the formula it states gives 0.9033)
    for f in (0.6, 0.8, 0.95):
        assert PL.bbpssw(f) == pytest.approx(bbpssw_step(f))
    assert PL.werner_fidelity(0.9, 0.0, 1.0) == 0.9
    assert PL.werner_fidelity(0.9, 1.0, 1.0) == pytest.approx(0.25 + 0.65 * math.exp(-2))
    assert PL.werner_fidelity(0.9, 1e9, 1.0) == pytest.approx(0.25)                    # the fully mixed state, not zero


def test_nothing_is_usable_before_its_herald_arrives():
    led = PL.PairLedger()
    delay = one_way_delay_s(1.47 * 25e3)
    pid = led.herald(AB, 0.0, 0.97, 1.0, delay)
    assert led.state(pid, delay / 2) == PL.PENDING and not led.usable(pid, delay / 2)
    with pytest.raises(PL.PairUnavailable, match="pending"):
        led.consume(pid, delay / 2)
    assert led.consume(pid, delay) == pytest.approx(PL.werner_fidelity(0.97, delay, 1.0))


def test_a_swap_consumes_its_inputs_and_waits_for_its_outcome():
    led = PL.PairLedger()
    a, b = led.herald(AB, 0.0, 0.95, 10.0), led.herald(BC, 0.0, 0.95, 10.0)
    dist = {"Alice": 30e3, "Charlie": 60e3}
    c = led.swap(a, b, 0.0, AlwaysSucceed(), 0.5, dist)
    assert led.state(a, 0.0) == led.state(b, 0.0) == PL.CONSUMED
    assert led.pairs[c].ends == ("Alice", "Charlie") and led.pairs[c].parents == (a, b) and led.pairs[c].f0 == pytest.approx(0.90333, abs=1e-5)
    assert led.pairs[c].ready_s == pytest.approx(one_way_delay_s(60e3))               # the outcome must reach the farther end
    with pytest.raises(PL.PairUnavailable, match="consumed"):
        led.consume(a, 1.0)                                                            # an input never comes back
    with pytest.raises(PL.PairUnavailable):
        led.swap(a, b, 1.0, AlwaysSucceed())


def test_a_failed_swap_restores_nothing():
    led = PL.PairLedger()
    a, b = led.herald(AB, 0.0, 0.95, 10.0), led.herald(BC, 0.0, 0.95, 10.0)
    assert led.swap(a, b, 0.0, AlwaysFail()) is None
    assert led.state(a, 0.0) == led.state(b, 0.0) == PL.CONSUMED and led.counts(0.0)["created"] == 2
    assert led.inventory(AB, 0.0) == led.inventory(BC, 0.0) == led.inventory(("Alice", "Charlie"), 0.0) == []
    led.check_invariants(0.0)


def test_purification_consumes_both_inputs_and_improves_fidelity_when_it_succeeds():
    led = PL.PairLedger()
    a, b = led.herald(AB, 0.0, 0.8, 10.0), led.herald(AB, 0.0, 0.8, 10.0)
    c = led.purify(a, b, 0.0, AlwaysSucceed(), link_delay_s=1e-4)
    assert led.pairs[c].f0 == pytest.approx(bbpssw_step(0.8)[0]) and led.pairs[c].f0 > 0.8 and led.pairs[c].ready_s == pytest.approx(1e-4)
    d, e = led.herald(AB, 0.0, 0.8, 10.0), led.herald(AB, 0.0, 0.8, 10.0)
    assert led.purify(d, e, 0.0, AlwaysFail()) is None and led.state(d, 0.0) == led.state(e, 0.0) == PL.CONSUMED
    with pytest.raises(ValueError):
        led.purify(c, led.herald(BC, 0.0, 0.8, 10.0), 1.0, AlwaysSucceed())            # different links


def test_decayed_pairs_expire_for_good():
    led = PL.PairLedger(floor=0.8)
    pid = led.herald(AB, 0.0, 0.9, 1.0)
    w_floor = (4 * 0.8 - 1) / 3
    t_cross = -0.5 * math.log(w_floor / ((4 * 0.9 - 1) / 3))                            # when F(t) reaches the floor
    assert led.expire(t_cross * 0.99) == [] and led.expire(t_cross * 1.01) == [pid]
    assert led.state(pid, 0.0) == PL.EXPIRED                                            # even asked about an earlier time
    with pytest.raises(PL.PairUnavailable):
        led.consume(pid, 0.0)
    led2 = PL.PairLedger(cutoff_s=0.1)
    q = led2.herald(AB, 0.0, 0.99, 100.0)
    assert led2.expire(0.2) == [q]


def test_bad_inputs_are_rejected():
    led = PL.PairLedger()
    for kw in ({"f0": 1.2}, {"f0": 0.1}, {"t_mem_s": 0.0}, {"herald_delay_s": -1.0}):
        args = {"f0": 0.9, "t_mem_s": 1.0, "herald_delay_s": 0.0, **kw}
        with pytest.raises(ValueError):
            led.herald(AB, 0.0, **args)
    with pytest.raises(ValueError):
        led.herald(("Alice", "Alice"), 0.0, 0.9, 1.0)
    a, b = led.herald(AB, 0.0, 0.9, 1.0), led.herald(AB, 0.0, 0.9, 1.0)
    with pytest.raises(ValueError):
        led.swap(a, b, 0.0, AlwaysSucceed())                                            # they share two nodes, not one
    with pytest.raises(PL.PairUnavailable):
        led.swap(a, a, 0.0, AlwaysSucceed())
    with pytest.raises(ValueError):
        PL.simulate_service(PL.ChainDesign(p_swap=0.0))
    for p, n in ((-0.1, 1), (0.1, -1)):
        with pytest.raises(ValueError):
            PL.survival_probability(p, n)


@pytest.mark.parametrize("seed", range(5))
def test_random_operation_sequences_conserve_every_pair(seed):
    """A property test by hand (no extra dependency): random heralds, swaps, purifications, consumptions, and expiries,
    after which every created pair is accounted for exactly once and no retired pair ever reappears."""
    rng = np.random.default_rng(seed)
    led = PL.PairLedger(floor=0.6, cutoff_s=0.5)
    now = 0.0
    for _ in range(400):
        now += rng.exponential(0.005)
        op = rng.integers(5)
        try:
            if op == 0:
                led.herald([AB, BC][rng.integers(2)], now, rng.uniform(0.7, 1.0), 1.0, rng.uniform(0, 0.002))
            elif op == 1 and led.inventory(AB, now) and led.inventory(BC, now):
                led.swap(rng.choice(led.inventory(AB, now)), rng.choice(led.inventory(BC, now)), now, rng, 0.5, {"Alice": 1e5, "Charlie": 1e5})
            elif op == 2 and len(led.inventory(AB, now)) >= 2:
                a, b = rng.choice(led.inventory(AB, now), 2, replace=False)
                led.purify(int(a), int(b), now, rng, 1e-4)
            elif op == 3:
                ids = list(led.pairs)
                led.consume(int(rng.choice(ids)), now) if ids else None
            else:
                led.expire(now)
        except PL.PairUnavailable:
            pass                                                                        # refusing is always allowed
        led.check_invariants(now)
    c = led.counts(now)
    assert c[PL.PENDING] + c[PL.AVAILABLE] + c[PL.CONSUMED] + c[PL.EXPIRED] == c["created"] > 50


def test_the_service_conserves_pairs_and_shows_that_supply_alone_is_not_enough():
    r = PL.simulate_service(PL.ChainDesign(), demand_hz=2.0, horizon_s=20.0, seed=1)
    c = r["counts"]
    assert c[PL.PENDING] + c[PL.AVAILABLE] + c[PL.CONSUMED] + c[PL.EXPIRED] == c["created"]
    assert r["served"] + r["missed"] + r["still_queued"] == r["requests"]
    assert r["min_fidelity"] >= PL.ChainDesign().floor                                 # nothing below the floor is delivered
    assert r["end_to_end_rate_hz"] > 2.0 and r["availability"] < 0.95                  # pairs expire faster than requests come
    longer = PL.simulate_service(PL.ChainDesign(t_mem_s=5.0), demand_hz=2.0, horizon_s=20.0, seed=1)
    assert longer["availability"] > r["availability"] + 0.1                            # a longer memory serves more of the same demand
    idle = PL.simulate_service(PL.ChainDesign(), demand_hz=0.0, horizon_s=5.0, seed=1)
    assert idle["requests"] == 0 and idle["availability"] == 1.0 and idle["counts"][PL.EXPIRED] > 0


def test_one_logical_qubit_cannot_survive_for_ever():
    assert PL.survival_probability(0.0, 1e12) == 1.0
    assert PL.survival_probability(1e-6, 1e6) == pytest.approx(math.exp(-1), rel=1e-6)
    assert PL.survival_probability(1e-9, 1e12) < 1e-300 + 1e-12                         # tends to zero for any p_L > 0
    n = PL.cycles_to_survival(1e-6, 0.99)
    assert PL.survival_probability(1e-6, n) >= 0.99 > PL.survival_probability(1e-6, n + 1)
    assert PL.cycles_to_survival(0.0, 0.5) == math.inf


def test_your_serving_policy_against_the_references():
    """Runs deadline_aware (yours to write) in the same service as the two reference policies; it must keep every
    invariant, and the printout compares availability, delivered fidelity, and waste."""
    led = PL.PairLedger()
    probe = [led.herald(AB, 0.0, 0.9, 1.0), led.herald(AB, 0.0, 0.95, 1.0)]
    try:
        choice = PL.deadline_aware(led, probe, 0.0)
    except NotImplementedError:
        pytest.skip("deadline_aware has not been written yet")
    assert choice in probe
    runs = {p.__name__: PL.simulate_service(PL.ChainDesign(), demand_hz=2.0, horizon_s=20.0, seed=4, policy=p)
            for p in (PL.oldest_first, PL.freshest_first, PL.deadline_aware)}
    for name, r in runs.items():
        print(f"{name:15s} availability {r['availability']:.3f}  mean F {r['mean_fidelity']:.4f}  expired {r['counts']['expired']}")
        assert r["min_fidelity"] >= PL.ChainDesign().floor and r["served"] + r["missed"] + r["still_queued"] == r["requests"]
