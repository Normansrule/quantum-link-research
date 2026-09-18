"""Phase 3 part 2: QKD protocols as ClassicalMessage rounds, bounded by PLOB (REQ-QKD-002)."""
import math

import numpy as np
import pytest

from qll.channels.light_time_delay import one_way_delay_s
from qll.constants.astro import EARTH_MARS_MIN_M
from qll.hardware.randomness import NumpyPRNG
from qll.qkd.bb84 import run_bb84
from qll.qkd.decoy_state import decoy_rate_per_pulse, no_decoy_pns_rate_per_pulse
from qll.qkd.e91 import di_rate_per_round, e91_rate_from_werner
from qll.qkd.error_correction import minimum_leak_bits, reconcile
from qll.qkd.key_rate import bb84_rate_per_sifted_bit
from qll.qkd.mdi import mdi_rate_per_pulse
from qll.qkd.plob_bound import plob_bits_per_use
from qll.qkd.privacy_amplification import final_key_length, toeplitz_hash
from qll.qkd.rate_bounds import assert_below_plob
from qll.qkd.sifting import sift, sifting_fraction_biased
from qll.qkd.twin_field import crossover_transmittance, twin_field_rate_per_pulse

pytestmark = pytest.mark.phase3


def test_sifting_half_and_biased():
    rng = np.random.default_rng(0)
    s = sift(rng.integers(0, 2, 20000), rng.integers(0, 2, 20000))
    assert abs(s.fraction - 0.5) < 0.02
    assert sifting_fraction_biased(0.5) == 0.5 and sifting_fraction_biased(0.9) == pytest.approx(0.82)


def test_bb84_ideal_intercept_resend_and_rate():
    r = run_bb84(40000, allow_pseudo=True)
    assert r.qber == 0.0 and r.secret_fraction_per_sifted == 1.0 and r.secret_bits > 0.45 * r.n_sent
    e = run_bb84(40000, intercept_resend=True, allow_pseudo=True)
    assert abs(e.qber - 0.25) < 0.01 and e.secret_bits == 0                 # 25% QBER → no key
    n = run_bb84(40000, channel_error=0.05, allow_pseudo=True)
    assert abs(n.secret_fraction_per_sifted - bb84_rate_per_sifted_bit(n.qber)) < 1e-9 and abs(n.qber - 0.05) < 0.01
    with pytest.raises(ValueError):
        run_bb84(100, entropy=NumpyPRNG(0))                                  # INV-7


def test_bb84_classical_time_respects_light_time():                            # INV-1
    r = run_bb84(2000, distance_m=EARTH_MARS_MIN_M, allow_pseudo=True, ec_scheme="ldpc")
    assert r.classical_time_s >= 2 * one_way_delay_s(EARTH_MARS_MIN_M)
    c = run_bb84(2000, distance_m=EARTH_MARS_MIN_M, allow_pseudo=True, ec_scheme="cascade")
    assert c.classical_time_s > r.classical_time_s + 3 * 2 * one_way_delay_s(EARTH_MARS_MIN_M)


def test_reconciliation_leak_and_privacy_amplification():
    a = np.random.default_rng(1).integers(0, 2, 1000, dtype=np.int8)
    rec = reconcile(a, a, 0.05)
    assert rec.leaked_bits >= minimum_leak_bits(1000, 0.05)
    l = final_key_length(100000, 0.05, 1.1 * 100000 * 0.2864)
    assert abs(l / 100000 - bb84_rate_per_sifted_bit(0.05) * 1.0) < 0.05     # ~ n(1 - 2.1 h2(Q))
    k = toeplitz_hash(a, 100, seed=3)
    assert k.shape == (100,) and set(k.tolist()) <= {0, 1}


def test_e91_di_rate_limits():
    assert di_rate_per_round(2 * math.sqrt(2), 0.0) == pytest.approx(1.0)
    assert di_rate_per_round(2.0, 0.0) == 0.0
    assert e91_rate_from_werner(1.0) == pytest.approx(1.0) and e91_rate_from_werner(0.8) == 0.0


def test_decoy_scales_linearly_and_pns_quadratically():
    r1, r2 = decoy_rate_per_pulse(1e-2), decoy_rate_per_pulse(1e-3)
    assert 8 < r1 / r2 < 12                                                   # ~ eta
    assert decoy_rate_per_pulse(1e-4) > no_decoy_pns_rate_per_pulse(1e-4)     # decoys win at high loss


def test_mdi_and_twin_field_scalings():
    assert 8 < mdi_rate_per_pulse(1e-1) / mdi_rate_per_pulse(1e-2) < 12       # ~ eta (symmetric arms); dark counts bite below 1e-3
    assert twin_field_rate_per_pulse(1e-4) / twin_field_rate_per_pulse(1e-6) == pytest.approx(10.0)   # ~ sqrt(eta)
    eta_c = crossover_transmittance()
    assert twin_field_rate_per_pulse(eta_c / 10) > plob_bits_per_use(eta_c / 10)


def test_all_repeaterless_rates_below_plob():                                  # REQ-QKD-002, INV-5
    for eta in (1e-1, 1e-3, 1e-6):
        assert_below_plob(0.5 * bb84_rate_per_sifted_bit(0.03) * eta, eta, "bb84")   # per pulse: sifting × eta × fraction
        assert_below_plob(decoy_rate_per_pulse(eta), eta, "decoy")
        assert_below_plob(mdi_rate_per_pulse(eta), eta, "mdi")
    with pytest.raises(AssertionError):
        assert_below_plob(2.0, 0.5, "impossible")
