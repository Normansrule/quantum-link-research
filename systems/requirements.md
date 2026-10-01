# Requirements

*Generated from `traceability_matrix.csv` by `scripts/build_systems_docs.py`; edit the matrix, not this file.*

37 requirements, 36 verified. A requirement is verified only when its test exists, the named test function exists in it (checked by `python -m qll.systems.traceability`), and the test passes in CI. Verification methods follow the classic set: **Test** (the implementation is exercised), **Analysis** (a tested model is evaluated against the requirement), **Demonstration** (a simulation shows the behaviour end to end), and **Inspection** (the code or documents are checked mechanically).

Prefixes: PHY physics invariants · THM thermal · CHN channel · CIR circuit · QKD key distribution · NET network · CAP capability · APP application · SYS systems · SPC space segment · SEC security · F1 flagship F1 · F2 flagship F2 · HW hardware node · QEC error correction · WEB website and README.

## N-1: Confidential Earth–Mars messaging whose security does not rest on computational assumptions alone

| ID | Requirement | Phase | Method | Verified by | Status |
|---|---|---|---|---|---|
| REQ-QKD-001 | BB84 secret-key rate reaches zero at QBER 11% | 1 | Analysis | [`tests/test_phase1_qkd_theory.py`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase1_qkd_theory.py) | verified |
| REQ-QKD-002 | All repeaterless QKD rates are bounded by the PLOB capacity | 3 | Analysis | [`test_all_repeaterless_rates_below_plob`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase3_qkd.py) | verified |
| REQ-APP-001 | The messenger refuses to send when the QKD key buffer is empty (never downgrades) and cannot deliver before d/c | 6 | Test | [`test_messenger_fails_closed_and_respects_light_time`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase6_app.py) | verified |
| REQ-APP-002 | Hybrid ML-KEM + QKD session keys agree on both ends and depend on both inputs | 6 | Test | [`test_hybrid_kem_both_sides_agree_and_depend_on_both_inputs`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase6_app.py) | verified |
| REQ-SEC-001 | The link can certify its own key device-independently with settings and outcomes exchanged no faster than d/c; the finite-key rate is positive once enough rounds accumulate per round trip | 6 | Analysis | [`test_s06_finite_key_di_limits_and_sealing`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_simulations.py) | verified (model) |
| REQ-CAP-003 | The baseline F3 design (source in space) delivers at least 1e5 useful pairs per day (F > 2/3) on every day of a synodic period outside solar conjunction | 5 | Analysis | [`test_baseline_meets_req_cap_003_every_available_day`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_mars_budget.py) | verified |
| REQ-CAP-005 | Background light: with the Mars receiver's off-axis rejection floor at 1e-9 at least 95 % of heralds are signal on every day with a link; a ground transmitter is shown to fail REQ-CAP-003 | 5 | Analysis | [`test_req_cap_005_stray_light_keeps_heralds_clean_every_available_day`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_mars_budget.py) | verified |
| REQ-APP-003 | A key bank sized by the sequent-peak rule carries the messenger's demand of 1e6 key bits per day through every day of a synodic period including conjunction; 1 % less capacity refuses | 6 | Analysis | [`test_req_app_003_a_bank_carries_the_messenger_through_every_conjunction`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_key_bank.py) | verified |

## N-2: A quantitative account of what temperature, loss, and light time do to every link in the chain

