# Coherent control of a spin: Rabi, Ramsey, Hahn echo (Jelezko et al. 2004; teaching version Sewani et al. 2020)

**Original.** Jelezko and colleagues drove Rabi oscillations of a single NV electron spin at room temperature, the first coherent control of a single solid-state spin.

**Physics.** `00_foundations/04`: $P_1(t)=\sin^2(\Omega t/2)$ on resonance; Ramsey gives $T_2^*$ and detuning; echo gives $T_2$; CPMG with $N$ pulses gives $T_2\propto N^{2/3}$ in a P1-center bath (de Lange 2010).

**Simple recreation (Tier 1, ~$10k).** Pulsed version of the ODMR bench: a switch on the microwave line driven by a pulse generator (FPGA or a fast microcontroller), a gated photodiode, and a permanent-magnet bias field. Sewani et al. give the full parts list and the sequences. Expect ensemble $T_2^*\sim1$ µs, echo $T_2\sim10$–100 µs depending on the diamond.

**What went wrong historically.** Room-temperature single-spin coherence was expected to be short; isotopic purification (2009) and dynamical decoupling (2010) extended it by orders of magnitude, which is the whole reason NV networks exist.

**Repo hook.** `qll/viz/rabi_ramsey.py`; Phase 2 `noise/phase_damping.py`; proposal E2.

- Jelezko, F., Gaebel, T., Popa, I., Gruber, A., & Wrachtrup, J. (2004). Observation of coherent oscillations in a single electron spin. *Physical Review Letters*, 92, 076401. https://doi.org/10.1103/PhysRevLett.92.076401
- Sewani, V. K., et al. (2020). *Am. J. Phys.*, 88, 1156. arXiv:2004.02643
- de Lange, G., et al. (2010). *Science*, 330, 60. https://doi.org/10.1126/science.1192739
