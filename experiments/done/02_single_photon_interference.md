# Single-photon interference and anticorrelation (Grangier, Roger, Aspect 1986)

**Original.** A heralded single photon sent to a beam splitter never produces coincidences between the two output detectors (anticorrelation parameter $\alpha<1$), yet the same photon shows interference fringes in a Mach–Zehnder interferometer. Particle and wave in one apparatus.

**Physics.** $\alpha=\frac{P_{\rm coinc}}{P_1P_2}$; classical fields give $\alpha\ge1$, a single photon gives $\alpha\to0$. Fringe visibility $V=(I_{\max}-I_{\min})/(I_{\max}+I_{\min})$.

**Simple recreation.** The SPDC bench (`experiments/bench/hardware_guide.md` Tier 1): one photon of the pair heralds the other; three single-photon detectors and a coincidence counter measure $\alpha$; Mark Beck's Reed College course does exactly this with undergraduates. Cost dominated by detectors (~$3–4k each) or Hamamatsu modules.

**What went wrong historically.** Earlier "single-photon" sources were attenuated lasers, which are Poissonian and never show $\alpha<1$; the heralded cascade source was the key.

**Repo hook.** `qll/hardware/photon_source.py` (Phase 3): heralded $g^{(2)}(0)$ test.

- Grangier, P., Roger, G., & Aspect, A. (1986). Experimental evidence for a photon anticorrelation effect on a beam splitter. *Europhysics Letters*, 1, 173. https://doi.org/10.1209/0295-5075/1/4/004
- Thorn, J. J., et al. (2004). Observing the quantum behavior of light in an undergraduate laboratory. *Am. J. Phys.*, 72, 1210. https://doi.org/10.1119/1.1737397
