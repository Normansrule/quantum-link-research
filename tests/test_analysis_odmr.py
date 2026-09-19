"""The ODMR pipeline must recover D and B from synthetic spectra before it sees real ones."""
import numpy as np
import pytest

from qll.analysis.odmr_fit import D_TEMPERATURE_COEFF_HZ_PER_K, fit_odmr, load_csv, synthetic_odmr
from qll.hardware.nv_node import D_ZFS_HZ

pytestmark = pytest.mark.phase1


@pytest.mark.parametrize("B", [10.0, 30.0, 55.0])   # 80 G would push the lines outside the 2.70-3.05 GHz sweep
def test_fit_recovers_field_and_zfs(B):
    f, s = synthetic_odmr(B, seed=1)
    fit = fit_odmr(f, s, 2, photon_rate_hz=1e10)
    assert fit.B_parallel_gauss == pytest.approx(B, abs=0.5)
    assert fit.D_hz == pytest.approx(D_ZFS_HZ, abs=0.5e6)
    assert 0.015 < fit.contrasts.mean() < 0.025 and 6e6 < fit.widths_hz.mean() < 10e6
    assert fit.sensitivity_t_per_sqrt_hz < 1e-6 and fit.residual_rms < 0.01


def test_temperature_shift_of_d():
    f, s = synthetic_odmr(20.0, T_kelvin=350.0, seed=2)
    assert fit_odmr(f, s).D_hz == pytest.approx(D_ZFS_HZ + 50 * D_TEMPERATURE_COEFF_HZ_PER_K, abs=0.5e6)


def test_example_csv_loads_and_fits():
    f, s = load_csv("data/_examples/2026-09-19_synthetic_odmr_30G.csv")
    assert fit_odmr(f, s).B_parallel_gauss == pytest.approx(30.0, abs=0.5)
