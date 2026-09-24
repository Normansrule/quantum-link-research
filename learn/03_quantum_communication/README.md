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
| 10 | [Post-processing with code](10_post_processing_with_code.md) | sifting, Cascade vs LDPC at Mars latency, Toeplitz hashing, authentication | `qll/qkd/{sifting,error_correction,privacy_amplification}.py` |

Figures: `docs/figures/link_loss_explorer.svg`, `light_time_explorer.svg`, `qkd_rate_explorer.svg`.
