# T06 — Quantum-limited receivers for the *classical* deep-space link

**The idea.** The two teleportation bits and every herald cross the Earth–Mars gap classically, over an optical link starved of photons (DSOC received ~10 photons per bit at 30 million km). The Holevo bound says a receiver that measures coherent-state codewords *jointly* can beat any receiver that detects symbol by symbol; the Dolinar receiver hits the two-state Helstrom limit, and superadditive joint-detection receivers approach Holevo. Fewer photons per bit means the classical half of the link closes with smaller telescopes or faster rates.

**Equations.** Photon-information efficiency (bits per photon) at low photon number: Holevo capacity $C\approx\bar n\log_2(1/\bar n)$ vs on–off keying with direct detection $\approx\bar n\log_2(1/\bar n)$ minus a gap that grows at low $\bar n$; Helstrom error for two coherent states $P_e=\frac12\left(1-\sqrt{1-e^{-4\lvert\alpha\rvert^2}}\right)$, roughly a 3 dB (later ~6 dB) advantage over homodyne/direct detection at low $\lvert\alpha\rvert^2$.

**Status.** Dolinar receivers demonstrated (2007–2013); superadditive receivers demonstrated at small scale; DSOC (2023–2024) used photon-counting with serially concatenated PPM codes at up to 267 Mb/s from 31 million km.

**What it would change.** The classical channel is on the critical path of every quantum protocol in this repo (heralds, corrections, reconciliation); a 3–6 dB receiver gain is worth a doubling of aperture area. Belongs in the Phase 5 link budget as a "classical channel" row.

**Key papers.** Helstrom, C. W. (1976). *Quantum Detection and Estimation Theory*. Academic Press. Dolinar, S. J. (1973). An optimum receiver for the binary coherent state quantum channel. MIT RLE Quarterly Progress Report 111. Guha, S. (2011). Structured optical receivers to attain superadditive capacity and the Holevo limit. *PRL*, 106, 240502. https://doi.org/10.1103/PhysRevLett.106.240502 Cook, R. L., Martin, P. J., & Geremia, J. M. (2007). Optical coherent state discrimination using a closed-loop quantum measurement. *Nature*, 446, 774. Biswas, A., et al. (2024). Deep Space Optical Communications (DSOC) technology demonstration. *Proc. SPIE* / NASA JPL reports. **TODO: verify citation.**

**Repo hook.** Phase 5 `qll/space/classical_link.py` (new): photons per bit vs range for DSOC-class terminals; feeds `light_time_delay` with a *bandwidth*, not only a delay.
