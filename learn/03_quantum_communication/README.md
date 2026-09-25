# Quantum Communication

| # | File | One line | Repo module |
|---|---|---|---|
| 01 | [QKD protocols](01_qkd_protocols.md) | BB84 → decoy → MDI → twin-field → DI | `qll/qkd/` |
| 02 | [Teleportation and swapping](02_teleportation_and_swapping.md) | one pair + two bits; no-signaling | `qll/circuits/teleportation.py` |
| 03 | [Repeaters and memories](03_repeaters_and_memories.md) | three generations; memory table with lifetimes *and* efficiencies | `qll/network/` |
| 04 | [Satellite and deep space](04_satellite_and_deep_space.md) | link budgets, Micius, Jinan-1, DSQL | `qll/channels/`, `qll/space/` |
| 05 | [Transduction](05_transduction.md) | microwave ↔ optical; why we design around it | — |
| 06 | [Micius link budget line by line](06_micius_link_budget_line_by_line.md) | the F2 must-pass target | `qll/channels/link_budget.py` |
| 07 | [Clock synchronization](07_clock_synchronization_for_quantum_networks.md) | ns timing from campus to Mars; relativity | `qll/space/ephemeris.py` |
| 08 | [Deep-space optical communication](08_deep_space_optical_communication_dsoc.md) | the classical half of F3 (DSOC, PPM, Holevo) | `qll/space/classical_link.py` |
| 09 | [Security proofs 101](09_security_proofs_101.md) | uncertainty relation → min-entropy → key length, as the code does it | `qll/qkd/{key_rate,privacy_amplification,e91}.py` |
| 11 | [Purification and repeater generations](11_purification_and_repeater_generations.md) | the BBPSSW map, its cost at Mars, why gen-2/3 exist | `qll/network/{purification,repeater_chain}.py` |
| 12 | [Turbulence and adaptive optics](12_turbulence_and_adaptive_optics.md) | why downlinks; r₀, Rytov, aperture averaging | `qll/channels/atmosphere.py` |
| 13 | [Relativistic effects on the link](13_relativistic_effects_on_the_link.md) | redshift, Doppler, Shapiro; the timing budget | `qll/space/relativity.py` |
| 14 | [Side channels and countermeasures](14_side_channels_and_countermeasures.md) | eight published attacks and the two structural answers | `qll/qkd/{decoy_state,mdi,e91}.py` |
| 15 | [Standards and roadmaps](15_standards_and_roadmaps.md) | ETSI, ITU, IETF, NIST, ISO, EuroQCI, DSQL, CCSDS | `qll/app/` |
| 16 | [AFC memories and rare-earth crystals](16_afc_memories_and_rare_earth_crystals.md) | efficiency laws, ZEFOZ, multiplexing, why < 5 % at hours | `qll/network/afc_memory.py` |
| 17 | [Continuous-variable QKD](17_cv_qkd_derivation.md) | GG02 rate, the excess-noise threshold, why it suits daylight | `qll/qkd/cv_qkd.py` |
| 10 | [Post-processing with code](10_post_processing_with_code.md) | sifting, Cascade vs LDPC at Mars latency, Toeplitz hashing, authentication | `qll/qkd/{sifting,error_correction,privacy_amplification}.py` |

Figures: `docs/figures/link_loss_explorer.svg`, `light_time_explorer.svg`, `qkd_rate_explorer.svg`.
