# 02 Research foundation: every experiment so far, and what each gives the mission

*Generated from `qll/systems/experiment_catalog.py` by `scripts/build_program_docs.py`.*

Nothing done so far is dropped. Each phase below lists the experiments it builds on: landmark experiments summarized with a cheap recreation, lab procedures, the two-site link's hardware ladder, proposals, and the three flagships. **Replicable** means four things exist: a step-by-step procedure, a digital twin in `qll/` that predicts the result, a test that checks the twin, and a data format the twin reads, so anyone can repeat the experiment and compare it with the prediction. The rule for this mission is that every physical experiment is replicable in that sense before it is built.

| Status | Count |
|---|---|
| replicable | 8 |
| procedure | 10 |
| landmark | 15 |
| proposed | 18 |
| flagship | 3 |

## Phase 0: Foundations: the simulation library and its evidence

| ID | Experiment | Status | Twin | Test | Cost | What it gives the mission |
|---|---|---|---|---|---|---|
| [D01](../../experiments/done/01_stern_gerlach.md) | Stern–Gerlach: spin is quantized | landmark | — | — | — | measurement disturbs: the root of why collapse cannot be steered into a message |
| [D04](../../experiments/done/04_odmr_nv.md) | ODMR of NV centers | landmark | [`nv_node.py`](../../qll/hardware/nv_node.py) | [`test_analysis_odmr.py`](../../tests/test_analysis_odmr.py) | $100-500 | a cheap spin qubit readout: the memory path, not the link path |
| [D05](../../experiments/done/05_rabi_ramsey_echo_nv.md) | Rabi, Ramsey, Hahn echo | landmark | [`rabi_ramsey.py`](../../qll/viz/rabi_ramsey.py) | [`test_phase1_viz.py`](../../tests/test_phase1_viz.py) | — | coherence times a quantum memory must exceed |
| [P01](../../experiments/protocols/P01_odmr_nv_bench.md) | ODMR on a $100–500 NV bench | replicable | [`odmr_fit.py`](../../qll/analysis/odmr_fit.py) | [`test_analysis_odmr.py`](../../tests/test_analysis_odmr.py) | $100-500 | first hands-on qubit; practice for the twin-versus-measurement method |
| [P02](../../experiments/protocols/P02_pulsed_nv_control.md) | Pulsed NV control | replicable | [`relaxation_fit.py`](../../qll/analysis/relaxation_fit.py) | [`test_analysis_relaxation.py`](../../tests/test_analysis_relaxation.py) | $~10k | memory coherence measured, not assumed |

## Phase 1: Two rooms: a fiber classical channel and a single-photon quantum link

