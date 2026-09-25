"""Stabilizer codes hands-on: the 3-qubit repetition code, the 5-qubit code, and Steane's 7-qubit code in Stim.

Physics
-------
A stabilizer code is the joint +1 eigenspace of a set of commuting Pauli operators; a Pauli error anticommutes with
some of them and flips their measured values (the syndrome), which identifies the error without measuring the logical
state [gottesman1997] [nielsen2010 ch. 10]. The [[5,1,3]] code is the smallest that corrects any single-qubit error
[laflamme1996]; the [[7,1,3]] Steane code is a CSS code with transversal Clifford gates [steane1996]. Here the
syndromes are computed by measuring the stabilizer generators with Stim after an injected error, and the lookup
table maps syndromes to corrections; the tests inject every single-qubit Pauli error and check that it is identified.
"""
from __future__ import annotations

import itertools

CODES = {
    "repetition3": {"n": 3, "stabilizers": ["ZZ_", "_ZZ"], "logical_z": "ZZZ", "logical_x": "XXX"},
    "five": {"n": 5, "stabilizers": ["XZZXI", "IXZZX", "XIXZZ", "ZXIXZ"], "logical_z": "ZZZZZ", "logical_x": "XXXXX"},
    "steane": {"n": 7, "stabilizers": ["IIIXXXX", "IXXIIXX", "XIXIXIX", "IIIZZZZ", "IZZIIZZ", "ZIZIZIZ"], "logical_z": "ZZZZZZZ", "logical_x": "XXXXXXX"},
}


def _stim_pauli(label: str):
    import stim
    return stim.PauliString(label.replace("_", "I"))


def syndrome_of_error(code: str, error: str) -> tuple[int, ...]:
    """Syndrome bits (1 = stabilizer anticommutes with the error) computed with Stim Pauli-string algebra."""
    c = CODES[code]
    e = _stim_pauli(error)
    return tuple(0 if _stim_pauli(s).commutes(e) else 1 for s in c["stabilizers"])


def syndrome_table(code: str) -> dict[tuple[int, ...], str]:
    """Map every single-qubit Pauli error (and the identity) to its syndrome; distinct if the code has distance >= 3
    for that error type."""
    c = CODES[code]
    n = c["n"]
    table: dict[tuple[int, ...], str] = {tuple([0] * len(c["stabilizers"])): "I" * n}
    for q in range(n):
        for P in "XYZ":
            lab = "I" * q + P + "I" * (n - q - 1)
            table.setdefault(syndrome_of_error(code, lab), lab)
    return table


def corrects_all_single_errors(code: str, error_types: str = "XYZ") -> bool:
    c = CODES[code]
    n = c["n"]
    seen = {}
    for q in range(n):
        for P in error_types:
            lab = "I" * q + P + "I" * (n - q - 1)
            s = syndrome_of_error(code, lab)
            if s in seen and seen[s] != lab or s == tuple([0] * len(c["stabilizers"])):
                return False
            seen[s] = lab
    return True


def memory_experiment_logical_error(code: str, p: float, rounds: int = 1, shots: int = 20000, seed: int = 0) -> float:
    """Stim simulation: prepare |0>_L, apply X errors with probability p per data qubit, measure stabilizers,
    correct by the lookup table (single-error assumption), measure Z_L; return logical error probability.
    Only X-type errors and Z-type stabilizers are used (a bit-flip memory), which is what the lookup covers."""
    import stim
    import numpy as np

    c = CODES[code]
    n = c["n"]
    z_stabs = [s for s in c["stabilizers"] if set(s) <= {"Z", "I", "_"}]
    if not z_stabs:
        raise ValueError("code needs Z-type stabilizers for a bit-flip memory experiment")
    circ = stim.Circuit()
    for q in range(n):
        circ.append("X_ERROR", [q], p)
    # measure Z stabilizers via MPP and the logical Z
    for s in z_stabs:
        circ.append("MPP", stim.target_combined_paulis(_stim_pauli(s)))
    circ.append("MPP", stim.target_combined_paulis(_stim_pauli(c["logical_z"])))
    m = circ.compile_sampler(seed=seed).sample(shots)
    # lookup on the Z-stabilizer syndrome (X errors only)
    table = {}
    for q in range(n):
        lab = "I" * q + "X" + "I" * (n - q - 1)
        table[tuple(0 if _stim_pauli(s).commutes(_stim_pauli(lab)) else 1 for s in z_stabs)] = q
    errors = 0
    for row in m:
        syn = tuple(int(x) for x in row[: len(z_stabs)])
        logical = int(row[len(z_stabs)])
        if any(syn):
            q = table.get(syn)
            if q is None:
                errors += 1                     # uncorrectable syndrome: count as failure (conservative)
                continue
            # an X on qubit q flips Z_L iff q is in its support (always, for these codes): undo
            logical ^= 1
        errors += logical
    return errors / shots
