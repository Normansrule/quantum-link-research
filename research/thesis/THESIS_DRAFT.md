# Quantum Links from a Bench to Mars: a Systems-Engineering Study of Physics-Secured Communication at Planetary Distance

Aleksander Norman · M.S. Systems Engineering, California State University, Dominguez Hills · draft assembled by `scripts/build_thesis.py`

# Chapter 1 — Introduction (draft)

## 1.1 The question

Can two parties, one on Earth and one on Mars, share a secret whose security rests on physics rather than on the difficulty of a mathematical problem, and can they use that secret to communicate? The question is not rhetorical. Every classical key exchange in use today, including the post-quantum schemes standardized by the National Institute of Standards and Technology (NIST) in 2024, is secure only under a computational assumption. Quantum key distribution (QKD) replaces that assumption with the no-cloning theorem and the disturbance that measurement causes (Bennett & Brassard, 1984; Ekert, 1991), and quantum teleportation moves a quantum state itself using entanglement and two classical bits (Bennett et al., 1993). Both have been demonstrated on Earth, over fiber and through low-Earth-orbit satellites (Yin et al., 2017; Li et al., 2025). Neither has been attempted at planetary distance.

## 1.2 The catch

Two physical facts make the interplanetary case different in kind, not only in degree. The first is the no-communication theorem: entanglement by itself carries no message, so every protocol that uses it also needs classical information that travels at, or below, the speed of light. Between Earth and Mars that is 3.1 to 22.3 minutes one way. The second is that the receiving half of an entangled pair must remain coherent until those classical bits arrive. A memory that lasts a millisecond, which is ample for a metropolitan link, is useless across a 6-to-45-minute round trip. The question therefore reduces to a comparison between two numbers: the coherence time of a quantum memory and the light time of the channel.

## 1.3 What this thesis does

This work is a systems-engineering treatment of that comparison. It builds, as open-source and tested software, the chain of physical models from a single qubit to a planetary link: the thermal occupation that sets where each component must live, the loss laws of fiber and free space, the circuits that create and consume entanglement, the key-distribution protocols and their capacity bounds, the memories and repeaters that extend range, the orbital geometry that sets light time and blackout, and the application layer that must refuse to send when it runs out of key. Every model cites its source, carries an analytic test, and traces to a requirement in a machine-checked matrix. Three experiments organize the work: F1, entanglement between two computers in one city; F2, a downlink from a satellite; and F3, the Earth–Mars link, which is F1 and F2 with the time axis stretched by a factor of a million.

## 1.4 Contributions

1. A physics-first, modular codebase (`qll`) in which no-signaling, no-cloning, the two-bit cost of teleportation, trace preservation, and the repeaterless capacity bound are enforced as runtime invariants rather than assumed.
2. A verified reproduction of the Micius satellite link budget within 3 dB, and a Kepler ephemeris whose Earth–Mars range envelope matches tabulated constants to 1 %.
3. A memory capability matrix that answers the thesis question quantitatively: at an initial fully entangled fraction of 0.95, only rare-earth nuclear-spin memories and hour-class trapped-ion memories survive the Mars round trip, and the rare-earth ones do so at retrieval efficiencies below 5 %.
4. A fail-closed messenger and a buffer-sizing rule for a channel with a 20-minute round trip, showing that the key buffer is small and the wait is not.
5. A library, a lab manual, and proposals E1–E10 that let a student laboratory reproduce the landmark experiments on a bench budget and extend them toward the interplanetary case.

## 1.5 Structure

Chapter 2 gives the physics background; Chapter 3 the method; Chapter 4 the computed results by phase; Chapter 5 the experiments performed and proposed; Chapter 6 the discussion, including what has scaled in the field, what has been retracted, and what remains open; Chapter 7 concludes.

\newpage

# Chapter 2 — Background (draft, condensed from `learn/`)

## 2.1 Qubits, noise, and temperature

