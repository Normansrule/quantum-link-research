# E4 — Daylight background at Mars-like solar elongation

**Gap.** Daylight QKD has been shown at 1550 nm on Earth with the receiver pointed well away from the Sun. Near conjunction the Earth–Mars line of sight passes within a few degrees of the Sun; the scattered-plus-thermal background there has not been measured for single-photon receivers.

**Cheapest version (Tier 1 rooftop).** Point the receiver at controlled angles 3°, 5°, 10°, 20° from the Sun (never at it; use a baffle and an attenuator on the alignment path), record counts vs filter bandwidth (3, 1, 0.3 nm) and field of view; fit to `background_count_rate()` and fix the "TODO: verify prefactor" in `qll/channels/thermal_background.py` with data.

**Verifies.** The channel-noise model; gives REQ-CHN-003 ("background prefactor validated on hardware").

**Failure modes.** Detector saturation and afterpulsing at high background; stray-light paths in the receiver; forgetting that Mars' own albedo adds to the background on the Earth-receiving side.

**Key references.** Avesani, M., et al. (2021). Full daylight quantum-key-distribution at 1550 nm enabled by integrated silicon photonics. *npj Quantum Inf.*, 7, 93. Liao, S.-K., et al. (2017). Long-distance free-space quantum key distribution in daylight towards inter-satellite communication. *Nature Photonics*, 11, 509. Mandel, L., & Wolf, E. (1995). *Optical Coherence and Quantum Optics*.
