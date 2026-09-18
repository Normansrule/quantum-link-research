# Other modalities and hybrids

| Modality | Qubit | Notable results | Why it matters here |
|---|---|---|---|
| **Bosonic cat and GKP qubits** | encoded states of a superconducting cavity | beyond-break-even QEC with GKP (Sivak 2023); bias-preserving cat qubits (Alice & Bob, AWS Ocelot 2025) | shows QEC can be hardware-efficient; still microwave-only |
| **Fluxonium** | superinductor-shunted junction | $T_1$ > 1 ms, 99.9% gates (2022–2024) | possible replacement for the transmon |
| **Rare-earth ions in crystals** (Eu:YSO, Er:YSO, Pr:YSO) | nuclear or electron spins of dopant ions, optically addressed | 6 h and 13.1 h nuclear coherence; one-hour optical storage; Er at 1550 nm couples directly to telecom | **the memory platform for the Earth–Mars round trip**; see `03_quantum_communication/03_repeaters_and_memories.md` |
| **Quantum-dot photon sources / spins** | InAs/GaAs dot exciton and resident spin | brightest deterministic single-photon sources; spin–photon cluster states | flying-qubit sources for repeaters |
| **Molecular qubits** | rotational/vibrational states of trapped molecules | entangling gates (2023) | long coherence, chemistry sensing |
| **NMR (historical)** | nuclear spins in liquid molecules | first Shor demonstration (15 = 3 × 5, 2001) | pseudo-pure states; not scalable, but every pulse technique came from here |
| **Electrons on helium / on neon** | motional or spin states of a single electron on a cryogenic surface | 0.1 ms coherence (2022) | new; silicon-like fabrication |
| **Hybrid: superconducting ↔ optical** | transduction via electro-optics, optomechanics, magnons, or atoms | efficiencies ~10⁻³–10⁻¹, added noise > 1 photon | the bottleneck for connecting processors to links |

## Key papers
- Vandersypen, L. M. K., et al. (2001). Experimental realization of Shor's quantum factoring algorithm using nuclear magnetic resonance. *Nature*, 414, 883. https://doi.org/10.1038/414883a
- Ofek, N., et al. (2016). Extending the lifetime of a quantum bit with error correction in superconducting circuits. *Nature*, 536, 441. https://doi.org/10.1038/nature18949
- Guillaud, J., & Mirrahimi, M. (2019). Repetition cat qubits for fault-tolerant quantum computation. *Physical Review X*, 9, 041053.
- Sivak, V. V., et al. (2023). Real-time quantum error correction beyond break-even. *Nature*, 616, 50.
- Zhong, M., et al. (2015). *Nature*, 517, 177. https://doi.org/10.1038/nature14025 ; Wang, F., et al. (2025). *PRX Quantum*, 6, 010302. https://doi.org/10.1103/PRXQuantum.6.010302
- Lauk, N., et al. (2020). Perspectives on quantum transduction. *Quantum Sci. Technol.*, 5, 020501.
- Zhou, X., et al. (2022). Single electrons on solid neon as a solid-state qubit platform. *Nature*, 605, 46.