| ID | Experiment | Status | Twin | Test | Cost | What it gives the mission |
|---|---|---|---|---|---|---|
| [D02](../../experiments/done/02_single_photon_interference.md) | Single-photon interference and anticorrelation | landmark | [`photon_source.py`](../../qll/hardware/photon_source.py) | [`test_phase3_links.py`](../../tests/test_phase3_links.py) | $3k-4k | proves a source is single-photon; the check the two-room link's weak pulses do not pass, hence decoys |
| [P07](../../experiments/protocols/P07_bb84_over_a_fiber_spool.md) | BB84 over a fiber spool | procedure | [`protocol_bb84.py`](../../qll/link/protocol_bb84.py) | [`test_two_site_link.py`](../../tests/test_two_site_link.py) | $100-2k | the fiber version of the two-room link |
| [P09](../../experiments/protocols/P09_mars_link_on_a_table.md) | The Mars link on a table | replicable | [`bench_twin.py`](../../qll/systems/bench_twin.py) | [`test_bench_twin.py`](../../tests/test_bench_twin.py) | $150-400 | the method this mission reuses: build, measure, and compare with a twin |
| [P10](../../experiments/protocols/P10_two_room_single_photon_link.md) | The two-room single-photon link | replicable | [`two_room.py`](../../qll/link/two_room.py) | [`test_two_room.py`](../../tests/test_two_room.py) | $530-1,180 | the mission's first quantum milestone: quantum states sent from one room to another |
| [P11](../../experiments/protocols/P11_collapse_code_on_a_cloud_processor.md) | The collapse code on a cloud processor | replicable | [`collapse_signalling.py`](../../qll/circuits/collapse_signalling.py) | [`test_collapse_signalling.py`](../../tests/test_collapse_signalling.py) | $0 | the first paper: can the way a shared state collapses carry a message? Measured, with a bound |
| [T1](../../systems/see510/10_real_world_experiments.md) | Tier 1: bright-light polarization analogue | replicable | [`bench_tier1.py`](../../qll/link/bench_tier1.py) | [`test_two_site_link.py`](../../tests/test_two_site_link.py) | $40-120 | the protocol on real hardware between the rooms before any single photons |
| [T2](../../systems/see510/10_real_world_experiments.md) | Tier 2: the fiber channel, characterized | procedure | [`models.py`](../../qll/link/models.py) | [`test_two_site_link.py`](../../tests/test_two_site_link.py) | $80-350 | loss and cross-talk of the fiber that carries the classical channel |
| [T3](../../systems/see510/10_real_world_experiments.md) | Tier 3: decoy-state BB84 at the single-photon level | procedure | [`decoy.py`](../../qll/link/decoy.py) | [`test_two_site_link.py`](../../tests/test_two_site_link.py) | $2k-8k | the laboratory-grade version of P10 |
| [E05](../../experiments/proposed/E05_fail_closed_messaging_20min_latency.md) | Fail-closed messaging under latency | proposed | [`messenger.py`](../../qll/app/messenger.py) | [`test_phase6_app.py`](../../tests/test_phase6_app.py) | — | the application the link serves |
| [E06](../../experiments/proposed/E06_qrng_basis_choice_on_a_cheap_bench.md) | Quantum-random bases on a cheap bench | proposed | [`randomness.py`](../../qll/hardware/randomness.py) | [`test_phase3_qkd.py`](../../tests/test_phase3_qkd.py) | — | the two-room link's basis choices |
| [E16](../../experiments/proposed/E16_zz_crosstalk_on_a_cloud_processor.md) | ZZ crosstalk on a cloud processor | proposed | [`zz_ramsey.py`](../../qll/circuits/zz_ramsey.py) | [`test_zz_ramsey.py`](../../tests/test_zz_ramsey.py) | $0 | the crosstalk that could fake a signal in P11; measure it on the same device |
| [E17](../../experiments/proposed/E17_can_collapse_carry_a_message.md) | Can collapse carry a message? | proposed | [`collapse_signalling.py`](../../qll/circuits/collapse_signalling.py) | [`test_collapse_signalling.py`](../../tests/test_collapse_signalling.py) | $0 | the mission's first paper |
| [F1](../../experiments/flagship/F1_earth_to_earth.md) | Two computers on Earth | flagship | — | — | — | — |

## Phase 2: Entanglement between two rooms

