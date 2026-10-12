"""The latency floor (qll/space/latency_floor.py) against closed forms: d/c is a hard floor that no route beats, the
great circle and the chord have their geometric limits, each route's length follows its geometry, and the trips
that security and teleportation add are counted from the protocols."""
import math

import pytest

from qll.constants.physical import C_LIGHT
from qll.space import latency_floor as L

pytestmark = pytest.mark.phase5
C = C_LIGHT


def _pair(a, b):
    return L.SITES[a], L.SITES[b]


def test_floor_is_distance_over_c_and_no_route_beats_it():
    for a in L.SITES.values():
        for b in L.SITES.values():
            if a == b or not (a.on_earth or b.on_earth):
                continue
            r = L.routes(a, b)
            for name, x in r["routes"].items():
                assert x["delay_s"] >= r["floor_s"] * (1 - 1e-12), (a.name, b.name, name)
                assert x["stretch"] >= 1 - 1e-12
            assert r["chord_floor_s"] <= r["floor_s"] * (1 + 1e-12)


def test_geometry_limits():
    ant = L.antipodal_floor_s()
    assert ant["great_circle_s"] == pytest.approx(math.pi * L.EARTH_RADIUS_M / C)       # 66.8 ms
    assert ant["chord_s"] == pytest.approx(2 * L.EARTH_RADIUS_M / C)                    # 42.5 ms
    a = L.Site("A", 0.0, 0.0)
    b = L.Site("B", 0.0, 90.0)                                                          # a quarter of the equator
    d = L.distances_m(a, b)
    assert d["angle_rad"] == pytest.approx(math.pi / 2) and d["chord_m"] == pytest.approx(math.sqrt(2) * L.EARTH_RADIUS_M)
    near = L.Site("N", 0.0, 1e-6)
    assert L.distances_m(a, near)["great_circle_m"] == pytest.approx(L.EARTH_RADIUS_M * math.radians(1e-6), rel=1e-6)


def test_route_lengths_follow_their_geometry():
    a, b = L.Site("A", 0.0, 0.0), L.Site("B", 0.0, 60.0)
    th = math.pi / 3
    r = L.routes(a, b, leo_altitude_m=550e3, fiber_stretch=1.5)["routes"]
    assert r["terrestrial fiber"]["delay_s"] == pytest.approx(1.5 * 1.47 * L.EARTH_RADIUS_M * th / C)
    assert r["hollow-core fiber"]["delay_s"] == pytest.approx(1.5 * 1.003 * L.EARTH_RADIUS_M * th / C)
    assert r["LEO laser mesh"]["length_m"] == pytest.approx(2 * 550e3 + (L.EARTH_RADIUS_M + 550e3) * th)
    rg = L.EARTH_RADIUS_M + L.GEO_ALTITUDE_M
    leg = math.sqrt(L.EARTH_RADIUS_M ** 2 + rg ** 2 - 2 * L.EARTH_RADIUS_M * rg * math.cos(th / 2))
    assert r["geostationary relay"]["length_m"] == pytest.approx(2 * leg)
    far = L.routes(L.Site("A", 0.0, 0.0), L.Site("B", 0.0, 170.0))["routes"]       # beyond 162.6°: no single GEO relay
    assert "geostationary relay" not in far


def test_leo_beats_fiber_far_away_and_loses_next_door():
    la_ny = L.report("Los Angeles", "New York")
    assert la_ny["best"] == "LEO laser mesh" and la_ny["routes"]["LEO laser mesh"]["stretch"] < la_ny["routes"]["terrestrial fiber"]["stretch"]
    london_sydney = L.report("London", "Sydney")
    th, R, h = london_sydney["distances"]["angle_rad"], L.EARTH_RADIUS_M, L.LEO_ALTITUDE_M
    assert london_sydney["best"] == "LEO laser mesh" and london_sydney["best_stretch"] == pytest.approx((2 * h + (R + h) * th) / (R * th))
    assert london_sydney["best_stretch"] < 1.2 < london_sydney["routes"]["terrestrial fiber"]["stretch"]
    close = L.routes(L.SITES["Carson, CA (CSUDH)"], L.SITES["Los Angeles"])["routes"]  # 21 km: the climb to 550 km dominates
    assert close["hollow-core fiber"]["delay_s"] < close["LEO laser mesh"]["delay_s"]


def test_space_endpoints_use_the_straight_line():
    moon = L.report("Los Angeles", "the Moon")
    assert set(moon["routes"]) == {"free space"} and moon["best_delay_s"] == pytest.approx(L.MOON_MEAN_DISTANCE_M / C)
    assert 1.27 < moon["best_delay_s"] < 1.29
    mars = L.report("Los Angeles", "Mars at its farthest")
    assert 21 * 60 < mars["best_delay_s"] < 23 * 60


def test_banking_brings_secure_messages_and_teleportation_to_the_floor():
    t = 0.0123
    lat = L.message_latency_s(t)
    assert lat["secure message"] == {"banked key": t, "QKD on demand": 3 * t, "TCP + TLS 1.3, new connection": 5 * t}
    assert lat["teleported qubit"] == {"banked pairs": t, "pair sent on demand": 2 * t}
    assert min(lat["secure message"].values()) == t                                   # nothing beats one trip


def test_bad_inputs_are_rejected():
    for kw in ({"lat_deg": 91, "lon_deg": 0}, {"lat_deg": 0, "lon_deg": 200}, {"range_m": -1.0}, {}, {"lat_deg": 0, "lon_deg": 0, "range_m": 1.0}):
        with pytest.raises(ValueError):
            L.Site("x", **kw)
    with pytest.raises(ValueError):
        L.routes(L.SITES["London"], L.SITES["Tokyo"], fiber_stretch=0.9)
    with pytest.raises(ValueError):
        L.message_latency_s(float("nan"))
    with pytest.raises(ValueError):
        L.distances_m(L.SITES["the Moon"], L.SITES["Mars at its closest"])


def test_leo_crossover_is_where_the_routes_tie():
    for n in (L.FIBER_INDEX, L.HOLLOW_CORE_INDEX):
        km = L.leo_crossover_km(n)
        th = km * 1e3 / L.EARTH_RADIUS_M
        b = L.Site("B", 0.0, math.degrees(th))
        r = L.routes(L.Site("A", 0.0, 0.0), b)["routes"]
        name = "terrestrial fiber" if n == L.FIBER_INDEX else "hollow-core fiber"
        assert r["LEO laser mesh"]["delay_s"] == pytest.approx(r[name]["delay_s"], rel=1e-9)
    assert 900 < L.leo_crossover_km() < 1100 and 2400 < L.leo_crossover_km(L.HOLLOW_CORE_INDEX) < 2800
    assert L.leo_crossover_km(1.0, 1.0) == math.inf                      # straight vacuum-speed fiber: the climb never pays
