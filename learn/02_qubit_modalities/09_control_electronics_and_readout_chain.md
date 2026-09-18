# Control electronics and the readout chain (the engineering layer every modality shares)

## The chain
```mermaid
flowchart LR
  SW[software: pulse schedule] --> AWG[arbitrary waveform generator / FPGA DAC, 1–2 GS/s, ns timing]
  AWG --> IQ[IQ mixer + local oscillator → microwave pulse] --> ATT[attenuation, filtering, thermalization at each fridge stage]
  ATT --> Q[qubit]
  Q --> RO[readout resonator / fluorescence / charge sensor]
  RO --> AMP[first-stage amplifier: JPA/TWPA (µW) · SNSPD/SPAD (optical) · SET/RF-SET (charge)]
  AMP --> HEMT[HEMT at 4 K] --> ADC[ADC + FPGA demodulation] --> DEC[real-time decision: feed-forward, decoder]
```

## Definitions
- **Pulse shaping**: Gaussian and DRAG (Derivative Removal by Adiabatic Gate) envelopes suppress leakage to the $\lvert2\rangle$ state of a weakly anharmonic transmon; the anharmonicity $\alpha\approx-E_C$ sets the minimum gate time (~$1/\alpha$).
- **Phase noise and drift**: the local oscillator's phase noise becomes qubit dephasing; every modality has a "laser or LO linewidth" requirement.
- **Timing and synchronization**: nanosecond-level alignment across channels; for networks, GPS-disciplined or White Rabbit clocks synchronize remote nodes (Micius used a pulsed laser for ns sync).
- **Feed-forward**: the classical decision loop (measure → decode → correct) must run within the coherence time: ~1 µs for surface-code cycles; this is where FPGAs and ASICs enter (relevant to the owner's FPGA background: the decoder, the QRNG, and the AES layer are all FPGA-class problems).
- **Cryo-CMOS**: control electronics at 4 K to cut the wiring bottleneck (Intel Horse Ridge, Google, Microsoft); trades heat load against cable count.
- **Optical control**: acousto-optic and electro-optic modulators (ns switching), frequency-stabilized lasers (kHz linewidth) locked to cavities or atomic references, for ions, atoms, and color centers.

## Equations
Leakage from a Gaussian pulse of width $\sigma$ on a transmon with anharmonicity $\alpha$: suppressed when $\sigma\alpha\gg1$; DRAG adds a quadrature component $\dot\Omega/\alpha$. Dephasing from LO phase noise $S_\phi(f)$: $1/T_\varphi\sim\int S_\phi(f)\,F(f)\,df$ with the filter function $F$ of the pulse sequence.

## Key references
- Motzoi, F., Gambetta, J. M., Rebentrost, P., & Wilhelm, F. K. (2009). Simple pulses for elimination of leakage in weakly nonlinear qubits. *Physical Review Letters*, 103, 110501. https://doi.org/10.1103/PhysRevLett.103.110501
- Krantz, P., et al. (2019). §IV–V (control and readout). https://doi.org/10.1063/1.5089550
- Macklin, C., et al. (2015). A near–quantum-limited Josephson traveling-wave parametric amplifier. *Science*, 350, 307. https://doi.org/10.1126/science.aaa8525
- Patra, B., et al. (2018). Cryo-CMOS circuits and systems for quantum computing applications. *IEEE J. Solid-State Circuits*, 53, 309.
- Bardin, J. C., et al. (2019). Design and characterization of a 28-nm bulk-CMOS cryogenic quantum controller dissipating less than 2 mW at 3 K. *IEEE J. Solid-State Circuits*, 54, 3043.
- Ryan, C. A., et al. (2017). Hardware for dynamic quantum computing. *Rev. Sci. Instrum.*, 88, 104703.

## In this repo
The bench-scale version is the ADF4351 + Arduino/ESP32 stack of the Uncut Gem and Stegemann builds; the FPGA pulse generator is Tier 1; the owner's FPGA/QRNG board slots into `qll/hardware/randomness.py` and the Phase 6 fail-closed messenger.
