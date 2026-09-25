# P05 — Single-Photon Anticorrelation (Grangier)

**What it shows.** A heralded photon at a beam splitter goes one way or the other, never both: the anticorrelation parameter $\alpha=\frac{N_{GTR}N_G}{N_{GT}N_{GR}}<1$ violates the classical bound $\alpha\ge1$ [grangier1986] [thorn2004]. This is the undergraduate experiment that separates a photon from a classical pulse, and the first thing the P03 source should demonstrate after coincidences appear.

**Uses.** The P03 SPDC source, three detectors (gate G on the idler; T and R on the two outputs of a 50:50 splitter in the signal arm), the coincidence electronics (FPGA or time-tagger), 2 ns windows.

**Procedure.** (1) With the splitter removed, maximize G–signal coincidences. (2) Insert the splitter; record $N_G$, $N_{GT}$, $N_{GR}$, $N_{GTR}$ over 10 minutes. (3) Compute $\alpha$ and its statistical error; expect $\alpha\sim0.01$–0.1 with a good source, $\alpha\to1$ if the coincidence window is opened to microseconds (accidentals). (4) Repeat with the pump attenuated to show $\alpha$ falling further.

**Analyze.** `alpha = N_GTR * N_G / (N_GT * N_GR)`; the Poisson error follows from the four counts. Report $\alpha$, the window, and the accidental rate $N_GN_T\tau$.

**Cost.** One extra detector and splitter over P03 (~$300–3 000 depending on detector class); one afternoon.

**Verifies.** The single-photon nature that every herald in `qll` assumes (photon_source.SpdcSource heralded g₂). Landmark: `experiments/done/02`.

**References.** Grangier, P., Roger, G., & Aspect, A. (1986). *Europhysics Letters*, 1, 173. Thorn, J. J., et al. (2004). *American Journal of Physics*, 72, 1210. https://doi.org/10.1119/1.1737397
