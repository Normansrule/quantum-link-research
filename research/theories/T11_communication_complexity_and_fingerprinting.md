# T11 — Quantum Communication Complexity and Fingerprinting

**Claim.** Some distributed tasks need exponentially fewer *transmitted* qubits than classical bits: quantum fingerprinting decides whether two n-bit files are equal with O(log n) qubits and no shared randomness, against Ω(√n) classical bits in the same model [buhrman2001]; coherent-state fingerprinting has been demonstrated beating the classical limit on transmitted information [xu2015] [guan2016].

**Mechanism.** Each party maps its file to a quantum state whose inner product is near 1 if the files are equal and bounded away otherwise; a referee performs a swap test. With coherent states the "fingerprint" is a sequence of weak pulses whose total mean photon number can be far below the classical bit count.

**Why it matters for a Mars link.** Bandwidth is not the bottleneck at Mars (DSOC-class links deliver tens of Mb/s), latency is; but for tasks where the *round count* rather than the bit count is the cost, quantum protocols that finish in one round replace multi-round classical protocols. Equality testing of large datasets between Earth and Mars in a single one-way transmission is the concrete example.

**What would change the design.** Nothing in the physical layer: fingerprinting uses the same weak coherent pulses as CV-QKD and BB84. It adds an application to Phase 6: a one-round equality check.

**Evidence and status.** Demonstrated in fibre over 20 km with a transmitted information advantage of an order of magnitude [guan2016]; not yet used operationally. TRL 3.

**Cheap version.** Simulate coherent-state fingerprinting with `qll.hardware.photon_source.WeakCoherentSource` and compare transmitted photons against the classical bound for n = 10⁶.

**References.** Buhrman, H., Cleve, R., Watrous, J., & de Wolf, R. (2001). Quantum fingerprinting. *Physical Review Letters*, 87, 167902. https://doi.org/10.1103/PhysRevLett.87.167902 Xu, F., et al. (2015). Experimental quantum fingerprinting with weak coherent pulses. *Nature Communications*, 6, 8735. https://doi.org/10.1038/ncomms9735 Guan, J.-Y., et al. (2016). Observation of quantum fingerprinting beating the classical limit. *Physical Review Letters*, 116, 240502. https://doi.org/10.1103/PhysRevLett.116.240502
