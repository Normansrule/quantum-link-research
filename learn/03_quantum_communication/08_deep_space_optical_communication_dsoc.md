# Deep-space optical communication: the classical half of F3

## Why a quantum-link repo needs it
Every teleportation needs two classical bits, every herald is classical, and every reconciliation round is classical. At Mars distance those bits ride an optical link that is itself photon-starved. NASA's Deep Space Optical Communications (DSOC) demonstration on the Psyche spacecraft (launched 2023) is the existence proof: laser downlinks at hundreds of Mbit/s from tens of millions of kilometres.

## Physics
- Same diffraction law as the quantum link, but the signal is a coherent laser (~4 W, 22 cm aperture on the spacecraft) and the receiver counts photons with superconducting-nanowire arrays behind a 5 m telescope (Palomar).
- Modulation: pulse-position modulation (PPM) with serially concatenated codes; photon-information efficiency of several bits per detected photon at low signal.
- Capacity: Holevo bound $C\approx\bar n\log_2(1/\bar n)$ bits per mode at low mean photon number $\bar n$; joint-detection receivers approach it ([T06](../../research/theories/T06_quantum_limited_optical_receivers.md)).
- Reported (2023–2024): 267 Mb/s at 31 million km; tens of Mb/s at 2.7 au-class ranges as Psyche receded. **TODO: verify the exact figures against the JPL reports before citing.**

## What it means for the Mars CONOPS
- The two bits per teleported qubit are cheap; the *latency* is not. Bandwidth is never the bottleneck of the quantum link; light time and memory are.
- The same terminal can carry the beacon and timing signals the quantum receiver needs (`07_clock_synchronization…`).
- Pointing: DSOC demonstrated sub-µrad pointing at deep-space range with a beacon uplink; the quantum link inherits the loop but with far fewer photons for tracking, which is open problem #5 ([research/cutting_edge/02](../../research/cutting_edge/02_open_problems.md)).

## Key references
Biswas, A., et al. NASA/JPL DSOC technology demonstration reports (2023–2025). **TODO: add the definitive citation.** Hemmati, H. (Ed.). (2006). *Deep Space Optical Communications*. Wiley/JPL. Dolinar, S., Moision, B., & Erkmen, B. (2012). Fundamentals of free-space optical communications. *Proc. SPIE* / JPL. Guha, S. (2011). *PRL*, 106, 240502. https://doi.org/10.1103/PhysRevLett.106.240502

## In this repo
Phase 5 `qll/space/classical_link.py` (planned): photons per bit vs range; feeds `light_time_delay` with bandwidth.
