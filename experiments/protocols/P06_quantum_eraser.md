# P06 — Quantum Eraser and Delayed Choice

**What it shows.** Which-path information destroys interference; erasing it restores it, and the choice can be made after the signal photon is detected [kim2000] [gogo2005]. On the P03 bench: the signal photon passes a polarization interferometer (two paths tagged H and V); its interference appears only when the idler is projected onto a diagonal basis that erases the tag.

**Uses.** P03 source with polarization-entangled pairs, a displaced Sagnac or Mach–Zehnder with a polarizer per path, half-wave plates, two detectors, coincidence electronics.

**Procedure.** (1) Align the interferometer with the tags removed; record fringes vs phase. (2) Tag the paths (H in one arm, V in the other); fringes vanish in singles and in coincidences with an idler measured in H/V. (3) Measure the idler at ±45°: fringes return in coincidence, with opposite phase for the two outcomes (they sum to no fringes, so no signaling). (4) Move the idler analyzer farther than the signal detector so the choice is "delayed"; nothing changes.

**Analyze.** Visibility $V=(N_{\max}-N_{\min})/(N_{\max}+N_{\min})$ per case; the anti-phased fringe pair is the no-signaling check that the repository's `ClassicalMessage` guard formalizes (INV-1).

**Cost.** Waveplates and polarizers over P03 (~$200–500); two afternoons.

**Verifies.** The no-communication theorem in the laboratory: the idler choice changes nothing in the signal statistics until coincidences are sorted, which needs the classical record.

**References.** Kim, Y.-H., Yu, R., Kulik, S. P., Shih, Y., & Scully, M. O. (2000). Delayed "choice" quantum eraser. *Physical Review Letters*, 84, 1. https://doi.org/10.1103/PhysRevLett.84.1 Gogo, A., Snyder, W. D., & Beck, M. (2005). Comparing quantum and classical correlations in a quantum eraser. *Physical Review A*, 71, 052103. https://doi.org/10.1103/PhysRevA.71.052103
