# 03 · Quantum communication

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

Figures: `docs/figures/link_loss_explorer.svg`, `light_time_explorer.svg`, `qkd_rate_explorer.svg`.
