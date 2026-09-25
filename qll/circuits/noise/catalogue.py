"""A catalogue of single-qubit channels, each as a CPTP-checked KrausChannel, for teaching and tests.

Physics
-------
Every named channel below is written in operator-sum form [nielsen2010 ch. 8]; construction fails unless
sum E_k^dagger E_k = I, so the catalogue doubles as a test of the formulas. Bit flip, phase flip, bit-phase flip:
Pauli channels with one error type. Depolarizing: all three. Amplitude damping (T1) and generalized amplitude
damping (finite temperature) [nielsen2010]. Phase damping (T_phi). Pauli twirling of an arbitrary channel keeps the
diagonal of the process matrix and is what randomized compiling relies on [wallman2016]. The 'reset' channel maps
everything to |0>; the 'measurement' channel dephases completely. 'Rotation error' is a coherent over-rotation:
a unitary, hence a single Kraus operator, whose average fidelity 1 - (2/3) sin^2(theta/2) shows why coherent errors
are worse than their infidelity suggests (they add in amplitude, not probability).
"""
from __future__ import annotations

import math

import numpy as np

from qll.circuits.noise._kraus_base import KrausChannel
from qll.circuits.noise.amplitude_damping import amplitude_damping
from qll.circuits.noise.depolarizing import depolarizing
from qll.circuits.noise.phase_damping import phase_damping
from qll.circuits.noise.thermal import bath_ground_weight, generalized_amplitude_damping_kraus

_I = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)


def bit_flip(p: float) -> KrausChannel:
    return KrausChannel((math.sqrt(1 - p) * _I, math.sqrt(p) * _X), "bit_flip")


def phase_flip(p: float) -> KrausChannel:
    return KrausChannel((math.sqrt(1 - p) * _I, math.sqrt(p) * _Z), "phase_flip")


def bit_phase_flip(p: float) -> KrausChannel:
    return KrausChannel((math.sqrt(1 - p) * _I, math.sqrt(p) * _Y), "bit_phase_flip")


def pauli_channel(px: float, py: float, pz: float) -> KrausChannel:
    p0 = 1 - px - py - pz
    return KrausChannel((math.sqrt(p0) * _I, math.sqrt(px) * _X, math.sqrt(py) * _Y, math.sqrt(pz) * _Z), "pauli")


def reset_to_zero() -> KrausChannel:
    return KrausChannel((np.array([[1, 0], [0, 0]], dtype=complex), np.array([[0, 1], [0, 0]], dtype=complex)), "reset")


def complete_dephasing() -> KrausChannel:
    return phase_damping(1.0)


def coherent_rotation_error(theta: float, axis: str = "x") -> KrausChannel:
    P = {"x": _X, "y": _Y, "z": _Z}[axis]
    U = math.cos(theta / 2) * _I - 1j * math.sin(theta / 2) * P
    return KrausChannel((U,), f"rotation_error_{axis}")


def thermal_gad(gamma: float, omega: float, T: float) -> KrausChannel:
    return KrausChannel(tuple(generalized_amplitude_damping_kraus(gamma, bath_ground_weight(omega, T))), "thermal_gad")


def pauli_twirl(channel: KrausChannel) -> KrausChannel:
    """Average the channel over conjugation by the Pauli group: keeps only the Pauli-diagonal part."""
    paulis = (_I, _X, _Y, _Z)
    # process matrix in the Pauli basis: chi_ij = sum_k <P_i,E_k><E_k,P_j>/... ; twirl keeps chi_ii
    coeffs = []
    for P in paulis:
        c = sum(abs(np.trace(P.conj().T @ E) / 2) ** 2 for E in channel.ops)
        coeffs.append(c)
    total = sum(coeffs)
    coeffs = [c / total for c in coeffs]
    return KrausChannel(tuple(math.sqrt(c) * P for c, P in zip(coeffs, paulis) if c > 1e-15), f"twirled_{channel.name}")


CATALOGUE = {
    "bit_flip(0.1)": lambda: bit_flip(0.1),
    "phase_flip(0.1)": lambda: phase_flip(0.1),
    "bit_phase_flip(0.1)": lambda: bit_phase_flip(0.1),
    "pauli(0.05,0.02,0.03)": lambda: pauli_channel(0.05, 0.02, 0.03),
    "depolarizing(0.1)": lambda: depolarizing(0.1),
    "amplitude_damping(0.3)": lambda: amplitude_damping(0.3),
    "thermal_gad(0.3, 5 GHz, 50 mK)": lambda: thermal_gad(0.3, 2 * math.pi * 5e9, 0.05),
    "phase_damping(0.3)": lambda: phase_damping(0.3),
    "complete_dephasing": complete_dephasing,
    "reset": reset_to_zero,
    "rotation_error(0.1 rad)": lambda: coherent_rotation_error(0.1),
    "twirled_rotation_error(0.1)": lambda: pauli_twirl(coherent_rotation_error(0.1)),
}
