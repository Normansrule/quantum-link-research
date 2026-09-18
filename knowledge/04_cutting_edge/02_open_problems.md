# Open problems, ranked by relevance to an Earth–Mars quantum link

1. **Memory lifetime versus efficiency.** Rare-earth memories hold coherence for hours but store and retrieve photons with low efficiency at long times; single spins are efficient but last minutes. No platform has both hour-scale storage and high efficiency. (`REQ-CAP-001`, proposal E1, E2.)
2. **Entanglement rate at AU-scale loss.** Even 10 m apertures give $\eta\sim10^{-9}$; rates of pairs per hour need multiplexing in time, frequency, and space by factors of $10^3$–$10^6$, or relays with memories at intermediate points (which do not exist between Earth and Mars). (Proposal E3.)
3. **Transduction with entanglement preservation.** Efficiency and added noise are not yet good enough to connect microwave processors to optical links. (Proposal E7 sidesteps it.)
4. **Daylight and sun-angle background.** Near conjunction the receiver looks close to the Sun; the background model needs data, not assumption. (Proposal E4.)
5. **Pointing at interplanetary range.** DSOC demonstrated classical pointing at 30 million km; single-photon-level links need the same pointing with far less signal for the tracking loop.
6. **Cryogenics in space.** 4 K closed-cycle coolers fly; 100 mK and 10 mK do not, in a form usable for a memory payload with an optical window. (Risk R-2.)
7. **Classical-latency-aware protocols.** Cascade, purification, and swapping schedulers assume millisecond round trips; redesigning them for 20-minute round trips is largely unstudied. (Proposal E5.)
8. **Certification.** How does Mars verify that the key or state it received is what Earth sent, when a Bell test itself needs classical communication of settings? Device-independent protocols over planetary latency are unexplored.
9. **Standardization and security proofs for hybrid PQC + QKD key hierarchies** under intermittent, high-latency links.
10. **Honest metrics.** Which single number should a Mars-link roadmap report: pairs per day, secret bits per pass, or end-to-end message latency at a target fidelity?
