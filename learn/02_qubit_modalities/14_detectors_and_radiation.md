# Single-Photon Detectors and Radiation Effects

## Detectors
| Detector | η | Dark counts | Jitter | Dead time | Temperature | Wavelength |
|---|---|---|---|---|---|---|
| Si single-photon avalanche diode (SPAD) | 0.5–0.7 | 25–250 /s | 350 ps | 20–50 ns | thermoelectric | 400–900 nm |
| InGaAs SPAD (gated) | 0.2–0.3 | 10³ /s | 200 ps | ~1 µs | 220–250 K | 1000–1700 nm |
| Superconducting nanowire (SNSPD) | > 0.9 | < 10 /s | 15–50 ps | 20–50 ns | 1–4 K | 400–2000 nm |
| Transition-edge sensor (TES) | > 0.95, number-resolving | ~0 | µs | µs | 100 mK | broad |

An SNSPD is a current-biased superconducting wire ~100 nm wide; one absorbed photon creates a resistive hotspot that produces a voltage pulse [gol'tsman2001] [esmaeil2021]. Its combination of efficiency, dark rate, and timing makes it the receiver for every deep-space photon-counting link (DSOC used SNSPD arrays at Palomar) and every satellite QKD ground station that can afford a cryostat. The click model in `qll/hardware/detector.py` carries the four parameters; a detector's timing jitter sets the shortest useful coincidence window, which is why P03's Bell test uses SPADs with ns gates and a future ground station needs SNSPDs.

## Radiation
A quantum payload in orbit or in deep space sits in a radiation environment that a laboratory never sees. Three effects matter:
- **Total ionizing dose (TID)** degrades detectors (dark counts rise in SPADs: Micius had to cool and anneal them) and optics (browning of glass) [tan2013] [yang2019].
- **Displacement damage** creates traps in semiconductor detectors and sources, raising dark counts permanently.
- **Single-event effects** flip bits in control electronics; cosmic-ray showers also cause correlated errors in superconducting qubits on the ground (a ground-level problem for processors) [mcewen2022].
Diamond and rare-earth crystals are radiation hard; the weak points are the detectors and the electronics, which are the parts already flown on Micius and Jinan-1 with mitigation (shielding, cooling, annealing). Proposal E15 in NEXT_100 would screen the P01 diamond and the SPDC crystal at a university gamma source.

## Key papers
- Gol'tsman, G. N., et al. (2001). Picosecond superconducting single-photon optical detector. *Applied Physics Letters*, 79, 705. https://doi.org/10.1063/1.1388868
- Esmaeil Zadeh, I., et al. (2021). Superconducting nanowire single-photon detectors: a perspective on evolution, state-of-the-art, future developments, and applications. *Applied Physics Letters*, 118, 190502. https://doi.org/10.1063/5.0045990
- Hadfield, R. H. (2009). Single-photon detectors for optical quantum information applications. *Nature Photonics*, 3, 696. https://doi.org/10.1038/nphoton.2009.230
- Tan, Y. C., Chandrasekara, R., Cheng, C., & Ling, A. (2013). Silicon avalanche photodiode operation and lifetime analysis for small satellites. *Optics Express*, 21, 16946. https://doi.org/10.1364/OE.21.016946
- McEwen, M., et al. (2022). Resolving catastrophic error bursts from cosmic rays in large arrays of superconducting qubits. *Nature Physics*, 18, 107. https://doi.org/10.1038/s41567-021-01432-8

## In this repo
`qll/hardware/detector.py`; `learn/02/09`; F2 stage S3 (ground-station detector choice); NEXT_100 #50, #47.
