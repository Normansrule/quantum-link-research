"""A logical qubit kept alive by repeated syndrome extraction with reused ancillas: the rotated surface code at
distances 3, 5, and 7 under circuit-level noise, decoded by minimum-weight perfect matching.

Physics
-------
A distance-d rotated surface code stores one logical qubit in d^2 data qubits and measures d^2 - 1 stabilizers with
one ancilla each, 2 d^2 - 1 physical qubits in all (17, 49, 97 for d = 3, 5, 7); it corrects any (d - 1)/2 arbitrary
single-qubit faults [fowler2012]. Each round entangles every ancilla with its data qubits by CNOTs, measures it, and
resets it for the next round (Stim's measure-and-reset), so the same ancillas are reused for as long as the memory
runs; comparing each round's syndrome with the last turns faults into detection events, which minimum-weight perfect
matching pairs up [higgott2023pymatching]. The circuits are Stim's generated rotated-memory circuits [gidney2021stim],
with the standard uniform circuit-level noise: depolarization p after every Clifford gate and on idle data before each
round, and flip probability p on every reset and measurement.

What the numbers say. Below a threshold near p = 0.6 % for this noise model, each step up in distance divides the
logical error by a roughly constant factor, so redundancy pays for its extra gates; above it, adding qubits makes the
memory worse. The logical error per round p_L then sets how long the memory survives: (1 - p_L)^N after N rounds
(qll/network/pair_ledger.survival_probability), which falls to zero for any p_L > 0. These are simulations of a model,
not measurements of a device.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DISTANCES = (3, 5, 7)


@dataclass(frozen=True)
class Resources:
    distance: int
    data: int
    ancillas: int
    total: int
    correctable_faults: int


def resources(d: int) -> Resources:
    if not (isinstance(d, int) and d >= 3 and d % 2 == 1):
        raise ValueError("distance must be an odd integer of at least 3")
    return Resources(d, d * d, d * d - 1, 2 * d * d - 1, (d - 1) // 2)


def memory_circuit(d: int, p: float, rounds: int | None = None):
    """Stim's rotated surface-code memory (Z basis) with uniform circuit-level noise p."""
    import stim

    resources(d)
    if not 0.0 <= p < 0.5:
        raise ValueError("physical error probability must lie in [0, 0.5)")
    r = d if rounds is None else rounds
    if not (isinstance(r, int) and r >= 1):
        raise ValueError("rounds must be a positive integer")
    return stim.Circuit.generated("surface_code:rotated_memory_z", distance=d, rounds=r, after_clifford_depolarization=p,
                                  before_round_data_depolarization=p, before_measure_flip_probability=p, after_reset_flip_probability=p)


def circuit_census(circuit) -> dict:
    """Which qubits the circuit uses and how often its ancillas are measured and reset."""
    used, mr_targets = set(), 0
    for inst in circuit.flattened():
        if inst.name in ("QUBIT_COORDS", "DETECTOR", "OBSERVABLE_INCLUDE", "TICK", "SHIFT_COORDS"):
            continue
        qs = [t.value for t in inst.targets_copy() if t.is_qubit_target]
        used.update(qs)
        if inst.name == "MR":
            mr_targets += len(qs)
    return {"qubits": len(used), "measure_and_reset": mr_targets}


def logical_error(d: int, p: float, rounds: int | None = None, shots: int = 20_000, seed: int = 0) -> dict:
    """Sample the memory, decode every shot by matching, and return the logical failure rate per shot and per round."""
    import pymatching

    c = memory_circuit(d, p, rounds)
    r = d if rounds is None else rounds
    matcher = pymatching.Matching.from_detector_error_model(c.detector_error_model(decompose_errors=True))
    det, obs = c.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    fails = int(np.count_nonzero(matcher.decode_batch(det)[:, 0] != obs[:, 0]))
    p_shot = fails / shots
    return {"distance": d, "p": p, "rounds": r, "shots": shots, "failures": fails, "p_shot": p_shot,
            "p_round": 1.0 - (1.0 - p_shot) ** (1.0 / r), "stderr": (p_shot * (1 - p_shot) / shots) ** 0.5}


def distance_scan(ps=(0.002, 0.004, 0.006, 0.008, 0.012), distances=DISTANCES, shots: int = 20_000, seed: int = 0) -> dict:
    return {d: [logical_error(d, p, shots=shots, seed=seed + 31 * i) for i, p in enumerate(ps)] for d in distances}
