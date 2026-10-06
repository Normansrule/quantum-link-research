# 03 Needs, requirements, and verification

Mission needs (MN) come from the mission statement; each requirement (MR) is a verifiable "shall" statement allocated to one phase and verified by one milestone. The verification methods follow the classic set [nasa2016seh]:

- **Test:** the hardware or code is exercised and measured against a criterion.
- **Analysis:** a tested model is evaluated.
- **Demonstration:** the system is operated and observed.
- **Inspection:** documents or artifacts are examined.

`tests/test_program_plan.py` checks that every milestone in the plan verifies at least one requirement here, and that every requirement names a milestone that exists.

## Mission needs

| ID | Need |
|---|---|
| MN-1 | Share quantum states between two separated places, starting at the scale of two rooms. |
| MN-2 | Know, before building, what each setup should measure (a digital twin), and confirm it afterwards. |
| MN-3 | Keep cash spending small and committed only after evidence (gates); fund larger steps from outside. |
| MN-4 | Make every experiment replicable by someone else from the published procedure, code, and data. |
| MN-5 | State the physical limits honestly: no requirement may depend on signalling through collapse or on unproven security. |
| MN-6 | Produce publishable results and a path to a product. |
| MN-7 | Grow toward entanglement-assisted secure communication that can reach anywhere on the planet (free space and satellites). |

## Requirements

