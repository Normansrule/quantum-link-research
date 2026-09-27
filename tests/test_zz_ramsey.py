"""The conditional-Ramsey ZZ measurement recovers a ZZ it did not know: circuits for hardware use delays, the
simulated fringes follow the analytic P1(tau), and the fit returns the injected ZZ (both signs), zero when there is
none, and the exact-diagonalisation ZZ of a tunable-coupler pair."""
import numpy as np
import pytest

from qll.circuits.zz_ramsey import fit_ramsey, measure_zz, ramsey_circuit, simulate
from qll.hardware.tunable_coupler import CoupledPair

pytestmark = pytest.mark.phase1
T = np.linspace(0, 30, 121)


def test_hardware_circuit_uses_delays_and_simulation_circuit_injects_zz():
    hw = ramsey_circuit(2.0, True, 0.5)
    names = [i.operation.name for i in hw.data]
    assert names.count("delay") == 2 and "rzz" not in names and names.count("x") == 1
    sim = ramsey_circuit(2.0, False, 0.5, zz_mhz=0.1, t2_us=40.0)
    names = [i.operation.name for i in sim.data]
    assert "rzz" in names and "delay" not in names and "kraus" in names and "x" not in names


def test_fringe_matches_the_analytic_ramsey_formula():
    zz, delta, t2 = 0.08, 0.5, 40.0
    d = simulate(T, delta, zz, t2, shots=20000, seed=3)
    for s, sign in ((0, +1), (1, -1)):
        f = delta + sign * zz / 2
        expected = 0.5 - 0.5 * np.exp(-T / t2) * np.cos(2 * np.pi * f * T)
        assert np.max(np.abs(d[s] - expected)) < 0.02          # 20 000 shots: 3.5 sigma of binomial noise


@pytest.mark.parametrize("zz", [0.05, -0.08, 0.0])
def test_fit_recovers_the_injected_zz(zz):
    d = simulate(T, 0.5, zz)
    assert measure_zz(T, d[0], d[1]) == pytest.approx(zz, abs=1.5e-3)       # 1.5 kHz
    f, t2 = fit_ramsey(T, d[0])
    assert t2 == pytest.approx(40.0, rel=0.1)


def test_recovers_the_coupler_model_zz_and_the_idle_point():
    pair = CoupledPair()
    for wc in (5.0, 6.0):
        z = pair.zz(wc) * 1e3
        d = simulate(T, 0.5, z, seed=11)
        assert measure_zz(T, d[0], d[1]) == pytest.approx(z, rel=0.03)
    z_idle = pair.zz(pair.zz_free_frequency(5.0, 5.5)) * 1e3
    d = simulate(T, 0.5, z_idle, seed=11)
    assert abs(measure_zz(T, d[0], d[1])) < 1.5e-3                             # below the experiment's resolution


def test_rejects_complex_input():
    with pytest.raises(TypeError):
        fit_ramsey(T, T + 0j)
    with pytest.raises(TypeError):
        ramsey_circuit(1.0 + 0j, False, 0.5)
