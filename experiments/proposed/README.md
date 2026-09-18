# Proposed experiments

Each proposal answers the same five questions: the gap in the literature, the cheapest version a student lab can run, the research version, the physics it would settle, and the requirement in `systems/traceability_matrix.csv` it would verify. E1–E7 are the link-level proposals first written in `experiments/bench/hardware_guide.md` §6; E8–E10 come from the modality survey in `learn/02_qubit_modalities/`. Together they form the experimental program of the thesis: start on a $500 bench, end with a mission-relevant number.

| ID | Title | Cheapest version | Verifies |
|---|---|---|---|
| E1 | Teleportation with a classical channel delayed to a planetary light-time | SPDC bench, herald delayed in software | REQ-CAP-001, REQ-PHY-002 |
| E2 | Memory coherence vs temperature vs required storage time | NV ensemble $T_1,T_2$ from 77 K to 350 K | REQ-THM-003, R-1, R-2 |
| E3 | Relay-constellation scheduling validated on Jinan-1 pass data | software (SeQUeNCe) | REQ-NET-001 |
| E4 | Daylight background at Mars-like sun angle | rooftop link, sun-angle sweep | thermal_background prefactor |
| E5 | Fail-closed messaging under 20-minute latency | software on the messenger | REQ-APP-001 |
| E6 | QRNG-selected measurement bases on a sub-$500 NV bench | EntropyLoop / owner's board | REQ-QKD-001 in hardware |
| E7 | Transduction-free hybrid link (photons transport, rare-earth memory stores) | simulation | trade study memory-vs-T |
| E8 | Modality trade study for a Mars memory node, with data | literature + `memory_decoherence.py` | REQ-CAP-001 |
| E9 | Herald-rate multiplexing at AU-scale loss | simulation, then SPDC bench with time-bin multiplexing | REQ-NET-001 |
| E10 | Device-independent certification under planetary latency | software (Stim CHSH sampling with delayed settings) | new REQ-SEC-001 |
