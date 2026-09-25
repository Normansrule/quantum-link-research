# T12 — Quantum Position Verification

**Claim.** A prover can convince verifiers that it is at a claimed location by responding to quantum challenges within the light-time constraints of that location; classical position verification is impossible against colluding adversaries, and quantum protocols are secure against adversaries with bounded pre-shared entanglement [buhrman2014] [chandran2009].

**Mechanism.** Verifiers at known positions send a qubit and classical instructions timed so that both arrive at the claimed location simultaneously; only a device actually there can apply the instructed measurement and return the result to both verifiers in time. Adversaries elsewhere would need to teleport the qubit between themselves, which costs entanglement; with enough pre-shared entanglement the attack succeeds, so security is conditional [beigi2011].

**Why it matters for a Mars link.** Authenticating that a message truly comes from the Mars node (not a relay or an impostor) is normally cryptographic; position verification makes it physical, using the same light-time reasoning that `qll.channels.light_time_delay` enforces everywhere. The 3–22 minute light times make the timing constraints loose, so the protocol needs entanglement-bounded adversaries at astronomical distances, which is a plausible assumption.

**What would change the design.** A second verifier (a relay at L4/L5) with an independent clock; nothing else.

**Evidence and status.** Theory mature; small experiments in fibre; no deployed system. TRL 2.

**Cheap version.** Implement the one-qubit protocol with `ClassicalMessage` timing from two verifiers and show the impossibility for a single adversary without entanglement.

**References.** Chandran, N., Goyal, V., Moriarty, R., & Ostrovsky, R. (2009). Position based cryptography. *CRYPTO 2009*, LNCS 5677, 391. https://doi.org/10.1007/978-3-642-03356-8_23 Buhrman, H., et al. (2014). Position-based quantum cryptography: impossibility and constructions. *SIAM Journal on Computing*, 43, 150. https://doi.org/10.1137/130913687 Beigi, S., & König, R. (2011). Simplified instantaneous non-local quantum computation with applications to position-based cryptography. *New Journal of Physics*, 13, 093036. https://doi.org/10.1088/1367-2630/13/9/093036
