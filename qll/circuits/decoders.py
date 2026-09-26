"""Decoding the repetition code under circuit-level noise: majority vote versus minimum-weight perfect matching.

Physics
-------
Stim generates a distance-d repetition-code memory with noisy syndrome extraction over d rounds ("circuit-level" noise:
data depolarization, measurement flips, reset flips) and compiles its detector error model; PyMatching finds the most
likely set of errors consistent with the observed detection events by minimum-weight perfect matching on that graph
[gidney2021stim] [higgott2023pymatching] [dennis2002]. Below threshold the logical error falls as (p/p_th)^((d+1)/2);
above it, larger codes are worse. Majority vote on the final data readout ignores the syndrome history and therefore
cannot correct measurement errors, which is why real decoders operate on space-time graphs.
"""
from __future__ import annotations

import numpy as np


def repetition_memory(distance: int, rounds: int, p: float):
    import stim

    return stim.Circuit.generated("repetition_code:memory", distance=distance, rounds=rounds,
                                  after_clifford_depolarization=p, before_measure_flip_probability=p,
                                  after_reset_flip_probability=p)


def logical_error_rate(distance: int, p: float, shots: int = 20000, rounds: int | None = None, seed: int = 0,
                       decoder: str = "matching") -> float:
    """Fraction of shots whose decoded logical observable is wrong."""
    rounds = rounds or distance
    circ = repetition_memory(distance, rounds, p)
    sampler = circ.compile_detector_sampler(seed=seed)
    dets, obs = sampler.sample(shots, separate_observables=True)
    if decoder == "matching":
        import pymatching

        m = pymatching.Matching.from_detector_error_model(circ.detector_error_model(decompose_errors=True))
        pred = m.decode_batch(dets)
        return float(np.mean(pred[:, 0] != obs[:, 0]))
    if decoder == "none":
        return float(np.mean(obs[:, 0]))
    raise ValueError("decoder must be 'matching' or 'none'")


def threshold_scan(distances=(3, 5, 7), ps=(0.01, 0.03, 0.05, 0.08, 0.12), shots: int = 20000) -> dict[int, list[float]]:
    return {d: [logical_error_rate(d, p, shots) for p in ps] for d in distances}
