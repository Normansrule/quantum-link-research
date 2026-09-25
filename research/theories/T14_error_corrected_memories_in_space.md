# T14 — Error-Corrected Quantum Memories in Space

**Claim.** A logical qubit in an error-correcting code can hold a state longer than any physical qubit, and the 2024–2025 below-threshold results make an error-corrected memory the long-term alternative to rare-earth crystals for holding entanglement across a Mars round trip [google2025willow] [bluvstein2024].

**Mechanism.** Surface-code memory with distance d: logical error per cycle falls as Λ^(−(d+1)/2), Λ ≈ 2 in the Willow experiment, so doubling d halves the exponent; the price is d² physical qubits per logical one and a cryostat. A memory that must survive 45 minutes at 1 µs cycle time runs 2.7 × 10⁹ cycles: with a physical error of 10⁻³ and Λ = 2, a distance ~25 code (≈ 1 250 qubits) reaches 10⁻¹⁰ per cycle, enough for a 0.3 chance of surviving the round trip — the arithmetic in `qll.circuits.stabilizer_codes` and S04 scaled up.

**Why it matters for a Mars link.** It moves the memory problem from materials (find a longer T₂) to engineering (build more qubits and a cooler), and it would let a *processor* hold the entanglement, enabling one-way (gen-2/3) repeater protocols that remove the purification round trips (learn 03/11).

**What would change the design.** A 4 K–10 mK payload, which `qll.space.platform_thermal` says does not fly today for a superconducting processor; a neutral-atom or ion logical memory needs only a vacuum system and lasers and is the plausible route.

**Evidence and status.** Ground: below-threshold memory (Google 2024), 48 logical qubits (Harvard/QuEra 2023). Space: none. TRL 2 for flight.

**Cheap version.** Extend S04 to a distance-d surface code in Stim with a decoder and compute the qubits needed for a given survival probability over the Mars round trip; compare with the rare-earth line in the capability matrix.

**References.** Google Quantum AI (2025). *Nature*, 638, 920. https://doi.org/10.1038/s41586-024-08449-y Bluvstein, D., et al. (2024). *Nature*, 626, 58. https://doi.org/10.1038/s41586-023-06927-3 Fowler, A. G., et al. (2012). *Physical Review A*, 86, 032324. https://doi.org/10.1103/PhysRevA.86.032324
