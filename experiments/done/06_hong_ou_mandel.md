# Hong–Ou–Mandel interference (1987)

**Original.** Two identical photons entering a 50:50 beam splitter from opposite ports always leave together; the coincidence rate dips to zero as the arrival times are scanned through overlap. The dip width gave a sub-picosecond timing measurement.

**Physics.** Bosonic exchange: $\lvert1,1\rangle\to(\lvert2,0\rangle-\lvert0,2\rangle)/\sqrt2$; visibility equals the indistinguishability $\lvert\langle\phi_1\vert\phi_2\rangle\rvert^2$. Every linear-optics Bell-state measurement, hence every photonic teleportation and every heralded spin–spin entanglement, is a HOM interference.

**Simple recreation (Tier 1).** Same SPDC source; send both photons of a pair to one beam splitter with a translation stage on one arm; scan the delay in 10 µm steps and record coincidences. Visibility > 90% is achievable with 3 nm bandpass filters.

**What went wrong historically.** Spectral and spatial mode mismatch kills the dip; the experiment is the standard diagnostic of source indistinguishability precisely because it is so unforgiving.

**Repo hook.** `qll/hardware/beam_splitter.py`, `perceval_adapter.py` (Phase 3); `circuits/bell_measurement.py` visibility parameter.

- Hong, C. K., Ou, Z. Y., & Mandel, L. (1987). *Physical Review Letters*, 59, 2044. https://doi.org/10.1103/PhysRevLett.59.2044
