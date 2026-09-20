"""Third-party simulators must agree with the analytic models: Perceval (linear optics) and SeQUeNCe (network)."""
import pytest

from qll.channels.light_time_delay import round_trip_delay_s
from qll.circuits.bell_measurement import BellMeasurement
from qll.hardware.beam_splitter import hom_coincidence_probability as hom_analytic

pytestmark = [pytest.mark.phase3, pytest.mark.slow]


@pytest.mark.parametrize("V", [1.0, 0.5, 0.0])
def test_perceval_hom_matches_analytic(V):
    pcvl = pytest.importorskip("perceval")
    from qll.hardware.perceval_adapter import hom_coincidence_probability
    assert hom_coincidence_probability(V) == pytest.approx(hom_analytic(0.5, V), abs=1e-9)


def test_perceval_bell_analyser_success_is_one_half():
    pytest.importorskip("perceval")
    from qll.hardware.perceval_adapter import bell_state_analyser_success
    assert bell_state_analyser_success() == BellMeasurement("linear_optics").success_probability == 0.5


def test_sequence_link_respects_light_time_and_slows_with_distance():
    pytest.importorskip("sequence")
    from qll.network.sequence_adapter import two_router_link
    near = two_router_link(10e3, n_pairs=5, stop_s=3.0)
    assert near.n_delivered == 5
    assert all(t >= near.herald_round_trip_s for t in near.delivery_times_s)          # INV-1 inside SeQUeNCe
    assert all(0.8 <= f <= 1.0 for f in near.fidelities)
    far = two_router_link(60e3, n_pairs=5, stop_s=3.0)
    assert far.mean_delivery_s > near.mean_delivery_s                                  # loss and herald time both grow
    assert far.herald_round_trip_s == pytest.approx(round_trip_delay_s(30e3 * 1.47))
