import math
import pytest

from qll.constants.astro import AU_METERS, EARTH_MARS_MAX_M, EARTH_MARS_MIN_M
from qll.constants.physical import C_LIGHT
from qll.channels.light_time_delay import ClassicalMessage, NotYetArrived, one_way_delay_s

pytestmark = pytest.mark.phase1


def test_speed_of_light_is_exact():
    assert C_LIGHT == 299792458.0


def test_one_au_light_time():
    assert math.isclose(one_way_delay_s(AU_METERS), 499.005, abs_tol=1e-3)


def test_earth_mars_one_way_minutes_and_no_early_receive():
    lo, hi = one_way_delay_s(EARTH_MARS_MIN_M) / 60, one_way_delay_s(EARTH_MARS_MAX_M) / 60
    assert 3.0 <= lo <= 3.2 and 22.0 <= hi <= 22.6
    msg = ClassicalMessage(payload=(0, 1), sent_at_s=0.0, distance_m=EARTH_MARS_MIN_M)
    with pytest.raises(NotYetArrived):
        msg.receive(now_s=1.0)
    assert msg.receive(now_s=msg.earliest_arrival_s) == (0, 1)
