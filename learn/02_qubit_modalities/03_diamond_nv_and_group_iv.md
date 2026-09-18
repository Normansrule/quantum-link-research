# Color centers in diamond: NV and the group-IV vacancies

The bench-buildable qubit and the platform with the strongest *network* record. The full hardware treatment (parts, vendors, budget tiers, step-by-step experiments) is in `experiments/bench/hardware_guide.md`; this file is the physics.

## The two levels
The negatively charged nitrogen-vacancy center (NV⁻) is a spin-1 ground state $^3A_2$ with $m_s=0,\pm1$, zero-field splitting $D=2.87$ GHz. The qubit is $m_s=0\leftrightarrow m_s=-1$ (or $+1$), split further by a magnetic field at $\gamma_e=2.8$ MHz/G. Green light (532 nm) pumps it into $m_s=0$ via a spin-selective intersystem crossing; fluorescence at 637 nm (zero-phonon line, ZPL) and the phonon sideband to ~800 nm is ~30% brighter for $m_s=0$, which is the readout contrast. Nearby ¹³C nuclear spins and the ¹⁴N nucleus are extra qubits with minute-scale coherence [Bradley et al. 2019].

Group-IV centers (SiV⁻, GeV, SnV) have inversion symmetry, so their optical lines are insensitive to electric-field noise; SiV⁻ in a nanophotonic cavity gives near-deterministic spin–photon coupling but needs ~100 mK.

## Equations
$$H_{\rm gs}=DS_z^2+\gamma_e\vec B\cdot\vec S+\sum_kA_k\,\vec S\cdot\vec I_k,\qquad f_\pm=D\pm\gamma_eB_\parallel$$
Optically detected magnetic resonance (ODMR) contrast $C\approx0.3$ for a single NV, a few percent for ensembles; magnetometer sensitivity $\eta\approx\frac{\hbar}{g\mu_B}\frac{1}{C\sqrt{R\,T_2^*}}$ with photon rate $R$.
Remote-entanglement success per attempt (two-photon Barrett–Kok scheme): $p\approx\frac12(\eta_{\rm ZPL}\eta_{\rm coll}\eta_{\rm det})^2\sim10^{-4}$–$10^{-6}$, dominated by the ~3% Debye–Waller factor; cavities (SiV) raise $\eta_{\rm ZPL}$ to near 1.

## Visual
```mermaid
flowchart TD
  G[532 nm pump] --> ES[excited state ³E]
  ES -->|spin-conserving, 637–800 nm photons| GS0[³A₂ m_s = 0  (bright)]
  ES -->|m_s = ±1 preferentially| ISC[singlet ¹A₁ → ¹E] --> GS0
  GS0 <-->|microwave 2.87 GHz ± γB| GS1[³A₂ m_s = ±1  (dim)]
```

## How it is built
- **Ensemble teaching qubit** (~$100–$500): fluorescent microdiamond, green laser or LED, ADF4351 microwave source + loop antenna, photodiode; ODMR in an afternoon (Uncut Gem, Stegemann cubes).
- **Coherent control** (~$10k): pulsed microwaves, gated photodiode, permanent-magnet bias: Rabi, Ramsey, Hahn echo.
- **Single-NV network node** (research): electronic-grade CVD diamond, solid-immersion lens or nanopillar, confocal microscope with 0.9 NA objective, 4 K cryostat, resonant red lasers for spin-selective excitation, charge-state control, and a Hong-Ou-Mandel beam splitter at the midpoint.

## How it is modeled
Spin Hamiltonian above in QuTiP; spin-bath decoherence with the $T_2\propto N^{2/3}$ decoupling scaling; herald probability from the efficiency product (`qll/hardware/nv_node.py`, Phase 3).

## Best published results
- Remote entanglement 3 m (2013), unconditional teleportation (2014), loophole-free Bell test 1.3 km (2015), deterministic entanglement delivery (2018), three-node network (2021), teleportation between non-neighbouring nodes (2022), 25 km deployed fiber with frequency conversion (2024). Full table with DOIs in `experiments/bench/hardware_guide.md` §3.2.
- SiV: memory-enhanced communication (2020), two SiV nodes over 35 km Boston fiber with second-scale nuclear memories (2024).

## What has failed or is hard
- The NV optical transition is spectrally unstable (charge noise), which blocks efficient cavities; this is exactly what pushed the field toward SiV.
- Herald rates of Hz mean minutes per entangled pair; scaling needs cavities, multiplexing, or both.
- Frequency conversion to telecom adds loss and noise.

## What it means for a link
This is the modality of the thesis. The nuclear-spin registers are the candidate *memory* in a repeater; the optical interface is native; the temperature requirement (4 K) is achievable on a spacecraft with closed-cycle coolers, unlike 10 mK. Whether NV/SiV memories can reach the 6–45 minute Earth–Mars round trip is open (they are at minutes; Eu:YSO is at hours): `../../experiments/proposed/`.

## Key papers
- Gruber, A., et al. (1997). Scanning confocal optical microscopy and magnetic resonance on single defect centers. *Science*, 276, 2012. https://doi.org/10.1126/science.276.5321.2012
- Jelezko, F., et al. (2004). Observation of coherent oscillations in a single electron spin. *Physical Review Letters*, 92, 076401.
- Doherty, M. W., et al. (2013). *Phys. Rep.*, 528, 1. https://doi.org/10.1016/j.physrep.2013.02.001
- Bernien, H., et al. (2013). *Nature*, 497, 86. Pfaff, W., et al. (2014). *Science*, 345, 532. Hensen, B., et al. (2015). *Nature*, 526, 682.
- Humphreys, P. C., et al. (2018). Deterministic delivery of remote entanglement on a quantum network. *Nature*, 558, 268. https://doi.org/10.1038/s41586-018-0200-5
- Bradley, C. E., et al. (2019). A ten-qubit solid-state spin register with quantum memory up to one minute. *Physical Review X*, 9, 031045. https://doi.org/10.1103/PhysRevX.9.031045
- Pompili, M., et al. (2021). *Science*, 372, 259. Hermans, S. L. N., et al. (2022). *Nature*, 605, 663. https://doi.org/10.1038/s41586-022-04697-y
- Bhaskar, M. K., et al. (2020). *Nature*, 580, 60. https://doi.org/10.1038/s41586-020-2103-5 Knaut, C. M., et al. (2024). *Nature*, 629, 573. https://doi.org/10.1038/s41586-024-07252-z
- Stegemann, J., et al. (2023). *Eur. J. Phys.*, 44, 035402. https://doi.org/10.1088/1361-6404/acbe7c Sewani, V. K., et al. (2020). arXiv:2004.02643.

## Exercises
1. Compute the ODMR line positions at $B_\parallel=50$ G and sketch the spectrum for an ensemble with the four NV orientations in a field along [111].
2. If $\eta_{\rm ZPL}\eta_{\rm coll}\eta_{\rm det}=0.02$ per photon and attempts run at 100 kHz, how long until one entangled pair on average?
