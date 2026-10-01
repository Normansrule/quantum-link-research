"""The tabletop Mars-link bench (P09): the twin's laws against analytic results, and the report recovering a known
bench from synthetic data."""
import math

import numpy as np
import pytest

from qll.analysis.bench_fit import fit_error_fraction, fit_phase, fit_rejection, loglog_slope
from qll.analysis.bench_report import TRUE_FOR_SYNTHETIC, main, predictions, report, write_synthetic
from qll.channels.planetshine import lambert_geometric_albedo, lambert_phase, single_mode_photon_rate
from qll.constants.physical import C_LIGHT
from qll.systems.bench_twin import (BenchDesign, background_power_w, ball_flux_w, error_fraction, field_of_view_rad,
                                    irradiance_from_photocurrent, mars_schedule, mode_ratio, photon_energy_j, purity,
                                    rejection, signal_power_w, surface_power_w, werner_equivalent_error)

pytestmark = pytest.mark.phase1
B = BenchDesign()


def test_background_errors_are_the_budgets_werner_errors():
    for f0 in (1.0, 0.95, 0.8):
        for w in np.linspace(0.0, 1.0, 11):
            assert error_fraction(w, 2 * (1 - f0) / 3) == pytest.approx(werner_equivalent_error(w, f0), abs=1e-15)


def test_lambert_sphere_geometric_albedo_is_two_thirds():
    # flux of a Lambert sphere at full phase: (A E / pi) \int mu^2 dA / d^2 = (2A/3) E R^2 / d^2
    th = np.linspace(0, np.pi / 2, 4001)
    integral = 2 * np.pi * np.trapezoid(np.cos(th) ** 2 * np.sin(th), th)
    assert 0.9 / np.pi * integral == pytest.approx(lambert_geometric_albedo(0.9), rel=1e-6)
    assert ball_flux_w(B, 1.1) / ball_flux_w(B, 0.0) == pytest.approx(lambert_phase(1.1))


def test_single_mode_background_is_the_mars_formula_and_mmf_counts_modes():
    L = B.albedo * B.lamp_irradiance_nm / np.pi + B.room_radiance_nm
    B_hz = B.filter_nm * 1e-9 * C_LIGHT / B.wavelength_m**2
    rate = surface_power_w(B, "smf") / photon_energy_j(B) / B.coupling
    assert rate == pytest.approx(single_mode_photon_rate(L, B.wavelength_m, B_hz), rel=1e-12)
    wide = BenchDesign(lens_diameter_m=0.05)               # fiber-limited: the ratio is V^2 / 4
    V = 2 * np.pi * wide.mmf_core_radius_m * wide.mmf_na / wide.wavelength_m
    assert mode_ratio(wide) == pytest.approx(V**2 / 4, rel=1e-12)
    assert surface_power_w(B, "mmf", filter_nm=30.0) == pytest.approx(3 * surface_power_w(B, "mmf"))


def test_rejection_shapes():
    tm = field_of_view_rad(B, "smf")
    assert rejection(B, tm, "smf") == pytest.approx(math.exp(-2))
    assert rejection(B, 0.9 * field_of_view_rad(B, "mmf"), "mmf") == 1.0
    assert rejection(B, 0.05, "smf") == B.stray_light == rejection(B, 0.05, "mmf")


def test_ground_transmitter_in_daylight_is_swamped_and_space_is_clean():
    S = signal_power_w(B, "mmf")
    day, night = purity(S, background_power_w(B, "mmf", "day")), purity(S, background_power_w(B, "mmf", "night"))
    space = purity(S, background_power_w(B, "mmf", "space", offset_radii=5))
    assert day < 0.1 and night > 0.999 and space > 0.99
    with pytest.raises(ValueError):
        background_power_w(B, "mmf", "space", offset_radii=1.0)
    with pytest.raises(ValueError):
        background_power_w(B, "fiber", "day")


def test_calibration_and_schedule():
    I = B.lamp_irradiance_nm * B.responsivity_a_per_w * B.detector_area_m2 * B.filter_nm
    assert irradiance_from_photocurrent(B, I) == pytest.approx(B.lamp_irradiance_nm)
    od = mars_schedule(np.array([2.0, 1.0, 0.0, 0.2]))
    assert od[0] == 0.0 and od[1] == pytest.approx(math.log10(2)) and math.isinf(od[2])
    with pytest.raises(TypeError):
        BenchDesign(albedo=0.9 + 0j)


def test_fits_recover_known_laws():
    a = np.radians(np.arange(0, 121, 10))
    assert fit_phase(a, [3 * lambert_phase(x) for x in a]).scale == pytest.approx(3.0)
    assert loglog_slope([1, 2, 4], [5, 10, 20]) == pytest.approx(1.0)
    th = np.r_[0, np.linspace(1e-5, 3e-4, 10), np.geomspace(3e-3, 3e-2, 5)]
    fit = fit_rejection(th, [rejection(B, t, "smf") for t in th], "smf", far_rad=2e-3)
    assert fit.mode_rad == pytest.approx(field_of_view_rad(B, "smf"), rel=0.05) and fit.floor == pytest.approx(B.stray_light)
    w = np.linspace(0.2, 1, 9)
    assert fit_error_fraction(w, [error_fraction(x, 0.04) for x in w])[0] == pytest.approx(0.04)


def test_report_recovers_a_synthetic_bench(tmp_path):
    truth = write_synthetic(tmp_path, seed=3)
    r = report(tmp_path, save=str(tmp_path / "bench.svg"), quiet=True)
    assert r["lamp_irradiance_nm"] == pytest.approx(TRUE_FOR_SYNTHETIC["lamp_irradiance_nm"], rel=0.03)
    assert r["albedo"] == pytest.approx(truth.albedo, rel=0.03)
    assert r["floor_smf"] == pytest.approx(truth.stray_light, rel=0.1)
    assert r["e_opt"] == pytest.approx(truth.e_opt, abs=0.003)
    assert r["mode_smf"] == pytest.approx(field_of_view_rad(truth, "smf"), rel=0.05)
    assert r["mode_ratio"] == pytest.approx(mode_ratio(truth), rel=0.1)
    assert abs(r["distance_slope_mmf"]) < 0.1 and r["filter_slope_mmf"] == pytest.approx(1.0, abs=0.1)
    for meas, twin in r["purity"].values():
        assert meas == pytest.approx(twin, abs=0.02)
    assert r["run_refused_without"] > 0 and r["run_refused_with"] == 0
    assert (tmp_path / "bench.svg").exists()


def test_cli(tmp_path, capsys):
    main(["predict"])
    assert "purity" in capsys.readouterr().out
    main(["schedule", "--out", str(tmp_path / "s.csv"), "--steps", "40"])
    lines = (tmp_path / "s.csv").read_text().splitlines()
    assert len(lines) == 41 and "inf" in "".join(lines)            # conjunction closes the shutter
    assert predictions(B)["mode_ratio"] == pytest.approx(mode_ratio(B))


def test_logged_units():
    from dataclasses import replace

    from qll.systems.bench_twin import in_logged_unit
    counts = replace(B, signal_unit="photons_per_s")
    assert in_logged_unit(B, 2e-12) == 2e-12
    assert in_logged_unit(counts, 2e-12) == pytest.approx(2e-12 / photon_energy_j(B) * B.detection_efficiency)
    with pytest.raises(ValueError):
        in_logged_unit(replace(B, signal_unit="volts"), 1.0)
