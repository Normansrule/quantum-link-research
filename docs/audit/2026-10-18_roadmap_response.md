# Response to the October 18, 2026 roadmap: a fault-tolerant global and interplanetary quantum network

**Received:** the roadmap's summary (executive recommendation, algorithms, swapping protocol, sustained-service argument, off-grid messaging, stage criteria, planetary delays, and implementation directive). The 21-file engineering package it mentions, including its reference scheduler and tests, was not attached, so this response builds from the summary.
**Release:** 0.59.0.

Each recommendation is answered with one label: **SIMULATED**, **VERIFIED SOFTWARE**, **MEASURED HARDWARE**, or **FUTURE RESEARCH**. Nothing in this release is MEASURED HARDWARE.

## Recommendations and responses

| # | Recommendation | Response | Label | Evidence |
|---|---|---|---|---|
| R1 | Build two separate systems: an internet-independent messenger and a fault-tolerant quantum research platform | Both are modelled, sharing nothing but authentication and application code; [program document 11](../../systems/program/11_healing_network.md) keeps them apart | SIMULATED | — |
| R2 | A pair ledger in which a consumed, expired, or failed pair can never become available again | `qll/network/pair_ledger.py`: forward-only statuses, an append-only event log, swaps and purifications that consume their inputs on failure too, new identifiers for new pairs, and a conservation check on every run | VERIFIED SOFTWARE | `tests/test_pair_ledger.py` (including randomized operation sequences) |
| R3 | A swapped pair is not usable before its classical correction arrives | A pair stays pending until `ready_s`, set by the light time to the farther end; using it earlier raises | VERIFIED SOFTWARE | `test_nothing_is_usable_before_its_herald_arrives`, `test_a_swap_consumes_its_inputs_and_waits_for_its_outcome` |
| R4 | Track fidelity through swaps instead of assuming connection length is free | Werner decay in memory, the swap map, and BBPSSW purification, reusing the repository's tested formulas | VERIFIED SOFTWARE | `test_closed_forms_match_the_repository_physics` |
| R5 | Measure sustained service availability, not the survival of one state | `simulate_service` (three nodes, random heralds and requests) reports availability, delivered fidelity, and waste; `survival_probability` gives (1 − p_L)^N | SIMULATED | `test_the_service_conserves_pairs_and_shows_that_supply_alone_is_not_enough`, `test_one_logical_qubit_cannot_survive_for_ever` |
| R6 | Repetition, Steane, and distance-3/5/7 rotated surface codes with ancilla reset and matching | Repetition, five-qubit, and Steane codes already existed; `qll/circuits/logical_memory.py` adds circuit-level rotated surface codes at d = 3, 5, 7 with d rounds of measure-and-reset ancillas and PyMatching | SIMULATED | `tests/test_logical_memory.py`: 17, 49, 97 qubits; each ancilla reset each round; threshold near 0.6 % |
| R7 | Test whether added distance pays for its extra gates | Below threshold each step in distance lowers the logical error; above it, it raises it | SIMULATED | `test_redundancy_pays_below_threshold_and_hurts_above_it` |
| R8 | Erasure-aware decoding, leakage and correlated errors, dynamical decoupling, Pauli-frame tracking | Not implemented in this release | FUTURE RESEARCH | — |
| R9 | An offline LoRa messenger whose status never mistakes a relay's acknowledgment for delivery | `qll/link/mesh_messenger.py`: delivery states queued, relayed, delivered, unreachable that only move forward; only the recipient's end-to-end acknowledgment marks delivery; LoRa sensitivity, time on air, radio horizon, and flooding with a hop limit | SIMULATED (formulas VERIFIED SOFTWARE) | `tests/test_mesh_messenger.py` |
| R10 | Encrypted radio only where lawful | The module states the U.S. amateur prohibition on messages encoded to obscure their meaning and assumes unlicensed ISM equipment | VERIFIED SOFTWARE (documentation) | `qll/link/mesh_messenger.py` docstring |
| R11 | A real LoRa demonstrator with measured coverage | Protocol, logger, and analysis ready (P16, `qll/link/radio_survey.py`, 0.60.0); the walk itself has not been run | VERIFIED SOFTWARE; hardware FUTURE RESEARCH | — |
| R12 | Earth–Moon, Earth–Mars, Earth–Jupiter delays from real orbital positions | Jupiter's mean elements join the ephemeris; the latency model and page include Jupiter | SIMULATED | `test_jupiter_is_half_an_hour_to_most_of_an_hour_away` |
| R13 | README paths: send messages offline, explore quantum science, build the quantum testbed | Done; the capability table adds the ledger, the logical memory, and the mesh with their labels | VERIFIED SOFTWARE (links tested) | `tests/test_readme_art.py` |
| R14 | Visualizations of syndrome correction, resource consumption and replacement, the mesh, and planetary delays, each labelled | The [network page](https://normansrule.github.io/quantum-link-research/network/) replays the ledger, the distance scan, and the mesh, labelled SIMULATED, with play, pause, step, and reset; the QEC lab already animates syndromes, and the latency page covers planetary delays | VERIFIED SOFTWARE | `test_network_page_replays_the_ledger_and_labels_everything_simulated`, `test_network_page_data_is_current` |
| R15 | Fix the carried-forward security findings before anything else | Already fixed in 0.56.0, before this roadmap arrived: replenishment from accepted secret bytes, sticky authentication states, one-time key identifiers, session-bound transport, CI gating; see the [findings matrix](2026-10-11_findings.md) | VERIFIED SOFTWARE | `tests/test_key_lifecycle.py`, `tests/test_two_room.py`, `tests/test_release_gates.py` |
| R16 | Authenticated heralds, so a forged or stale Bell-measurement result cannot create a pair | The ledger already refuses any pair before its herald time; carrying heralds over the session-bound transport between processes is the next step | FUTURE RESEARCH | — |

## Corrections to the roadmap's numbers

- **Swapped fidelity.** For two Werner pairs of fidelity 0.95, the formula the roadmap states, F₁F₂ + (1 − F₁)(1 − F₂)/3, gives **0.9033**, not 0.9042. The Werner parameters multiply: w = (4 × 0.95 − 1)/3 = 0.9333, w² = 0.8711, F = (3w² + 1)/4 = 0.9033.
- **Earth–Jupiter light time.** The mean-element ephemeris gives **32.9 to 53.7 minutes** one way over two Jovian orbits (3.95 to 6.45 au), wider than the roadmap's approximate 35 to 52 minutes, as the roadmap anticipated when it asked for orbital positions.
- **The surface-code resource table** (17, 49, 97 physical qubits for d = 3, 5, 7) is confirmed against the generated circuits.
