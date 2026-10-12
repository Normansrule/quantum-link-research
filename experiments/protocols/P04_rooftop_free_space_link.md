# P04 — Campus free-space link: loss versus distance and daylight background

## Safety
> This is a planning document, not a laser-safety authorization. Use a qualified review of the actual source, pulse behavior, accessible emissions, and alignment configuration before operating it, and record the approval in the [evaluation specification](../specs/two_room_evaluation_spec.md). Nominal attenuation is not a substitute for measurement or fault assessment.

Never point the alignment laser at people, windows, aircraft, or vehicles; use a red alignment laser < 1 mW for visual alignment. The 810 nm pair photons carry the data and are invisible; the pair-source pump laser that makes them is far brighter and must stay enclosed and terminated inside the source, and the accessible emission of the whole assembly must be assessed, not assumed safe. Check campus and aviation rules for any outdoor beam.

## Parts
The P03 source · 50 mm achromatic lenses or 2× beam expanders at both ends · a receiver telescope (50–100 mm) with a 3 nm 810 nm filter and a field stop · fiber coupling to a detector · a GPS-disciplined 1 pps clock or a shared cable for coincidence timing · tripods and a sunshade baffle.

## Measure
1. Set up at 20 m, 100 m, 300 m (roof to roof); at each distance record singles and coincidences with the pump on and off (background).
2. Record background vs filter bandwidth (10 nm, 3 nm) and field of view (field stop 1, 2, 4 mm) at noon and at night.
3. For proposal E4, record background at controlled angles 3°, 5°, 10°, 20° from the Sun using the baffle (never at the Sun).

## Analyze
Fit transmittance vs distance to `qll.channels.free_space_diffraction.geometric_transmittance` with the measured waist; fit background to `qll.channels.thermal_background.background_count_rate` and fix its prefactor; compute the background-induced QBER $Q_{\rm bg}\approx N\tau/(2(R\eta+N\tau))$ and the resulting BB84 key rate.

## Expected numbers
Geometric loss small at 300 m with 50 mm optics (the beam is still narrower than the receiver), so the measured loss will be dominated by coupling and pointing; that is itself the lesson. Daylight background of $10^3$–$10^5$ counts/s with a 3 nm filter and 1 mrad field of view.

## Digital twin with the Phase 1 hardware (milestones M3.2 and M3.3)
[`qll/link/outdoor_link.py`](../../qll/link/outdoor_link.py) carries the P10 source and receiver onto the roofs. The path loss is the product of beam spreading, pointing jitter, air extinction, and receiver coupling (Bourgoin et al., 2013). Skylight reaching the detectors is $N = L_\lambda A \Omega \Delta\lambda/(hc/\lambda)$ times the receiver efficiency, and it adds to each gate's dark clicks. With a 10 mm sending waist, a 50 mm receiving lens, 10 µrad of jitter, a 3 nm filter, and a 1 mrad field of view, the twin predicts:

| Sky (W m⁻² sr⁻¹ nm⁻¹) | Receiver | 300 m | 1 km | 2 km |
|---|---|---|---|---|
| City night (10⁻⁶) | silicon photomultipliers (P10) | 5.4 % error, no key | 9.7 %, no key | 15 %, no key |
| City night (10⁻⁶) | used avalanche-diode modules | 1.5 %, 31,000 bits | 1.5 %, 8,500 bits | 1.5 %, 1,300 bits |
| Twilight (10⁻³) | used avalanche-diode modules | 8.1 %, no key | 14 %, no key | 21 %, no key |
| Sunlit day (10⁻¹) | either | about 46 %, no key | about 48 %, no key | about 49 %, no key |

The path loss is 4.5, 8.0, and 10.8 dB at the three distances. The sky radiances are orders of magnitude, so step 2's measured background replaces them. The [outdoor lab](https://normansrule.github.io/quantum-link-research/lab/outdoor/) shows every factor and lets you move each part. The lesson for the build is that the P10 SiPMs measure loss and background well but need quieter detectors to make a key outdoors, and that a 405 nm link works only after dark.

## References
Bourgoin et al. (2013) *New J. Phys.* 15, 023006 · Liao et al. (2017) *Nature Photonics* 11, 509 (daylight free-space QKD) · Avesani et al. (2021) *npj Quantum Inf.* 7, 93.
