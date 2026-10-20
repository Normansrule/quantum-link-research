# 11 · A network that heals: from a tabletop ledger to the outer planets

Two systems grow side by side and share their routing, authentication, and application layers, but are never confused:

1. **An off-grid messenger** that people can use in mountains, wilderness, and disaster zones over radio relays, and over satellites where they exist. It is classical, encrypted where that is lawful, and achievable now.
2. **A fault-tolerant quantum-network research platform** that studies how entangled logical qubits are protected, exchanged, refreshed, and supplied continuously, from a tabletop to planetary distances.

Entanglement alone carries no message and cannot replace the radio, optical, or satellite path to a remote person. The research target is therefore a service that keeps replacing the entanglement it spends, not one pair that survives for ever: with any nonzero logical error p_L per cycle, one stored state survives N cycles with probability (1 − p_L)^N, which tends to zero. The architecture follows RFC 9340, which separates entanglement generation, swapping, distillation, and classical control (Kozlowski et al., 2023).

Every result carries one label: **SIMULATED** (a model's output), **VERIFIED SOFTWARE** (code behaviour tested against closed forms or invariants), **MEASURED HARDWARE** (raw data from a device), or **FUTURE RESEARCH** (not yet built).

## What exists now

| Capability | Where | Label | Evidence |
|---|---|---|---|
| Pair ledger: pairs pending until heralded at light speed, swaps and purifications that consume their inputs whether or not they succeed, decay and expiry, an append-only event log | [`qll/network/pair_ledger.py`](../../qll/network/pair_ledger.py) | VERIFIED SOFTWARE | `tests/test_pair_ledger.py`: closed forms, causality, consumption, failure restores nothing, expiry, randomized conservation runs |
| Three-node sustained service (Alice · Relay · Charlie): availability, delivered fidelity, waste | same | SIMULATED | With 0.5 s memories, supply of 3 pairs/s against demand of 2 requests/s still misses about a quarter of requests, because swapped pairs decay in about 60 ms; 5 s memories serve all or nearly all |
| Logical memory with reused ancillas: rotated surface code d = 3, 5, 7 (17, 49, 97 qubits), d rounds of syndrome extraction with measure-and-reset, matching decoder | [`qll/circuits/logical_memory.py`](../../qll/circuits/logical_memory.py) | SIMULATED | `tests/test_logical_memory.py`: qubit counts, every ancilla reset every round, threshold near 0.6 % (distance helps below it, hurts above it) |
| Repetition, five-qubit, and Steane codes with syndrome tables; code-capacity surface code with matching; purification (BBPSSW, DEJMPS) | `qll/circuits/stabilizer_codes.py`, `surface_code_capacity.py`, `qll/network/purification.py` | VERIFIED SOFTWARE | existing analytic tests |
| Off-grid mesh: LoRa sensitivity and time on air, radio horizon, flooding with a hop limit, and delivery states in which a relay's rebroadcast is never delivery | [`qll/link/mesh_messenger.py`](../../qll/link/mesh_messenger.py) | SIMULATED (formulas VERIFIED SOFTWARE) | `tests/test_mesh_messenger.py`; the two-valley scenario delivers in 1.3 s with a ridge relay and is unreachable without one |
| Messages in one trip from banked key, between two independent processes | [`qll/link/banked_messenger.py`](../../qll/link/banked_messenger.py) | VERIFIED SOFTWARE (emulated delay) | `tests/test_banked_messenger.py` |
| Light-time floor anywhere, including Jupiter (32.9 to 53.7 minutes one way from the ephemeris) | [`qll/space/latency_floor.py`](../../qll/space/latency_floor.py) | SIMULATED | `tests/test_latency_floor.py` |

The [network page](https://normansrule.github.io/quantum-link-research/network/) replays these runs.

## Stages and release criteria

| Stage | Build | Required demonstration | Status |
|---|---|---|---|
| 0. Simulation | Python models: ledger, logical memory, mesh, latency | Correct accounting, no-signalling, repeatable results | VERIFIED SOFTWARE for the pieces above |
| 1. Tabletop | Two separated endpoints, an optical source, qualified detectors (P10) | Independently measured channel behaviour, raw logs | FUTURE RESEARCH (blocked by the safety review; see the evaluation specification) |
| 2. Three nodes | Two quantum links joined through a relay | Real or clearly simulated Bell measurement, pair consumption, fidelity, classical corrections | SIMULATED (the ledger); hardware is FUTURE RESEARCH |
| 3. Campus and region | Several optical or fiber nodes with independent control | Finite-memory routing, recovery from failed links | FUTURE RESEARCH |
| 4. Mountain mesh | Phones, LoRa radios, solar ridge relays | Encrypted messaging without internet, with measured coverage | SIMULATED; hardware is the most achievable next build |
| 5. Satellite | Ground stations and optical-link research | Verified link budgets, visibility, telemetry | SIMULATED (Micius budget reproduced); measurements need a partner |
| 6. Earth–Moon | Lunar optical and memory feasibility | Correct delays, measured subsystem constraints | SIMULATED delays |
| 7. Earth–Mars and Jupiter | Mission-scale quantum and classical-backhaul simulations | Causal operation, finite resources, outages, memory decay | SIMULATED; nothing here is mission-qualified |

## Next steps, in order

1. **Mountain mesh on real radios.** Two or three LoRa radios on lawful equipment and bands, the delivery states of `mesh_messenger.py` in a phone app, and measured coverage across real terrain (MEASURED HARDWARE when done). The first step is ready: [P16](../../experiments/protocols/P16_lora_range_walk.md), a $60 two-board range walk whose log `qll/link/radio_survey.py` fits and compares with the model.
2. **Ledger plus logical memory.** Store pairs in logical qubits whose failure per cycle comes from `logical_memory.py`, and compare the service's availability with physical memories.
3. **Contact-aware scheduling.** Generate and bank resources around satellite passes and solar conjunction (the key bank already does this for classical key).
4. **Two-computer runs.** The banked messenger and, later, a two-process ledger with authenticated heralds, so a forged or stale herald cannot create a pair that does not exist.

## References

Kozlowski, W., Wehner, S., Van Meter, R., Rijsman, B., Cacciapuoti, A. S., Caleffi, M., & Nagayama, S. (2023). *Architectural principles for a quantum internet* (RFC 9340). Internet Research Task Force. https://doi.org/10.17487/RFC9340

Fowler, A. G., Mariantoni, M., Martinis, J. M., & Cleland, A. N. (2012). Surface codes: Towards practical large-scale quantum computation. *Physical Review A, 86*, 032324. https://doi.org/10.1103/PhysRevA.86.032324

Briegel, H.-J., Dür, W., Cirac, J. I., & Zoller, P. (1998). Quantum repeaters: The role of imperfect local operations in quantum communication. *Physical Review Letters, 81*, 5932–5935. https://doi.org/10.1103/PhysRevLett.81.5932
