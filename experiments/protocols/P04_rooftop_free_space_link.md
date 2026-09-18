# P04 — Campus free-space link: loss versus distance and daylight background

## Safety
Never point the alignment laser at people, windows, aircraft, or vehicles; use a red alignment laser < 1 mW for visual alignment and the 810 nm photons (invisible, eye-safe at these powers) for data; check campus and aviation rules for outdoor beams.

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

## References
Bourgoin et al. (2013) *New J. Phys.* 15, 023006 · Liao et al. (2017) *Nature Photonics* 11, 509 (daylight free-space QKD) · Avesani et al. (2021) *npj Quantum Inf.* 7, 93.
