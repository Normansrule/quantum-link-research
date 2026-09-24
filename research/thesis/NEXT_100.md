# Next 100

Grouped by door. Each is one file, one module, one figure, one experiment, or one bench task. Cross-reference BACKLOG.md for the code and bench items already scheduled; this list is the *content* roadmap.

## learn/ — foundations and computing (1–30)
1. Time evolution operators and the Heisenberg picture
2. The harmonic oscillator in full: coherent-state dynamics, displacement, squeezing operators
3. Angular momentum coupling tables (Clebsch–Gordan) with the NV/¹³C example worked
4. Hydrogen fine and hyperfine structure; why ¹⁷¹Yb⁺ and ⁸⁷Rb are chosen
5. Symmetries and conservation laws (Noether, parity, time reversal) and their use in selection rules
6. Scattering theory basics: cross sections, why photons scatter off atoms (the readout mechanism)
7. Path integrals in one page and why they matter for interference (link to the Veritasium video)
8. Second quantization worked examples: Hubbard model, Jaynes–Cummings ladder
9. Bell inequalities beyond CHSH: CH, Eberhard, Mermin–GHZ, and steering
10. Entanglement measures for mixed states: negativity, PPT criterion, entanglement witnesses
11. Quantum channels catalogue: 12 named channels with Kraus operators and figures
12. Master equations beyond Lindblad: Bloch–Redfield, non-Markovian baths, 1/f noise
13. Quantum thermodynamics: Landauer, Maxwell's demon, thermal machines with qubits
14. Gate decompositions: Solovay–Kitaev, KAK, two-qubit gate synthesis
15. Measurement-based quantum computing and cluster states
16. Adiabatic gates and optimal control (GRAPE, CRAB) with a worked pulse
17. Quantum Fourier transform derived and drawn; phase estimation circuit walk-through
18. Hamiltonian simulation resource counts with a small worked molecule (H₂)
19. Stabilizer formalism tutorial with Stim examples (5-qubit code, Steane, surface)
20. Decoders: MWPM, union-find, belief propagation, neural; PyMatching demo
21. Magic-state distillation and the T-count economy
22. qLDPC codes explained (bivariate bicycle, gross code) with a figure
23. Bosonic codes: cat, binomial, GKP with Wigner-function figures
24. Randomized benchmarking notebook: simulate, fit, extract error per Clifford
25. Quantum volume and other holistic benchmarks; why they mislead
26. Noise spectroscopy: dynamical decoupling as a filter function
27. Quantum machine learning: what is real, what dequantizes
28. Quantum random walks and their algorithms
29. Complexity: QMA, BQP vs NP, the PH separation, sampling hardness, in one narrative
30. A math appendix on group theory for physicists (SU(2), SO(3), Pauli/Clifford groups)

## learn/ — modalities and engineering (31–50)
31. Fluxonium in depth: circuit, spectrum, why it may replace the transmon
32. Tunable couplers and the CZ gate on Google-class hardware, with a pulse figure
33. Cross-resonance gate (IBM) derivation
34. Readout physics: dispersive shift derivation, JPA/TWPA, single-shot fidelity budget
35. Silicon spin: valley physics, micromagnets, gate-based reflectometry readout
36. Hole spins in germanium and why they are fast
37. Donor qubits (Kane) and the flip-flop qubit
38. NV: charge-state dynamics (NV⁻/NV⁰) and why resonant excitation needs charge control
39. SiV/GeV/SnV comparison table with strain, temperature, and cavity requirements
40. Nanophotonic cavities: Purcell factor, cooperativity, a worked design
41. Trapped-ion gate zoo: Cirac–Zoller, Mølmer–Sørensen, light-shift, Raman vs quadrupole
42. QCCD architecture and ion shuttling; photonic interconnects between traps
43. Rydberg gates in detail: blockade, Levine–Pichler gate, erasure conversion
44. Optical tweezer arrays: SLM vs AOD, loading, rearrangement algorithms
45. Photonic qubits: quantum-dot single-photon sources, indistinguishability, brightness
46. Integrated photonics for quantum: waveguide loss, thin-film lithium niobate modulators
47. Superconducting nanowire single-photon detectors (SNSPD): physics, efficiency, jitter, timing
48. Frequency conversion (NV→telecom): efficiency, noise, PPLN design
49. Cryogenic wiring budget: heat load per line, attenuation, filtering, a worked 100-qubit budget
50. Radiation effects on qubits (cosmic rays, TID) with implications for spaceflight

