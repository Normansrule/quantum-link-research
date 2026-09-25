# Quantum-Dot Sources and Integrated Photonics

## Deterministic single photons
Spontaneous parametric down-conversion is probabilistic: a bright source of pairs is a source of multi-pairs (`SpdcSource.heralded_g2` ≈ 2x). A semiconductor quantum dot (InAs in GaAs) is a two-level emitter that gives one photon per excitation pulse: $g^{(2)}(0)<0.01$, indistinguishability above 99 % under resonant excitation, and, in a micropillar or open cavity, collection efficiencies above 50 % into a fibre at repetition rates of hundreds of MHz [somaschi2016] [tomm2021]. Their photons sit at 900–950 nm; telecom-band dots and frequency conversion bring them to 1550 nm. For a network they are a *source*, not a memory: the electron spin in the dot decoheres in microseconds, so the dot's role is to feed photons into linear-optics repeaters (T02) or to herald entanglement between memories elsewhere.

## Integrated photonics
Silicon and silicon-nitride waveguides carry photons with 0.1–1 dB/cm loss; thin-film lithium niobate adds electro-optic modulators at tens of GHz with volts of drive [zhu2021]; superconducting nanowire detectors are integrated on the same chips. A boson-sampling processor with 216 squeezed modes ran on a programmable photonic chip in 2022 [madsen2022]. For the link, the relevant integrated pieces are the transmitter (modulators, phase stabilization for twin-field or time-bin encoding), the Bell-state analyser (a 4-mode interferometer with detectors, exactly the circuit Perceval evaluates in `qll/hardware/perceval_adapter.py`), and the frequency-conversion waveguide (`qll/channels/frequency_conversion.py`). Loss per component is the number to track: a 1 dB component in a repeaterless link is 20 % of the key; in a twin-field link it is 10 %.

## Key papers
- Somaschi, N., et al. (2016). Near-optimal single-photon sources in the solid state. *Nature Photonics*, 10, 340. https://doi.org/10.1038/nphoton.2016.23
- Tomm, N., et al. (2021). A bright and fast source of coherent single photons. *Nature Nanotechnology*, 16, 399. https://doi.org/10.1038/s41565-020-00831-x
- Zhu, D., et al. (2021). Integrated photonics on thin-film lithium niobate. *Advances in Optics and Photonics*, 13, 242. https://doi.org/10.1364/AOP.411024
- Madsen, L. S., et al. (2022). *Nature*, 606, 75. https://doi.org/10.1038/s41586-022-04725-x
- Wang, J., Sciarrino, F., Laing, A., & Thompson, M. G. (2020). Integrated photonic quantum technologies. *Nature Photonics*, 14, 273. https://doi.org/10.1038/s41566-019-0532-1

## In this repo
`qll/hardware/photon_source.py`, `beam_splitter.py`, `perceval_adapter.py`; `learn/02/06`; T02.
