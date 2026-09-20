# Chapter 4 — Results (draft; every number from `results/tables.md`)

## 4.1 Temperature decides where components live

A 5 GHz superconducting qubit sees about 1250 thermal photons per mode at room temperature and about 10⁻⁷ at 15 mK, whereas a 193 THz telecom photon sees 4 × 10⁻¹⁴ at room temperature. The optical carrier is therefore the only carrier that can cross a warm channel, and any microwave processor at a network node must either be transduced to optical wavelengths or kept behind a local optical interconnect. This single computation motivates the design stance, adopted in Chapter 6, of building the link around platforms with native optical transitions.

## 4.2 Circuits (Phase 2)

Ideal teleportation reproduces the input to a fidelity of 1 within numerical precision; with a Werner resource of fully entangled fraction f the Haar-averaged fidelity follows (2f+1)/3 to within 2 × 10⁻³, crossing the classical limit of 2/3 at f = 1/2. The CHSH value of the ideal pair is 2√2 to 10⁻⁶, and the Werner formula 2√2(4f−1)/3 holds to 10⁻⁹. Entanglement swapping of two Werner pairs reproduces the Briegel recurrence F² + (1−F)²/3 to 10⁻⁹. The three canonical noise channels agree with QuTiP master-equation solutions to 10⁻⁵, and the finite-temperature channel reduces to zero-temperature damping when the bath occupation vanishes.

## 4.3 Links (Phase 3)

The exact Gaussian-over-aperture law recovers the 1/L² far-field scaling and shows that the uniform-disc estimate used in early drafts under-counts collected power by exactly a factor of two. With the reported 10 µrad divergence, a 1.2 m receiver, 1.2 µrad pointing, and representative atmospheric and optical factors, the model gives a two-downlink Micius loss of 66 dB at 30° elevation and 79 dB at 15°, inside the reported 64–82 dB. The BB84 threshold is 11.00 %; every repeaterless protocol rate implemented (decoy-state BB84, MDI) sits below the PLOB capacity at 10⁻¹, 10⁻³, and 10⁻⁶ transmittance, while the twin-field rate crosses it at a few hundred kilometres of fiber.

## 4.4 Memories and repeaters (Phase 4)

The memory capability matrix (Table 5) is the central result. With an initial fraction of 0.95, a depolarizing memory keeps a pair useful for teleportation for T ln(2.8) ≈ 1.03 T. Atomic ensembles clear only the metropolitan baseline; silicon-vacancy nuclear spins reach geostationary distance; the diamond nitrogen-vacancy carbon-13 register reaches the Moon; and the Mars round trip of 44.6 minutes at maximum range is cleared by three demonstrated memories: the hour-class trapped-ion qubit with less than 1.5× margin at 99 % efficiency, and the two europium-doped crystal memories with wide margin at efficiencies of 1 % and 0.5 %. A pure-dephasing memory acting on a Werner pair drives the fraction to (2f₀+1)/6, which lies below one half, so dephasing alone also ends teleportation, at T₂ ln((4f₀−1)/(2−2f₀)).

A repeater chain of eight segments with one-second memories beats direct transmission beyond about 390 km and stalls when the hold time exceeds the memory; with millisecond memories it never wins. Purification from F = 0.80 to 0.99 by the BBPSSW recurrence, verified against a full 16-dimensional simulation, costs three rounds and about eighteen input pairs per output pair, each round a classical round trip.

## 4.5 Space segment (Phase 5)

A Kepler mean-element ephemeris gives an Earth–Mars range envelope of 0.3711 to 2.6755 au, matching the tabulated constants to 1 %, and a synodic period of 779.9 days. Solar conjunction blocks a 3° line of sight ten times in twenty years for about twenty days each; a relay at Sun–Earth L4 or L5 keeps a path open through every conjunction. A DSOC-class classical terminal delivers tens of megabits per second beyond 2 au, so the two classical bits per teleported qubit are never the bottleneck; light time is.

## 4.6 Application (Phase 6)

The messenger refuses to send when its QKD key buffer is empty rather than downgrading to a computational key, and cannot deliver before d/c. The buffer needed to sustain one message per minute through a Mars-maximum round trip with no key replenishment is about 1.4 kB; a key rate matched to consumption needs almost none. The honest statement of performance is therefore three numbers, not one: key bits per day, round-trip time, and refusals.
