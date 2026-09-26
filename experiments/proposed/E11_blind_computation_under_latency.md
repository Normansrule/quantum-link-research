# E11 — Blind (delegated) quantum computation under a 20-minute latency

**Gap.** Universal blind quantum computation lets a client with only single-qubit preparation delegate a computation to a server that learns nothing about it [broadbent2009]; every published protocol is interactive, with one classical round per measurement layer. At Mars distance each round costs 6–45 minutes.

**Question.** For a circuit of depth D, how much wall-clock time does blind delegation cost at Mars, and how much can batching (pre-sending all rotated qubits, adaptive corrections folded into classical post-processing where the circuit's Clifford structure allows) recover?

**Cheap version (software).** Model the protocol as D rounds of `ClassicalMessage` exchanges; implement the one-bit-teleportation measurement pattern from `qll/circuits/decompositions.one_bit_teleportation` on a small cluster in Qiskit; compute wall-clock time versus D for Earth–Moon and Earth–Mars; identify which layers are Clifford (non-adaptive) and can be batched.

**Research version.** A protocol that trades extra qubits for fewer rounds (e.g. measuring Clifford layers non-adaptively and deferring corrections), with its security argument.

**Verifies.** A new requirement on delegated computation latency; relates to T07.

**References.** Broadbent, A., Fitzsimons, J., & Kashefi, E. (2009). *FOCS*, 517. https://doi.org/10.1109/FOCS.2009.36 Barz, S., et al. (2012). Demonstration of blind quantum computing. *Science*, 335, 303. https://doi.org/10.1126/science.1214707
