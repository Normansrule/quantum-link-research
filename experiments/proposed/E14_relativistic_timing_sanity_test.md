# E14 — A relativistic timing sanity test with two GPS-disciplined nodes

**Gap.** `qll/space/relativity.py` predicts Doppler, redshift, and Shapiro terms for Mars; the timing chain that would have to correct them has never been exercised on the bench.

**Question.** Can two GPS-disciplined oscillators and a fibre link maintain a coincidence window of 1 ns over a day, and does a deliberately introduced frequency offset (emulating the Earth–Mars redshift of 3.5 × 10⁻⁹, i.e. 0.3 ms/day) show up and get corrected by the timing model?

**Cheap version (bench).** Two GPSDOs (~$100–300 each), a time-tagger or the timestamping FPGA, the P03 source split over a fibre spool; log the coincidence peak position over 24 h with and without a synthetic offset applied in software.

**Research version.** Entanglement-based time transfer (T13) between two buildings; Sagnac correction for an east–west link.

**Verifies.** The timing assumption behind every coincidence window in the repository; T13's cheap version.

**References.** Ashby, N. (2003). *Living Reviews in Relativity*, 6, 1. https://doi.org/10.12942/lrr-2003-1 Ho, C., Lamas-Linares, A., & Kurtsiefer, C. (2009). *New Journal of Physics*, 11, 045011. https://doi.org/10.1088/1367-2630/11/4/045011
