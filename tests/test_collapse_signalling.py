"""The collapse code (experiments/proposed/E17): no choice of Alice's reaches Bob's statistics, the analysis bounds
the information per use as 1/n, and both controls (teleportation with its two bits, and a physical leak) are seen."""
import numpy as np
import pytest
from scipy import stats

from qll.circuits import collapse_signalling as C
from qll.circuits.bell import bell_state, werner_state

pytestmark = pytest.mark.phase2
MSG = np.random.default_rng(1).integers(0, 2, 200)


def _haar_state(rng, d=4):
    v = rng.normal(size=d) + 1j * rng.normal(size=d)
    return v / np.linalg.norm(v)


def _random_instrument(rng, k=3):
    """A random k-outcome instrument: the top 2 rows of a Haar unitary on C^(2k) give Kraus operators summing to I."""
    z = rng.normal(size=(2 * k, 2 * k)) + 1j * rng.normal(size=(2 * k, 2 * k))
    q, r = np.linalg.qr(z)
    q = q * (np.diag(r) / np.abs(np.diag(r)))
    v = q[:, :2]                                                  # isometry C^2 -> C^(2k)
    return [v[2 * i:2 * i + 2, :] for i in range(k)]


def test_no_instrument_of_alices_changes_bobs_state():
    rng = np.random.default_rng(7)
    for _ in range(50):
        psi = _haar_state(rng)
        rho = np.outer(psi, psi.conj())
        before = C.bob_state_after(rho, [np.eye(2)])
        ks = _random_instrument(rng)
        assert np.allclose(sum(k.conj().T @ k for k in ks), np.eye(2), atol=1e-12)
        assert np.allclose(C.bob_state_after(rho, ks), before, atol=1e-12)
    for f in (0.25, 0.7, 1.0):                                    # mixed states too: Bob's half stays I/2
        rho = werner_state(f)
        for s in C.SCHEMES:
            for x in (0, 1):
                assert np.allclose(C.bob_state_after(rho, C.instrument(s, x)), np.eye(2) / 2, atol=1e-12)


def test_joint_probabilities_are_correlated_but_bobs_marginal_is_flat():
    for alpha in np.linspace(0, np.pi, 7):
        for v in (0.5, 0.97, 1.0):
            P = [[C.joint_probability(a, b, alpha, 0.0, v) for b in (0, 1)] for a in (0, 1)]
            assert np.isclose(np.sum(P), 1.0)
            assert np.allclose(np.sum(P, axis=0), 0.5)                 # Bob
            assert np.allclose(np.sum(P, axis=1), 0.5)                 # Alice
    assert np.isclose(C.joint_probability(0, 0, 0.0, 0.0), 0.5)        # perfect correlation in a shared basis
    rho = np.outer(bell_state("phi+"), bell_state("phi+").conj())      # the formula is the Born rule for |Phi+>
    for alpha, beta in ((0.3, 1.1), (np.pi / 4, 0.0)):
        pa, pb = C.projectors(alpha), C.projectors(beta)
        for a in (0, 1):
            for b in (0, 1):
                assert np.isclose(np.trace(np.kron(pa[a], pb[b]) @ rho).real, C.joint_probability(a, b, alpha, beta))


@pytest.mark.parametrize("scheme", C.SCHEMES)
def test_bob_cannot_read_the_collapse_code(scheme):
    r = C.simulate(MSG, 500, scheme, seed=3)
    v = C.analyze(r.x, r.b)
    assert not v.signalling_detected and v.p_value > 0.05
    assert v.bias_interval[0] < 0 < v.bias_interval[1]
    assert v.mi_upper < 3e-4
    assert 0.3 < C.decode(r.b, r.symbol, MSG) < 0.7                   # no better than a coin on the held-out slots


def test_the_test_has_the_right_size_under_the_null():
    p = [C.analyze(*(lambda r: (r.x, r.b))(C.simulate(MSG[:40], 200, "basis", seed=s))).p_value for s in range(200)]
    assert stats.kstest(p, "uniform").pvalue > 0.01                   # p-values uniform: the 1 % level means 1 %


