"""Phase 4: memory decoherence (exact Kraus vs analytic), purification (numeric vs recurrence), scheduling,
repeater chain crossover (REQ-NET-001), capability matrix (REQ-CAP-001), routing."""
import math

import networkx as nx
import numpy as np
import pytest

from qll.channels.light_time_delay import round_trip_delay_s
from qll.circuits.bell import bell_state, werner_state
from qll.constants.astro import EARTH_MARS_MAX_M
from qll.network.memory_decoherence import (BASELINES, MEMORY_TABLE, capability_matrix, crossover_time_s,
                                             fraction_after_storage_analytic, fully_entangled_fraction, stored_pair,
                                             teleportation_fidelity_after_storage)
from qll.network.purification import bbpssw_numeric, bbpssw_rounds_to_target, bbpssw_step, purify_werner
from qll.network.repeater_chain import all_photonic_chain, crossover_distance_km, direct_rate_hz, memory_chain
from qll.network.routing import widest_path
from qll.network.swapping_scheduler import expected_max_of_two_geometric, nested_expected_time_s, three_halves_rule_time_s

pytestmark = pytest.mark.phase4


@pytest.mark.parametrize("model", ["depolarizing", "dephasing"])
@pytest.mark.parametrize("t_over_T", [0.0, 0.5, 2.0])
def test_stored_pair_matches_analytic(model, t_over_T):
    w = werner_state(0.95)
    rho = stored_pair(w, t_over_T, 1.0, model)
    assert fully_entangled_fraction(rho) == pytest.approx(fraction_after_storage_analytic(0.95, t_over_T, 1.0, model), abs=1e-12)
    assert np.trace(rho).real == pytest.approx(1.0)


def test_crossover_time_and_teleportation_limit():
    tc = crossover_time_s(0.95, 3600.0)
    assert teleportation_fidelity_after_storage(0.95, tc, 3600.0) == pytest.approx(2 / 3, abs=1e-12)
    assert crossover_time_s(0.5, 100.0) == 0.0
    tcd = crossover_time_s(0.95, 1.0, "dephasing")
    assert fraction_after_storage_analytic(0.95, tcd, 1.0, "dephasing") == pytest.approx(0.5, abs=1e-12)
    assert math.isinf(crossover_time_s(1.0, 1.0, "dephasing"))


def test_capability_matrix_req_cap_001():                                        # REQ-CAP-001
    m = capability_matrix(0.95)
    assert m["NV 13C register"]["metro 25 km fiber"] and m["NV 13C register"]["Moon"]
    assert not m["NV 13C register"]["Mars min"]
    assert m["Eu:YSO nuclear spin, 13.1 h"]["Mars max"] and m["171Yb+ hyperfine"]["Mars min"]
    assert not m["Rb/Cs atomic ensemble (DLCZ)"]["GEO 36000 km"]
    mars_capable = {p.name for p in MEMORY_TABLE if m[p.name]["Mars max"]}
    assert mars_capable == {"171Yb+ hyperfine", "Eu:YSO nuclear spin, 6 h (ZEFOZ+DD)", "Eu:YSO nuclear spin, 13.1 h"}
    rare_earth = [p for p in MEMORY_TABLE if p.name.startswith("Eu:YSO")]
    assert all(p.efficiency < 0.05 for p in rare_earth)                            # the honest price of hour-class storage
    assert m["171Yb+ hyperfine"]["Mars max"] and crossover_time_s(0.95, 3600.0) / BASELINES["Mars max"] < 1.5   # ions clear it, barely
    assert BASELINES["Mars max"] == pytest.approx(round_trip_delay_s(EARTH_MARS_MAX_M))


@pytest.mark.parametrize("F", [0.55, 0.7, 0.9, 0.99])
def test_bbpssw_numeric_equals_recurrence(F):
    w = werner_state(F)
    rho, p = bbpssw_numeric(w, w)
    F2, p2 = bbpssw_step(F)
    assert fully_entangled_fraction(rho) == pytest.approx(F2, abs=1e-12)
    assert p == pytest.approx(p2, abs=1e-12)
    assert F2 > F


