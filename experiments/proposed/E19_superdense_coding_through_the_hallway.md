# E19 — Superdense coding through the hallway: more than one bit per photon

**Gap.** Every message in Phase 1 rides on the classical channel; the photons only carry key. Superdense coding reverses that: the photon crossing the hallway *is* the message, and because its partner was shared in advance it carries more than the one bit any single qubit can carry on its own [holevo1973] [bennett1992]. Mattle et al. (1996) reached 1.13 bits per photon on one optical table with linear optics [mattle1996]; no open, twin-matched version runs between two rooms on a borrowed teaching kit.

**Physics.**
- **Encoding.** The pair is shared as $|\Phi^+\rangle$, one photon to Alice and one to Bob through fiber. Alice applies $I$, $X$, $Z$, or $XZ$ with waveplates and sends her photon across the hallway.
- **Decoding.** Bob overlaps the two photons on a 50/50 beamsplitter and resolves polarization at both outputs. Linear optics identifies three classes: $\Psi^-$, $\Psi^+$, and the two $\Phi$ states together. With three messages, the ideal is $\log_2 3 = 1.585$ bits per photon.
- **Imperfections.** Pair visibility $V$ mixes the Bell states. Two-photon interference visibility $V_{HOM}$ [hong1987] confuses $\Psi^+$ with $\Psi^-$.
- **The model.** [`qll/circuits/superdense_photonic.py`](../../qll/circuits/superdense_photonic.py) computes the confusion matrix and the information per detected pair. Above 1 bit needs, for example, $V = 0.94$ and $V_{HOM} = 0.9$, which gives 1.16 bits.
- **Caveat.** Detection is post-selected, so the comparison with one bit assumes fair sampling: losses that do not depend on the message.

**Cheapest version.**
- **Runs on.** The Phase 2 rig (milestone M2.6): a borrowed entangled-photon source, the fiber to room B, Alice's two waveplates on a motorized or hand-turned mount, and Bob's beamsplitter with four detectors from the same kit.
- **Added cost.** About $200–1,500, mostly mounts and a fiber delay line to match the photons' arrival times.
- **Warm-up.** Run it first on a free cloud processor ([P12](../protocols/P12_teleportation_and_superdense_coding_on_a_cloud_processor.md)), where the Bell measurement is complete and the ideal is 2 bits.

**Research version.**
- **Hyperentanglement.** Pairs entangled in two degrees of freedom allow a complete Bell measurement with linear optics, so all four messages fit.
- **Distance.** Repeat the experiment through fiber spools and out of the building, measuring bits per photon against loss.

**Failure modes to expect.**
- **Arrival mismatch.** The photons must arrive within their coherence time; scan the delay for the HOM dip first.
- **Polarization drift.** Drift in Bob's fiber rotates the Bell basis; correct it with paddles, using the P14 certificate.
- **Accidental coincidences.** Accidentals lower the effective visibility; keep the coincidence window short.

**Repo hook.**
- **Model:** [`qll/circuits/superdense_photonic.py`](../../qll/circuits/superdense_photonic.py).
- **Cloud warm-up:** [`qll/circuits/superdense_cloud.py`](../../qll/circuits/superdense_cloud.py).
- **Tests:** [`tests/test_quantum_channels.py`](../../tests/test_quantum_channels.py).
- **Mission:** milestone M2.6 and requirement MR-2.6, with the framework in [`systems/program/09_quantum_channels.md`](../../systems/program/09_quantum_channels.md).

**References.**
- Mattle, K., Weinfurter, H., Kwiat, P. G., & Zeilinger, A. (1996). Dense coding in experimental quantum communication. *Physical Review Letters, 76*, 4656–4659. https://doi.org/10.1103/PhysRevLett.76.4656
- Bennett, C. H., & Wiesner, S. J. (1992). Communication via one- and two-particle operators on Einstein-Podolsky-Rosen states. *Physical Review Letters, 69*, 2881–2884. https://doi.org/10.1103/PhysRevLett.69.2881
- Hong, C. K., Ou, Z. Y., & Mandel, L. (1987). Measurement of subpicosecond time intervals between two photons by interference. *Physical Review Letters, 59*, 2044–2046. https://doi.org/10.1103/PhysRevLett.59.2044
