"""Phase 3: exact Gaussian beam, atmosphere, pointing, link budgets reproducing published missions, hardware models."""
import math

import numpy as np
import pytest

from qll.channels.atmosphere import airmass, atmospheric_transmittance
from qll.channels.free_space_diffraction import beam_radius_m, geometric_transmittance, geometric_transmittance_far_field
from qll.channels.link_budget import JINAN1_2025, MICIUS_2017, LinkBudget, slant_range_m
from qll.channels.pointing_jitter import pointing_efficiency
from qll.hardware.beam_splitter import beam_splitter_unitary, hom_coincidence_probability
from qll.hardware.detector import SI_SPAD, SNSPD
from qll.hardware.nv_node import D_ZFS_HZ, GAMMA_E_HZ_PER_G, NvNode, odmr_frequencies_hz
from qll.hardware.photon_source import SingleEmitterSource, SpdcSource, WeakCoherentSource
from qll.qkd.plob_bound import plob_bits_per_use

pytestmark = pytest.mark.phase3


def test_exact_gaussian_reduces_to_far_field_and_near_field_limits():           # REQ-CHN-002
    exact = geometric_transmittance(2e6, 810e-9, 0.05, 0.3)
    approx = geometric_transmittance_far_field(2e6, 810e-9, 0.05, 0.3)
    assert exact / approx == pytest.approx(2.0, rel=0.02)   # Gaussian peak intensity is 2x the uniform-disc estimate
    assert geometric_transmittance(1.0, 810e-9, 0.05, 1.0) > 0.999              # near field, big aperture
    assert geometric_transmittance(2e6, 810e-9, 0.05, 0.3) / geometric_transmittance(4e6, 810e-9, 0.05, 0.3) == pytest.approx(4.0, rel=0.05)
    assert beam_radius_m(0.0, 810e-9, 0.05) == pytest.approx(0.05)


def test_atmosphere_and_pointing_limits():
    assert airmass(90) == pytest.approx(1.0)
    assert atmospheric_transmittance(90, 1550e-9) > atmospheric_transmittance(90, 810e-9) > atmospheric_transmittance(20, 810e-9)
    assert pointing_efficiency(0.0, 1e6, 5.0) == 1.0
    assert 0.5 < pointing_efficiency(1e-6, 0.5e6, 2.0) < 1.0


def test_micius_two_downlink_loss_within_3db_of_reported():                      # REQ-F2-001 (part 1)
    # Yin et al. 2017 report 64-82 dB total (two downlinks) for ranges ~1000-2000 km
    lo = 2 * MICIUS_2017.loss_db(slant_range_m(500e3, 30), 30)   # ~900 km each
    hi = 2 * MICIUS_2017.loss_db(slant_range_m(500e3, 15), 15)   # ~1400 km each
    assert 64 - 3 <= lo <= 82 + 3 and 64 - 3 <= hi <= 82 + 3


def test_jinan1_single_downlink_loss_plausible():                                 # REQ-F2-001 (part 2, TODO tighten)
    loss = JINAN1_2025.loss_db(slant_range_m(500e3, 45), 45)
    assert 30 <= loss <= 60


def test_qber_floor_and_plob_consistency():
    q = LinkBudget.qber_from_background(1e4, 1e5, 1e-9, 1e8)
    assert q == pytest.approx(0.25)                          # 1e-4 signal/gate vs 1e-4 background/gate
    assert LinkBudget.qber_from_background(1e4, 1e3, 1e-9, 1e8) < 0.01
    eta = MICIUS_2017.eta_total(slant_range_m(500e3, 45), 45)
    assert plob_bits_per_use(eta) < 1.5 * eta                                      # INV-5 sanity (REQ-QKD-002 groundwork)


def test_sources_statistics():
    s = SpdcSource(0.01)
    assert abs(sum(s.p_n_pairs(n) for n in range(50)) - 1) < 1e-9
    assert 0.015 < s.heralded_g2() < 0.045   # ~2x for small x, x = 0.01 (heralded thermal-minus-vacuum)
    w = WeakCoherentSource(0.5)
    assert w.p_n(0) == pytest.approx(math.exp(-0.5))
    assert 0.2 < w.multiphoton_fraction() < 0.3
    e = SingleEmitterSource()
    assert 1e-7 < e.herald_probability_two_photon() < 1e-4


def test_detectors_and_hom():
    assert SI_SPAD.p_click(0, 1e-9) == pytest.approx(1 - math.exp(-100 * 1e-9))
    assert SNSPD.p_click(1, 1e-9) > 0.93
    U = beam_splitter_unitary()
    assert np.allclose(U.conj().T @ U, np.eye(2))
    assert hom_coincidence_probability(0.5, 1.0) == pytest.approx(0.0)
    assert hom_coincidence_probability(0.5, 0.0) == pytest.approx(0.5)


def test_nv_odmr_lines_and_herald_rate():
    f1, f2 = odmr_frequencies_hz([0, 0, 50])
    assert f1 == pytest.approx(D_ZFS_HZ - 50 * GAMMA_E_HZ_PER_G, rel=1e-6)
    assert f2 == pytest.approx(D_ZFS_HZ + 50 * GAMMA_E_HZ_PER_G, rel=1e-6)
    node = NvNode()
    assert 1e-6 < node.herald_probability() < 1e-4
    assert NvNode(purcell_factor=30).herald_probability() > 10 * node.herald_probability()
