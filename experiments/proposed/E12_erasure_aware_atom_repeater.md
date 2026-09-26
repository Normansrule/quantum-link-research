# E12 — An erasure-aware neutral-atom repeater node

**Gap.** Converting a qubit's dominant error into a detected erasure roughly doubles the tolerable error rate for correction [wu2022]; repeater analyses treat memory errors as undetected.

**Question.** If a neutral-atom node flags Rydberg decay and atom loss as erasures, how much does the entanglement-swapping fidelity and the chain crossover distance improve compared with the same error rate undetected?

**Cheap version (software).** In `qll/network/repeater_chain`, add a per-swap erasure probability that discards (rather than corrupts) the pair; compare the chain's rate and final fidelity with the same probability as depolarization; Stim for a small code on the node.

**Research version.** Alkaline-earth atoms (Yb) where the erasure conversion is native; a node design with photon emission from a telecom-compatible transition.

**Verifies.** Extends REQ-NET-001 with an error model; relates to learn 02/16 and T14.

**References.** Wu, Y., Kolkowitz, S., Puri, S., & Thompson, J. D. (2022). *Nature Communications*, 13, 4657. https://doi.org/10.1038/s41467-022-32094-6 Ma, S., et al. (2023). High-fidelity gates and mid-circuit erasure conversion in an atomic qubit. *Nature*, 622, 279. https://doi.org/10.1038/s41586-023-06438-1
