# Standards and Roadmaps

What a systems engineer must cite when a quantum link leaves the laboratory. Version numbers change; verify each before citing in a document (all entries marked TODO in `docs/references.md` until checked).

| Body | Document | What it fixes | Status to verify |
|---|---|---|---|
| ETSI ISG-QKD | GS QKD 014 (key delivery API), GS QKD 016 (protection profile), GS QKD 004 (application interface) | how keys are handed to applications; security certification of QKD modules | TODO |
| ITU-T SG13 / SG17 | Y.3800 series (QKD networks), X.1710 series (security) | network architecture, key management, security requirements | TODO |
| IETF QIRG | Architectural principles for a quantum internet (RFC 9340) | terminology and architecture for entanglement-based networks | RFC 9340 published 2023 (confident) |
| NIST | FIPS 203/204/205 (ML-KEM, ML-DSA, SLH-DSA) | the post-quantum algorithms a hybrid link pairs with QKD | FIPS 203 (confident) [nist2024fips203] |
| NIST | SP 800-90B | entropy-source validation (the QRNG board's yardstick) | confident |
| ISO/IEC | 23837-1/-2 | security requirements and test methods for QKD modules | TODO |
| EU | EuroQCI | a continental QKD infrastructure with a space segment (Eagle-1) | TODO: mission status |
| NASA / JPL | Deep Space Quantum Link (DSQL) concept | the only published Earth–Moon–Mars quantum link concept [mohageg2022] | concept study |
| CCSDS | Optical communications standards (e.g. 141.0-B) | the classical optical link the quantum link rides beside | TODO |

## How the repository maps onto them
`qll/app/hybrid_kem.py` implements the FIPS 203 half of a hybrid; `qll/hardware/randomness.py` carries SP 800-90B-style health checks; the messenger's key-delivery interface would be the ETSI 014 API in a deployment; the network layer's terminology follows RFC 9340.

## Key sources
- Wehner, S., Elkouss, D., & Hanson, R. (2018). Quantum internet: a vision for the road ahead. *Science*, 362, eaam9288. https://doi.org/10.1126/science.aam9288
- Kozlowski, W., Wehner, S., et al. (2023). Architectural principles for a quantum internet. RFC 9340. https://doi.org/10.17487/RFC9340
- NIST (2024). FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard. https://doi.org/10.6028/NIST.FIPS.203
- Mohageg, M., et al. (2022). The deep space quantum link. *EPJ Quantum Technology*, 9, 25. https://doi.org/10.1140/epjqt/s40507-022-00143-0
