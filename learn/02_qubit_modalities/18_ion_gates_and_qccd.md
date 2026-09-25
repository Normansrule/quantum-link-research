# Ion Gates and the QCCD Architecture

## The gate zoo
- **Cirac–Zoller** [cirac1995]: sideband pulses map spin to motion and back; needs ground-state cooling; historically first.
- **Mølmer–Sørensen (MS)** [molmer1999] [sorensen2000]: a bichromatic field detuned by $\pm\delta$ from the sidebands drives a spin-dependent force; the motion returns to its origin after $t_g=2\pi K/\delta$ with $\delta=2\eta\Omega\sqrt K$, leaving a geometric phase; insensitive to the motional state to first order, which is why it is the workhorse.
- **Light-shift (σ_z) gates**: a spin-dependent force from an off-resonant standing wave; used in the 99.9 % Be⁺ result [gaebler2016].
- **Raman versus quadrupole**: Raman beams (two lasers, large effective wavevector, Lamb–Dicke $\eta\approx0.2$) versus a direct narrow quadrupole transition at 729 nm in Ca⁺ ($\eta\approx0.08$).

The model in `qll/hardware/trapped_ion.py` gives $\eta\propto1/\sqrt{m\omega_z}$, a 12 µs MS gate at 200 kHz Rabi frequency, and a budget in which heating ($\dot n t_g$), scattering, and off-resonant coupling $(\Omega/\omega_z)^2$ trade against speed: slowing the gate cuts the off-resonant error and raises the heating error, which is why the record fidelities sit at tens of microseconds.

## QCCD
The quantum charge-coupled device [kielpinski2002] splits a trap into zones (storage, interaction, readout) connected by transport: ions are shuttled, split, merged, and swapped by moving the trapping potentials. Quantinuum's H-series implements it with all-to-all connectivity and mid-circuit measurement [pino2021] [moses2023]. Transport costs time (tens to hundreds of microseconds per operation) and heating; sympathetic cooling with a second species restores the motion between gates. Scaling beyond a few hundred ions needs either larger 2-D trap arrays or photonic interconnects between traps [monroe2014], which is where the trapped-ion network node of this thesis enters: the same ion that stores a Mars-round-trip pair can also compute.

## Key papers
- Cirac, J. I., & Zoller, P. (1995). *Physical Review Letters*, 74, 4091. https://doi.org/10.1103/PhysRevLett.74.4091
- Mølmer, K., & Sørensen, A. (1999). *Physical Review Letters*, 82, 1835. https://doi.org/10.1103/PhysRevLett.82.1835
- Ballance, C. J., Harty, T. P., Linke, N. M., Sepiol, M. A., & Lucas, D. M. (2016). High-fidelity quantum logic gates using trapped-ion hyperfine qubits. *Physical Review Letters*, 117, 060504. https://doi.org/10.1103/PhysRevLett.117.060504
- Gaebler, J. P., et al. (2016). High-fidelity universal gate set for ⁹Be⁺ ion qubits. *Physical Review Letters*, 117, 060505. https://doi.org/10.1103/PhysRevLett.117.060505
- Kielpinski, D., Monroe, C., & Wineland, D. J. (2002). Architecture for a large-scale ion-trap quantum computer. *Nature*, 417, 709. https://doi.org/10.1038/nature00784
- Pino, J. M., et al. (2021). Demonstration of the trapped-ion quantum CCD computer architecture. *Nature*, 592, 209. https://doi.org/10.1038/s41586-021-03318-4
- Moses, S. A., et al. (2023). A race-track trapped-ion quantum processor. *Physical Review X*, 13, 041052. https://doi.org/10.1103/PhysRevX.13.041052

## In this repo
`qll/hardware/trapped_ion.py`; `learn/02/04`; the memory table's ¹⁷¹Yb⁺ entry; E8.
