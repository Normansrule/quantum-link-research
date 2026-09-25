# Theories

| # | Idea | Maturity | If it works, the Mars architecture… |
|---|---|---|---|
| [T01](T01_quantum_internet_stack.md) | A layered quantum-network stack (link layer, network layer, transport) | protocols demonstrated on NV nodes (2019–2022) | gets a protocol design instead of ad hoc scheduling |
| [T02](T02_all_photonic_repeaters.md) | All-photonic repeaters: no memories, photonic cluster states | theory 2015; small demos | needs no cryogenic memory in space, at the cost of enormous photon counts |
| [T03](T03_gkp_and_bosonic_repeaters.md) | GKP / bosonic-code repeaters and CV error correction | theory 2018–2021; GKP states in microwave and optics | corrects loss directly on the photon |
| [T04](T04_device_independent_qkd.md) | Device-independent and semi-DI QKD | first demos 2022 | Mars never has to trust its own hardware |
| [T05](T05_quantum_clock_networks_and_relativity.md) | Networks of entangled clocks; relativistic and gravitational effects on entanglement | proposals 2014; DSQL 2022–2025 | timing and reference frames become physics, not assumptions; tests fundamental physics for free |
| [T06](T06_quantum_limited_optical_receivers.md) | Holevo-capacity receivers (Dolinar, superadditive) for classical deep-space links | theory 1970s; demos 2010s | the *classical* two bits arrive with fewer photons; DSN throughput |
| [T07](T07_blind_and_delegated_quantum_computing.md) | Blind / delegated quantum computing over a network | demos 2012–2017 | a Mars crew can run computations on Earth hardware without revealing inputs |
| [T08](T08_entanglement_routing_and_qos.md) | Entanglement routing, multiplexing, and quality of service | simulation-level | relay constellations get a routing theory |
| [T09](T09_cv_qkd_and_satellite_cv.md) | Continuous-variable QKD with coherent states and homodyne detection | terrestrial deployment; satellite proposals | uses DSOC-class coherent-light terminals instead of single-photon detectors |
| [T10](T10_certified_randomness_and_semi_di_devices.md) | Certified and semi-device-independent randomness | commercial QRNGs; DI demos 2018 | the QRNG board's output becomes provably random, not just tested |

Every file: **The idea · Equations · Status (with years) · What it would change · Key papers · Repo hook**.
| T11 | [Communication complexity and fingerprinting](T11_communication_complexity_and_fingerprinting.md) | one-round equality checks with fewer transmitted photons than classical bits | 3 |
| T12 | [Position verification](T12_position_verification.md) | physical authentication of the Mars node by light-time constraints | 2 |
| T13 | [Quantum-secured time transfer](T13_quantum_secured_time_transfer.md) | tamper-evident clock synchronization riding on the entanglement channel | 4 |
| T14 | [Error-corrected memories in space](T14_error_corrected_memories_in_space.md) | logical memories as the long-term alternative to rare-earth crystals | 2 |
| T15 | [ML decoders and remote calibration](T15_machine_learning_decoders_and_remote_calibration.md) | autonomy at the node as the answer to 20-minute command loops | 3 |