## learn/ — communication (51–65)
51. ~~Security proofs 101~~ done in 0.13.1
52. ~~Post-processing walkthrough with code~~ done in 0.13.1
~~53. Side-channel attacks catalogue (blinding, Trojan horse, time-shift) and countermeasures~~ done in 0.20.0
54. Twin-field QKD derivation of the √η scaling
55. CV-QKD Gaussian modulation rate derivation with a figure
56. ~~Entanglement purification with recurrence plots~~ done in 0.18.0–0.19.0 (BBPSSW and DEJMPS; hashing remains)
57. ~~Repeater generations compared quantitatively~~ done in 0.18.0
58. Atomic-frequency-comb memories: how AFC storage works, multimode capacity
59. Rare-earth ZEFOZ and dynamical decoupling: how 13 hours is reached, and the efficiency price
60. Free-space link budget worked example: Micius numbers reproduced line by line
~~61. Atmospheric turbulence: Fried parameter, scintillation, adaptive optics for quantum links~~ done in 0.20.0
62. Clock synchronization for networks: GPS-disciplined, White Rabbit, optical two-way time transfer
63. Deep-space optical communication: DSOC, PPM coding, photon-starved links (classical half)
~~64. Relativistic effects on photons over interplanetary baselines (redshift, Doppler, Shapiro)~~ done in 0.20.0
~~65. Standards and roadmaps: ETSI QKD, IETF QIRG, EuroQCI, NIST PQC timelines~~ done in 0.20.0

## experiments/ — protocols and recreations (66–80)
66. P05: Single-photon anticorrelation (Grangier) on the SPDC bench
67. P06: Quantum eraser and delayed choice on the SPDC bench
68. P07: BB84 over a 1 km fiber spool with the SPDC source and the QRNG board
69. P08: Time-bin encoding and a fiber interferometer (the format satellites and NV links use)
70. P09: NV T₁ vs temperature with a liquid-nitrogen dewar (E2, full procedure)
71. P10: NV ensemble magnetometry sensitivity measurement and Allan deviation
72. P11: ODMR with the four NV orientations and vector magnetometry
73. P12: Software recreation of the surface code (Stim + PyMatching) with Λ extraction
74. P13: Software recreation of a three-node repeater with SeQUeNCe
75. P14: Lindblad simulation of thermal T₁ in QuTiP and comparison with `thermal.py`
76. done/11: Aspect 1982 in full detail with the switching scheme
77. done/12: Furusawa 1998 unconditional CV teleportation
78. done/13: Bhaskar 2020 memory-enhanced communication
79. done/14: Jinan-1 2025 microsatellite QKD, step by step
80. done/15: Bluvstein 2024 logical atom processor

## experiments/ — proposals and lessons (81–88)
81. E11: Delegated (blind) computation under 20-minute latency, batched rounds
82. E12: Erasure-conversion-aware repeater with neutral-atom nodes
83. E13: Frequency-multiplexed heralding on the SPDC bench with fiber Bragg gratings
84. E14: Relativistic timing test with two GPS-disciplined nodes and a fiber link (Sagnac/redshift-scale sanity)
85. E15: Radiation-hardness screening of NV and SPDC components (gamma source at a university facility)
86. lessons/03: History of over-optimistic timelines (1990s "10 years away")
87. lessons/04: Reproducibility checklist for quantum experiments (data, code, calibration logs)
88. lessons/05: Case study of the QKD hacking–countermeasure cycle

## research/ — theories and process (89–95)
89. T11: Quantum advantage in communication complexity (fingerprinting) — what a Mars link could compute with fewer bits
90. T12: Quantum position verification and its relevance to spacecraft authentication
91. T13: Quantum-secured time transfer and clock networks for navigation
92. T14: Error-corrected quantum memories in space (surface-code memories vs rare-earth)
93. T15: Machine-learning decoders and calibration for remote hardware with high latency
94. thesis/ THESIS_OUTLINE.md: chapter map with pointers to files and figures
95. thesis/ VERIFICATION_PLAN.md: which requirement is verified by which test, bench, or literature value

## visuals and apps (96–100)
96. Interactive Bloch-sphere gate explorer in the browser app
97. Surface-code lattice animation (syndromes lighting up) in the browser app
98. Repeater-chain rate explorer with sliders for p, q, T₂, and distance
99. Earth–Mars orbit and light-time animation with ephemeris data
100. Modality comparison radar chart generated from a data file (so it updates with the table)
