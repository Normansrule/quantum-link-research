# quantum-link-research: Hardware, Experiments, and Literature Guide

Version 0.1 · 2026-09-16 · lives at `experiments/bench/hardware_guide.md`
Companion file: `docs/references_additions.bib` (new bibkeys used below; merge into `docs/references.bib`).

This guide maps the six software phases of the repository onto (1) the physics each phase encodes, (2) the landmark experiments that established that physics in hardware, (3) what a student lab can actually build, at three budget tiers, with links to real vendors and open-source designs, and (4) experiments nobody has run yet that would move the Earth-Mars concept of operations (CONOPS) from Technology Readiness Level (TRL) 1-2 toward TRL 3-4.

Citation policy reminder (CONTRIBUTING.md rule 3): every bibkey below has an entry in `references_additions.bib`. Digital Object Identifiers (DOIs) marked **[verified]** were confirmed against the publisher page on 2026-09-16; anything marked **TODO: verify** must be checked before it is cited in code or in the thesis.

---

## 0. The three rules, restated for hardware people

| Rule | What it forbids in a lab | Where the repo enforces it |
|---|---|---|
| No-communication theorem | No experiment, however clever, sends a bit from Alice to Bob using only the entangled pair. Every "signal" needs a classical message. | `qll/channels/light_time_delay.py` is the only source of latency; teleportation returns `classical_bits` explicitly. |
| No-cloning [wootters1982] | No amplifier or repeater in the chain copies a qubit. Quantum repeaters swap entanglement; they never amplify the signal. | Phase 2 no-cloning guard test. |
| Teleportation costs 2 classical bits per qubit [bennett1993] | Earth-Mars teleportation of one qubit costs 2 bits over the Deep Space Network (DSN) at light speed: 3 to 22 minutes one way. | `REQ-PHY-002`. |

Everything in this document is downstream of those three rows.

---

## 1. Layer map: from a qubit on a bench to an Earth-Mars link

```
Level 0  Qubit components         NV/SiV spins in diamond, photons from SPDC, detectors, microwave control
Level 1  Two-qubit primitives     Bell pairs, CHSH, teleportation, entanglement swapping   (Phase 2)
Level 2  One link                 Fiber or free-space channel, QKD, loss, thermal noise     (Phase 3)
Level 3  Network                  Memories, repeaters, swapping schedulers, routing         (Phase 4)
Level 4  Space segment            LEO/GEO relays, pointing, background light, ephemeris     (Phase 5)
Level 5  Application              Key management, fail-closed messenger, benchmarks         (Phase 6)
```

Temperature enters every level (see `qll/circuits/noise/thermal.py` and `qll/channels/thermal_background.py`): spins want millikelvin or at least liquid-helium temperatures for long coherence, photons at 637 nm or 1550 nm cross warm channels because their thermal occupation is negligible, and the transduction between the two is the open engineering problem [lauk2020].

---

## 2. Level 0: qubit components and abstract ideas

### 2.1 Why nitrogen-vacancy (NV) centers in diamond are the reference platform

The negatively charged NV center is a spin-1 electronic defect (a substitutional nitrogen next to a lattice vacancy) with a ground-state zero-field splitting of 2.87 GHz, optically initialized and read out through spin-dependent fluorescence at 637 nm (zero-phonon line) with a broad phonon sideband to ~800 nm [doherty2013]. Three facts make it the workhorse of quantum-network experiments:

1. It works at room temperature for sensing and for teaching (optically detected magnetic resonance, ODMR), and at 4 K for network-grade spin-photon entanglement.
2. Surrounding carbon-13 nuclear spins act as a multi-qubit register with coherence times of seconds to minutes [bradley2019, bradley2022].
3. It has the longest track record of remote entanglement, loophole-free Bell tests, and teleportation of any solid-state qubit [bernien2013, hensen2015, pfaff2014, pompili2021, hermans2022, stolk2024].

The silicon-vacancy (SiV) center is the main alternative for networking because its optical transition is far less sensitive to electric-field noise, which allows nanophotonic cavities and, with quantum frequency conversion to 1350 nm, deployed-fiber entanglement across Boston [bhaskar2020, knaut2024].