| ID | Requirement | Phase | Method | Verified by | Status |
|---|---|---|---|---|---|
| REQ-PHY-001 | Classical information latency is never below d/c | 1 | Test | [`tests/test_phase1_constants.py`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase1_constants.py) | verified |
| REQ-PHY-002 | Teleportation consumes exactly 2 classical bits per qubit | 2 | Test | [`test_teleportation_costs_two_bits_and_one_pair_and_respects_light_time`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase2_circuits.py) | verified |
| REQ-PHY-003 | No public function returns two copies of an unknown input state | 2 | Test | [`tests/test_phase2_no_cloning.py`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase2_no_cloning.py) | verified |
| REQ-THM-001 | Thermal occupation obeys Bose-Einstein limits at T=0 and high T | 1 | Analysis | [`tests/test_phase1_thermal.py`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase1_thermal.py) | verified |
| REQ-THM-002 | Generalized amplitude damping is trace preserving | 1 | Analysis | [`tests/test_phase2_noise.py`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase2_noise.py) | verified |
| REQ-THM-003 | Memory coherence time is modeled as a function of temperature | 4 | Test (bench) | — | planned (bench E2; the memory table carries operating temperature) |
| REQ-CHN-001 | Fiber transmittance follows 10^(-alpha L/10) | 1 | Analysis | [`tests/test_phase1_channels.py`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase1_channels.py) | verified |
| REQ-CHN-002 | Free-space geometric loss follows the exact Gaussian-over-aperture law with 1/L^2 far-field limit | 3 | Analysis | [`test_exact_gaussian_reduces_to_far_field_and_near_field_limits`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase3_links.py) | verified |
| REQ-CIR-001 | Ideal teleportation fidelity equals 1 | 2 | Analysis | [`test_teleportation_ideal_fidelity_is_one`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase2_circuits.py) | verified |
| REQ-CIR-002 | Noisy teleportation fidelity is compared with the 2/3 classical limit | 2 | Analysis | [`test_teleportation_werner_fidelity_matches_2f_plus_1_over_3`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase2_circuits.py) | verified |
| REQ-CIR-003 | Ideal CHSH value equals 2*sqrt(2) | 2 | Analysis | [`test_chsh_ideal_and_werner`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase2_circuits.py) | verified |
| REQ-NET-001 | A repeater chain beats direct transmission beyond a crossover distance that depends on memory time | 4 | Analysis | [`test_repeater_chain_crossover_exists_and_depends_on_memory`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase4_network.py) | verified |
| REQ-SPC-001 | Earth-Mars range envelope from the ephemeris matches the constants within 1 % and the light-time bounds 3.0-3.2 and 22.0-22.6 min | 5 | Analysis | [`test_range_envelope_matches_constants`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase5_space.py) | verified |
| REQ-SPC-002 | Solar-conjunction blackouts recur once per synodic period with 2-3 week duration at SEP < 3 deg and an L4/L5 relay keeps availability above 99.9 % | 5 | Analysis | [`test_relays_raise_availability_and_l4_geometry`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase5_space.py) | verified |
| REQ-SPC-003 | Memory operating temperature and heat load are checked against flown cooler classes | 5 | Analysis | [`test_platform_thermal_table`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase5_space.py) | verified |
| REQ-CAP-004 | Architecture trade: a pair crosses one astronomical distance in the baseline; a dual-downlink relay is at least 1e6 times slower with the same hardware | 5 | Analysis | [`test_dual_downlink_pays_diffraction_twice`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_mars_budget.py) | verified |
| REQ-HW-001 | The processor node's simulated CZ gate reaches coherent average fidelity of at least 0.999 with leakage at most 1e-3 | 2 | Analysis | [`test_calibrated_default_is_a_cz_with_negligible_leakage`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_cz_gate.py) | verified |
| REQ-HW-002 | Static ZZ at the tunable coupler's idle point is below the conditional-Ramsey resolution of 1.5 kHz, and the experiment recovers the model's ZZ elsewhere within 3 % | 2 | Analysis | [`test_recovers_the_coupler_model_zz_and_the_idle_point`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_zz_ramsey.py) | verified |
| REQ-QEC-001 | A matching-decoded surface code shows threshold behaviour: larger codes fail less below 5 % and more above 13 % bit-flip probability, crossing between 8.5 % and 10.5 % | 2 | Analysis | [`test_threshold_crossing`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_surface_code_capacity.py) | verified |

## N-3: An honest separation of what is achievable today from what is open research

| ID | Requirement | Phase | Method | Verified by | Status |
|---|---|---|---|---|---|
| REQ-CAP-001 | Each demonstrated memory is compared against the classical round trip of each baseline (metro to Mars max) | 4 | Analysis | [`test_capability_matrix_req_cap_001`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase4_network.py) | verified |
| REQ-CAP-002 | Teleportation completes after a light-time-delayed classical channel (bench analogue: simulation S02) | 2 | Demonstration | [`tests/test_simulations.py`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_simulations.py) | verified |
| REQ-F2-001 | Link-budget model reproduces the Micius two-downlink loss (64-82 dB) within 3 dB; Jinan-1 within 3 dB once exact figures are verified | 3 | Analysis | [`test_micius_two_downlink_loss_within_3db_of_reported`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase3_links.py) | verified (Micius); Jinan-1 pending |
| REQ-NET-002 | Repeater results are credited only for pairs above the classical teleportation limit (F > 2/3): the chain model reports delivered fidelity and the minimum memory time for a useful chain that beats direct transmission | 4 | Analysis | [`test_minimum_memory_for_a_useful_chain_grows_steeply_with_distance`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_purified_chain.py) | verified |
| REQ-CHN-003 | The background model is validated on a bench (P09): radiance conservation, single-mode etendue lambda^2, off-axis rejection, background-limited purity, and the error-rate identity, each predicted by the twin and recovered by the analysis from data | 3 | Test (bench) | [`test_report_recovers_a_synthetic_bench`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_bench_twin.py) | verified (model and analysis); hardware pending (P09) |

## N-4: Reproducible, citable models suitable for a master's thesis and for teaching

| ID | Requirement | Phase | Method | Verified by | Status |
|---|---|---|---|---|---|
| REQ-SYS-001 | No traceability row points at a non-existent test | 1 | Inspection | [`tests/test_phase1_systems.py`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase1_systems.py) | verified |
| REQ-SYS-002 | No module imports upward in the physical stack (constants→channels→circuits→qkd→network→space→app) | 2 | Inspection | [`tests/test_phase2_dag.py`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_phase2_dag.py) | verified |
| REQ-NET-003 | Closed-form repeater waiting times agree with exact sampling of the protocol within 10 % for up to 8 segments | 4 | Analysis | [`test_closed_form_is_conservative_when_nested`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_repeater_montecarlo.py) | verified |
| REQ-WEB-001 | Every number the website and README show is computed by the tested code, and every JavaScript port agrees with its Python model | 6 | Test | [`tests/test_site.py`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_site.py) | verified |
| REQ-F1-002 | The two-site laboratory link (SEE 510 case study, systems/see510) is simulated end to end: its statistics match closed-form detection and error-rate models, it rejects intercept-resend above the threshold and any tampered classical message, Cascade leaves matching keys, and only accepted key reaches the external application | 3 | Analysis | [`test_every_validation_check_passes`](https://github.com/Normansrule/quantum-link-research/blob/main/tests/test_two_site_link.py) | verified (simulation); hardware pending (P07) |