def test_bbpssw_fixed_points_and_costs():
    assert bbpssw_step(1.0)[0] == pytest.approx(1.0) and bbpssw_step(0.5)[0] == pytest.approx(0.5)
    assert bbpssw_step(0.4)[0] < 0.4                                               # below 1/2 it gets worse
    rounds, F, pairs = bbpssw_rounds_to_target(0.8, 0.99)
    assert F >= 0.99 and pairs > 2**rounds                                        # at least 2^rounds pairs consumed
    rec = purify_werner(0.8, 0.99, distance_m=EARTH_MARS_MAX_M)
    assert rec.classical_time_s == pytest.approx(rec.rounds * round_trip_delay_s(EARTH_MARS_MAX_M))


def test_scheduler_max_of_geometrics_and_three_halves_rule():
    p = 0.3
    rng = np.random.default_rng(0)
    x = rng.geometric(p, 200000); y = rng.geometric(p, 200000)
    assert abs(np.maximum(x, y).mean() - expected_max_of_two_geometric(p)) < 0.02
    exact = nested_expected_time_s(1e6, 3, 1e-3, 0.5)
    rule = three_halves_rule_time_s(1e6, 3, 1e-3, 0.5)
    assert 0.5 < exact / rule < 2.0                                                # the 3/2 rule is a good approximation


def test_repeater_chain_crossover_exists_and_depends_on_memory():               # REQ-NET-001
    L = crossover_distance_km(3, 1.0)
    assert L is not None and 100 < L < 1000
    assert memory_chain(L * 1.2, 3, 1.0).rate_hz > direct_rate_hz(L * 1.2)
    assert memory_chain(L * 1.2, 3, 3600.0).rate_hz > memory_chain(L * 1.2, 3, 1.0).rate_hz * 0.99   # longer memory never hurts
    assert crossover_distance_km(3, 1e-3) is None                                  # a millisecond memory never wins
    assert memory_chain(5000, 3, 1.0).rate_hz == 0.0                               # stalls when hold time >> memory


def test_all_photonic_needs_no_memory_but_dies_with_segment_loss():
    assert all_photonic_chain(200, 8) > all_photonic_chain(1000, 8) > all_photonic_chain(5000, 8)
    assert all_photonic_chain(1000, 16) > all_photonic_chain(1000, 4)             # shorter segments help


def test_routing_widest_path_with_fidelity_floor():
    G = nx.Graph()
    G.add_edge("A", "B", rate=0.1, fraction=0.9, length_m=50e3)
    G.add_edge("B", "C", rate=0.1, fraction=0.9, length_m=50e3)
    G.add_edge("A", "C", rate=0.001, fraction=0.99, length_m=120e3)
    r = widest_path(G, "A", "C", q_swap=0.5)
    assert r.path == ["A", "B", "C"] and r.bottleneck_rate == pytest.approx(0.05)
    assert r.fidelity_fraction == pytest.approx(0.9 * 0.9 + 0.1 * 0.1 / 3)
    assert r.herald_round_trip_s == pytest.approx(round_trip_delay_s(100e3))
    strict = widest_path(G, "A", "C", f_min=0.85)
    assert strict.path == ["A", "C"]                                              # fidelity floor forces the direct link


def test_dejmps_numeric_matches_deutsch_map_round_by_round_and_beats_bbpssw():
    from qll.network.purification import bell_diagonal_weights, dejmps_numeric, dejmps_rounds_to_target, dejmps_step
    rho = werner_state(0.8); p = bell_diagonal_weights(rho)
    for _ in range(4):
        rho, N = dejmps_numeric(rho, rho)
        p, N2 = dejmps_step(p)
        assert bell_diagonal_weights(rho)[0] == pytest.approx(p[0], abs=1e-9) and N == pytest.approx(N2, abs=1e-9)
    assert p[0] > 0.99
    rb, Fb, pairs_b = bbpssw_rounds_to_target(0.8, 0.99)
    rd, Fd, pairs_d = dejmps_rounds_to_target(bell_diagonal_weights(werner_state(0.8)), 0.99)
    assert rd < rb and pairs_d < pairs_b / 50                                  # 4 rounds / ~32 pairs vs 10 / ~2900
