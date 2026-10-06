"""Every experiment in the repository, in one place, with what it takes to replicate it and which phase of the
mission (systems/program/) it feeds. The catalog is data: scripts/build_program_docs.py turns it into
systems/program/02_research_foundation.md, and tests/test_program_plan.py checks that every experiment file in the
repository is listed, that every path exists, and that every "replicable" entry names its procedure, its twin, and
its test, so nothing done so far can drop out of the plan.

Status vocabulary
-----------------
landmark      a published experiment the field rests on, summarized with a cheap recreation (experiments/done/)
procedure     a step-by-step lab protocol with a simulation that predicts it (experiments/protocols/)
replicable    a procedure, a digital twin in qll/, a test, and a data format: anyone can repeat it and compare
proposed      a gap nobody has measured, with a cheapest version and a research version (experiments/proposed/)
flagship      one of the three end-to-end goals the repository serves (experiments/flagship/)
"""
from __future__ import annotations

from dataclasses import dataclass

PHASES = {
    0: "Foundations: the simulation library and its evidence",
    1: "Two rooms: a fiber classical channel and a single-photon quantum link",
    2: "Entanglement between two rooms",
    3: "Outdoors and toward orbit",
    4: "Entanglement-assisted communication: the frontier",
}


@dataclass(frozen=True)
class Experiment:
    id: str
    title: str
    path: str
    status: str
    phases: tuple[int, ...]
    twin: str = ""                 # the qll module that predicts it
    test: str = ""                 # the test file that checks the twin
    procedure: str = ""            # the protocol to follow (for replicable entries)
    cost: str = ""                 # as stated in the file, US dollars, planning
    role: str = ""                 # what it contributes to the mission


