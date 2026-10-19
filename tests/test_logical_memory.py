"""A logical qubit kept by repeated syndrome extraction with reused ancillas (qll/circuits/logical_memory.py): the
circuits have exactly 2d^2 - 1 qubits, measure and reset every ancilla every round, make no logical errors without
noise, and show the threshold: more distance helps below it and hurts above it."""
import pytest

from qll.circuits import logical_memory as LM
from qll.network.pair_ledger import cycles_to_survival, survival_probability

pytestmark = pytest.mark.phase2
pytest.importorskip("stim")
pytest.importorskip("pymatching")


@pytest.mark.parametrize("d,total", [(3, 17), (5, 49), (7, 97)])
def test_resources_match_the_circuit_and_ancillas_are_reused_every_round(d, total):
    r = LM.resources(d)
    assert (r.data, r.ancillas, r.total, r.correctable_faults) == (d * d, d * d - 1, total, (d - 1) // 2)
    census = LM.circuit_census(LM.memory_circuit(d, 0.001, rounds=4))
    assert census["qubits"] == total
    assert census["measure_and_reset"] == r.ancillas * 4                                # every ancilla, every round


def test_no_noise_no_logical_errors():
    assert LM.logical_error(5, 0.0, shots=2000)["failures"] == 0


def test_redundancy_pays_below_threshold_and_hurts_above_it():
    below = [LM.logical_error(d, 0.002, shots=20_000, seed=1)["p_shot"] for d in LM.DISTANCES]
    above = [LM.logical_error(d, 0.012, shots=20_000, seed=2)["p_shot"] for d in LM.DISTANCES]
    assert below[0] > below[1] > below[2]
    assert above[0] < above[1] < above[2]


def test_per_round_error_sets_how_long_the_memory_survives():
    r = LM.logical_error(3, 0.002, shots=20_000, seed=3)
    assert r["p_round"] == pytest.approx(1 - (1 - r["p_shot"]) ** (1 / 3))
    n = cycles_to_survival(r["p_round"], 0.5)
    assert survival_probability(r["p_round"], n) >= 0.5 > survival_probability(r["p_round"], n + 1)


def test_bad_inputs_are_rejected():
    for d in (2, 4, 1, 3.0):
        with pytest.raises(ValueError):
            LM.resources(d)
    with pytest.raises(ValueError):
        LM.memory_circuit(3, 0.6)
    with pytest.raises(ValueError):
        LM.memory_circuit(3, 0.01, rounds=0)
