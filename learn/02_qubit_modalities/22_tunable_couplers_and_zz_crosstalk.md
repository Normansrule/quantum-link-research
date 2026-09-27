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
To entangle, the coupler is pulsed toward the qubits for tens of nanoseconds so that $|11\rangle$ approaches $|20\rangle$ (or $|02\rangle$). The state acquires a conditional phase of $\pi$ and returns: a CZ gate. Fast adiabatic pulse shapes keep the population in the computational states; Google's Sycamore and Willow processors and IBM's Heron family use this architecture, with two-qubit errors near $10^{-3}$ [barends2019] [foxen2020] [sung2021]. The competing fixed-frequency approach, IBM's earlier cross-resonance gate (drive the control qubit at the target's frequency and get an effective $ZX$), has no flux noise but lives with residual ZZ; its effective Hamiltonian is derived in [magesan2020].

## Why it matters for the link
A network node that also computes on superconducting qubits inherits this crosstalk budget. It is one more item in the case for an optical-native node (E7), and the model here is the one to extend if a thesis chapter needs the error budget of a microwave processor node.

## Key papers
- Krantz, P., et al. (2019). A quantum engineer's guide to superconducting qubits. *Applied Physics Reviews*, 6, 021318. https://doi.org/10.1063/1.5089550
- Yan, F., et al. (2018). Tunable coupling scheme for implementing high-fidelity two-qubit gates. *Physical Review Applied*, 10, 054062. https://doi.org/10.1103/PhysRevApplied.10.054062
- Ku, J., et al. (2020). Suppression of unwanted ZZ interactions in a hybrid two-qubit system. *Physical Review Letters*, 125, 200504. https://doi.org/10.1103/PhysRevLett.125.200504
- Sung, Y., et al. (2021). Realization of high-fidelity CZ and ZZ-free iSWAP gates with a tunable coupler. *Physical Review X*, 11, 021058. https://doi.org/10.1103/PhysRevX.11.021058
- Foxen, B., et al. (2020). Demonstrating a continuous set of two-qubit gates for near-term quantum algorithms. *Physical Review Letters*, 125, 120504. https://doi.org/10.1103/PhysRevLett.125.120504
- Magesan, E., & Gambetta, J. M. (2020). Effective Hamiltonian models of the cross-resonance gate. *Physical Review A*, 101, 052308. https://doi.org/10.1103/PhysRevA.101.052308

## In this repo
`qll/hardware/tunable_coupler.py` (exact and perturbative ZZ, `CoupledPair`), `qll/viz/zz_coupler.py`; `learn/02/01`, `02/15`.

## Exercises
1. Using `static_zz_exact`, find the detuning $\Delta$ at which ZZ changes sign for two transmons with $\alpha=-300$ MHz. Why is it near $\Delta=\pm\alpha$?
2. With `CoupledPair`, double the direct coupling $g_{12}$. Does the idle point move toward or away from the qubits? Explain with $g_{\rm eff}$.
