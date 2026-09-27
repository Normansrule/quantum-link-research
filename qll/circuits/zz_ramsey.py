"""Measuring static ZZ with a conditional Ramsey experiment: the circuits a student can run on a cloud processor,
a local simulation that injects a known ZZ, and the fit that recovers it.

Physics
-------
Put qubit 0 on the equator (Hadamard), leave qubit 1 in |0> or flip it to |1>, wait tau, rotate qubit 0's frame by a
virtual detuning 2 pi delta tau, and close the interferometer [ramsey1950] [krantz2019]. The probability of reading 1 is
    P1(tau) = 1/2 - (1/2) e^{-tau/T2} cos(2 pi f_s tau),
and the fringe frequency depends on the neighbour's state s because the static ZZ shifts qubit 0's frequency by
-zeta/2 (s = 0) or +zeta/2 (s = 1):
    f_s = delta - (+/- zeta/2),   so   zeta = f_0 - f_1
for the Hamiltonian H/h = (zeta/4) Z (x) Z, whose E11 - E10 - E01 + E00 is zeta (the definition in
qll/hardware/tunable_coupler.py). The virtual detuning must exceed |zeta|/2 so both fringes have the same sign.

On hardware the wait is a delay instruction and the ZZ is whatever the device has. In `simulate` the wait is replaced
by the exact ZZ evolution RZZ(pi zeta tau) (zeta in MHz, tau in microseconds) and pure dephasing on qubit 0, a
phase-damping channel that multiplies the coherence by e^{-tau/T2} [nielsen2002], so the fit can be tested against a
known answer before it meets a real device.
"""
from __future__ import annotations

import numpy as np


def _check_real(*values) -> None:
    for v in values:
        if np.iscomplexobj(np.asarray(v)):
            raise TypeError("delays, frequencies, and times must be real")


def ramsey_circuit(tau_us: float, neighbor_excited: bool, detuning_mhz: float, zz_mhz: float | None = None,
                   t2_us: float | None = None):
    """One conditional-Ramsey circuit. With zz_mhz=None it uses a hardware delay; otherwise it injects the ZZ (and
    optional dephasing with time constant t2_us) for simulation."""
    _check_real(tau_us, detuning_mhz, 0.0 if zz_mhz is None else zz_mhz, 0.0 if t2_us is None else t2_us)
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Kraus

    qc = QuantumCircuit(2, 1)
    qc.h(0)
    if neighbor_excited:
        qc.x(1)
    if zz_mhz is None:
        qc.delay(float(tau_us), 0, unit="us")
        qc.delay(float(tau_us), 1, unit="us")
    else:
        qc.rzz(np.pi * zz_mhz * tau_us, 0, 1)
        if t2_us is not None:
            lam = 1.0 - np.exp(-2.0 * tau_us / t2_us)          # coherence x sqrt(1 - lam) = e^{-tau/T2}
            k0 = np.array([[1, 0], [0, np.sqrt(1 - lam)]])
            k1 = np.array([[0, 0], [0, np.sqrt(lam)]])
            qc.append(Kraus([k0, k1]), [0])
    qc.rz(2 * np.pi * detuning_mhz * tau_us, 0)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def simulate(delays_us, detuning_mhz: float, zz_mhz: float, t2_us: float | None = 40.0, shots: int = 4000,
             seed: int = 7) -> dict[int, np.ndarray]:
    """P(1) on qubit 0 for each delay, with the neighbour in |0> (key 0) and |1> (key 1), sampled with Aer."""
    _check_real(delays_us, detuning_mhz, zz_mhz)
    from qiskit_aer import AerSimulator

    sim = AerSimulator(method="density_matrix", seed_simulator=seed)   # Kraus channel sampled exactly, not per shot
    out = {}
    for s in (0, 1):
        circs = [ramsey_circuit(float(t), bool(s), detuning_mhz, zz_mhz, t2_us) for t in np.asarray(delays_us, float)]
        res = sim.run(circs, shots=shots).result()
        out[s] = np.array([res.get_counts(k).get("1", 0) / shots for k in range(len(circs))])
    return out


def fit_ramsey(delays_us, p1) -> tuple[float, float]:
    """Least-squares fit of P1 = a - b e^{-tau/T2} cos(2 pi f tau + phi); returns (f in MHz, T2 in us).
    The starting frequency is the peak of the zero-padded Fourier transform."""
    _check_real(delays_us, p1)
    from scipy.optimize import curve_fit

    t, y = np.asarray(delays_us, float), np.asarray(p1, float)
    dt = t[1] - t[0]
    spec = np.abs(np.fft.rfft(y - y.mean(), n=16 * len(t)))
    f0 = np.fft.rfftfreq(16 * len(t), dt)[int(np.argmax(spec[1:])) + 1]
    model = lambda t, a, b, T, f, ph: a - b * np.exp(-t / T) * np.cos(2 * np.pi * f * t + ph)
    popt, _ = curve_fit(model, t, y, p0=[0.5, 0.5, t[-1], f0, 0.0],
                        bounds=([0, 0, dt, 0, -np.pi], [1, 1, 1e6, 1 / (2 * dt), np.pi]))
    return float(popt[3]), float(popt[2])


def measure_zz(delays_us, p1_neighbor_ground, p1_neighbor_excited) -> float:
    """zeta = f_0 - f_1 (MHz) from the two fringes."""
    return fit_ramsey(delays_us, p1_neighbor_ground)[0] - fit_ramsey(delays_us, p1_neighbor_excited)[0]
