# T10 — Certified randomness and semi-device-independent devices

**The idea.** A Bell violation certifies that outcomes are unpredictable to *anyone*, even the device's maker (randomness expansion); semi-device-independent protocols certify randomness with fewer assumptions than a full physical model but without needing loophole-free Bell tests, e.g., by bounding the source's dimension or energy. This upgrades the owner's diode-noise QRNG from "passes NIST tests" to "provably random under stated assumptions."

**Equations.** Min-entropy bound from CHSH: $H_{\min}\ge1-\log_2\!\left(1+\sqrt{2-S^2/4}\right)$ bits per round; semi-DI bounds from an energy or dimension constraint, e.g., $H_{\min}\ge-\log_2 P_{\rm guess}(\omega)$ for a bounded-energy source.

**Status.** Loophole-free certified randomness demonstrated (Bierhorst et al. 2018, NIST); semi-DI protocols demonstrated with telecom components; commercial QRNGs remain non-certified.

**What it would change.** The basis choices in every Bell-test-based protocol on the link (E6, E10, T04) would carry a certificate; the FPGA board becomes a semi-DI device if its optical source can be energy-bounded.

**Key papers.** Pironio, S., et al. (2010). Random numbers certified by Bell's theorem. *Nature*, 464, 1021. https://doi.org/10.1038/nature09008 Bierhorst, P., et al. (2018). Experimentally generated randomness certified by the impossibility of superluminal signals. *Nature*, 556, 223. https://doi.org/10.1038/s41586-018-0019-0 Lunghi, T., et al. (2015). Self-testing quantum random number generator. *PRL*, 114, 150501. Rusca, D., et al. (2019). Self-testing quantum random-number generator based on an energy bound. *PRA*, 100, 062338. Herrero-Collantes & Garcia-Escartin (2017). *Rev. Mod. Phys.*, 89, 015004.

**Repo hook.** `qll/hardware/randomness.py` gains a `min_entropy_from_chsh(S)` and an energy-bounded semi-DI estimator; E6.
