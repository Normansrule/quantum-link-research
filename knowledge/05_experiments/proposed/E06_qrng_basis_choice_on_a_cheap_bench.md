# E6 — Quantum-random measurement bases on a sub-$500 NV bench and on the SPDC Bell test

**Gap.** Random basis choice from a quantum source has been done in the large loophole-free Bell tests (Hensen 2015; Big Bell Test 2018), never on a teaching-lab bench; and the owner's own QRNG PCB (reverse-biased diode and optical noise into an FPGA) has never been exercised as the entropy source of a Bell test.

**Cheapest version.** EntropyLoop (~$35) or the owner's board selects the half-wave-plate angle (via a stepper) or the microwave phase (on the NV bench) per trial; log the seed with each event; compare $S$ against runs with a pseudo-random generator and with fixed settings. Implements invariant INV-7 in hardware.

**Verifies.** REQ-QKD-001 with quantum randomness in the loop; gives `qll/hardware/randomness.py` a real `SerialQrng` device to test against (NIST SP 800-90B health tests).

**Failure modes.** Slow mechanical setting changes make the "freedom of choice" symbolic rather than space-like; declare that honestly. Bias or correlation in the QRNG output will show up as an $S$ that depends on the seed stream.

**Key references.** The BIG Bell Test Collaboration (2018). Challenging local realism with human choices. *Nature*, 557, 212. Abellán, C., et al. (2014). *Optics Express*, 22, 1645. Herrero-Collantes, M., & Garcia-Escartin, J. C. (2017). Quantum random number generators. *Rev. Mod. Phys.*, 89, 015004. Turan, M. S., et al. (2018). NIST SP 800-90B.
