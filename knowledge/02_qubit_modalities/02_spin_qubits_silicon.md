# Spin qubits in silicon and germanium

## The two levels
The spin-up and spin-down states of a single electron (or hole) confined in a **gate-defined quantum dot**, split by a magnetic field: $\hbar\omega=g\mu_BB$ (about 28 GHz/T for $g=2$; ~1 T fields give ~20–30 GHz, or hundreds of MHz at tens of mT). Alternatively the nuclear spin of a single ³¹P donor in silicon (Kane 1998), with coherence of seconds to minutes.

Isotopically purified ²⁸Si removes the ²⁹Si nuclear-spin bath that limits natural silicon, which is why $T_2$ jumped from µs to ms.

## Equations
Loss–DiVincenzo Hamiltonian for two dots:
$$H=\sum_i\frac{g\mu_B}{2}\vec B_i\cdot\vec\sigma_i+J(t)\,\vec S_1\cdot\vec S_2,\qquad J\approx\frac{4t^2}{U}$$
$J$ is switched by the detuning or tunnel-barrier gate voltage; $\sqrt{\rm SWAP}$ takes $\pi\hbar/2J$. Single-qubit control by electron spin resonance (ESR, microwave magnetic field) or electric-dipole spin resonance (EDSR, micromagnet gradient or spin–orbit coupling). Readout by spin-to-charge conversion (Elzerman or Pauli spin blockade) sensed with a single-electron transistor or gate-based reflectometry.

## Visual
```mermaid
flowchart LR
  G[gate electrodes on Si/SiGe or Si-MOS] --> D1[dot 1: one electron] --- J[tunnel barrier: J(V)] --- D2[dot 2: one electron]
  B[B field ~ 0.1–1 T] --> D1 & D2
  ESR[microwave line / micromagnet] --> D1
  SET[charge sensor] --> D1
```

## How it is built
1. Si-MOS (like a transistor, with an Al or poly-Si gate stack) or Si/SiGe heterostructures grown by chemical vapour deposition; ²⁸Si-enriched channel.
2. Nanometre-scale gate patterning by electron-beam lithography; 300 mm foundry processes now exist (Intel Tunnel Falls, imec).
3. Operation at 100 mK–1 K; hot-qubit operation above 1 K demonstrated, which relaxes cryogenic cooling power enormously (a 1 K stage delivers ~1000× the cooling power of 20 mK).
4. Control: on-chip or cryo-CMOS electronics are the scaling bet.

## How it is modeled
Two-level Hamiltonians with quasi-static Overhauser and charge noise; QuTiP for driven dynamics; noise as $T_2^*$ from Gaussian-distributed detuning plus $1/f$ charge noise on $J$.

## Best published results (verify)
- Single-qubit fidelity > 99.9%; two-qubit > 99.5% in ²⁸Si/SiGe (Xue et al. 2022; Noiri et al. 2022; Mądzik et al. 2022 for donors).
- Six-qubit Si/SiGe processor (Philips et al. 2022); 12-qubit foundry chip (Intel 2023).
- Nuclear spin $T_2$ of ³¹P donor > 30 s; electron $T_2$ (with decoupling) > 1 s in ²⁸Si.

## What has failed or is hard
- Device-to-device variability (valley splitting in silicon, disorder at interfaces) makes every dot different.
- Readout speed and fidelity lag superconducting qubits; wiring density (one gate stack per qubit) is the scaling bottleneck ("wiring bottleneck", Franke et al. 2019).

## What it means for a link
No native optical transition: spin–photon interfaces exist only through hybrid schemes (donor-bound excitons, or coupling to a color center). Silicon spins are candidates for dense processors, not for the network memory.

## Key papers
- Loss, D., & DiVincenzo, D. P. (1998). Quantum computation with quantum dots. *Physical Review A*, 57, 120. https://doi.org/10.1103/PhysRevA.57.120
- Kane, B. E. (1998). A silicon-based nuclear spin quantum computer. *Nature*, 393, 133. https://doi.org/10.1038/30156
- Petta, J. R., et al. (2005). Coherent manipulation of coupled electron spins in semiconductor quantum dots. *Science*, 309, 2180. https://doi.org/10.1126/science.1116955
- Veldhorst, M., et al. (2014). An addressable quantum dot qubit with fault-tolerant control-fidelity. *Nature Nanotechnology*, 9, 981. https://doi.org/10.1038/nnano.2014.216
- Veldhorst, M., et al. (2015). A two-qubit logic gate in silicon. *Nature*, 526, 410. https://doi.org/10.1038/nature15263
- Xue, X., et al. (2022). Quantum logic with spin qubits crossing the surface code threshold. *Nature*, 601, 343. https://doi.org/10.1038/s41586-021-04273-w
- Noiri, A., et al. (2022). Fast universal quantum gate above the fault-tolerance threshold in silicon. *Nature*, 601, 338.
- Mądzik, M. T., et al. (2022). Precision tomography of a three-qubit donor quantum processor in silicon. *Nature*, 601, 348.
- Burkard, G., et al. (2023). Semiconductor spin qubits. *Rev. Mod. Phys.*, 95, 025003. https://doi.org/10.1103/RevModPhys.95.025003

## Exercises
1. For $t/h=10$ GHz and $U/h=1$ THz, compute $J$ and the $\sqrt{\rm SWAP}$ time.
2. Explain why moving from natural Si to ²⁸Si changes $T_2^*$ but not $T_1$.
