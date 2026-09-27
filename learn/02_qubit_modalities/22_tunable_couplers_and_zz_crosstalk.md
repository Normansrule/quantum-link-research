# Tunable Couplers and ZZ Crosstalk

## The always-on interaction
Two transmons coupled by a fixed exchange $J$ never fully decouple. Their $|11\rangle$ level is pushed by its neighbours $|02\rangle$ and $|20\rangle$ (the transmon's third level sits only an anharmonicity $\alpha\approx-200$ MHz below where a harmonic oscillator would put it), so the energy of $|11\rangle$ is not the sum of $|01\rangle$ and $|10\rangle$. The residue is the static ZZ rate
$$\zeta=E_{11}-E_{10}-E_{01}+E_{00}\approx\frac{2J^2(\alpha_1+\alpha_2)}{(\Delta+\alpha_1)(\Delta-\alpha_2)},\qquad\Delta=\omega_1-\omega_2$$
[krantz2019] [ku2020]. It never switches off: an idle qubit picks up a phase that depends on its neighbour's state, a coherent error that grows with every gate and that randomized benchmarking under-reports (`learn/01/09`, `01/10`).

`qll/hardware/tunable_coupler.py` computes $\zeta$ exactly by diagonalising the coupled Duffing Hamiltonian and checks the formula against it: they agree to 0.2 % at $J=3$ MHz and the ratio goes to one as $J\to0$. The first draft of this module had the second factor's sign wrong, as the formula is often misremembered; the exact computation caught it.

## The tunable coupler
Put a third transmon, the coupler, between the qubits [yan2018]. Its virtual exchange adds an indirect coupling of the opposite sign to the direct one,
$$g_{\rm eff}=g_{12}+\frac{g_{1c}g_{2c}}{2}\left(\frac{1}{\omega_1-\omega_c}+\frac{1}{\omega_2-\omega_c}\right),$$
so moving the coupler's frequency $\omega_c$ with a flux line turns the interaction off or on. Exact diagonalisation of the three-transmon system (qubits at 4.00 and 4.10 GHz, $g_{qc}=100$ MHz, direct $g=6.7$ MHz) gives ZZ of about 1 MHz with the coupler close to the qubits, hundreds of kHz with it far away, and **zero at $\omega_c=5.221$ GHz**, the idle point where the processor parks it between gates.

![ZZ vs coupler frequency](../../docs/figures/zz_coupler.svg)

## From off to a gate
To entangle, one qubit is pulsed toward the point where $|11\rangle$ meets $|20\rangle$ (at $\omega_1=\omega_2-\alpha$), waits, and comes back. Near the crossing the two levels repel with coupling $\sqrt2\,g$, the ZZ grows to about 11 MHz, and $|11\rangle$ collects a phase the other three computational states do not share,
$$\phi=-2\pi\int\zeta(\omega_1(t))\,dt,$$
[strauch2003] [dicarlo2009]. When $\phi=\pi$ the gate is a controlled-Z (CZ); the single-qubit phases it also leaves are removed by a frame change in software. Google's Sycamore and Willow processors and IBM's Heron family build on this, with two-qubit errors near $10^{-3}$ [barends2019] [foxen2020] [sung2021]. The competing fixed-frequency approach, IBM's earlier cross-resonance gate (drive the control qubit at the target's frequency and get an effective $ZX$), has no flux noise but lives with residual ZZ; its effective Hamiltonian is derived in [magesan2020].

`qll/hardware/cz_gate.py` integrates the Schrödinger equation for both transmons with three levels each (qubit 1 from 6.00 to 5.25 GHz, qubit 2 at 5.00 GHz, $g=20$ MHz) and reads the conditional phase, the leakage, and the average gate fidelity [pedersen2007] from the propagator:

- **The adiabatic limit is checked, not assumed.** For slow pulses the simulated phase matches the integral above to better than 1 %, and the small residue halves when the pulse is twice as long: the second-order (super-adiabatic) correction.
- **The shape of the pulse is the gate.** Ramps shaped smoothly in the $|11\rangle$–$|20\rangle$ mixing angle $\theta$, $\tan 2\theta=2\sqrt2 g/\Delta$ [martinis2014], slow down exactly where the gap is small. Calibrated to $\phi=\pi$, the 59.5 ns pulse leaves $8\times10^{-5}$ in $|20\rangle$ and reaches a fidelity of 0.99998 (coherent errors only; add $T_1$ and $T_2$ for the real number). The same 15 ns ramps shaped linearly in frequency, calibrated the same way, leave 4 % behind.
- **Hybridization is not leakage.** At the interaction point the dressed $|11\rangle$ is 17 % bare $|20\rangle$; that population returns when the pulse does. What counts is what is left at the end. Fast gates deliberately drive large intermediate leakage and bring it back [negirneac2021].

