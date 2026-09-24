# Problem Set 3 — Loss, Keys, Memories, Purification

Read `learn/03_quantum_communication/01`, `03`, `04`, `11`. Check with `python -m pytest tests/test_assignments.py -k ps3`.

1. **Fiber.** Transmittance of 150 km of fiber at 0.2 dB/km. *(`ps3_eta_fiber_150`)*
2. **Free space.** Exact Gaussian-over-aperture transmittance from a 15 cm waist at 810 nm to a 1 m receiver at 1 000 km. *(`ps3_eta_leo`)*
3. **Key rate.** Secret fraction per sifted bit for BB84 at QBER 4 %. What is the PLOB capacity in bits per use at the transmittance of question 1, and does the decoy-state rate stay below it? *(`ps3_bb84_frac_004`, `ps3_plob_150`)*
4. **Memory.** A Bell pair of fraction 0.95 is stored in a depolarizing memory with $T=3600$ s. After how many seconds does its teleportation fidelity reach 2/3? Does this exceed the Mars-maximum round trip? *(`ps3_crossover_s`, `ps3_beats_mars_max` as True/False)*
5. **Purification.** How many BBPSSW rounds take $F=0.8$ to 0.99, and how many DEJMPS rounds? *(`ps3_bbpssw_rounds`, `ps3_dejmps_rounds`)*
6. *(written)* Using the memory capability matrix, propose a node design for the Mars leg and state its efficiency penalty.
7. *(written)* Explain in one paragraph why the twin-field protocol may exceed the PLOB bound without contradicting it.
