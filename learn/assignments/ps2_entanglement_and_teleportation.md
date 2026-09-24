# Problem Set 2 — Entanglement, Teleportation, Light Time

Read `learn/00_foundations/05`, `learn/03_quantum_communication/02`. Check with `python -m pytest tests/test_assignments.py -k ps2`.

1. **CHSH.** For a Werner state with fully entangled fraction $f=0.85$, compute the CHSH value at the optimal settings. *(`ps2_chsh_085`)*
2. **Threshold.** Below which $f$ does the Werner state stop violating CHSH? Below which does teleportation fall to the classical fidelity 2/3? *(`ps2_f_chsh_threshold`, `ps2_f_teleport_threshold`)*
3. **Teleportation fidelity.** Average teleportation fidelity with the $f=0.85$ resource. *(`ps2_tele_fid_085`)*
4. **Light time.** A teleportation is performed with Bob at 1.2 au. How long after Alice's Bell measurement can Bob first apply his correction, in minutes? How many classical bits did Alice send? *(`ps2_delay_min`, `ps2_bits`)*
5. *(written)* Bob measures his qubit before Alice's bits arrive. What does he see, and why does this not let Alice signal him? Use `qll.circuits.teleportation.SealedQubit` in your answer.
6. *(written)* A vendor claims a "quantum link" that sends messages faster than light using entanglement. Write the two-sentence reply a systems engineer should give, citing the theorem.