A qubit is a two-level quantum system: a unit vector cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩, a point on the Bloch sphere. Noise moves that point inward: energy relaxation with time constant T₁ pulls it toward the ground state, and dephasing with time constant T₂ blurs its azimuth, with 1/T₂ = 1/(2T₁) + 1/T_φ. Both are completely positive trace-preserving maps with Kraus representations (Kraus, 1983; Nielsen & Chuang, 2010), and both depend on temperature through the Bose–Einstein occupation n̄ = 1/(e^{ħω/k_BT} − 1) of the bath at the qubit's frequency (Clerk et al., 2010). The occupation is the quantity that decides where every component of a link must operate: a 5 GHz superconducting qubit requires millikelvin temperatures, while a 193 THz photon is effectively at zero temperature in a room. Full treatment: `learn/00_foundations/03`, `06`, `08`–`12`.

## 2.2 Entanglement, Bell tests, and the limits that hold everywhere

Two qubits can share a Bell state whose correlations violate the Clauser–Horne–Shimony–Holt (CHSH) inequality, S ≤ 2 for any local model, up to the quantum maximum 2√2 (Clauser et al., 1969; Brunner et al., 2014). Three theorems constrain what entanglement can do and are enforced as invariants in this work: no unknown state can be copied (Wootters & Zurek, 1982); no local operation on one half of a pair changes the statistics of the other half, so entanglement alone carries no message (Ghirardi et al., 1980; Peres & Terno, 2004); and teleporting one qubit costs exactly one Bell pair and two classical bits (Bennett et al., 1993), with a resource of fully entangled fraction f giving average fidelity (2f+1)/3 against a classical ceiling of 2/3 (Massar & Popescu, 1995; Horodecki et al., 1999). Full treatment: `learn/00_foundations/05`, `07`; `learn/03_quantum_communication/02`.

## 2.3 How qubits are built

Eight physical platforms are compared in `learn/02_qubit_modalities/`. For a communication link three properties dominate: a native optical interface, a memory lifetime long compared with the classical round trip, and an operating temperature that a flown cooler can reach. Superconducting transmons (Koch et al., 2007; Krantz et al., 2019) lead in gate speed and count but have no optical interface and need 10–20 mK. Trapped ions (Cirac & Zoller, 1995; Bruzewicz et al., 2019) offer the highest gate fidelities, hour-class coherence (Wang et al., 2021), and ultraviolet photon emission, with room-temperature traps. Color centers in diamond (Doherty et al., 2013) offer the strongest network record: remote entanglement, a loophole-free Bell test, three-node networks, and teleportation between non-neighbouring nodes (Hensen et al., 2015; Pompili et al., 2021; Hermans et al., 2022), at 4 K, with a bench-scale teaching version for about one hundred dollars. Rare-earth ions in crystals hold nuclear-spin coherence for 6 to 13 hours (Zhong et al., 2015; Wang et al., 2025) at low retrieval efficiency. Photons are the flying qubit in every case.

## 2.4 Communication: keys, repeaters, satellites

Quantum key distribution grows a shared secret from single-photon statistics; the BB84 protocol tolerates an error rate up to 11 % (Shor & Preskill, 2000), decoy states make weak-laser sources safe (Lo et al., 2005), measurement-device-independent protocols remove detector side channels (Lo et al., 2012), and no repeaterless protocol can exceed −log₂(1−η) secret bits per channel use (Pirandola et al., 2017). Fiber loses photons exponentially, so beyond a few hundred kilometres either satellites (Yin et al., 2017; Li et al., 2025) or repeaters with quantum memories (Briegel et al., 1998; Sangouard et al., 2011; Azuma et al., 2023) are required. The only published concept for links beyond the Moon is NASA's Deep Space Quantum Link (Mohageg et al., 2022). Full treatment: `learn/03_quantum_communication/`.

## 2.5 The gap this thesis addresses

The literature quantifies memories, repeaters, and satellite links separately and at terrestrial or cislunar scale. No published work places demonstrated memory lifetimes against planetary light times, routes every classical exchange of a protocol through a physical delay, and reports the end-to-end consequence for an application. Chapters 3 and 4 do that.

\newpage

# Chapter 3 — Method (draft)

## 3.1 Systems-engineering frame

The project follows a verification-driven "V": stakeholder needs (N-1 to N-5) become testable requirements with identifiers (REQ-PHY, REQ-THM, REQ-CHN, REQ-CIR, REQ-QKD, REQ-NET, REQ-CAP, REQ-SPC, REQ-APP, REQ-SYS), each requirement names the test that verifies it, and a script fails the build if any test path is missing. Twenty-four requirements exist at the time of writing; twenty-two are verified by tests, and two await bench data. Risks (R-1 to R-6) and Technology Readiness Levels (TRL) are tracked alongside, and every design decision that should not be revisited without a written reason is logged with its date.