def test_the_bound_on_information_per_use_falls_as_one_over_n():
    ub = [C.analyze(*(lambda r: (r.x, r.b))(C.simulate(MSG, n, "basis", seed=4))).mi_upper for n in (100, 1000, 10000)]
    assert ub[0] > ub[1] > ub[2]
    assert 5 < ub[0] / ub[1] < 20 and 5 < ub[1] / ub[2] < 20


def test_mutual_information_and_its_convexity_bound():
    assert C.mutual_information(0.5, 0.5) == 0.0 and np.isclose(C.mutual_information(0.0, 1.0), 1.0)
    d = 0.01                                                           # near 1/2: delta^2 / (2 ln 2)
    assert np.isclose(C.mutual_information(0.5 - d / 2, 0.5 + d / 2), d ** 2 / (2 * np.log(2)), rtol=1e-3)
    rng = np.random.default_rng(0)                                     # corners bound every channel in the box
    for _ in range(200):
        lo0, lo1 = rng.uniform(0, 0.9, 2); hi0, hi1 = lo0 + rng.uniform(0, 0.1), lo1 + rng.uniform(0, 0.1)
        corner = max(C.mutual_information(a, b) for a in (lo0, hi0) for b in (lo1, hi1))
        inside = C.mutual_information(rng.uniform(lo0, hi0), rng.uniform(lo1, hi1))
        assert inside <= corner + 1e-12


def test_controls_classical_bits_and_a_physical_leak_are_detected():
    x, sym, b = C.teleport_bits(MSG, 1, with_classical_bits=True)
    assert C.decode(b, sym, MSG) == 0.0                                # with Alice's two bits: the message arrives
    x, sym, b = C.teleport_bits(MSG, 1, with_classical_bits=False, seed=2)
    assert 0.3 < C.decode(b, sym, MSG) < 0.7                           # without them: a coin
    r = C.simulate(MSG, 2000, "measure", leak=0.1, seed=5)
    v = C.analyze(r.x, r.b)
    assert v.signalling_detected and v.bias == pytest.approx(-0.05, abs=0.005)     # P(b=1|x=1) = (1 - leak)/2
    assert C.decode(r.b, r.symbol, MSG) < 0.1


def test_sample_size_detects_the_bias_it_was_sized_for():
    n = C.uses_to_detect(0.02, alpha=0.01, power=0.9)
    z = stats.norm.ppf(0.995) + stats.norm.ppf(0.9)
    assert n == pytest.approx(z ** 2 / (2 * 0.02 ** 2), rel=1e-3)
    hits = 0
    for s in range(60):                                                # empirical power close to 0.9
        rng = np.random.default_rng(100 + s)
        b0 = rng.random(n) < 0.49; b1 = rng.random(n) < 0.51
        v = C.analyze(np.r_[np.zeros(n), np.ones(n)], np.r_[b0, b1].astype(int))
        hits += v.p_value < 0.01
    assert 0.75 < hits / 60 <= 1.0


def test_qiskit_circuits_agree_with_the_model():
    pytest.importorskip("qiskit_aer")
    for scheme in C.SCHEMES:
        x, b = C.counts_to_outcomes(C.run_aer(scheme, 40_000, seed=11))
        v = C.analyze(x, b)
        assert v.p_value > 0.001 and v.mi_upper < 2e-4
    counts = C.run_aer("basis", 40_000, seed=11)
    same = lambda c: sum(n for k, n in c.items() if k[0] == k[1]) / sum(c.values())
    assert same(counts[0]) == 1.0 and abs(same(counts[1]) - 0.5) < 0.01   # a = b in a shared basis; 50 % at 45 degrees
    x, b = C.counts_to_outcomes(C.run_aer("measure", 200_000, leak=0.05, seed=12))
    assert C.analyze(x, b).bias == pytest.approx(-0.025, abs=0.005)


def test_hardware_path_rehearses_on_a_fake_device():
    pytest.importorskip("qiskit_ibm_runtime")
    pytest.importorskip("qiskit_aer")
    from qiskit_ibm_runtime.fake_provider import FakeTorino
    counts = C.run_on_backend(FakeTorino(), "basis", shots=4000, layout=(0, 1), repeats=2, seed=3)
    assert sum(counts[0].values()) == sum(counts[1].values()) == 8000
    x, b = C.counts_to_outcomes(counts)
    v = C.analyze(x, b)
    assert v.p_value > 1e-4                                            # the fake device has noise but no crosstalk model