| ID | Requirement | Need | Phase | Method | Verified by |
|---|---|---|---|---|---|
| MR-0.1 | The simulation library shall reproduce every analytic case it implements, in continuous integration. | MN-2 | 0 | Test | M0.1 |
| MR-0.2 | The two-site link simulation shall trace every SEE 510 need to a module, test, and evidence. | MN-2, MN-4 | 0 | Inspection | M0.2 |
| MR-1.1 | The classical channel between the rooms shall carry authenticated, sequenced frames with zero undetected alterations and a 99th-percentile round trip under 5 ms. | MN-1 | 1 | Test | M1.1 |
| MR-1.2 | The collapse-code experiment shall report, for each scheme and qubit pair, a 99 % upper bound on the information per use, and shall detect an injected leak of 0.1. | MN-5, MN-6 | 1 | Analysis | M1.2 |
| MR-1.3 | The bright-light analogue shall run between the rooms, and its log shall be processed by the same protocol code as the simulation. | MN-2, MN-4 | 1 | Demonstration | M1.3 |
| MR-1.4 | The single-photon receiver's dark-count rate, relative efficiency, and afterpulse fraction shall be measured and entered into the twin. | MN-2 | 1 | Test | M1.4 |
| MR-1.5 | The source shall deliver mean photon numbers of 0.5 (signal) and 0.1 (decoy), within 10 %, with vacuum slots, chosen at random per pulse. | MN-1 | 1 | Test | M1.5 |
| MR-1.6 | The two-room link shall produce an accepted session whose click probability is within 15 % and whose error rate is within 1.5 percentage points of the twin's prediction for the measured parts. | MN-1, MN-2 | 1 | Test | M1.6 |
| MR-1.7 | Data, code, configuration, and analysis of Phase 1 shall be published so that an outside reader can repeat the analysis from the files alone. | MN-4, MN-6 | 1 | Inspection | M1.7 |
| MR-1.8 | Phase 1 cash spending shall not exceed $1,400. | MN-3 | 1 | Inspection | M1.6 |
| MR-2.1 | An entangled-photon source shall be available to the project by loan or partnership before any purchase over $1,000. | MN-3 | 2 | Inspection | M2.1 |
| MR-2.2 | The two rooms shall share entangled photons with a CHSH value above 2 by at least five standard deviations. | MN-1 | 2 | Test | M2.2 |
| MR-2.3 | An entanglement-based key (BBM92) shall be accepted from photons measured in the two rooms, with its error rate inside the twin's interval. | MN-1, MN-2 | 2 | Test | M2.3 |
| MR-2.4 | Bob's records alone shall show no dependence on Alice's analyzer setting beyond the reported bound, and the correlation shall appear when the records are compared. | MN-5 | 2 | Analysis | M2.4 |
| MR-2.5 | Phase 2 results shall be published with data. | MN-4, MN-6 | 2 | Inspection | M2.5 |
| MR-3.1 | The repository's link budget shall reproduce the published Micius and Jinan-1 channel losses within 3 dB, and give pass schedules for a chosen ground site. | MN-7 | 3 | Analysis | M3.1 |
| MR-3.2 | The Phase 1 link shall run outdoors, with measured loss and daylight background compared with the twin. | MN-2, MN-7 | 3 | Test | M3.2 |
| MR-3.3 | A key shall be accepted over a 0.5–2 km free-space path at night. | MN-7 | 3 | Test | M3.3 |
| MR-3.4 | A ground station shall track a satellite pass and timestamp detections within 10 ns of a second clock. | MN-7 | 3 | Demonstration | M3.4 |
| MR-3.5 | A satellite partnership or hosted-payload proposal shall be submitted before any satellite hardware is bought. | MN-3, MN-7 | 3 | Inspection | M3.5 |
| MR-3.6 | A space segment shall proceed only with outside funding, and shall demonstrate in-orbit entanglement and a downlink. | MN-3, MN-7 | 3 | Test | M3.6 |
| MR-4.1 | Teleportation shall be demonstrated with an average fidelity above 2/3 using the two classical bits, and shown to fall to chance without them. | MN-5, MN-7 | 4 | Test | M4.1 |
| MR-4.2 | Superdense coding shall decode two classical bits per transmitted qubit above chance. | MN-7 | 4 | Test | M4.2 |
| MR-4.3 | Teleportation fidelity shall be measured against the delay of the classical channel. | MN-7 | 4 | Analysis | M4.3 |
| MR-4.4 | A three-node network shall give keys between every pair of nodes in the twin, then with two rooms plus one. | MN-7 | 4 | Test | M4.4 |
| MR-4.5 | Photonic teleportation between the rooms shall exceed fidelity 2/3. | MN-7 | 4 | Test | M4.5 |
| MR-4.6 | The measurement-only Majorana teleportation protocol shall be emulated with two parity bits (average fidelity above 2/3) and with one (at or below 2/3), and compared with its error budget. | MN-5, MN-7 | 4 | Test | M4.6 |
| MR-S.1 | At least 30 potential customers shall be interviewed before any money is spent on forming a company. | MN-6, MN-3 | startup | Inspection | S1 |
| MR-S.2 | The company and its intellectual property shall be set up only after the university's intellectual-property policy has been checked. | MN-6 | startup | Inspection | S2 |
| MR-S.3 | A pilot user shall run the kit and match its twin. | MN-6, MN-4 | startup | Demonstration | S3 |
| MR-S.4 | Applications for outside funding shall be submitted with the validated results attached. | MN-3, MN-6 | startup | Inspection | S4 |
| MR-X.1 | No requirement, test, or claim shall depend on signalling through collapse or exceed the security the evidence supports. | MN-5 | all | Inspection | M1.2 |

## Interfaces between phases

- **Data format.** Every link experiment writes one log per site in the format of [`qll/link/hardware_log.py`](../../qll/link/hardware_log.py) (Site A: `pulse, alice_bit, alice_basis[, alice_intensity]`; Site B: `pulse, bob_basis, bob_bit`). Phases 2 and 3 keep it, so the same protocol code processes a hallway, a rooftop, and a satellite pass.
- **Classical channel.** [`qll/link/net_transport.py`](../../qll/link/net_transport.py) from Phase 1 on; the protocol's own Wegman–Carter tags sit on top.
- **Twin configuration.** A `LinkConfig` per setup, generated from measured parts (`two_room.write_preset`), versioned with the data.
