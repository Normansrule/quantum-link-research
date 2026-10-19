"""The off-grid mesh model (qll/link/mesh_messenger.py): the radio formulas against hand values, coverage set by the
horizon and the link budget, floods bounded by the hop limit, and a delivery record that never mistakes a neighbour's
rebroadcast for delivery."""
import math

import pytest

from qll.link import mesh_messenger as M

pytestmark = pytest.mark.phase3


def test_radio_formulas():
    assert M.sensitivity_dbm(7) == pytest.approx(-174 + 10 * math.log10(125e3) + 6 - 7.5)            # -124.5 dBm
    assert M.sensitivity_dbm(12) - M.sensitivity_dbm(7) == pytest.approx(-12.5)                         # 2.5 dB per step
    assert M.free_space_loss_db(1.0, 915.0) == pytest.approx(91.67, abs=0.01)
    assert M.free_space_loss_db(2.0, 915.0) - M.free_space_loss_db(1.0, 915.0) == pytest.approx(20 * math.log10(2))
    assert M.radio_horizon_km(2.0, 300.0) == pytest.approx(4.12 * (math.sqrt(2) + math.sqrt(300)))
    assert M.time_on_air_s(20, 7) == pytest.approx(0.056576, rel=1e-6)                                   # Semtech's formula, SF7
    assert M.time_on_air_s(20, 12) == pytest.approx(1.318912, rel=1e-6)                                  # SF12, with low-data-rate mode
    assert M.time_on_air_s(20, 12) / M.time_on_air_s(20, 7) > 20
    for bad in ((M.sensitivity_dbm, (6,)), (M.free_space_loss_db, (0.0,)), (M.radio_horizon_km, (-1.0, 1.0)), (M.time_on_air_s, (300,))):
        with pytest.raises(ValueError):
            bad[0](*bad[1])


def test_a_neighbours_rebroadcast_is_never_delivery():
    d = M.Delivery("A", "B")
    d.relay_heard(0.1, "relay")
    assert d.state == M.RELAYED
    d.relay_heard(0.2, "another relay")                                          # still only relayed
    assert d.state == M.RELAYED
    with pytest.raises(ValueError):
        d.end_to_end_ack(0.3, "relay")                                           # only the recipient can acknowledge
    d.end_to_end_ack(0.4, "B")
    assert d.state == M.DELIVERED
    with pytest.raises(ValueError):
        d.advance(M.RELAYED, 0.5, "backwards")                                   # states only move forward
    d.timeout(9.9)
    assert d.state == M.DELIVERED and [h[1] for h in d.history] == [M.RELAYED, M.DELIVERED]


def test_the_ridge_relay_makes_the_difference():
    with_relay = M.send(M.mountain_scenario(True), "hiker A", "hiker B")
    without = M.send(M.mountain_scenario(False), "hiker A", "hiker B")
    assert with_relay.state == M.DELIVERED and with_relay.history[-1][0] < 5.0
    assert without.state == M.UNREACHABLE and [h[1] for h in without.history] == [M.RELAYED, M.UNREACHABLE]


def test_floods_stop_at_the_hop_limit_and_only_relays_rebroadcast():
    nodes = {f"n{i}": M.Node(f"n{i}", 8.0 * i, 0.0, 2.0) for i in range(6)}        # a chain 8 km apart: 2 m masts see 11.7 km
    mesh = M.Mesh(nodes, hop_limit=3)
    assert mesh.neighbours("n0") == ["n1"]
    assert mesh.flood_hops("n0") == {"n0": 0, "n1": 1, "n2": 2, "n3": 3}
    assert M.send(mesh, "n0", "n3").state == M.DELIVERED and M.send(mesh, "n0", "n4").state == M.UNREACHABLE
    nodes["n1"] = M.Node("n1", 8.0, 0.0, 2.0, relay=False)
    assert M.Mesh(nodes, hop_limit=3).flood_hops("n0") == {"n0": 0, "n1": 1}


def test_the_horizon_and_the_budget_both_limit_a_link():
    far = {"a": M.Node("a", 0.0, 0.0, 2.0), "b": M.Node("b", 12.0, 0.0, 2.0)}      # beyond 11.7 km of horizon for 2 m masts
    assert M.Mesh(far).link_margin_db("a", "b") is None
    near = {"a": M.Node("a", 0.0, 0.0, 2.0), "b": M.Node("b", 3.0, 0.0, 2.0)}
    m = M.Mesh(near)
    assert m.link_margin_db("a", "b") > M.Mesh(near, sf=7).link_margin_db("a", "b")  # a higher spreading factor reaches further
    assert M.Mesh(near, obstructed={frozenset(("a", "b")): 80.0}).neighbours("a") == []
