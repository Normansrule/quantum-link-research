# E5 — Fail-closed messaging under 20-minute latency with a quantum-derived key hierarchy

**Gap.** Hybrid post-quantum (ML-KEM, FIPS 203) plus QKD key management is demonstrated on terrestrial networks with millisecond acknowledgments. Key-exhaustion behavior, rekey scheduling, and replay protection for an application whose acknowledgments take 6–45 minutes are unstudied.

**Cheapest version.** Software: `qll/app/messenger.py` with keys from EntropyLoop or the owner's FPGA QRNG board, ML-KEM from kyber-py, AES-256-GCM from `cryptography`, every message routed through `light_time_delay.DelayQueue`. Measure the key buffer needed so a conversation never blocks, and prove the messenger refuses to send when the buffer is empty (fail closed) rather than falling back to a weaker key.

**Verifies.** REQ-APP-001.

**Failure modes.** Nonce reuse across a 20-minute window with retransmissions; clock skew between endpoints; the hybrid KEM handshake itself costing several round trips (design a one-round-trip handshake).

**Key references.** NIST (2024). FIPS 203, Module-Lattice-Based Key-Encapsulation Mechanism Standard. Bindel, N., et al. (2019). Hybrid key encapsulation mechanisms and authenticated key exchange. *PQCrypto 2019*. Dworkin, M. (2007). NIST SP 800-38D (GCM). Mohageg, M., et al. (2022). *EPJ Quantum Technol.*, 9, 25.
