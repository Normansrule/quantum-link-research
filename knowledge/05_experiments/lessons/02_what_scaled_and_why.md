# What scaled, what did not, and why

| Scaled | Why |
|---|---|
| Transmons (1 → 1000 qubits in 15 years) | one solvable problem at a time: charge noise (transmon), readout (circuit QED), materials (Ta), architecture (tunable couplers); a fabrication process inherited from semiconductors |
| Neutral-atom arrays (1 → 6000 atoms in 8 years) | identical atoms need no fabrication; optical addressing scales with commercial photonics (SLMs, AODs) |
| Satellite QKD (600 kg → 23 kg payload in 8 years) | the physics was proven once at scale, then engineering shrank it; portable ground stations turned a national facility into a product |
| Photonic detectors (SNSPD efficiency 10% → 98%) | materials and geometry optimization with a clear metric |
| Error correction (theory 1995 → below threshold 2024) | 29 years of gate-fidelity improvement across all platforms toward a fixed target (~1%) |

| Did not (yet) scale | Why |
|---|---|
| Topological qubits | the qubit itself has not been convincingly demonstrated; theory led evidence |
| NMR quantum computing | pseudo-pure states lose signal exponentially with qubit number |
| Photonic gate-model computing | probabilistic gates without deterministic sources and near-lossless components |
| Single-NV network nodes | herald rates set by the 3% zero-phonon fraction; scaling needed a different emitter (SiV) or cavities |
| Long-distance fiber QKD | exponential loss; the answer was satellites and twin-field, not better lasers |

**Pattern.** Platforms scaled when they (1) had a single dominant noise source that a design change removed, (2) reused an existing industrial fabrication or optics supply chain, and (3) had one agreed metric to optimize. The Earth–Mars link should be designed the same way: identify the single dominant loss (diffraction), reuse a supply chain (DSOC-class optical terminals, DSN), and pick one metric (end-to-end secret bits per day at a target fidelity, with classical latency counted honestly).

**Key references.** Kjaergaard, M., et al. (2020). Superconducting qubits: current state of play. *Annu. Rev. Condens. Matter Phys.*, 11, 369. Manetsch, H. J., et al. (2024). A tweezer array with 6100 highly coherent atomic qubits. arXiv:2403.12021. Li, Y., et al. (2025). *Nature*, 640, 47. Hadfield, R. H. (2009). *Nature Photonics*, 3, 696.
