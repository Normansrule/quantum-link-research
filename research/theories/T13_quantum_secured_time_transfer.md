# T13 — Quantum-Secured Time Transfer

**Claim.** The arrival times of entangled photon pairs can synchronize two clocks to picoseconds and, because the pairs' timing correlations cannot be forged without breaking their entanglement, the synchronization is tamper-evident [ho2009] [lee2019]. Time transfer is the hidden dependency of every timing-based protocol in this repository, from coincidence windows to position verification.

**Mechanism.** Cross-correlate the detection times of the two halves of SPDC pairs at the two stations; the peak's position gives the clock offset, its width the timing precision (set by detector jitter, tens of picoseconds for SNSPDs). An adversary who intercepts and re-emits photons changes the correlation and is detected by a simultaneous Bell test.

**Why it matters for a Mars link.** Chapter 3 of this thesis assumes clocks agree to the coincidence window; over 20 minutes of light time with Doppler shifts of 6 × 10⁻⁵ (`qll.space.relativity`) that agreement must be actively maintained. A time transfer that rides on the entanglement channel itself needs no separate reference and detects spoofing.

**What would change the design.** The detectors already exist; the addition is a time-tagger with picosecond resolution and a correlation engine, which P03 buys anyway.

**Evidence and status.** Demonstrated in fibre and free space over tens of kilometres with sub-nanosecond stability; a satellite demonstration proposed. TRL 4.

**Cheap version.** P03 bench: record time tags on both arms with the QRNG board's FPGA (a timestamping tile is the natural hardware), compute the offset, then insert a variable delay and recover it.

**References.** Ho, C., Lamas-Linares, A., & Kurtsiefer, C. (2009). *New Journal of Physics*, 11, 045011. https://doi.org/10.1088/1367-2630/11/4/045011 Lee, J., et al. (2019). Symmetrical clock synchronization with time-correlated photon pairs. *Applied Physics Letters*, 114, 101102. https://doi.org/10.1063/1.5086493 Quan, R., et al. (2016). Demonstration of quantum synchronization based on second-order quantum coherence of entangled photons. *Scientific Reports*, 6, 30453. https://doi.org/10.1038/srep30453