Rare-earth ions (europium in yttrium orthosilicate, Eu:YSO) are the memory platform relevant to the Earth-Mars problem: nuclear-spin coherence of 6 hours [zhong2015], later exceeding 10 hours [wang2025memory], and one-hour coherent optical storage [ma2021]. That is the only class of memory whose demonstrated lifetime already exceeds the Earth-Mars round-trip light time (6-45 minutes), which is why `R-1` in the risk register is not yet closed but is closable.

### 2.2 Components of an NV node, cheapest to research grade

| Function | Teaching-lab part (approx. cost) | Research-grade part | Notes |
|---|---|---|---|
| Diamond with NV ensemble | Adámas fluorescent microdiamond, 150 µm, NV-rich; also low-nitrogen grade for better contrast ([product page](https://www.adamasnano.com/fluorescent-diamonds), [low-N details](https://www.adamasnano.com/low-nitrogen-information)) | CVD plate, [N] < 5 ppm, or a single-NV electronic-grade plate ([Adámas plates](https://www.adamasnano.com/diamond-plates)); Element Six for wafers | Microdiamond glued to a microstrip line is the standard student sample [stegemann2023]. Price on request; ensembles are tens of dollars to a few hundred, single-NV plates are thousands. |
| Green excitation | 520-532 nm laser diode module < 1 mW (class 2) or a high-power green LED [williams2025] | 532 nm DPSS laser, 50-100 mW, with acousto-optic modulator (AOM) for pulsing | LED excitation is safer for a classroom and still yields ODMR at ~1 µT/√Hz [williams2025]. |
| Microwave source (2.87 GHz) | ADF4351 evaluation board, 35-4400 MHz, driven by an Arduino or ESP32, plus a 1-2 W amplifier and a microstrip or wire loop antenna (used in [stegemann2023] and in the digital-polarity magnetometer of [ivaldi2025]) | Bench signal generator + IQ modulator + arbitrary waveform generator (AWG) for pulsed Rabi/Ramsey/Hahn-echo sequences [sewani2020] | The ADF4351 is the single biggest cost saving in the whole build. |
| Fluorescence detection | BPW34 photodiode + transimpedance amplifier [stegemann2023], or a silicon photomultiplier (SiPM) board | Excelitas SPCM-AQRH single-photon counting module ([product page](https://www.excelitas.com/product/spcm-aqrh)), Hamamatsu C13001-01 fiber-coupled SPAD module ([product page](https://www.hamamatsu.com/us/en/product/optical-sensors/mppc/photon-counting-module/C13001-01.html)) | For ensemble ODMR a photodiode is enough; single-photon modules are only needed for single NVs or photon statistics. |
| Optics | 3D-printed cube system, acrylic lens, cheap dichroic or 50:50 splitter + long-pass film [stegemann2023] | Confocal microscope with 0.9 NA objective, 3-axis stage ([low-cost confocal](https://arxiv.org/abs/2301.08326)) | |
| Magnetic bias | Permanent magnet on a screw [stegemann2023] | Three-axis Helmholtz coils | |
| Control and readout | Arduino/ESP32 with on-board ADC [stegemann2025, tsukamoto2023] | Field-programmable gate array (FPGA) pulse generator, e.g., the open-source platforms listed in [sewani2020] | |

Two fully open designs cover this whole table:

- **Uncut Gem** (Quantum Village): a full-stack open-source NV magnetometer with PCB files for JLCPCB/PCBWay, Arduino firmware, and a build guide; reported cost ~£115, single-board variant under $100 [carney2025]. Repository: https://github.com/QuantumVillage/UncutGem, build guide: https://github.com/QuantumVillage/UncutGem/blob/main/BuildGuide/BuildGuide.md. License is AGPL-3.0.
- **Stegemann modular cube ODMR** (Münster): 3D-printed optical cubes on a magnetic base plate, class-2 laser, BPW34 detection, whole setup under €250 [stegemann2023]; the 2025 follow-up moves readout onto a microcontroller [stegemann2025]. Paper: https://doi.org/10.1088/1361-6404/acbe7c.

For coherent control (Rabi, Ramsey, Hahn echo, T1, T2), the Sewani et al. teaching setup is the reference design with a full parts list in its appendix [sewani2020]: https://arxiv.org/abs/2004.02643.

### 2.3 Photonic components (the "flying" qubits)

Spontaneous parametric down-conversion (SPDC) in beta-barium borate (BBO) pumped at 405 nm produces 810 nm photon pairs; two crossed type-I crystals give polarization entanglement [kwiat1999, dehlinger2002a]. Parts:

| Function | Cheapest workable | Comfortable | Link |
|---|---|---|---|
| Pump laser | 405 nm multimode laser diode, 50-100 mW; broadband multimode diodes have been shown to work for entangled sources [li2021multimode] | Single-frequency 405 nm diode (Toptica or equivalent) | https://arxiv.org/abs/2105.00454 |
| Nonlinear crystal | BBO pair for 405 nm type-I | PPKTP for higher brightness | Thorlabs SPDC crystals: https://www.thorlabs.com/bbo-crystals-for-spontaneous-parametric-down-conversion-spdc ; Newlight Photonics 405 nm SPDC component list: https://www.newlightphotonics.com/SPDC-Components/405nm-Pumped-SPDC-Components |
| Detectors (two needed, four for CHSH with polarizing beam splitters) | Hamamatsu C13001-01 SPAD module (fiber-coupled) or a SiPM evaluation board with custom front end [diblasio2025] | Excelitas SPCM-AQRH (>70% detection efficiency at 650 nm, TTL output); available through DigiKey | https://www.excelitas.com/product/spcm-aqrh ; https://www.digikey.com/en/product-highlight/e/excelitas/single-photon-counting-modules |
| Coincidence counter | Programmable system-on-chip (PSoC) or FPGA coincidence unit built for a few tens of dollars [masters2018]; 250 MHz logic-gate coincidence module [ipus2017] | Commercial time tagger | https://advlabs.aapt.org/document/ServeFile.cfm?ID=13806&DocID=4227 ; https://arxiv.org/abs/1706.04927 |
| Filters, wave plates, polarizers | 810 ± 10 nm bandpass, half-wave plates, film polarizers | Cage-mounted precision rotation stages | Thorlabs |

Commercial turnkey alternatives when time matters more than money:

- Thorlabs EDU-QOP1(/M) Quantum Optics Educational Kit (type-I BBO source, single-photon detectors, alignment laser) and the EDU-QOPA1(/M) Polarization-Entanglement Extension Kit with compensation crystals for a Bell test: https://www.thorlabs.com/quantum-optics-educational-kits . Requires a breadboard.
- qutools quED Entanglement Demonstrator and its successor quEDU (single-photon detectors plus time-tagging electronics, experiment boards including an NV board): https://qutools.com/qued/ and https://qutools.com/quantum-physics-education-science-kits/ . The quED brochure reports CHSH S ≈ 2.7 out of the box.

### 2.4 Abstract ideas each component realizes

| Idea | Minimal experiment | Repo file |
|---|---|---|
| Superposition and coherent control | Rabi oscillation of an NV ensemble | (Phase 2 tomography tests) |
| Decoherence T1, T2, and its temperature dependence | Hahn echo vs. temperature; ODMR line width vs. laser power | `noise/thermal.py`, `noise/phase_damping.py` |
| Single-photon nature of light | Grangier anticorrelation with a heralded SPDC photon | `hardware/photon_source.py` (Phase 3) |
| Entanglement and nonlocality | CHSH with two-crystal SPDC, target S > 2 by > 5σ [dehlinger2002b] | `circuits/chsh.py` |
| Measurement incompatibility and basis choice | BB84 with polarization qubits on the same bench | `qkd/bb84.py` |
| Randomness as a quantum resource | Phase-diffusion or vacuum-noise quantum random number generator (QRNG) for basis selection | `hardware/`, ties to the owner's QRNG board |

---

## 3. Level 1: teleportation and entanglement-swapping schemes, with the experiments that proved them

### 3.1 The protocols (what Phase 2 must encode)

1. **Standard teleportation** [bennett1993]. Alice holds |ψ⟩ and half of a Bell pair; a Bell-state measurement (BSM) yields 2 bits; Bob applies one of {I, X, Z, XZ}. Fidelity 1 ideally; the best classical (measure-and-prepare) strategy averages F = 2/3 [massar1995].
2. **Entanglement swapping** [zukowski1993]. A BSM on two halves of two independent pairs entangles the two remaining halves, which never met. This is the repeater primitive [briegel1998].
3. **Heralded spin-spin entanglement** [barrett2005]. Each node emits a photon entangled with its spin; a BSM on the photons at a midpoint heralds spin-spin entanglement. Success probability scales with the square of single-photon efficiency (two-photon schemes) or linearly (single-photon schemes at the cost of phase stabilization).
4. **Measurement-based and topological variants**, including the Majorana parity-teleportation proposal the owner shared [crogman2025]. Keep this cited only in the thesis narrative until the DOI is verified.

### 3.2 Landmark hardware demonstrations (chronological)

| Year | Experiment | Platform | What it settled | Reference |
|---|---|---|---|---|
| 1997 | First photonic teleportation | SPDC photons | Teleportation is physical, not just a theorem | [bouwmeester1997] |
| 2013 | Heralded entanglement of two NV spins 3 m apart | NV in diamond, 4 K | Solid-state spins can be entangled through photons | [bernien2013] |
| 2014 | Unconditional teleportation between NV nodes | NV + C-13 nuclear spin | Deterministic BSM with a matter qubit | [pfaff2014] |
| 2015 | Loophole-free Bell test at 1.3 km | NV, Delft | Local realism ruled out with detection and locality loopholes closed simultaneously | [hensen2015] |
| 2017 | Ground-to-satellite teleportation, 1400 km | Micius satellite | Uplink teleportation over a space channel | [ren2017] |
| 2017 | Satellite-distributed entanglement over 1200 km | Micius | Free-space entanglement distribution beats fiber by orders of magnitude | [yin2017] |
| 2020 | Memory-enhanced quantum communication | SiV in nanocavity | A quantum memory can beat the direct-transmission bound | [bhaskar2020] |
| 2020 | Entanglement-based QKD over 1120 km without trusted relay | Micius | Untrusted-node satellite QKD | [yin2020] |
| 2021 | Three-node NV network with entanglement swapping | NV, Delft | First multi-node network primitive | [pompili2021] |
| 2022 | Teleportation between non-neighboring nodes | NV, three nodes | Teleporter built by swapping plus memory storage; fidelity above 2/3 with unit efficiency | [hermans2022] **[verified DOI 10.1038/s41586-022-04697-y]** |
| 2024 | Metropolitan-scale heralded NV entanglement, Delft-The Hague, 25 km deployed fiber | NV + frequency conversion | Entanglement outside the lab with active stabilization | [stolk2024] |
| 2024 | SiV memory nodes entangled over 35 km deployed Boston fiber | SiV, 1350 nm conversion | Second-long nuclear-spin storage in a telecom network | [knaut2024] **[verified DOI 10.1038/s41586-024-07252-z]** |
| 2024 | Memory-memory entanglement in a metropolitan network (atomic ensembles) | Atomic ensemble, Hefei | Three-node memory network over 12.5 km | [liu2024] |
| 2025 | Real-time microsatellite QKD with 100 kg portable ground stations; 12,900 km China-South Africa relay | Jinan-1 | Constellation-shaped economics: 23 kg payload, up to ~1 Mbit key per pass | [li2025jinan] **[verified DOI 10.1038/s41586-025-08739-z]** |
| 2025 | Nuclear-spin coherence exceeding 10 hours | Eu:YSO, sub-kelvin | Memory lifetime longer than any planetary light-time | [wang2025memory] **[verified DOI 10.1103/PRXQuantum.6.010302]** |

Read [azuma2023] for the repeater taxonomy that connects every row above.

### 3.3 Step-by-step: how the NV teleportation experiments were actually run

This is the sequence the Phase 2 `teleportation.py` record should mirror, because it is what real nodes do [pfaff2014, hermans2022]:

1. **Initialize.** Green (or resonant red) laser pumps each NV electron spin into m_s = 0; nuclear-spin memory qubits are initialized by swap gates.
2. **Generate remote entanglement.** Each node applies a microwave π/2 pulse, then a resonant optical π pulse; the emitted photon's time bin (early/late) is entangled with the spin. Photons travel to a midpoint beam splitter; a coincidence pattern on two single-photon detectors heralds |Ψ±⟩ between the spins. Success probability per attempt is ~10^-4 to 10^-6, so this step repeats at kHz rates for seconds to minutes.
3. **Protect the memory.** While waiting for the herald, the nuclear-spin memory is decoupled from the electron spin (dynamical decoupling), which was one of the key innovations of [hermans2022].
4. **Store and swap.** The heralded entanglement is moved into a nuclear-spin memory; the middle node repeats step 2 on its other link and then performs a BSM between its two qubits (entanglement swapping), which is heralded to the outer nodes classically.
5. **Prepare the input state.** The sending node's electron spin is prepared in |ψ⟩ by a calibrated microwave pulse (six cardinal states are used for process tomography).
6. **Bell-state measurement.** A controlled-NOT between the input electron spin and the memory qubit, then single-shot readout of both. This yields the two classical bits.
7. **Classical transfer.** The two bits are sent over an ordinary link. In the lab this takes microseconds; the CONOPS says minutes. Nothing else changes.
8. **Feed-forward and verify.** Bob applies the Pauli correction and reads out; the average fidelity over the six input states is compared with 2/3.

Every arrow in that list corresponds to a hardware subsystem in section 2.2, and steps 3 and 7 are exactly where the Earth-Mars problem lives.

### 3.4 Step-by-step: how the satellite teleportation and entanglement distribution were run [ren2017, yin2017, li2025jinan]

1. Onboard SPDC source at 810 nm (Micius) or a 625 MHz decoy-state laser-diode source at 850 nm (Jinan-1) produces the quantum signal.
2. Acquisition, pointing, and tracking (APT): a beacon laser is exchanged; coarse pointing uses the satellite attitude loop (~300 µrad) and fine pointing a fast-steering mirror (~1 µrad at the satellite) [li2025jinan].
3. The downlink beam diffracts to a spot of a few hundred meters at 500 km (see `free_space_diffraction.py`), and a 1 m class telescope collects a few photons per thousand.
4. Timing synchronization to nanoseconds via a pulsed laser and GPS-disciplined clocks; polarization reference-frame compensation for the rotating satellite.
5. Key sifting, error correction, and privacy amplification run in real time over a laser-communication downlink multiplexed with the quantum channel (Jinan-1).
6. For teleportation [ren2017]: the ground station performs the BSM on the input photon and one downlink photon, then sends the 2 bits to the satellite over radio; fidelity 0.80 ± 0.01 averaged over six input states.

---

## 4. Level 2-4: the quantum communication system

### 4.1 Channel physics already in the repo, with the hardware that validates it

| Equation (file) | Bench validation | Field validation |
|---|---|---|
| Fiber transmittance 10^(-αL/10) (`fiber_loss.py`) | 25 km spool on the SPDC bench with a SPAD at 810 nm (expect ~10^-1 at 2 dB/km) or at 1550 nm with an InGaAs detector | Deployed 25-35 km loops [stolk2024, knaut2024] |
| Diffraction 1/L² (`free_space_diffraction.py`) | Rooftop-to-rooftop link across campus with a 405/810 nm pair and 50 mm optics | Micius and Jinan-1 link budgets [yin2017, li2025jinan] |
| Blackbody background (`thermal_background.py`) | Count rate vs. filter bandwidth and field-of-view on the bench under room lights | Daylight QKD experiments (Phase 3 literature task) |
| Light-time delay d/c (`light_time_delay.py`) | Deliberately delay the herald in software or fiber and watch fidelity vs. delay | DSN round-trip time to Mars missions |
| BB84 threshold 11% (`key_rate.py`) | Rotate the analyzer to inject a known QBER and watch the key rate hit zero | Jinan-1 pass statistics (open data on Zenodo, DOI 10.5281/zenodo.14732295) |
| PLOB bound (`plob_bound.py`) | Compare measured pairs per pump photon with the bound at the measured loss | Twin-field QKD beats it over 833 km [wang2022tf] |

### 4.2 Repeater and memory literature the Phase 4 stubs must cite

- Repeater concept and nested purification [briegel1998]; DLCZ atomic-ensemble scheme [duan2001]; the modern review with the three repeater generations [azuma2023].
- Memory platforms ranked by demonstrated lifetime: Eu:YSO nuclear spins 13.1 h [wang2025memory]; Eu:YSO 6 h [zhong2015]; one-hour optical storage [ma2021]; trapped-ion single qubit > 1 h [wang2021ion]; NV C-13 registers, minutes [bradley2019]; SiV nuclear spin, seconds [knaut2024]; germanium-vacancy nuclear spin 2.5 s with an 18 s projection [pieplow2025].
- Memory-enhanced communication, the first experimental proof that a memory node beats direct transmission [bhaskar2020].
- The single-satellite time-delayed repeater, where a memory on the satellite carries entanglement around the orbit; this is the closest published analogue to a Mars relay carrying stored entanglement [gundogan2024].
- Entanglement of quantum memories over 420 km of fiber, the current fiber-distance frontier for memory-memory entanglement (arXiv 2025) [liu2025fourtwenty] **TODO: verify journal publication**.

### 4.3 Space segment literature for Phase 5

- Micius overview and entanglement-based QKD [yin2017, yin2020]; microsatellite constellation economics [li2025jinan].
- NASA Deep Space Quantum Link (DSQL): the only published mission concept for quantum optical links at lunar and beyond-lunar baselines, including long-range teleportation and gravitational tests; 2025 status update [mohageg2022, mohageg2025]. These two papers are the best external justification for the interplanetary CONOPS in the thesis.
- Europe's Eagle-1 prototype for the European Quantum Communication Infrastructure (EuroQCI) was planned for launch in early 2026 (mentioned in [lc2025]); check status before citing.

---

## 5. What a student lab can build: three budget tiers

Approximate costs are for planning only; obtain quotes. All links were live on 2026-09-16.

### Tier 0 — under $500, one weekend each

| Build | Physics | Parts and links | Repo hook |
|---|---|---|---|
| **Uncut Gem NV magnetometer** | ODMR, Zeeman splitting, spin-1 ground state, room-temperature qubit readout | https://github.com/QuantumVillage/UncutGem (PCB files, firmware, build guide); diamond from https://www.adamasnano.com/fluorescent-diamonds | `noise/thermal.py` T1 vs. laser power, temperature |
| **Stegemann cube ODMR** | Same, but fully modular optics; magnetic bias on a screw | https://doi.org/10.1088/1361-6404/acbe7c and the 2025 microcontroller version https://doi.org/10.1140/epjqt/s40507-025-00326-5 | Same |
| **EntropyLoop phase-diffusion QRNG** (~$35, open source, from the same group) | Vacuum/phase noise as an entropy source; feeds the owner's FPGA encryption board | https://github.com/QuantumVillage (EntropyLoop repository) | `app/hybrid_kem.py` key material; `hardware/` QRNG adapter |
| **Fiber-delay light-time emulator** | d/c as a physical, not simulated, delay | 1 km fiber spool (≈5 µs) or a software queue in `light_time_delay.py` | `REQ-PHY-001` |

### Tier 1 — $5k to $15k, one semester

| Build | Physics | Parts and links |
|---|---|---|
| **Two-crystal SPDC Bell test** (Dehlinger-Mitchell design) | Polarization entanglement, CHSH S ≈ 2.3-2.7, BB84 on the same bench | Instructions: https://doi.org/10.1119/1.1498860 (physics) and https://arxiv.org/abs/quant-ph/0205172 (apparatus); crystals from Thorlabs or Newlight (links in section 2.3); two Excelitas SPCM-AQRH or Hamamatsu C13001-01 modules; coincidence counter per [masters2018] |
| **Pulsed NV coherent control** (Sewani design) | Rabi, Ramsey, Hahn echo, T2 vs. temperature and field | Parts list in https://arxiv.org/abs/2004.02643 ; ADF4351 or a used signal generator; FPGA pulse generator |
| **Rooftop free-space link** | Diffraction, pointing jitter, daylight background | Reuse the SPDC source, add 50 mm beam expanders and a 810 nm 3 nm bandpass filter |

### Tier 2 — $20k to $60k, turnkey

| Build | Link |
|---|---|
| Thorlabs EDU-QOP1 + EDU-QOPA1 (Bell test with compensation crystals, single-photon interference, quantum eraser) | https://www.thorlabs.com/quantum-optics-educational-kits |
| qutools quEDU with ED (entanglement) and NV boards, time tagger included | https://qutools.com/quantum-physics-education-science-kits/ |

### Tier 3 — research collaboration, not purchase

Single-NV confocal nodes at 4 K, SiV nanocavities, Eu:YSO memories in dilution refrigerators. The CSUDH route is a collaboration or summer program; the USEQIP summer school at the University of Waterloo runs pulsed-NV coherent-control labs for undergraduates [useqip2026]. The traceability rows `REQ-THM-003`, `REQ-NET-001`, and `REQ-CAP-001` can be verified in simulation first and by collaboration second.

---

## 6. Experiments that have not been done: proposals that move the CONOPS forward

Each proposal states the gap, the cheapest version, the research version, and the traceability row it would verify. None of these violates the three rules.

### E1. Teleportation with a deliberately delayed classical channel equal to a planetary light-time

- **Gap.** Every teleportation experiment to date closes the classical channel in microseconds to milliseconds. No one has held the pre-shared entangled state in a memory for 3-22 minutes (Earth-Mars one-way) and then completed teleportation after the bits arrive. [hermans2022] stored for milliseconds; [knaut2024] stored for seconds.
- **Cheapest version (Tier 1).** Photonic: store the 2 bits, not the qubit. Run the SPDC Bell test with the herald delayed by a fiber spool or a software queue and show that the conditional correlations are identical at any delay (a direct classroom demonstration of the no-communication theorem plus the 2-bit cost).
- **Research version.** Eu:YSO or NV-C13 memory holding one half of an entangled pair for the full light-time, with the BSM bits transferred over a link that is throttled to the DSN round-trip time. Fidelity vs. storage time is the deliverable; the crossover with 2/3 is the number the thesis needs.
- **Verifies.** `REQ-CAP-001` (memory time vs. light delay), `REQ-PHY-002`.

### E2. Memory coherence vs. temperature, benchmarked against light-time, as a trade study with data

- **Gap.** The literature reports T2 per platform at one temperature each; nobody has published a single normalized plot of coherence time vs. temperature vs. required storage time for a given baseline (LEO, GEO, lunar, Mars conjunction, Mars opposition).
- **Cheapest version (Tier 0-1).** NV ensemble T1 and T2 from 77 K (liquid nitrogen dewar, cheap) to 350 K using the Sewani setup; plot against `thermal_t1()` from `noise/thermal.py`.
- **Verifies.** `REQ-THM-003`, risk `R-1`, `R-2`.

### E3. Constellation scheduling validated against real pass data

- **Gap.** Jinan-1 published per-pass key yields for 20 orbits (Zenodo DOI 10.5281/zenodo.14732295). No published work has fed those yields into a relay-constellation scheduler for a Mars link with solar-conjunction outages.
- **Cheapest version.** Pure software: `network/relay_constellation.py` + SeQUeNCe, with the Jinan-1 numbers as the per-pass distribution and JPL Horizons ephemerides for Earth-Mars range.
- **Verifies.** `REQ-NET-001`, trade study "relay placement".

### E4. Daylight background at Mars-like solar elongation

- **Gap.** Daylight QKD has been shown on Earth at 1550 nm; nobody has measured the blackbody-plus-scattered background for a receiver pointed within a few degrees of the Sun, which is the geometry near conjunction.
- **Cheapest version.** Rooftop link with the receiver pointed at a controlled sun-angle, count rate vs. filter bandwidth and field of view; fit to `background_count_rate()` and fix the "TODO: verify prefactor".
- **Verifies.** `thermal_background.py` derivation (open item 3 in the handoff).

### E5. Fail-closed messaging under 20-minute latency with a quantum-derived key hierarchy

- **Gap.** Post-quantum key encapsulation (ML-KEM, FIPS 203) plus QKD has been demonstrated on terrestrial networks. No one has tested key-exhaustion behavior and rekey scheduling for an application whose acknowledgments take 6-45 minutes.
- **Cheapest version.** Pure software on the owner's messenger (`app/messenger.py`): QRNG-seeded keys from EntropyLoop or the owner's FPGA board, ML-KEM from kyber-py, AES-GCM from `cryptography`, all traffic routed through `light_time_delay.py`. Measure the key-buffer size needed so that a conversation never blocks.
- **Verifies.** `REQ-APP-001`.

### E6. QRNG-selected measurement bases on a sub-$500 NV bench

- **Gap.** Random basis choice from a quantum source has been done in the large Bell tests, never on a teaching-lab NV or SPDC bench. It ties the owner's QRNG PCB directly into the quantum-optics build.
- **Cheapest version.** EntropyLoop or the owner's diode-noise board selects wave-plate angles or ODMR microwave phases in real time; compare S against a pseudo-random baseline.
- **Verifies.** `REQ-QKD-001` in hardware.

### E7. Transduction-free hybrid: photonic qubits everywhere, spins only as memory

- **Gap.** [lauk2020] frames microwave-to-optical transduction as the bottleneck. A link that never puts a qubit in the microwave domain (SPDC photons for transport, Eu:YSO absorptive memory for storage) sidesteps it. Absorptive-memory entanglement was shown in 2021 [liu2021absorptive]; nobody has combined it with a minutes-long ZEFOZ storage in a link-level demonstration.
- **Cheapest version.** Simulation in `network/memory_decoherence.py` using published storage efficiencies.
- **Verifies.** trade study "memory vs. T", `R-2`.

---

## 7. Learning resources (English)

- Nielsen and Chuang, chapters 1, 8, and 12 [nielsen2010].
- Doherty et al., NV center review [doherty2013].
- Azuma et al., repeater review [azuma2023].
- Wehner, Elkouss, and Hanson, quantum-internet roadmap [wehner2018].
- Sewani et al., NV teaching lab, with parts list [sewani2020].
- Dehlinger and Mitchell, SPDC Bell test, two companion papers [dehlinger2002a, dehlinger2002b].
- Reed College "Modern Undergraduate Quantum Mechanics Experiments" (M. Beck): https://people.reed.edu/~beckm/QM/
- Quantum Village build guides and talks: https://quantumvillage.org/projects.html
- Mohageg et al., DSQL mission concept and 2025 update [mohageg2022, mohageg2025].

---

## 8. Open items created by this document

1. Verify every **TODO** DOI in `references_additions.bib` before Phase 2 code cites it.
2. Add `REQ-CAP-002` (E1: teleportation completes after a delayed classical channel) and `REQ-CHN-003` (E4: background prefactor validated) to `systems/traceability_matrix.csv` with `test_path` TBD.
3. Decide which Tier 0 build (Uncut Gem vs. Stegemann cubes) the owner will actually assemble; both need a fluorescent microdiamond order.
4. Request quotes: Excelitas SPCM-AQRH (via DigiKey), Hamamatsu C13001-01, Adámas microdiamond, Thorlabs EDU-QOP1/QOPA1, qutools quEDU.
