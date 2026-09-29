# Concept of operations

**Operational levels.** (0) Bench qubits and photons; (1) two-qubit primitives; (2) one link; (3) a network with memories; (4) the Earth–Mars link.

**Baseline scenario (level 4, from trade studies TS-1 to TS-4).**
1. An Earth station with a multiplexed pair source (about 10¹² pairs/s across 1000 modes) stores one photon of each pair in a trapped-ion memory and sends the other through a 0.5 m-waist beam toward a 4 m receiver at Mars.
2. The Mars station heralds arrivals, stores its photons in memories, and reports which modes arrived; roughly 10⁶–10⁷ pairs a day survive (learn 03/21).
3. To teleport, Earth performs a Bell measurement on the message qubit and its stored half and sends two classical bits over the deep-space optical link; Mars applies the correction when they arrive, 3–22 minutes later, holding its half for up to one round trip (REQ-CAP-001).
4. For key, both ends measure stored pairs in random bases (BBM92) and distil a secret; the messenger spends it and refuses to send when it runs out (REQ-APP-001). Near maximum range the pairs are useful for teleportation but too noisy for key.
5. During the three weeks of solar conjunction each synodic period the direct line is blocked; a relay at L4 or L5 with its own memory stores keys or pairs and forwards them (REQ-SPC-002), and the messenger's buffer must cover the gap (docs/monitor).

**Open question.** Whether a memory can hold entanglement for the 6–45 minute round trip with both high coherence and high retrieval: today only the trapped ion does both, with a margin under 1.5× at maximum range (R-1).
