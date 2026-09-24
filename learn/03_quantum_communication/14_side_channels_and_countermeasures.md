# Side Channels and Countermeasures

A security proof covers the model; the hardware is not the model. Every entry below is a published attack on a deployed or prototype QKD system, with the assumption it broke and the countermeasure that closed it [lydersen2010] [jain2016] [xu2020].

| Attack | Assumption broken | Mechanism | Countermeasure |
|---|---|---|---|
| Photon-number splitting | single photons | keep one photon of a multi-photon pulse, forward the rest | decoy states [lo2005] |
| Detector blinding (bright illumination) | detectors respond only to single photons | drive avalanche photodiodes into linear mode and control their clicks with classical pulses | measurement-device-independent QKD [lo2012]; watchdog detectors; randomized efficiency |
| Time-shift / efficiency mismatch | equal detector efficiencies | shift arrival times so one detector sees the photon | four-state readout with random assignment; MDI |
| Trojan-horse (back-reflection) | no light leaves the sender's box | probe the modulator with bright light and read the reflection | isolators, filters, monitoring photodiode |
| Wavelength-dependent beam splitter | basis choice is passive and wavelength-blind | send an off-wavelength photon to force a basis | narrow filters |
| Laser seeding / damage | source spectrum and power as specified | inject light into the laser to change it, or damage attenuators with high power | optical isolation, power limiters, integrity monitoring |
| Dead-time and afterpulsing | detector clicks are independent | exploit blocked or delayed clicks | careful gating, characterization |
| Side-channel from the classical channel | authenticated and correct implementation | timing, power, or software bugs in post-processing | audited code; constant-time implementations |

## The two structural answers
Measurement-device-independence removes every detector attack by construction; device-independence removes every attack on the physical model at the price of a loophole-free Bell test and a low rate (E10 in this repository computes what that costs at Mars). Neither removes attacks on the classical layer or on the random numbers, which is why `qll` insists on a declared entropy source (INV-7) and authenticates every message.

## Key papers
- Lydersen, L., et al. (2010). Hacking commercial quantum cryptography systems by tailored bright illumination. *Nature Photonics*, 4, 686. https://doi.org/10.1038/nphoton.2010.214
- Jain, N., et al. (2016). Attacks on practical quantum key distribution systems (and how to prevent them). *Contemporary Physics*, 57, 366. https://doi.org/10.1080/00107514.2016.1148333
- Xu, F., Ma, X., Zhang, Q., Lo, H.-K., & Pan, J.-W. (2020). Secure quantum key distribution with realistic devices. *Reviews of Modern Physics*, 92, 025002. https://doi.org/10.1103/RevModPhys.92.025002
- Lo, H.-K., Curty, M., & Qi, B. (2012). Measurement-device-independent quantum key distribution. *Physical Review Letters*, 108, 130503. https://doi.org/10.1103/PhysRevLett.108.130503

## In this repo
`qll/qkd/{decoy_state,mdi,e91}.py`; `experiments/lessons/01_contested_claims.md`; risk R-5.
