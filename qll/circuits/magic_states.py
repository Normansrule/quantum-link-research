"""Magic-state distillation: why T gates set the cost of fault-tolerant algorithms.

Physics
-------
Clifford gates are cheap in a stabilizer code (transversal or by lattice surgery) but cannot compute beyond what a
classical computer can simulate [gottesman1998]; a non-Clifford T gate needs a magic state |T> = (|0> + e^{i pi/4}|1>)/sqrt2,
which is injected with the physical error rate p and then distilled. The 15-to-1 protocol [bravyi2005] takes 15
noisy T states to one with error 35 p^3 (to leading order), so d rounds give ~ (35 p^3)^... nested; a target error
of 1e-12 from p = 1e-3 needs two rounds and 15^2 = 225 input states per output T. A useful algorithm needs 1e8-1e10
T gates [gidney2021factor], so magic-state factories dominate the footprint of a fault-tolerant machine.
"""
from __future__ import annotations

import math


def distilled_error_15_to_1(p: float) -> float:
    return 35 * p**3


def rounds_and_inputs(p_in: float, p_target: float, max_rounds: int = 10) -> tuple[int, int, float]:
    """(rounds, input T states per output, achieved error) for nested 15-to-1 distillation."""
    p, rounds = p_in, 0
    while p > p_target and rounds < max_rounds:
        p = distilled_error_15_to_1(p)
        rounds += 1
    return rounds, 15**rounds, p


def t_count_budget(p_in: float, n_t_gates: float, eps_algorithm: float = 0.01) -> dict[str, float]:
    """How good each T must be (eps/N) and how many raw states a factory needs for an algorithm of N T gates."""
    p_target = eps_algorithm / n_t_gates
    r, inputs, p = rounds_and_inputs(p_in, p_target)
    return {"target_error_per_T": p_target, "rounds": r, "raw_states_per_T": inputs, "raw_states_total": inputs * n_t_gates, "achieved": p}