| ID | Experiment | Status | Twin | Test | Cost | What it gives the mission |
|---|---|---|---|---|---|---|
| [D02](../../experiments/done/02_single_photon_interference.md) | Single-photon interference and anticorrelation | landmark | [`photon_source.py`](../../qll/hardware/photon_source.py) | [`test_phase3_links.py`](../../tests/test_phase3_links.py) | $3k-4k | proves a source is single-photon; the check the two-room link's weak pulses do not pass, hence decoys |
| [D03](../../experiments/done/03_bell_test_spdc.md) | Bell test with entangled photons | landmark | [`chsh.py`](../../qll/circuits/chsh.py) | [`test_phase2_circuits.py`](../../tests/test_phase2_circuits.py) | — | the Phase 2 pass criterion: CHSH above 2 between the rooms |
| [D06](../../experiments/done/06_hong_ou_mandel.md) | Hong–Ou–Mandel interference | landmark | [`beam_splitter.py`](../../qll/hardware/beam_splitter.py) | [`test_phase3_links.py`](../../tests/test_phase3_links.py) | — | the Bell-state measurement that teleportation and repeaters need (Phase 4) |
| [D11](../../experiments/done/11_aspect_1982_time_varying_analyzers.md) | Aspect 1982: time-varying analyzers | landmark | [`chsh.py`](../../qll/circuits/chsh.py) | [`test_phase2_circuits.py`](../../tests/test_phase2_circuits.py) | $1k-3k | switch settings faster than light can cross: the no-signalling check at its strictest |
| [P03](../../experiments/protocols/P03_spdc_bell_test.md) | SPDC source, HOM, CHSH, and BB84 | procedure | [`chsh.py`](../../qll/circuits/chsh.py) | [`test_phase2_circuits.py`](../../tests/test_phase2_circuits.py) | $5k-15k | the entangled source Phase 2 borrows or builds |
| [P05](../../experiments/protocols/P05_single_photon_anticorrelation.md) | Single-photon anticorrelation | procedure | [`photon_source.py`](../../qll/hardware/photon_source.py) | [`test_phase3_links.py`](../../tests/test_phase3_links.py) | $300-3k | certify a heralded source before trusting it |
| [P06](../../experiments/protocols/P06_quantum_eraser.md) | Quantum eraser and delayed choice | procedure | [`collapse_signalling.py`](../../qll/circuits/collapse_signalling.py) | [`test_collapse_signalling.py`](../../tests/test_collapse_signalling.py) | $200-500 | the classic 'collapse at a distance' demonstration: fringes appear only after records are compared |
| [P07](../../experiments/protocols/P07_bb84_over_a_fiber_spool.md) | BB84 over a fiber spool | procedure | [`protocol_bb84.py`](../../qll/link/protocol_bb84.py) | [`test_two_site_link.py`](../../tests/test_two_site_link.py) | $100-2k | the fiber version of the two-room link |
| [T4](../../systems/see510/10_real_world_experiments.md) | Tier 4: entanglement-based BBM92 | procedure | [`e91.py`](../../qll/qkd/e91.py) | [`test_phase3_qkd.py`](../../tests/test_phase3_qkd.py) | $15k-60k or a lent kit | Phase 2: key from entangled pairs measured in two rooms |
| [E06](../../experiments/proposed/E06_qrng_basis_choice_on_a_cheap_bench.md) | Quantum-random bases on a cheap bench | proposed | [`randomness.py`](../../qll/hardware/randomness.py) | [`test_phase3_qkd.py`](../../tests/test_phase3_qkd.py) | — | the two-room link's basis choices |
| [E13](../../experiments/proposed/E13_frequency_multiplexed_heralding.md) | Frequency-multiplexed heralding | proposed | — | — | $300-1k | — |
| [E14](../../experiments/proposed/E14_relativistic_timing_sanity_test.md) | Relativistic timing with two GPS-disciplined nodes | proposed | [`relativity.py`](../../qll/space/relativity.py) | [`test_phase5_relativity_turbulence.py`](../../tests/test_phase5_relativity_turbulence.py) | $100-300 | shared clocks for timing detections in separate rooms and at a ground station |
| [F1](../../experiments/flagship/F1_earth_to_earth.md) | Two computers on Earth | flagship | — | — | — | — |

## Phase 3: Outdoors and toward orbit

