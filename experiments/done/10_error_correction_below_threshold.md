# Error correction below threshold (Google 2023, 2025) and logical atom arrays (Harvard/QuEra 2024)

**Original.** Google's Sycamore showed a distance-5 surface code with lower logical error than distance 3 (2023); Willow (105 qubits) showed $\Lambda\approx2.14$ from $d=3\to5\to7$ with a logical memory lifetime exceeding the best physical qubit (2024/2025). Harvard/MIT/QuEra ran 48 logical qubits encoded in 280 atoms with logical gates and mid-circuit readout (2024).

**Physics.** `learn/01_quantum_computing_core/03`: $p_L\propto(p/p_{\rm th})^{(d+1)/2}$; the experiments measure $\Lambda$ directly.

**Simple recreation.** Software only: Stim + PyMatching simulate a surface-code memory with circuit-level noise in minutes on a laptop; sweep $p$ and $d$, recover $\Lambda$, and compare with the published values. This is a natural extension test for Phase 4 (repeater generations) and is pinned already (`stim==1.16.0`).

**What went wrong historically.** Correlated errors (cosmic rays, leakage to non-computational states, crosstalk) violated the independent-error assumption; real-time decoding at 1 µs cycles was a systems problem as hard as the physics.

**Repo hook.** Stim stubs for Phase 4 repeater-generation comparison; `research/cutting_edge/01` timeline.

- Google Quantum AI (2023). *Nature*, 614, 676. Google Quantum AI (2025). *Nature*, 638, 920 (**TODO: verify DOI**).
- Bluvstein, D., et al. (2024). *Nature*, 626, 58. https://doi.org/10.1038/s41586-023-06927-3
- Higgott, O., & Gidney, C. (2025). Sparse Blossom: correcting a million errors per core second with minimum-weight matching. *Quantum*, 9, 1600. (PyMatching.) **TODO: verify.**
