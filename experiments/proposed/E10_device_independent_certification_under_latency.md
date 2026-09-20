# E10 — Device-independent certification under planetary latency

**Gap.** Device-independent QKD and self-testing certify a channel from a Bell violation, but the protocol needs the settings and outcomes exchanged classically, and the security analysis assumes prompt exchange. With 20-minute one-way delay, how many rounds can be buffered, how is the freedom-of-choice condition stated, and what is the finite-key penalty?

**Cheapest version.** Software: Stim samples CHSH trials with settings drawn from `hardware/randomness.py`; a `DelayQueue` holds the classical records for the light-time; compute the DI key rate $r\ge1-h_2\big(\frac{1+\sqrt{S^2/4-1}}{2}\big)-h_2(Q)$ with finite-size corrections vs buffer length.

**Cheapest version implemented (0.14.0).** `simulations/s06_di_certification_under_latency.py`: with a simplified finite-key penalty, an S = 0.95·2√2 device needs ≈ 2 500 rounds for a positive key at ε = 10⁻¹⁰; one Mars-maximum round trip at 1 pair/s holds ≈ 2 700, so the pair rate rather than the delay decides certifiability. Records are sealed for the light time by `ClassicalMessage`.

**Verifies.** A new requirement REQ-SEC-001: "the link can certify its own security without trusting the Mars device, with classical exchange bounded by d/c."

**Key references.** Acín, A., et al. (2007). *Physical Review Letters*, 98, 230501. Pironio, S., et al. (2009). *New J. Phys.*, 11, 045021. Nadlinger, D. P., et al. (2022). Experimental quantum key distribution certified by Bell's theorem. *Nature*, 607, 682. Zhang, W., et al. (2022). A device-independent quantum key distribution system for distant users. *Nature*, 607, 687.
