# E2 — Memory coherence versus temperature versus required storage time

**Gap.** Coherence times are published per platform at one temperature each. No single normalized plot exists of $T_2(T)$ against the storage time required for each baseline (LEO 2 ms, GEO 0.24 s, Moon 2.6 s, Mars 6–45 min round trip).

**Cheapest version (Tier 0–1, ~$500–$10k).** NV ensemble $T_1$ and $T_2$ (Hahn echo) at 77 K (liquid-nitrogen dewar, a Styrofoam cup is enough), 200 K, 300 K, 350 K; fit to `thermal_t1()` in `qll/circuits/noise/thermal.py`; note that the NV $T_1$ at room temperature is phonon-limited (~ms) rather than bath-occupation-limited, which the fit will reveal as a model failure, and that is the point.

**Research version.** Extend the same plot with literature values for Eu:YSO, SiV, ions, and atoms, each at its operating temperature, and overlay the spacecraft cooler capabilities (4 K closed-cycle: flown; 100 mK: not flown for optical payloads).

**Verifies.** REQ-THM-003; risks R-1 and R-2 get numbers instead of adjectives.

**Deliverable.** A figure that belongs in the thesis and in `qll/viz/`: storage time (log) vs temperature (log) with the baselines as horizontal lines and the flown-cooler limit as a vertical line.

**Key references.** Krantz, P., et al. (2019). *Appl. Phys. Rev.*, 6, 021318. Jarmola, A., et al. (2012). Temperature- and magnetic-field-dependent longitudinal spin relaxation in nitrogen-vacancy ensembles in diamond. *Physical Review Letters*, 108, 197601. Bradley, C. E., et al. (2019). *Physical Review X*, 9, 031045.
