# Chapter 5 — Experiments (draft)

## 5.1 Three flagship experiments

The work is organized around three experiments at three distances that share one physics (`experiments/flagship/`): F1, heralded entanglement and teleportation between two computers in one city; F2, a single-photon downlink from low Earth orbit; and F3, the Earth–Mars link. Each is staged as simulate, bench, and field, with a pass number per stage.

## 5.2 Simulations performed

Seven simulations (`simulations/S01–S07`) were run and are regression-tested against analytic limits:
- S01: CHSH versus depolarizing noise in Qiskit Aer; the ideal value 2√2 is reproduced to 0.03 and the violation is lost near p ≈ 0.15 per qubit.
- S02: teleportation with the two classical bits delayed by a light time while a one-hour memory decays; fidelity crosses 2/3 at T₂ ln 3 ≈ 66 minutes, so the Mars maximum one-way delay of 22 minutes leaves F ≈ 0.85. The `NotYetArrived` guard is exercised in the same run.
- S03: photons per second at the receiver from a 10⁸ pairs/s source, from 1 km of fiber to Mars at maximum range.
- S04: a repetition code in Stim with majority-vote decoding, showing logical error falling with distance below threshold.
- S05: secret bits per 300-second satellite pass against background count rate, showing that daylight ends the key before it ends the signal.
- S06: device-independent key with settings and outcomes sealed for the light time (E10); the pair rate, not the delay, decides certifiability.
- S07: teleportation fidelity through a transducer versus a native optical emitter (E7); the transduction-free architecture is confirmed as baseline.

The Perceval and SeQUeNCe adapters (`tests/test_adapters.py`) add two third-party checks: the linear-optics Bell analyser succeeds exactly half the time, and no simulated memory becomes entangled before the herald round trip.

## 5.3 Bench experiments prepared

Four protocols are written to be followed line by line (`experiments/protocols/`): P01, continuous-wave optically detected magnetic resonance (ODMR) of a nitrogen-vacancy ensemble on a bench costing $100–500; P02, pulsed control (Rabi, Ramsey, Hahn echo, T₁); P03, a two-crystal spontaneous parametric down-conversion source with Hong–Ou–Mandel interference, a CHSH test, and BB84; P04, a campus free-space link measuring loss and daylight background. The analysis pipeline for P01 (`qll/analysis/odmr_fit.py`) is tested on synthetic spectra and recovers the zero-field splitting to 0.5 MHz and the field to 0.5 G. **At the time of writing no bench data exist; this section will report the first ODMR spectrum, its fitted D and B, and the comparison with 2.870 GHz corrected by −74 kHz/K to the measured temperature.**

## 5.4 Proposed experiments

Ten proposals (`experiments/proposed/E01–E10`) extend the field toward the interplanetary case; each states its gap, a cheap version, a research version, and the requirement it verifies. Six have their cheap version in this repository's code (E1, E5, E7, E8, E9, E10). Three of the remainder are within reach of a student laboratory in one semester and directly serve the thesis: E1, teleportation on the photonic bench with the classical record released only after a software delay equal to the Mars light time (a bench demonstration of the no-signaling theorem and the two-bit cost); E2, nitrogen-vacancy T₁ and T₂ from 77 K to 350 K against the thermal model, which closes REQ-THM-003; and E6, measurement bases chosen by a quantum random-number generator on the same bench, which closes the freedom-of-choice loophole at teaching-lab scale.
