# Status

Version 0.39.0 · 659 tests · 32/33 requirements verified · 403 references (21 verified) · 92 learn files · 8 simulations · 44 figures

| Requirement | Statement | Phase | Status |
|---|---|---|---|
| REQ-PHY-001 | Classical information latency is never below d/c | 1 | verified |
| REQ-PHY-002 | Teleportation consumes exactly 2 classical bits per qubit | 2 | verified |
| REQ-PHY-003 | No public function returns two copies of an unknown input state | 2 | verified |
| REQ-THM-001 | Thermal occupation obeys Bose-Einstein limits at T=0 and high T | 1 | verified |
| REQ-THM-002 | Generalized amplitude damping is trace preserving | 1 | verified |
| REQ-THM-003 | Memory coherence time is modeled as a function of temperature | 4 | planned (bench E2; the memory table carries operating temperature) |
| REQ-CHN-001 | Fiber transmittance follows 10^(-alpha L/10) | 1 | verified |
| REQ-CHN-002 | Free-space geometric loss follows the exact Gaussian-over-aperture law with 1/L^2 far-field limit | 3 | verified |
| REQ-CIR-001 | Ideal teleportation fidelity equals 1 | 2 | verified |
| REQ-CIR-002 | Noisy teleportation fidelity is compared with the 2/3 classical limit | 2 | verified |
| REQ-CIR-003 | Ideal CHSH value equals 2*sqrt(2) | 2 | verified |
| REQ-QKD-001 | BB84 secret-key rate reaches zero at QBER 11% | 1 | verified |
| REQ-QKD-002 | All repeaterless QKD rates are bounded by the PLOB capacity | 3 | verified |
| REQ-NET-001 | A repeater chain beats direct transmission beyond a crossover distance that depends on memory time | 4 | verified |
| REQ-CAP-001 | Each demonstrated memory is compared against the classical round trip of each baseline (metro to Mars max) | 4 | verified |
| REQ-APP-001 | The messenger refuses to send when the QKD key buffer is empty (never downgrades) and cannot deliver before d/c | 6 | verified |
| REQ-SYS-001 | No traceability row points at a non-existent test | 1 | verified |
| REQ-CAP-002 | Teleportation completes after a light-time-delayed classical channel (bench analogue: simulation S02) | 2 | verified |
| REQ-SYS-002 | No module imports upward in the physical stack (constants→channels→circuits→qkd→network→space→app) | 2 | verified |
| REQ-F2-001 | Link-budget model reproduces the Micius two-downlink loss (64-82 dB) within 3 dB; Jinan-1 within 3 dB once exact figures are verified | 3 | verified (Micius); Jinan-1 pending |
| REQ-SPC-001 | Earth-Mars range envelope from the ephemeris matches the constants within 1 % and the light-time bounds 3.0-3.2 and 22.0-22.6 min | 5 | verified |
| REQ-SPC-002 | Solar-conjunction blackouts recur once per synodic period with 2-3 week duration at SEP < 3 deg and an L4/L5 relay keeps availability above 99.9 % | 5 | verified |
| REQ-SPC-003 | Memory operating temperature and heat load are checked against flown cooler classes | 5 | verified |
| REQ-APP-002 | Hybrid ML-KEM + QKD session keys agree on both ends and depend on both inputs | 6 | verified |
| REQ-SEC-001 | The link can certify its own key device-independently with settings and outcomes exchanged no faster than d/c; the finite-key rate is positive once enough rounds accumulate per round trip | 6 | verified (model) |
| REQ-NET-002 | Repeater results are credited only for pairs above the classical teleportation limit (F > 2/3): the chain model reports delivered fidelity and the minimum memory time for a useful chain that beats direct transmission | 4 | verified |
| REQ-NET-003 | Closed-form repeater waiting times agree with exact sampling of the protocol within 10 % for up to 8 segments | 4 | verified |
| REQ-CAP-003 | The baseline F3 design delivers at least 1e5 useful pairs per day (F > 2/3) on every day of a synodic period outside solar conjunction | 5 | verified |
| REQ-CAP-004 | Architecture trade: a pair crosses one astronomical distance in the baseline; a dual-downlink relay is at least 1e6 times slower with the same hardware | 5 | verified |
| REQ-HW-001 | The processor node's simulated CZ gate reaches coherent average fidelity of at least 0.999 with leakage at most 1e-3 | 2 | verified |
| REQ-HW-002 | Static ZZ at the tunable coupler's idle point is below the conditional-Ramsey resolution of 1.5 kHz, and the experiment recovers the model's ZZ elsewhere within 3 % | 2 | verified |
| REQ-QEC-001 | A matching-decoded surface code shows threshold behaviour: larger codes fail less below 5 % and more above 13 % bit-flip probability, crossing between 8.5 % and 10.5 % | 2 | verified |
| REQ-WEB-001 | Every number the website and README show is computed by the tested code, and every JavaScript port agrees with its Python model | 6 | verified |
