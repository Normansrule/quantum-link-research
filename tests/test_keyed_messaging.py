"""The messenger keyed by the program's links: supplies come from the twins, spending follows each policy, the bank is
the sequent-peak capacity, a preloaded bank lasts bank/net-drain days, and latency is the light time."""
import math

import pytest

from qll.app.key_bank import sequent_peak, simulate
from qll.channels.light_time_delay import one_way_delay_s
from qll.link import keyed_messaging as K
from qll.link import outdoor_link as O
from qll.link import satellite_pass as S
from qll.link import two_room
from qll.link.expected_session import expected_session

pytestmark = pytest.mark.phase6


def test_supplies_are_the_twins():
    src = K.sources()
    c = two_room.config()
    assert src["two rooms (P10)"]["bits_per_day"] == pytest.approx(expected_session(c)["key_bits"] / (c.n_pulses / c.pulse_rate_hz) * 86400, rel=1e-12)
    p = O.OutdoorParts(distance_m=1000.0, receiver=O.RECEIVERS["spad"])
    assert src["two buildings at night, 1 km"]["bits_per_day"] == pytest.approx(8 * 3600 * O.predict(p)["key_bits"] / 10.0, rel=1e-12)
    assert src["one satellite pass a night"]["bits_per_day"] == pytest.approx(S.pass_summary(S.PRESETS["micius"])["key_bits"], rel=1e-12)
    assert src["a Mars lander (key loaded before launch)"]["bits_per_day"] == 0


def test_spending_per_policy():
    assert K.bits_per_message("one-time pad", 200) == 8 * 200 + 127
    assert K.bits_per_message("QKD-keyed AES-256-GCM", 200, 100) == 2.56 == K.bits_per_message("hybrid ML-KEM + QKD", 5000, 100)
    assert K.bits_per_message("conventional ECDHE + AES (today)") == 0
    with pytest.raises(ValueError):
        K.bits_per_message("rot13")


def test_bank_is_the_sequent_peak_and_never_refuses():
    r = K.plan("two buildings at night, 1 km", "one-time pad", messages_per_day=500)
    assert r["bank_bits"] == pytest.approx(500 * (8 * 200 + 127), rel=1e-12)      # all key arrives at night, all spending by day
    supply = K.sources()["two buildings at night, 1 km"]["hourly_bits"] * 3
    demand = K.demand_hourly(500, r["bits_per_message"]) * 3
    run = simulate(supply, demand, capacity=r["bank_bits"] * (1 + 1e-12))
    assert run.refused_days == 0
    assert K.plan("two rooms (P10)", "one-time pad", messages_per_day=500)["bank_bits"] == 0      # the rooms out-supply every hour
    assert sequent_peak(K.sources()["one satellite pass a night"]["hourly_bits"], K.demand_hourly(100, 2.56)) == pytest.approx(256, rel=1e-9)


def test_demand_above_supply_fails_closed():
    r = K.plan("one satellite pass a night", "one-time pad", messages_per_day=10_000)
    assert not r["sustainable"] and math.isinf(r["bank_bits"])
    assert K.plan("one satellite pass a night", "one-time pad", messages_per_day=1000)["sustainable"]


def test_lander_bank_and_latency():
    r = K.plan("a Mars lander (key loaded before launch)", "one-time pad", messages_per_day=500, preloaded_bits=8e12, distance_m=4.0e11)
    assert r["preload_days"] == pytest.approx(8e12 / (500 * 1727), rel=1e-12)       # a terabyte of pad: tens of thousands of years
    assert r["one_way_s"] == pytest.approx(one_way_delay_s(4.0e11)) and r["round_trip_s"] == pytest.approx(2 * r["one_way_s"])
    aes = K.plan("a Mars lander (key loaded before launch)", "QKD-keyed AES-256-GCM", messages_per_day=500, preloaded_bits=8e12)
    assert aes["preload_days"] > 600 * r["preload_days"]
