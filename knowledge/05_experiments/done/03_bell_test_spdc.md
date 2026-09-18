# Bell test with entangled photons (Aspect 1982; undergraduate version Dehlinger & Mitchell 2002)

**Original.** Aspect, Dalibard, and Roger used a calcium cascade source and acousto-optic switches changing the analyzer settings during the photons' flight; $S=2.697\pm0.015$. Loophole-free versions came in 2015 (Hensen NV; Giustina and Shalm with photons).

**Physics.** CHSH $S\le2$ locally, $2\sqrt2$ quantum; angles $0,45°,22.5°,67.5°$ for polarization (half of the spin angles because polarization is spin-1).

**Simple recreation (Tier 1, one semester).** 405 nm pump → two crossed type-I BBO crystals → 810 nm pairs; half-wave plates and polarizers on each arm; two single-photon detectors; coincidence window ~10 ns. Expect $S\approx2.3$–$2.7$; the quED kit reports 2.7 out of the box. Full parts list and links in `docs/hardware_and_experiments_guide.md` §2.3 and §5. Add the owner's QRNG board to choose settings and you have a freedom-of-choice demonstration nobody has published on a $5k bench (proposal E6).

**What went wrong historically.** The detection loophole (low efficiency, fair-sampling assumption) stood for 33 years; closing it needed > 83% system efficiency (photons) or deterministic readout (spins).

**Repo hook.** `qll/circuits/chsh.py` with the Werner-state formula $S=2\sqrt2(4f-1)/3$; the measured $S$ gives an estimate of the source's singlet fraction.

- Aspect, A., Dalibard, J., & Roger, G. (1982). *Physical Review Letters*, 49, 1804. https://doi.org/10.1103/PhysRevLett.49.1804
- Dehlinger, D., & Mitchell, M. W. (2002). *Am. J. Phys.*, 70, 903 https://doi.org/10.1119/1.1498860 and 70, 898.
- Giustina, M., et al. (2015). Significant-loophole-free test of Bell's theorem with entangled photons. *Physical Review Letters*, 115, 250401. Shalm, L. K., et al. (2015). *Physical Review Letters*, 115, 250402.