| ID | Experiment | Status | Twin | Test | Cost | What it gives the mission |
|---|---|---|---|---|---|---|
| [D09](../../experiments/done/09_satellite_qkd_micius_jinan.md) | Satellite QKD: Micius and Jinan-1 | landmark | [`link_budget.py`](../../qll/channels/link_budget.py) | [`test_phase3_links.py`](../../tests/test_phase3_links.py) | — | the satellite link budget Phase 3 reproduces before building anything |
| [D14](../../experiments/done/14_jinan1_2025_microsatellite_qkd.md) | Jinan-1 2025: microsatellite QKD | landmark | [`decoy_state.py`](../../qll/qkd/decoy_state.py) | [`test_phase3_qkd.py`](../../tests/test_phase3_qkd.py) | — | a small satellite and a portable ground station: the scale Phase 3 aims at |
| [P04](../../experiments/protocols/P04_rooftop_free_space_link.md) | Rooftop free-space link | procedure | [`free_space_diffraction.py`](../../qll/channels/free_space_diffraction.py) | [`test_phase3_links.py`](../../tests/test_phase3_links.py) | — | Phase 3's first outdoor step: loss and daylight background |
| [P08](../../experiments/protocols/P08_time_bin_encoding.md) | Time-bin encoding and a fiber interferometer | procedure | — | — | $500-1k | the encoding that survives long fiber; Phase 3 option |
| [T5](../../systems/see510/10_real_world_experiments.md) | Tier 5: a commercial or testbed link | procedure | — | — | — | deployed fiber through a partner |
| [E03](../../experiments/proposed/E03_constellation_scheduling_on_real_pass_data.md) | Constellation scheduling on real pass data | proposed | [`relay_constellation.py`](../../qll/space/relay_constellation.py) | [`test_phase5_space.py`](../../tests/test_phase5_space.py) | $0 | satellite work with public data, before hardware |
| [E04](../../experiments/proposed/E04_sun_angle_background.md) | Daylight background at solar elongation | proposed | [`thermal_background.py`](../../qll/channels/thermal_background.py) | [`test_phase1_channels.py`](../../tests/test_phase1_channels.py) | — | — |
| [E14](../../experiments/proposed/E14_relativistic_timing_sanity_test.md) | Relativistic timing with two GPS-disciplined nodes | proposed | [`relativity.py`](../../qll/space/relativity.py) | [`test_phase5_relativity_turbulence.py`](../../tests/test_phase5_relativity_turbulence.py) | $100-300 | shared clocks for timing detections in separate rooms and at a ground station |
| [E15](../../experiments/proposed/E15_radiation_screening.md) | Radiation screening of bench parts | proposed | — | — | — | — |
| [F2](../../experiments/flagship/F2_earth_to_satellite.md) | A computer on Earth to a satellite | flagship | — | — | — | — |

## Phase 4: Entanglement-assisted communication: the frontier