![CZ pulse, populations, and conditional phase](../../docs/figures/cz_pulse.svg)

## Measuring ZZ yourself
The static ZZ is one of the first things a student can measure on a real processor with free cloud access. Prepare qubit 0 on the equator, leave its neighbour in $|0\rangle$ or flip it to $|1\rangle$, wait $\tau$, and close the Ramsey interferometer [ramsey1950]. The fringe frequency shifts by exactly $\zeta$ between the two cases: $\zeta=f_0-f_1$. `qll/circuits/zz_ramsey.py` writes the circuits (with `delay` instructions for hardware), simulates them in Qiskit Aer with a known ZZ and dephasing injected, and fits the fringes. In simulation it recovers the coupler model's ZZ at every coupler frequency to within 3 %, and it cannot resolve the idle point's ZZ from zero, which is the point of the idle point. Proposal [E16](../../experiments/proposed/E16_zz_crosstalk_on_a_cloud_processor.md) takes it to hardware.

![Conditional Ramsey fringes and the recovered ZZ](../../docs/figures/zz_ramsey.svg)

## Why it matters for the link
A network node that also computes on superconducting qubits inherits this crosstalk budget. It is one more item in the case for an optical-native node (E7), and the model here is the one to extend if a thesis chapter needs the error budget of a microwave processor node.

## Key papers
- Krantz, P., et al. (2019). A quantum engineer's guide to superconducting qubits. *Applied Physics Reviews*, 6, 021318. https://doi.org/10.1063/1.5089550
- Yan, F., et al. (2018). Tunable coupling scheme for implementing high-fidelity two-qubit gates. *Physical Review Applied*, 10, 054062. https://doi.org/10.1103/PhysRevApplied.10.054062
- Ku, J., et al. (2020). Suppression of unwanted ZZ interactions in a hybrid two-qubit system. *Physical Review Letters*, 125, 200504. https://doi.org/10.1103/PhysRevLett.125.200504
- Sung, Y., et al. (2021). Realization of high-fidelity CZ and ZZ-free iSWAP gates with a tunable coupler. *Physical Review X*, 11, 021058. https://doi.org/10.1103/PhysRevX.11.021058
- Foxen, B., et al. (2020). Demonstrating a continuous set of two-qubit gates for near-term quantum algorithms. *Physical Review Letters*, 125, 120504. https://doi.org/10.1103/PhysRevLett.125.120504
- Strauch, F. W., et al. (2003). Quantum logic gates for coupled superconducting phase qubits. *Physical Review Letters*, 91, 167005. https://doi.org/10.1103/PhysRevLett.91.167005
- DiCarlo, L., et al. (2009). Demonstration of two-qubit algorithms with a superconducting quantum processor. *Nature*, 460, 240–244. https://doi.org/10.1038/nature08121
- Martinis, J. M., & Geller, M. R. (2014). Fast adiabatic qubit gates using only σz control. *Physical Review A*, 90, 022307. https://doi.org/10.1103/PhysRevA.90.022307
- Negîrneac, V., et al. (2021). High-fidelity controlled-Z gate with maximal intermediate leakage operating at the speed limit in a superconducting quantum processor. *Physical Review Letters*, 126, 220502. https://doi.org/10.1103/PhysRevLett.126.220502
- Magesan, E., & Gambetta, J. M. (2020). Effective Hamiltonian models of the cross-resonance gate. *Physical Review A*, 101, 052308. https://doi.org/10.1103/PhysRevA.101.052308

## In this repo
`qll/hardware/tunable_coupler.py` (exact and perturbative ZZ, `CoupledPair`), `qll/hardware/cz_gate.py` (`CZPulse`, `flat_time_for_cz`), `qll/circuits/zz_ramsey.py` (circuits, simulation, fit), and the figures `zz_coupler`, `cz_pulse`, `zz_ramsey`; `learn/02/01`, `02/15`; proposal E16.

## Exercises
1. Using `static_zz_exact`, find the detuning $\Delta$ at which ZZ changes sign for two transmons with $\alpha=-300$ MHz. Why is it near $\Delta=\pm\alpha$?
2. With `CoupledPair`, double the direct coupling $g_{12}$. Does the idle point move toward or away from the qubits? Explain with $g_{\rm eff}$.
3. With `CZPulse` and `flat_time_for_cz`, calibrate CZ gates for ramp times from 8 to 30 ns in both shapes and plot leakage against total duration. Where is the shortest gate with leakage below $10^{-3}$?
4. Run `ramsey_circuit` with `zz_mhz=None` on a free IBM Quantum device for a neighbouring pair and fit with `measure_zz`. Is the result closer to a fixed-coupling or a tunable-coupler processor?
