# Concept of operations

**Operational levels.** (0) Bench qubits and photons; (1) two-qubit primitives; (2) one link; (3) a network with memories; (4) the Earth–Mars link.

**Baseline scenario (level 4, from trade studies TS-1 to TS-4 and TS-6).**
1. An Earth-end node on a spacecraft at about the lunar distance from Earth, off Earth's disk as seen from Mars, carries a multiplexed pair source (about 10¹² pairs/s across 1000 modes), stores one photon of each pair in a trapped-ion memory, and sends the other through a 0.5 m-waist beam toward a 4 m receiver at Mars. Ground users reach the node over a short link; a transmitter on the ground would be lost in the glare of sunlit Earth for most of each synodic period (R-9).
2. The Mars station filters each mode to 100 MHz, rejects the off-axis Earthshine to a floor of 10⁻⁹, heralds arrivals, stores its photons in memories, and reports which modes arrived; roughly 10⁶–10⁷ pairs a day survive, at least 96 % of heralds being signal (learn 03/21).
3. To teleport, Earth performs a Bell measurement on the message qubit and its stored half and sends two classical bits over the deep-space optical link; Mars applies the correction when they arrive, 3–22 minutes later, holding its half for up to one round trip (REQ-CAP-001).
4. For key, both ends measure their photons in random bases as they arrive (BBM92), with no memory, and distil a secret from 5 × 10⁵ to 2 × 10⁷ bits a day depending on range. The key goes into a bank of about 17 MB at each end, from which the messenger spends 10⁶ bits a day as one-time pad or session keys, and it refuses to send if the bank runs dry (REQ-APP-001, REQ-APP-003, TS-7).
5. During the three weeks of solar conjunction each synodic period the direct line is blocked; the key bank carries the messenger through the gap (REQ-APP-003), and a relay at L4 or L5 can forward classical traffic around the Sun (REQ-SPC-002).

**Open question.** Whether a memory can hold entanglement for the 6–45 minute round trip with both high coherence and high retrieval: today only the trapped ion does both, with a margin under 1.5× at maximum range (R-1).