D, P, E, F = "experiments/done/", "experiments/protocols/", "experiments/proposed/", "experiments/flagship/"
CATALOG: tuple[Experiment, ...] = (
    # ---------------------------------------------------------------- landmarks: what the field already showed
    Experiment("D01", "Stern–Gerlach: spin is quantized", D + "01_stern_gerlach.md", "landmark", (0,),
               role="measurement disturbs: the root of why collapse cannot be steered into a message"),
    Experiment("D02", "Single-photon interference and anticorrelation", D + "02_single_photon_interference.md", "landmark", (1, 2),
               twin="qll/hardware/photon_source.py", test="tests/test_phase3_links.py", cost="3k-4k",
               role="proves a source is single-photon; the check the two-room link's weak pulses do not pass, hence decoys"),
    Experiment("D03", "Bell test with entangled photons", D + "03_bell_test_spdc.md", "landmark", (2,),
               twin="qll/circuits/chsh.py", test="tests/test_phase2_circuits.py",
               role="the Phase 2 pass criterion: CHSH above 2 between the rooms"),
    Experiment("D04", "ODMR of NV centers", D + "04_odmr_nv.md", "landmark", (0,), twin="qll/hardware/nv_node.py",
               test="tests/test_analysis_odmr.py", cost="100-500", role="a cheap spin qubit readout: the memory path, not the link path"),
    Experiment("D05", "Rabi, Ramsey, Hahn echo", D + "05_rabi_ramsey_echo_nv.md", "landmark", (0,),
               twin="qll/viz/rabi_ramsey.py", test="tests/test_phase1_viz.py", role="coherence times a quantum memory must exceed"),
    Experiment("D06", "Hong–Ou–Mandel interference", D + "06_hong_ou_mandel.md", "landmark", (2, 4),
               twin="qll/hardware/beam_splitter.py", test="tests/test_phase3_links.py",
               role="the Bell-state measurement that teleportation and repeaters need (Phase 4)"),
    Experiment("D07", "Photonic teleportation", D + "07_teleportation_photonic.md", "landmark", (4,),
               twin="qll/circuits/teleportation.py", test="tests/test_phase2_circuits.py",
               role="two classical bits per qubit: the frontier's honest form"),
    Experiment("D08", "NV remote entanglement and networks", D + "08_nv_remote_entanglement_and_network.md", "landmark", (4,),
               role="heralded entanglement between distant nodes: where the network goes after Phase 4"),
    Experiment("D09", "Satellite QKD: Micius and Jinan-1", D + "09_satellite_qkd_micius_jinan.md", "landmark", (3,),
               twin="qll/channels/link_budget.py", test="tests/test_phase3_links.py",
               role="the satellite link budget Phase 3 reproduces before building anything"),
    Experiment("D10", "Error correction below threshold", D + "10_error_correction_below_threshold.md", "landmark", (4,),
               role="what long-lived memories for a network will rest on"),
    Experiment("D11", "Aspect 1982: time-varying analyzers", D + "11_aspect_1982_time_varying_analyzers.md", "landmark", (2,),
               twin="qll/circuits/chsh.py", test="tests/test_phase2_circuits.py", cost="1k-3k",
               role="switch settings faster than light can cross: the no-signalling check at its strictest"),
    Experiment("D12", "Furusawa 1998: continuous-variable teleportation", D + "12_furusawa_1998_cv_teleportation.md", "landmark", (4,),
               twin="qll/circuits/oscillator_states.py", test="tests/test_computing_core.py", cost="50k-100k",
               role="the other encoding for teleportation"),
    Experiment("D13", "Bhaskar 2020: memory-enhanced communication", D + "13_bhaskar_2020_memory_enhanced_communication.md", "landmark", (4,),
               twin="qll/network/repeater_chain.py", test="tests/test_phase4_network.py",
               role="a memory beating direct transmission: the repeater idea in one node"),
    Experiment("D14", "Jinan-1 2025: microsatellite QKD", D + "14_jinan1_2025_microsatellite_qkd.md", "landmark", (3,),
               twin="qll/qkd/decoy_state.py", test="tests/test_phase3_qkd.py",
               role="a small satellite and a portable ground station: the scale Phase 3 aims at"),
    Experiment("D15", "Bluvstein 2024: logical atom processor", D + "15_bluvstein_2024_logical_atom_processor.md", "landmark", (4,),
               twin="qll/circuits/stabilizer_codes.py", test="tests/test_computing_core.py",
               role="error-corrected memories without a cryostat"),
    # ---------------------------------------------------------------- lab procedures already written
    Experiment("P01", "ODMR on a $100–500 NV bench", P + "P01_odmr_nv_bench.md", "replicable", (0,),
               twin="qll/analysis/odmr_fit.py", test="tests/test_analysis_odmr.py", procedure=P + "P01_odmr_nv_bench.md",
               cost="100-500", role="first hands-on qubit; practice for the twin-versus-measurement method"),
    Experiment("P02", "Pulsed NV control", P + "P02_pulsed_nv_control.md", "replicable", (0,),
               twin="qll/analysis/relaxation_fit.py", test="tests/test_analysis_relaxation.py", procedure=P + "P02_pulsed_nv_control.md",
               cost="~10k", role="memory coherence measured, not assumed"),
    Experiment("P03", "SPDC source, HOM, CHSH, and BB84", P + "P03_spdc_bell_test.md", "procedure", (2,),
               twin="qll/circuits/chsh.py", test="tests/test_phase2_circuits.py", procedure=P + "P03_spdc_bell_test.md",
               cost="5k-15k", role="the entangled source Phase 2 borrows or builds"),
    Experiment("P04", "Rooftop free-space link", P + "P04_rooftop_free_space_link.md", "procedure", (3,),
               twin="qll/channels/free_space_diffraction.py", test="tests/test_phase3_links.py", procedure=P + "P04_rooftop_free_space_link.md",
               role="Phase 3's first outdoor step: loss and daylight background"),
    Experiment("P05", "Single-photon anticorrelation", P + "P05_single_photon_anticorrelation.md", "procedure", (2,),
               twin="qll/hardware/photon_source.py", test="tests/test_phase3_links.py", procedure=P + "P05_single_photon_anticorrelation.md",
               cost="300-3k", role="certify a heralded source before trusting it"),
    Experiment("P06", "Quantum eraser and delayed choice", P + "P06_quantum_eraser.md", "procedure", (2,),
               twin="qll/circuits/collapse_signalling.py", test="tests/test_collapse_signalling.py", procedure=P + "P06_quantum_eraser.md",
               cost="200-500", role="the classic 'collapse at a distance' demonstration: fringes appear only after records are compared"),
    Experiment("P07", "BB84 over a fiber spool", P + "P07_bb84_over_a_fiber_spool.md", "procedure", (1, 2),
               twin="qll/link/protocol_bb84.py", test="tests/test_two_site_link.py", procedure=P + "P07_bb84_over_a_fiber_spool.md",
               cost="100-2k", role="the fiber version of the two-room link"),
    Experiment("P08", "Time-bin encoding and a fiber interferometer", P + "P08_time_bin_encoding.md", "procedure", (3,),
               procedure=P + "P08_time_bin_encoding.md", cost="500-1k",
               role="the encoding that survives long fiber; Phase 3 option"),
    Experiment("P09", "The Mars link on a table", P + "P09_mars_link_on_a_table.md", "replicable", (1,),
               twin="qll/systems/bench_twin.py", test="tests/test_bench_twin.py", procedure=P + "P09_mars_link_on_a_table.md",
               cost="150-400", role="the method this mission reuses: build, measure, and compare with a twin"),
    Experiment("P10", "The two-room single-photon link", P + "P10_two_room_single_photon_link.md", "replicable", (1,),
               twin="qll/link/two_room.py", test="tests/test_two_room.py", procedure=P + "P10_two_room_single_photon_link.md",
               cost="530-1,180", role="the mission's first quantum milestone: quantum states sent from one room to another"),
    Experiment("P11", "The collapse code on a cloud processor", P + "P11_collapse_code_on_a_cloud_processor.md", "replicable", (1, 4),
               twin="qll/circuits/collapse_signalling.py", test="tests/test_collapse_signalling.py",
               procedure=P + "P11_collapse_code_on_a_cloud_processor.md", cost="0",
               role="the first paper: can the way a shared state collapses carry a message? Measured, with a bound"),
    Experiment("P12", "Teleportation and superdense coding on a cloud processor", P + "P12_teleportation_and_superdense_coding_on_a_cloud_processor.md",
               "replicable", (4,), twin="qll/circuits/teleport_cloud.py", test="tests/test_cloud_frontier.py",
               procedure=P + "P12_teleportation_and_superdense_coding_on_a_cloud_processor.md", cost="0",
               role="what entanglement does deliver, each with the control that shows the classical channel is needed"),
    # ---------------------------------------------------------------- the two-site link's hardware ladder
    Experiment("T1", "Tier 1: bright-light polarization analogue", "systems/see510/10_real_world_experiments.md", "replicable", (1,),
               twin="qll/link/bench_tier1.py", test="tests/test_two_site_link.py", procedure="systems/see510/10_real_world_experiments.md",
               cost="40-120", role="the protocol on real hardware between the rooms before any single photons"),
    Experiment("T2", "Tier 2: the fiber channel, characterized", "systems/see510/10_real_world_experiments.md", "procedure", (1,),
               twin="qll/link/models.py", test="tests/test_two_site_link.py", procedure="systems/see510/10_real_world_experiments.md",
               cost="80-350", role="loss and cross-talk of the fiber that carries the classical channel"),
    Experiment("T3", "Tier 3: decoy-state BB84 at the single-photon level", "systems/see510/10_real_world_experiments.md", "procedure", (1,),
               twin="qll/link/decoy.py", test="tests/test_two_site_link.py", procedure="systems/see510/10_real_world_experiments.md",
               cost="2k-8k", role="the laboratory-grade version of P10"),
    Experiment("T4", "Tier 4: entanglement-based BBM92", "systems/see510/10_real_world_experiments.md", "procedure", (2,),
               twin="qll/qkd/e91.py", test="tests/test_phase3_qkd.py", procedure="systems/see510/10_real_world_experiments.md",
               cost="15k-60k or a lent kit", role="Phase 2: key from entangled pairs measured in two rooms"),
    Experiment("T5", "Tier 5: a commercial or testbed link", "systems/see510/10_real_world_experiments.md", "procedure", (3,),
               procedure="systems/see510/10_real_world_experiments.md", role="deployed fiber through a partner"),
    # ---------------------------------------------------------------- proposals already written
    Experiment("E01", "Teleportation with a delayed classical channel", E + "E01_delayed_classical_channel_teleportation.md", "proposed", (4,),
               twin="qll/channels/light_time_delay.py", test="tests/test_phase2_circuits.py", role="teleportation waits for its bits; how long can it wait"),
    Experiment("E02", "Memory coherence versus temperature and light time", E + "E02_memory_vs_temperature_vs_light_time.md", "proposed", (4,),
               twin="qll/circuits/noise/thermal.py", test="tests/test_phase2_noise.py", cost="500-10k"),
    Experiment("E03", "Constellation scheduling on real pass data", E + "E03_constellation_scheduling_on_real_pass_data.md", "proposed", (3,),
               twin="qll/space/relay_constellation.py", test="tests/test_phase5_space.py", cost="0", role="satellite work with public data, before hardware"),
    Experiment("E04", "Daylight background at solar elongation", E + "E04_sun_angle_background.md", "proposed", (3,),
               twin="qll/channels/thermal_background.py", test="tests/test_phase1_channels.py"),
    Experiment("E05", "Fail-closed messaging under latency", E + "E05_fail_closed_messaging_20min_latency.md", "proposed", (1, 4),
               twin="qll/app/messenger.py", test="tests/test_phase6_app.py", role="the application the link serves"),
    Experiment("E06", "Quantum-random bases on a cheap bench", E + "E06_qrng_basis_choice_on_a_cheap_bench.md", "proposed", (1, 2),
               twin="qll/hardware/randomness.py", test="tests/test_phase3_qkd.py", role="the two-room link's basis choices"),
    Experiment("E07", "Transduction-free hybrid link", E + "E07_transduction_free_hybrid_link.md", "proposed", (4,),
               twin="qll/hardware/transduction.py", test="tests/test_simulations.py"),
    Experiment("E08", "Modality trade for a Mars memory node", E + "E08_modality_trade_study_mars_memory_node.md", "proposed", (4,)),
    Experiment("E09", "Multiplexing at AU-scale loss", E + "E09_multiplexing_at_au_scale_loss.md", "proposed", (4,)),
    Experiment("E10", "Device-independent certification under latency", E + "E10_device_independent_certification_under_latency.md", "proposed", (4,)),
    Experiment("E11", "Blind computation under latency", E + "E11_blind_computation_under_latency.md", "proposed", (4,)),
    Experiment("E12", "Erasure-aware atom repeater", E + "E12_erasure_aware_atom_repeater.md", "proposed", (4,)),
    Experiment("E13", "Frequency-multiplexed heralding", E + "E13_frequency_multiplexed_heralding.md", "proposed", (2,), cost="300-1k"),
    Experiment("E14", "Relativistic timing with two GPS-disciplined nodes", E + "E14_relativistic_timing_sanity_test.md", "proposed", (2, 3),
               twin="qll/space/relativity.py", test="tests/test_phase5_relativity_turbulence.py", cost="100-300",
               role="shared clocks for timing detections in separate rooms and at a ground station"),
    Experiment("E15", "Radiation screening of bench parts", E + "E15_radiation_screening.md", "proposed", (3,)),
    Experiment("E16", "ZZ crosstalk on a cloud processor", E + "E16_zz_crosstalk_on_a_cloud_processor.md", "proposed", (1,),
               twin="qll/circuits/zz_ramsey.py", test="tests/test_zz_ramsey.py", cost="0",
               role="the crosstalk that could fake a signal in P11; measure it on the same device"),
    Experiment("E17", "Can collapse carry a message?", E + "E17_can_collapse_carry_a_message.md", "proposed", (1, 4),
               twin="qll/circuits/collapse_signalling.py", test="tests/test_collapse_signalling.py", cost="0",
               role="the mission's first paper"),
    # ---------------------------------------------------------------- flagships
    Experiment("F1", "Two computers on Earth", F + "F1_earth_to_earth.md", "flagship", (1, 2)),
    Experiment("F2", "A computer on Earth to a satellite", F + "F2_earth_to_satellite.md", "flagship", (3,)),
    Experiment("F3", "Earth to Mars", F + "F3_earth_to_mars.md", "flagship", (4,)),
)


def by_id(eid: str) -> Experiment:
    for e in CATALOG:
        if e.id == eid:
            return e
    raise KeyError(eid)


def for_phase(phase: int) -> list[Experiment]:
    return [e for e in CATALOG if phase in e.phases]