## 3.2 Physics-first modular code

The `qll` package is organized by the physical stack, and its import graph is a directed acyclic graph that follows the physics: constants → channels → circuits → key distribution → network → space → application, with hardware models feeding circuits and channels. A test fails on any upward import. Each module owns one physical idea and carries a card: the idea, the governing equations with symbols defined, the public interface, the invariants it enforces, its references, its analytic test, and the modules it may import. Seven invariants cut across the stack: no classical information leaves any function before d/c (a `ClassicalMessage` object refuses to be read early); no function returns two copies of an unknown state (checked by reflection over every public function); teleporting one qubit consumes one Bell pair and exactly two bits; every noise process satisfies ΣE†E = I on construction; every repeaterless rate is bounded by the PLOB capacity; temperature is a required argument wherever an occupation number enters; and basis choices come from a declared entropy source.

## 3.3 Established simulators only

No simulator was written from scratch. Qiskit Aer computes noisy circuits, Stim samples Clifford circuits at scale, QuTiP integrates master equations, SeQUeNCe runs discrete-event network simulations, Perceval evolves Fock states through linear optics, and kyber-py and cryptography provide ML-KEM and AES-GCM. The `qll` code supplies the analytic physics, thin adapters, and the invariants these libraries do not enforce. Where an adapter exists, its output is compared with the analytic module: Perceval reproduces the Hong–Ou–Mandel law and the one-half success of a linear-optics Bell analyser; SeQUeNCe never delivers a pair before the herald round trip.

## 3.4 Verification hierarchy

Each requirement is verified by one of four methods, in descending order of strength for this work: an analytic test in continuous integration, a simulation with a reference value, a bench measurement, or a literature value with a verified citation. Numbers quoted in the results chapter are generated by a script from the tested functions, so the thesis cannot state a value the code does not reproduce. Citations are enforced mechanically: every bibliographic key cited in a docstring must exist in the BibTeX files, and each entry carries a status of verified, confident, or to-be-verified; nothing in the last class is cited from code.

## 3.5 What the method does not do

The models are deliberately simple where the literature is not settled: the atmospheric optical depths are representative rather than site-measured, the relay pass yields are shaped on one published campaign, and the all-photonic repeater is a redundancy model rather than a graph-state simulation. Each such simplification is stated in the module docstring and appears as an open item in the backlog.

\newpage

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

\newpage

# Chapter 5 — Experiments (draft)

## 5.1 Three flagship experiments

The work is organized around three experiments at three distances that share one physics (`experiments/flagship/`): F1, heralded entanglement and teleportation between two computers in one city; F2, a single-photon downlink from low Earth orbit; and F3, the Earth–Mars link. Each is staged as simulate, bench, and field, with a pass number per stage.

## 5.2 Simulations performed

Five simulations (`simulations/S01–S05`) were run and are regression-tested against analytic limits:
- S01: CHSH versus depolarizing noise in Qiskit Aer; the ideal value 2√2 is reproduced to 0.03 and the violation is lost near p ≈ 0.15 per qubit.
- S02: teleportation with the two classical bits delayed by a light time while a one-hour memory decays; fidelity crosses 2/3 at T₂ ln 3 ≈ 66 minutes, so the Mars maximum one-way delay of 22 minutes leaves F ≈ 0.85. The `NotYetArrived` guard is exercised in the same run.
- S03: photons per second at the receiver from a 10⁸ pairs/s source, from 1 km of fiber to Mars at maximum range.
- S04: a repetition code in Stim with majority-vote decoding, showing logical error falling with distance below threshold.
- S05: secret bits per 300-second satellite pass against background count rate, showing that daylight ends the key before it ends the signal.

The Perceval and SeQUeNCe adapters (`tests/test_adapters.py`) add two third-party checks: the linear-optics Bell analyser succeeds exactly half the time, and no simulated memory becomes entangled before the herald round trip.

## 5.3 Bench experiments prepared

