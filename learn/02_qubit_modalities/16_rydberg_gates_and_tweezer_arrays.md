# Rydberg Gates and Tweezer Arrays

## Blockade
Two atoms excited to a Rydberg state interact by $C_6/R^6$ with $C_6\propto n^{11}$; when that exceeds the excitation Rabi frequency the second excitation is blocked within $R_b=(C_6/\hbar\Omega)^{1/6}$ [jaksch2000] [saffman2010]. For rubidium 70S at $\Omega/2\pi=5$ MHz the model gives $R_b\approx7.5$ µm, larger than the 3–5 µm tweezer spacing, which is what makes a controlled-phase gate between neighbours possible in a few hundred nanoseconds [levine2019].

## Gate budget
The leading infidelities are Rydberg-state decay ($t_{\rm gate}/\tau_R$; $\tau_R\sim100$–300 µs, roughly halved by a room-temperature blackbody relative to a cryogenic enclosure [beterov2009]), Doppler dephasing from atom temperature, laser phase noise, and finite blockade $(\Omega/V)^2$. For a 250 ns gate at 3 µm the model's budget sums below 1 %, and the 2023 record of 99.5 % two-qubit fidelity [evered2023] came from suppressing the laser noise and using a time-optimal pulse. Erasure conversion, detecting Rydberg decay as a flagged loss rather than an undetected error, roughly doubles the tolerable error for correction [wu2022].

## Arrays
Optical tweezers from a spatial light modulator (static pattern) or acousto-optic deflectors (moving rows) hold hundreds to thousands of atoms; rearrangement fills defects after stochastic loading; a zoned architecture separates storage, entangling, and readout regions, with the 2024 logical processor moving atoms coherently between them [bluvstein2024]. Loading and rearrangement take tens of milliseconds, so the cycle rate is low; the count and the connectivity (any pair can be brought together) are the platform's strengths.

## Key papers
- Jaksch, D., et al. (2000). *Physical Review Letters*, 85, 2208. https://doi.org/10.1103/PhysRevLett.85.2208
- Saffman, M., Walker, T. G., & Mølmer, K. (2010). *Reviews of Modern Physics*, 82, 2313. https://doi.org/10.1103/RevModPhys.82.2313
- Levine, H., et al. (2019). Parallel implementation of high-fidelity multiqubit gates with neutral atoms. *Physical Review Letters*, 123, 170503. https://doi.org/10.1103/PhysRevLett.123.170503
- Evered, S. J., et al. (2023). High-fidelity parallel entangling gates on a neutral-atom quantum computer. *Nature*, 622, 268. https://doi.org/10.1038/s41586-023-06481-y
- Wu, Y., Kolkowitz, S., Puri, S., & Thompson, J. D. (2022). Erasure conversion for fault-tolerant quantum computing in alkaline earth Rydberg atom arrays. *Nature Communications*, 13, 4657. https://doi.org/10.1038/s41467-022-32094-6
- Beterov, I. I., Ryabtsev, I. I., Tretyakov, D. B., & Entin, V. M. (2009). Quasiclassical calculations of blackbody-radiation-induced depopulation rates and effective lifetimes of Rydberg nS, nP, and nD alkali-metal atoms with n ≤ 80. *Physical Review A*, 79, 052504. https://doi.org/10.1103/PhysRevA.79.052504

## In this repo
`qll/hardware/rydberg.py`; `learn/02/05`; E12 (erasure-aware repeater) in NEXT_100.
