# E1 — Teleportation with the classical channel delayed to a planetary light-time

**Gap.** Every teleportation experiment to date closes the classical channel within microseconds to milliseconds. No one has completed teleportation where the two bits arrive 3–22 minutes after the Bell measurement, which is the operating regime of an Earth–Mars link.

**Physics being tested.** The no-signaling theorem says the delay changes nothing about Bob's state until the bits arrive; the memory-decoherence model says the fidelity when they arrive is $F=(2f(t)+1)/3$ with $f(t)$ the stored singlet fraction. The experiment measures $F$ versus classical delay and finds where it crosses $2/3$.

**Cheapest version (Tier 1, SPDC bench).** Do not delay the qubit, delay the *record*: run the CHSH/teleportation bench, log Alice's Bell-measurement outcomes with timestamps, and release them to Bob's analysis only after a software delay equal to the Mars light-time (`qll/channels/light_time_delay.py` `DelayQueue`). Show that the conditional correlations are identical for any delay: a direct classroom demonstration that the two bits, and nothing else, carry the state. Cost: zero above the Bell bench.

**Research version.** Store one half of an entangled pair in a Eu:YSO or NV-¹³C memory for the full light-time, transfer the two bits over a link throttled to the Deep Space Network round-trip time, apply the correction, and measure $F(t)$. The rare-earth memory is the only one whose lifetime already allows the 45-minute worst case.

**Verifies.** REQ-CAP-001 (memory time vs light delay), REQ-PHY-002 (2 bits), and adds REQ-CAP-002 ("teleportation completes after a light-time-delayed classical channel").

**Failure modes to expect.** Timestamp synchronization between Alice and Bob (GPS-disciplined clocks); memory efficiency at long storage times (rare-earth AFC efficiency falls below 1% at hours); the temptation to read the qubit early, which the `NotYetArrived` guard makes impossible in software and which the protocol must forbid in hardware.

**Key references.** Bennett, C. H., et al. (1993). *Physical Review Letters*, 70, 1895. Hermans, S. L. N., et al. (2022). *Nature*, 605, 663. Wang, F., et al. (2025). *PRX Quantum*, 6, 010302. Peres, A., & Terno, D. R. (2004). *Rev. Mod. Phys.*, 76, 93.