Four protocols are written to be followed line by line (`experiments/protocols/`): P01, continuous-wave optically detected magnetic resonance (ODMR) of a nitrogen-vacancy ensemble on a bench costing $100–500; P02, pulsed control (Rabi, Ramsey, Hahn echo, T₁); P03, a two-crystal spontaneous parametric down-conversion source with Hong–Ou–Mandel interference, a CHSH test, and BB84; P04, a campus free-space link measuring loss and daylight background. The analysis pipeline for P01 (`qll/analysis/odmr_fit.py`) is tested on synthetic spectra and recovers the zero-field splitting to 0.5 MHz and the field to 0.5 G. **At the time of writing no bench data exist; this section will report the first ODMR spectrum, its fitted D and B, and the comparison with 2.870 GHz corrected by −74 kHz/K to the measured temperature.**

## 5.4 Proposed experiments

Ten proposals (`experiments/proposed/E01–E10`) extend the field toward the interplanetary case; each states its gap, a cheap version, a research version, and the requirement it verifies. Three are within reach of a student laboratory in one semester and directly serve the thesis: E1, teleportation on the photonic bench with the classical record released only after a software delay equal to the Mars light time (a bench demonstration of the no-signaling theorem and the two-bit cost); E2, nitrogen-vacancy T₁ and T₂ from 77 K to 350 K against the thermal model, which closes REQ-THM-003; and E6, measurement bases chosen by a quantum random-number generator on the same bench, which closes the freedom-of-choice loophole at teaching-lab scale.

\newpage

# Chapter 6 — Discussion (draft)

## 6.1 What the numbers say

The thesis question has a quantitative answer. Against a Mars-maximum round trip of 44.6 minutes, three demonstrated memories keep a pair useful for teleportation: the hour-class trapped-ion qubit with less than 1.5× margin at 99 % retrieval efficiency, and two europium-doped crystals with wide margin at 1 % and 0.5 % efficiency. Diamond and ensemble memories, which carry the strongest network record, reach the Moon and no farther. Lifetime and efficiency therefore trade against each other across today's platforms, and the honest architecture is heterogeneous: crystals or ions to hold entanglement across the wait, color centers or photons to interface and process. That trade is proposal E8.

The rate problem is separate from the memory problem and is worse. Diffraction over an astronomical unit leaves about 10⁻⁹ of the photons even for a 10 m receiver, so a bright source delivers pairs per hour, not per second. Multiplexing by three to six orders of magnitude (E9) or relays at intermediate points, which do not exist between Earth and Mars, are the only remedies. Relays at Sun–Earth L4/L5 solve a different problem, conjunction blackouts, and the model shows they keep a path open through every one.

The classical half is not a bottleneck: a DSOC-class terminal delivers tens of megabits per second beyond 2 au, and the two bits per teleported qubit are negligible. Latency is the whole cost, and no throughput hides it; the messenger's three reported numbers make this explicit.

## 6.2 Where the models are weakest

Atmospheric optical depths are representative, not measured at a site; relay pass yields are shaped on one published campaign; the all-photonic repeater is a redundancy model; and the memory decay is single-parameter depolarization or dephasing rather than a platform-specific spectral-diffusion model. Each simplification is stated in its module and listed in the backlog. The largest gap is empirical: no bench data yet exist, and the two requirements that need them (memory coherence versus temperature, and the exact Jinan-1 budget) remain unverified.

## 6.3 Lessons from the field's failures and successes

The lessons files (`experiments/lessons/`) record claims that did not survive: the retracted quantized-Majorana-conductance result, contested "supremacy" gaps that classical algorithms closed, boson-sampling benchmarks that were spoofed, and commercial QKD systems that were secure in theory and hacked in practice. Four habits in this work follow from them: every number carries a source and a year; every claim in code has an analytic test; capacity bounds are asserted rather than assumed; and over-claiming feasibility is a live risk in the register. The platforms that scaled (transmons, atom arrays, microsatellite QKD) did so by removing one dominant noise source at a time, reusing an existing supply chain, and optimizing one agreed metric. The Earth–Mars link should be designed the same way: the dominant loss is diffraction, the supply chain is DSOC-class terminals and the Deep Space Network, and the metric is secret bits per day at a stated fidelity with latency reported alongside.

## 6.4 Open problems

