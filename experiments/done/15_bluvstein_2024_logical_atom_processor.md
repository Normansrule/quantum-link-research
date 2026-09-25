# Bluvstein 2024: a logical processor on reconfigurable atom arrays

**Original.** Harvard, MIT, and QuEra ran circuits on up to 48 logical qubits encoded in surface and colour codes across 280 physical rubidium atoms held in optical tweezers. Atoms were moved between storage, entangling, and readout zones with acousto-optic deflectors; entangling gates acted on whole logical blocks in parallel; and logical error rates fell as the code distance grew from 3 to 7 [bluvstein2024]. It was the first demonstration that dozens of logical qubits can be operated together.

**Physics.** Transversal gates: a logical CNOT between two code blocks is a physical CNOT between each pair of corresponding atoms, executed in one parallel Rydberg-gate step because the two blocks are moved into overlap (`learn/02/16`). The zoned architecture separates the noisy operations (entangling, readout) from storage, so idle logical qubits sit in a quiet region; the movement itself costs ~100 µs per rearrangement but negligible decoherence.

**Simple recreation (Tier 3 for hardware; Tier 1 for the logic).** The processor is a university laboratory of first rank. The logical-qubit behaviour is reproducible in Stim: `qll/circuits/stabilizer_codes.py` builds the codes and S04 shows logical error falling with distance; a student project builds a distance-3 colour code in Stim and applies a transversal CNOT between two blocks.

**What went wrong historically.** Nothing; the caveat is that the gates were post-selected on no atom loss in some experiments, and that the logical error rates were measured for shallow circuits. The 2025 follow-ups added mid-circuit measurement and continuous operation.

**Repo hook.** T14 (error-corrected memories in space) rests on this platform: a logical atom memory needs no cryostat, which `qll/space/platform_thermal.py` says is the difference between flying and not.

- Bluvstein, D., et al. (2024). Logical quantum processor based on reconfigurable atom arrays. *Nature*, 626, 58. https://doi.org/10.1038/s41586-023-06927-3
- Evered, S. J., et al. (2023). *Nature*, 622, 268. https://doi.org/10.1038/s41586-023-06481-y
- Bluvstein, D., et al. (2022). A quantum processor based on coherent transport of entangled atom arrays. *Nature*, 604, 451. https://doi.org/10.1038/s41586-022-04592-6
