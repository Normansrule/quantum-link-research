# Verification Plan

Each requirement is verified by one of: **T** an analytic test in CI, **S** a simulation with a reference value, **B** a bench measurement, or **L** a literature value with a verified citation. Status mirrors `systems/traceability_matrix.csv`.

| Requirement | Method | Evidence | Status |
|---|---|---|---|
| REQ-PHY-001 latency floor d/c | T | `test_phase1_constants.py` | verified |
| REQ-PHY-002 two bits per qubit | T | `test_phase2_circuits.py` | verified |
| REQ-PHY-003 no cloning | T | `test_phase2_no_cloning.py` | verified |
| REQ-THM-001/002 thermal occupation, GAD CPTP | T | phase 1 and 2 noise tests | verified |
| REQ-THM-003 memory coherence vs T | B + L | E2 bench data; Jarmola 2012 | planned |
| REQ-CHN-001/002 fiber law, 1/L² | T | `test_phase1_channels.py` | verified |
| REQ-CHN-003 background prefactor | B | P04 / E4 | planned |
| REQ-CIR-001..003 F = 1, (2f+1)/3, 2√2 | T | `test_phase2_circuits.py` | verified |
| REQ-QKD-001 11 % threshold | T | `test_phase1_qkd_theory.py` | verified |
| REQ-QKD-002 rates ≤ PLOB | T | Phase 3 | planned |
| REQ-NET-001 chain beats direct | S | `repeater_rate_explorer`, Phase 4 | simulation |
| REQ-CAP-001 memory vs light time | S + L | S02, memory table | simulation |
| REQ-CAP-002 teleportation after delayed bits | S | `test_simulations.py::S02` | verified |
| REQ-APP-001 fail closed | T | Phase 6 | planned |
| REQ-SYS-001/002 traceability, import DAG | T | `test_phase1_systems.py`, `test_phase2_dag.py` | verified |
| REQ-F1-001 herald > 1 Hz, S > 2.2 over 1 km | B | F1 stage S3 | planned |
| REQ-F2-001 budget within ±3 dB of two missions | S + L | F2 stage S1 | planned |
| REQ-SEC-001 DI certification under latency | S | E10 | planned |