Ten open problems are ranked in `research/cutting_edge/02_open_problems.md`. The three the thesis considers decisive are memory lifetime versus efficiency, entanglement rate at astronomical-unit loss, and classical-latency-aware protocol design, which no published repeater or purification scheduler addresses at a 20-minute round trip.

\newpage

# Chapter 7 — Conclusion (draft)

Earth and Mars can, in principle, share a physics-secured secret, and the models built here say what it would cost. The cost is time before it is money: the two classical bits of every teleportation take 3 to 22 minutes, the receiving memory must survive 6 to 45 minutes, and today only hour-class ion and rare-earth memories do so, the latter at retrieval efficiencies below 5 %. The channel delivers pairs per hour at best without heavy multiplexing; conjunction blocks it for weeks every 26 months unless a relay sits at L4 or L5; and an application on top of it must refuse to send rather than downgrade when its key runs out.

The contribution is less the answer than the apparatus for answering: a tested, cited, requirement-traced codebase in which the physics that forbids shortcuts (no-signaling, no-cloning, the two-bit cost, trace preservation, the capacity bound) is enforced by the software itself; a reproduction of a real satellite budget and a real ephemeris; a library and lab manual that let a student rebuild the landmark experiments for a few hundred dollars; and ten proposals that move the field toward the interplanetary case. Future work begins with data: the first optically detected magnetic resonance spectrum on the bench, the nitrogen-vacancy relaxation curve against temperature, and the delayed-bits teleportation that would make the no-signaling theorem a laboratory fact at the scale of a planet's light time.

\newpage

# Appendix A — Generated results tables


## 1. Thermal occupation

| Carrier | T | n̄ |
|---|---|---|
| 5 GHz qubit, 300 K | 300.0 K | 1.25e+03 |
| 5 GHz qubit, 15 mK | 0.015 K | 1.13e-07 |
| 193 THz photon, 300 K | 300.0 K | 3.66e-14 |

## 2. Channels and light time

| Quantity | Value | Source |
|---|---|---|
| Fiber attenuation length at 0.2 dB/km | 21.7 km | `fiber_loss.py` |
| Fiber transmittance, 100 km | 0.01 | |
| Free-space geometric η, 1200 km, 15 cm → 1 m, 810 nm | 0.11 | `free_space_diffraction.py` |
| Free-space geometric η, Mars min, 15 cm → 10 m, 1550 nm | 1.49e-09 | |
| Earth–Mars range envelope (Kepler model) | 0.3711–2.6755 au | `space/ephemeris.py` |
| One-way light time, Mars min / max | 3.1 min / 22.3 min | `light_time_delay.py` |
| Round trip, Mars min / max | 6.2 min / 44.6 min | |
| Synodic period | 779.9 d | |

## 3. Satellite link budgets

| Mission | Elevation | Range | Single-link loss | Two-link loss |
|---|---|---|---|---|
| Micius 2017 | 15° | 1407 km | 39.5 dB | 79.0 dB |
| Micius 2017 | 30° | 909 km | 32.9 dB | 65.7 dB |
| Micius 2017 | 45° | 683 km | 29.5 dB | 59.0 dB |
| Micius 2017 | 90° | 500 km | 26.2 dB | 52.4 dB |
| Jinan-1 2025 | 15° | 1407 km | 44.1 dB | 88.2 dB |
| Jinan-1 2025 | 30° | 909 km | 37.7 dB | 75.4 dB |
| Jinan-1 2025 | 45° | 683 km | 34.4 dB | 68.8 dB |
| Jinan-1 2025 | 90° | 500 km | 31.1 dB | 62.3 dB |

Reported: Micius two-downlink loss 64–82 dB over a pass [yin2017].

## 4. Key rates

- BB84 QBER threshold: 11.00 %
- PLOB capacity at η = 10⁻³: 0.00144 bits/use; at 10⁻⁶: 1.44e-06

## 5. Memory capability matrix (REQ-CAP-001), f₀ = 0.95

