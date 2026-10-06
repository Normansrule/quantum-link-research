# E18 — Majorana parity teleportation, emulated: one bit or two?

**Gap.** Crogman, Dang, and Erenso (2025) describe teleportation between Majorana-encoded qubits by joint parity measurements alone [crogman2025]. Their main-text protocol sends one parity bit; their Theorem A4 uses two. Huang et al. (2021) emulated a Majorana teleportation on a superconducting processor [huang2021]. No open, reproducible emulation compares the one-bit and two-bit versions side by side on hardware, with the error budget of the paper's Equations 17–20 set against what a real processor's noise does.

**Physics.** Under Jordan–Wigner, $\gamma_1 = X_A$, $\gamma_2 = Y_A$, $\gamma_3 = Z_AX_B$, $\gamma_4 = Z_AY_B$, $\gamma_5 = Z_AZ_BX_C$, $\gamma_6 = Z_AZ_BY_C$. So $P_{23} = i\gamma_2\gamma_3 = -X_AX_B$ and $P_{14} = i\gamma_1\gamma_4 = Y_AY_B$. Both parities make a Bell measurement, so with two bits the average fidelity is 1. One bit caps the average fidelity at the classical 2/3 [massar1995]; the literal correction $X_C$ gives 1/2. Without bits Bob's state is $I/2$ [bennett1993]. All of this is computed exactly in [`qll/circuits/majorana_teleport.py`](../../qll/circuits/majorana_teleport.py).

**Cheapest version ($0).** Protocol [P13](../protocols/P13_majorana_teleportation_on_a_cloud_processor.md): four modes (two-bit, one-bit with the best correction, one-bit as written, no bits) on six cardinal states, on a free cloud processor, with the fidelity of each mode and its interval.

**Research version.**
- Encode each logical qubit in four modes (a tetron) at fixed total parity [karzig2017], mapped to qubits with the same transformation.
- Emulate the parity readout as a weak, noisy measurement with the paper's misclassification model (Equation 18), and compare the inferred error budget with the processor's calibration data.
- With the authors, map the dimensionless knobs (readout signal-to-noise, $\Delta/k_BT$, poisoning per readout, $L/\xi$) to the devices of their Table 2.

**Failure modes to expect.**
- The bit order in Qiskit counts is easily reversed (classical bit 1 printed first).
- On devices without feed-forward, only the deferred version runs, and it carries no classical channel.
- Readout error on the parity qubits mimics a lower parity-readout fidelity; separate it with the processor's reported readout errors.

**Repo hook.**
- Exact model: [`qll/circuits/majorana_teleport.py`](../../qll/circuits/majorana_teleport.py).
- Circuits: [`qll/circuits/majorana_cloud.py`](../../qll/circuits/majorana_cloud.py).
- Error budget: [`qll/hardware/majorana_error_budget.py`](../../qll/hardware/majorana_error_budget.py).
- Tests: [`tests/test_majorana_teleport.py`](../../tests/test_majorana_teleport.py).
- Theory note: [T16](../../research/theories/T16_majorana_measurement_only_teleportation.md).
- Mission milestone M4.6.

**Key references.** Crogman, H. T., Dang, T., & Erenso, D. (2025). *Quantum Reports, 7*, 42. https://doi.org/10.3390/quantum7030042 · Huang, H.-L., et al. (2021). *Physical Review Letters, 126*, 090502. https://doi.org/10.1103/PhysRevLett.126.090502 · Bennett, C. H., et al. (1993). *Physical Review Letters, 70*, 1895. https://doi.org/10.1103/PhysRevLett.70.1895