| ID | Experiment | Status | Twin | Test | Cost | What it gives the mission |
|---|---|---|---|---|---|---|
| [D06](../../experiments/done/06_hong_ou_mandel.md) | Hong–Ou–Mandel interference | landmark | [`beam_splitter.py`](../../qll/hardware/beam_splitter.py) | [`test_phase3_links.py`](../../tests/test_phase3_links.py) | — | the Bell-state measurement that teleportation and repeaters need (Phase 4) |
| [D07](../../experiments/done/07_teleportation_photonic.md) | Photonic teleportation | landmark | [`teleportation.py`](../../qll/circuits/teleportation.py) | [`test_phase2_circuits.py`](../../tests/test_phase2_circuits.py) | — | two classical bits per qubit: the frontier's honest form |
| [D08](../../experiments/done/08_nv_remote_entanglement_and_network.md) | NV remote entanglement and networks | landmark | — | — | — | heralded entanglement between distant nodes: where the network goes after Phase 4 |
| [D10](../../experiments/done/10_error_correction_below_threshold.md) | Error correction below threshold | landmark | — | — | — | what long-lived memories for a network will rest on |
| [D12](../../experiments/done/12_furusawa_1998_cv_teleportation.md) | Furusawa 1998: continuous-variable teleportation | landmark | [`oscillator_states.py`](../../qll/circuits/oscillator_states.py) | [`test_computing_core.py`](../../tests/test_computing_core.py) | $50k-100k | the other encoding for teleportation |
| [D13](../../experiments/done/13_bhaskar_2020_memory_enhanced_communication.md) | Bhaskar 2020: memory-enhanced communication | landmark | [`repeater_chain.py`](../../qll/network/repeater_chain.py) | [`test_phase4_network.py`](../../tests/test_phase4_network.py) | — | a memory beating direct transmission: the repeater idea in one node |
| [D15](../../experiments/done/15_bluvstein_2024_logical_atom_processor.md) | Bluvstein 2024: logical atom processor | landmark | [`stabilizer_codes.py`](../../qll/circuits/stabilizer_codes.py) | [`test_computing_core.py`](../../tests/test_computing_core.py) | — | error-corrected memories without a cryostat |
| [P11](../../experiments/protocols/P11_collapse_code_on_a_cloud_processor.md) | The collapse code on a cloud processor | replicable | [`collapse_signalling.py`](../../qll/circuits/collapse_signalling.py) | [`test_collapse_signalling.py`](../../tests/test_collapse_signalling.py) | $0 | the first paper: can the way a shared state collapses carry a message? Measured, with a bound |
| [P12](../../experiments/protocols/P12_teleportation_and_superdense_coding_on_a_cloud_processor.md) | Teleportation and superdense coding on a cloud processor | replicable | [`teleport_cloud.py`](../../qll/circuits/teleport_cloud.py) | [`test_cloud_frontier.py`](../../tests/test_cloud_frontier.py) | $0 | what entanglement does deliver, each with the control that shows the classical channel is needed |
| [P13](../../experiments/protocols/P13_majorana_teleportation_on_a_cloud_processor.md) | Majorana parity teleportation on a cloud processor | replicable | [`majorana_cloud.py`](../../qll/circuits/majorana_cloud.py) | [`test_majorana_teleport.py`](../../tests/test_majorana_teleport.py) | $0 | the measurement-only teleportation of Crogman, Dang, and Erenso (2025), emulated: two parity bits teleport, one cannot |
| [E01](../../experiments/proposed/E01_delayed_classical_channel_teleportation.md) | Teleportation with a delayed classical channel | proposed | [`light_time_delay.py`](../../qll/channels/light_time_delay.py) | [`test_phase2_circuits.py`](../../tests/test_phase2_circuits.py) | — | teleportation waits for its bits; how long can it wait |
| [E02](../../experiments/proposed/E02_memory_vs_temperature_vs_light_time.md) | Memory coherence versus temperature and light time | proposed | [`thermal.py`](../../qll/circuits/noise/thermal.py) | [`test_phase2_noise.py`](../../tests/test_phase2_noise.py) | $500-10k | — |
| [E05](../../experiments/proposed/E05_fail_closed_messaging_20min_latency.md) | Fail-closed messaging under latency | proposed | [`messenger.py`](../../qll/app/messenger.py) | [`test_phase6_app.py`](../../tests/test_phase6_app.py) | — | the application the link serves |
| [E07](../../experiments/proposed/E07_transduction_free_hybrid_link.md) | Transduction-free hybrid link | proposed | [`transduction.py`](../../qll/hardware/transduction.py) | [`test_simulations.py`](../../tests/test_simulations.py) | — | — |
| [E08](../../experiments/proposed/E08_modality_trade_study_mars_memory_node.md) | Modality trade for a Mars memory node | proposed | — | — | — | — |
| [E09](../../experiments/proposed/E09_multiplexing_at_au_scale_loss.md) | Multiplexing at AU-scale loss | proposed | — | — | — | — |
| [E10](../../experiments/proposed/E10_device_independent_certification_under_latency.md) | Device-independent certification under latency | proposed | — | — | — | — |
| [E11](../../experiments/proposed/E11_blind_computation_under_latency.md) | Blind computation under latency | proposed | — | — | — | — |
| [E12](../../experiments/proposed/E12_erasure_aware_atom_repeater.md) | Erasure-aware atom repeater | proposed | — | — | — | — |
| [E17](../../experiments/proposed/E17_can_collapse_carry_a_message.md) | Can collapse carry a message? | proposed | [`collapse_signalling.py`](../../qll/circuits/collapse_signalling.py) | [`test_collapse_signalling.py`](../../tests/test_collapse_signalling.py) | $0 | the mission's first paper |
| [E18](../../experiments/proposed/E18_majorana_parity_teleportation_emulated.md) | Majorana parity teleportation, emulated: one bit or two? | proposed | [`majorana_teleport.py`](../../qll/circuits/majorana_teleport.py) | [`test_majorana_teleport.py`](../../tests/test_majorana_teleport.py) | $0 | a concrete collaboration with the CSUDH authors: their protocol, emulated and set against their error budget |
| [F3](../../experiments/flagship/F3_earth_to_mars.md) | Earth to Mars | flagship | — | — | — | — |

## How to replicate any entry

1. Read the file in the ID column; procedures list parts, steps, and expected numbers.
2. Run its twin's test (`python -m pytest <test file>`) to see the prediction checked against closed forms.
3. Build or borrow the setup, log data in the twin's format (for the link: `qll/link/hardware_log.py`, one file per site), and run the same analysis.
4. Compare measurement and prediction; record both, with the configuration and seed, as the evidence.
5. Follow [`experiments/lessons/04_reproducibility_checklist.md`](../../experiments/lessons/04_reproducibility_checklist.md).