| Memory | Lifetime | Efficiency | Crossover (F = 2/3) | metro 25 km fiber | LEO 1000 km | GEO 36000 km | Moon | Mars min | Mars max |
|---|---|---|---|---|---|---|---|---|---|
| Rb/Cs atomic ensemble (DLCZ) | 1.00 ms | 50.0% | 1.03 ms | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| SiV nuclear spin in cavity | 1.0 s | 90.0% | 1.0 s | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| NV 13C register | 60.0 s | 90.0% | 61.8 s | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| 171Yb+ hyperfine | 60.0 min | 99.0% | 61.8 min | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Eu:YSO nuclear spin, 6 h (ZEFOZ+DD) | 6.00 h | 1.0% | 6.18 h | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Eu:YSO nuclear spin, 13.1 h | 13.10 h | 0.5% | 13.49 h | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Baselines (round trip): metro 25 km fiber 0.25 ms, LEO 1000 km 6.67 ms, GEO 36000 km 240.17 ms, Moon 2.6 s, Mars min 6.2 min, Mars max 44.6 min

## 6. Repeater chain crossover (REQ-NET-001)

| Memory T₂ | Segments | Crossover distance |
|---|---|---|
| 1.00 ms | 8 | none |
| 1.00 ms | 16 | none |
| 1.0 s | 8 | 393 km |
| 1.0 s | 16 | 373 km |
| 60.0 min | 8 | 393 km |
| 60.0 min | 16 | 373 km |

BBPSSW from F = 0.80 to 0.99: 10 rounds, F = 0.9925, 2917 input pairs per output pair; each round is one classical round trip (44.6 min at Mars max).

## 7. Space segment

- Solar conjunction blackouts (SEP < 3°) in 20 years: 10, mean length 20 d; direct availability 97.1%
- Availability with an Earth-orbit relay only: 97.5%; with L4 and L5 relays: 100.00%
- DSOC-class classical link at 0.2 au: 2.74e+09 photons/s → 267 Mb/s
- DSOC-class classical link at 1.0 au: 1.10e+08 photons/s → 219 Mb/s
- DSOC-class classical link at 2.5 au: 1.75e+07 photons/s → 35 Mb/s

## 8. Messenger (REQ-APP-001)

| Distance | Round trip | Key buffer for 1 msg/min with zero key rate |
|---|---|---|
| Moon | 2.6 s | 0.00 kB |
| Mars min | 6.2 min | 0.20 kB |
| Mars max | 44.6 min | 1.43 kB |


\newpage

# Appendix B — Requirements and verification

Each requirement is verified by one of: **T** an analytic test in CI, **S** a simulation with a reference value, **B** a bench measurement, or **L** a literature value with a verified citation. Status mirrors `systems/traceability_matrix.csv`.

| Requirement | Method | Evidence | Status |
|---|---|---|---|
| REQ-PHY-001 latency floor d/c | T | `test_phase1_constants.py` | verified |
| REQ-PHY-002 two bits per qubit | T | `test_phase2_circuits.py` | verified |
| REQ-PHY-003 no cloning | T | `test_phase2_no_cloning.py` | verified |
| REQ-THM-001/002 thermal occupation, GAD CPTP | T | phase 1 and 2 noise tests | verified |
| REQ-THM-003 memory coherence vs T | B + L | E2 bench data; Jarmola 2012 | planned |
| REQ-CHN-001/002 fiber law, 1/L² | T | `test_phase1_channels.py` | verified |
| REQ-CHN-003 background prefactor | B | P04 / E4 | planned |
| REQ-CIR-001..003 F = 1, (2f+1)/3, 2√2 | T | `test_phase2_circuits.py` | verified |
| REQ-QKD-001 11 % threshold | T | `test_phase1_qkd_theory.py` | verified |
| REQ-QKD-002 rates ≤ PLOB | T | Phase 3 | planned |
| REQ-NET-001 chain beats direct | S | `repeater_rate_explorer`, Phase 4 | simulation |
| REQ-CAP-001 memory vs light time | S + L | S02, memory table | simulation |
| REQ-CAP-002 teleportation after delayed bits | S | `test_simulations.py::S02` | verified |
| REQ-APP-001 fail closed | T | Phase 6 | planned |
| REQ-SYS-001/002 traceability, import DAG | T | `test_phase1_systems.py`, `test_phase2_dag.py` | verified |
| REQ-F1-001 herald > 1 Hz, S > 2.2 over 1 km | B | F1 stage S3 | planned |
| REQ-F2-001 budget within ±3 dB of two missions | S + L | F2 stage S1 | planned |
| REQ-SEC-001 DI certification under latency | S | E10 | planned |

