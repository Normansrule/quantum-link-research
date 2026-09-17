import math
import pytest

from qll.qkd.binary_entropy import h2
from qll.qkd.key_rate import bb84_qber_threshold, bb84_rate_per_sifted_bit
from qll.qkd.plob_bound import plob_bits_per_use

pytestmark = pytest.mark.phase1


def test_binary_entropy_endpoints_and_midpoint():
    assert h2(0.0) == 0.0 and h2(1.0) == 0.0 and math.isclose(h2(0.5), 1.0)


def test_bb84_threshold_eleven_percent():
    assert math.isclose(bb84_qber_threshold(), 0.1100, abs_tol=5e-4)


def test_bb84_rate_positive_at_five_percent():
    assert bb84_rate_per_sifted_bit(0.05) > 0.0


def test_bb84_rate_zero_at_twelve_percent():
    assert bb84_rate_per_sifted_bit(0.12) == 0.0


def test_plob_small_eta_limit():
    eta = 1e-4
    assert math.isclose(plob_bits_per_use(eta), eta / math.log(2), rel_tol=1e-3)


def test_plob_monotone():
    vals = [plob_bits_per_use(e) for e in (1e-6, 1e-4, 1e-2, 0.5, 0.9)]
    assert all(a < b for a, b in zip(vals, vals[1:]))
