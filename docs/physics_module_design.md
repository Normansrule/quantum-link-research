# quantum-link-research: Physics-First Modular Design Specification

Version 0.1 · 2026-09-16 · lives at `docs/physics_module_design.md`
Companion bib: `docs/references_additions_2.bib` (new keys introduced here). Earlier keys are in `references.bib` and `references_additions.bib`.

## How to read this document

Every file in the repository is one **module card**. A card has seven fields, and a file is not allowed to exist without all seven:

```
IDEA        one sentence naming the single physical idea the file owns
EQUATIONS   the governing formula(s), with symbols defined
INTERFACE   the public functions, typed; nothing else is public
INVARIANTS  what the file asserts at runtime (guards) and what it refuses to do
REFERENCES  [bibkeys]; every default number traces to one
TEST        the analytic result pytest checks; the file is unverified until this passes
DEPENDS ON  the only modules it may import from within qll
```

Rule 5 of CONTRIBUTING.md ("one physical idea per file") is enforced by the card: if a card would need two IDEA lines, split the file. Rule 3 is enforced by the REFERENCES line. Rule 4 by the TEST line.

Modules are grouped into packages by **level of the physical stack**, and the import graph is a directed acyclic graph (DAG) that follows the physics: a channel may import constants, a circuit may import a channel (for latency), a network may import circuits and channels, an application may import everything below it, and nothing imports upward. `qll/systems/traceability.py` will grow a `check_import_dag()` that fails CI on any upward import.

```
constants ──► channels ──► circuits ──► qkd ──► network ──► space ──► app
                  ▲            ▲                    ▲
                  └── hardware ┘                    │
                       (photon sources, detectors)  │
systems ◄───────────────────────────────────────────┘  (reads everything, imported by nothing)
```

Symbols used throughout: ħ (reduced Planck constant), k_B (Boltzmann constant), c (speed of light), ω (angular frequency), ν (frequency), λ (wavelength), T (temperature), η (transmittance or efficiency), Q (quantum bit error rate, QBER), F (fidelity), S (CHSH value), n̄ (thermal mean occupation).

---

## 0. Global invariants (enforced across all modules)

| ID | Invariant | Physics | Enforcement |
|---|---|---|---|
| INV-1 | No classical information leaves any function faster than d/c. | No-communication theorem [ghirardi1980, peres2004]. | The only latency source is `channels/light_time_delay.py`; every function that returns "classical bits" returns them wrapped in a `ClassicalMessage(bits, earliest_arrival_s)` record. |
| INV-2 | No function returns two copies of an unknown input state. | No-cloning [wootters1982, dieks1982]. | `tests/test_phase2_no_cloning.py` reflects on every public callable in `qll.circuits`. |
| INV-3 | Teleporting one qubit consumes exactly one Bell pair and exactly 2 classical bits. | [bennett1993]. | `TeleportationRecord.classical_bits` has length 2; a resource counter asserts one pair consumed. |
| INV-4 | Every completely positive trace-preserving (CPTP) map satisfies ΣE_k†E_k = I to 1e-12. | Kraus representation [nielsen2010, kraus1983]. | `noise/_kraus_base.py` checks on construction. |
| INV-5 | Every rate is bounded above by its capacity bound where one exists. | PLOB bound [pirandola2017]; Holevo bound [holevo1973]. | `qkd/key_rate.py` asserts rate ≤ PLOB at the same η. |
| INV-6 | Temperature is a required argument wherever an occupation number enters; no hidden T = 0. | Bose-Einstein statistics [clerk2010]. | Function signatures take `T_kelvin` with no default. |
| INV-7 | Randomness for basis choice comes from a declared source object, never from an implicit global RNG. | Bell-test freedom-of-choice loophole [brunner2014, bigbell2018]. | `hardware/randomness.py` defines the `EntropySource` protocol; QRNG board plugs in here. |

---

## 1. `qll/constants/` — exact numbers, nothing computed

### `physical.py`
- IDEA: The 2019 SI defining constants used everywhere.
- EQUATIONS: c = 299 792 458 m/s; h = 6.626 070 15e-34 J s; k_B = 1.380 649e-23 J/K; ħ = h/2π.
- INTERFACE: module-level floats only.
- INVARIANTS: values are exact by definition; tests compare with `==`.
- REFERENCES: [codata2018] (**TODO: verify DOI**), [bipm2019] (SI Brochure 9th ed.).
- TEST: `C_LIGHT == 299792458.0`.
- DEPENDS ON: nothing.

### `astro.py`
- IDEA: Solar-system distances as envelope values, replaced by an ephemeris in Phase 5.
- EQUATIONS: 1 au = 149 597 870 700 m (exact). Earth-Mars range ∈ [0.372, 2.68] au.
- INTERFACE: floats; `earth_mars_envelope_m() -> tuple[float, float]`.
- REFERENCES: [iau2012]; Earth-Mars extrema "TODO: verify vs JPL Horizons".
- TEST: 1 au / c = 499.005 s ± 0.001.
- DEPENDS ON: `physical`.

### `optical.py` (new, Phase 3)
- IDEA: Named carrier wavelengths and their photon energies.
- EQUATIONS: E = hc/λ; ν = c/λ. Table: NV zero-phonon line 637 nm; SiV 737 nm; SPDC degenerate 810 nm; telecom O-band 1310 nm, C-band 1550 nm; frequency-converted NV 1588 nm [tchebotareva2019]; Jinan-1 850 nm [li2025jinan].
- TEST: E(1550 nm) = 0.800 eV ± 0.001.

---

## 2. `qll/channels/` — where photons lose, spread, delay, and pick up noise

### `fiber_loss.py`
- IDEA: Exponential attenuation in glass.
- EQUATIONS: η(L) = 10^(−αL/10); L_att = 10/(α ln 10). α defaults: 0.2 dB/km at 1550 nm, 0.35 at 1310 nm, ~2 dB/km at 810 nm, ~8 dB/km at 637 nm [agrawal2010, pirandola2017].
- INTERFACE: `transmittance(L_km, alpha_db_per_km) -> float`; `attenuation_length_km(alpha) -> float`.
- INVARIANTS: 0 ≤ η ≤ 1; α > 0.
- TEST: 100 km at 0.2 dB/km → 0.01; L_att ≈ 21.7 km.
- Experiment anchor: 35 km Boston loop [knaut2024]; 25 km Delft-The Hague [stolk2024].

### `free_space_diffraction.py`
- IDEA: A Gaussian beam spreads; the receiver aperture catches a fraction.
- EQUATIONS: θ = λ/(πw₀); w(L) = w₀√(1+(L/z_R)²) with z_R = πw₀²/λ (the current linear form w = θL is the far-field limit and must be replaced); η_geo = 1 − exp(−2r_R²/w(L)²) (exact Gaussian-over-circular-aperture form; the current min(1,(D_R/2w)²) is the small-aperture limit).
- INTERFACE: `beam_radius_m(L_m, w0_m, lambda_m)`; `geometric_transmittance(L_m, w0_m, lambda_m, D_rx_m)`.
- REFERENCES: [siegman1986, bourgoin2013, liao2017].
- TEST: far field 1/L²; near field η → 1; Micius 1200 km, 300 mm transmitter, 1 m receiver gives ~10^-6 to 10^-5 total with pointing [yin2017].

### `atmosphere.py` (Phase 3)
- IDEA: Extinction and turbulence of a slant path through air.
- EQUATIONS: Beer-Lambert η_atm = exp(−∫β dz) with airmass scaling ~1/sin(elevation); Fried parameter r₀ ∝ (C_n² path integral)^(−3/5); beam wander variance ∝ C_n² L³/w₀^(1/3) [andrews2005].
- INTERFACE: `atmospheric_transmittance(elevation_deg, lambda_m, visibility_km)`; `fried_parameter_m(...)`.
- REFERENCES: [andrews2005, bourgoin2013, bedington2017].
- TEST: zenith 1550 nm clear sky ≈ 0.9; η(10°) < η(90°).

### `pointing_jitter.py` (Phase 3)
- IDEA: Pointing error is a random offset of the beam center; average η over its distribution.
- EQUATIONS: For Gaussian jitter σ_p (rad) and beam radius w at range L, η_point = w²/(w² + 4σ_p²L²) [bourgoin2013 Appendix].
- INTERFACE: `pointing_efficiency(sigma_rad, L_m, w_m)`.
- TEST: σ → 0 gives 1; Jinan-1 numbers (~1 µrad fine pointing at the satellite) give η_point > 0.9 at 500 km [li2025jinan].

### `link_budget.py` (Phase 3)
- IDEA: The whole link is a product of independent efficiencies plus additive noise.
- EQUATIONS: η_total = η_src η_geo η_atm η_point η_optics η_det; count rate R = R_pair η_total; noise rate N from `thermal_background.py`; signal-to-noise per gate SNR = R/(N τ_gate).
- INTERFACE: `LinkBudget` dataclass with `.eta_total()`, `.qber_from_background()`.
- INVARIANTS: every factor in [0,1]; QBER from background = N τ/(2(Rη + Nτ)) form [ma2007].
- TEST: reproduce the Micius 1200 km loss (~64-82 dB) and Jinan-1 per-pass key order of magnitude within a factor of 3.
- REFERENCES: [yin2017, li2025jinan, bedington2017, sidhu2021].

### `deep_space_geometry.py`
- IDEA: Ranges and relay placement between two planets.
- EQUATIONS: range envelope from `astro.py`; `split_path(total, fractions)`; later `ephemeris_range_m(t)` from a Horizons table.
- TEST: segments sum to total.
- Phase 5 replacement: [khatri2021] for space-based entanglement distribution analysis, [vergoossen2020] constellation modeling, [polnik2020] pass scheduling.

### `light_time_delay.py`
- IDEA: Classical information takes at least d/c. This is the sole latency source.
- EQUATIONS: τ₁ = d/c; τ_RT = 2d/c. Earth-Mars τ₁ ∈ [3.03, 22.3] min.
- INTERFACE: `one_way_delay_s(d_m)`; `round_trip_delay_s(d_m)`; `ClassicalMessage` dataclass `(payload: bytes|tuple[int,...], sent_at_s, distance_m)` with `.earliest_arrival_s`; `DelayQueue` that refuses `.receive(now)` before arrival.
- INVARIANTS: INV-1. `DelayQueue.receive` raises `NotYetArrived`.
- REFERENCES: [ghirardi1980, peres2004].
- TEST: 1 au → 499.005 s; receive before arrival raises.

### `thermal_background.py`
- IDEA: A warm scene at temperature T fills each spatio-temporal-polarization mode with n̄ photons.
- EQUATIONS: n̄(ν,T) = 1/(e^{hν/k_BT} − 1); number of spatial modes M = A Ω/λ²; background count rate N = n̄ · M · B · η_det · (1 polarization) where B is the filter bandwidth in Hz. **Derivation to check in Phase 3:** N = n̄ M B η_det follows from photon flux per mode = n̄ per (1/B) time [mandel1995].
- INTERFACE: `blackbody_occupation(nu_hz, T_kelvin)`; `spatial_modes(area_m2, solid_angle_sr, lambda_m)`; `background_count_rate(...)`.
- TEST: n̄(193 THz, 300 K) ≈ 4e-14; n̄(5 GHz, 300 K) ≈ 1250; M = 1 for a diffraction-limited receiver (A Ω = λ²).
- Experiment anchor: full-daylight QKD at 1550 nm [avesani2021] and sun-angle background (proposal E4).

### `frequency_conversion.py` (Phase 3, new)
- IDEA: A three-wave mixing stage moves a photon's color while preserving its quantum state, at an efficiency cost and with pump-induced noise.
- EQUATIONS: η_conv = sin²(√(η_norm P) L); noise rate from pump Raman/SPDC background; fidelity after conversion F = (R_s η_conv)/(R_s η_conv + N_conv τ).
- REFERENCES: [tchebotareva2019] (NV 637 → 1588 nm), [knaut2024] (SiV → 1350 nm), [kumar1990] (theory).
- TEST: η_conv ≤ 1; state fidelity unchanged at zero noise.

---

## 3. `qll/circuits/` — qubits, entanglement, and the protocols that use them

All state-vector and density-matrix code wraps Qiskit Aer; Clifford-only large-n circuits wrap Stim; open-system checks wrap QuTiP. No custom simulator.

### `bell.py`
- IDEA: The four maximally entangled two-qubit states.
- EQUATIONS: |Φ±⟩ = (|00⟩ ± |11⟩)/√2, |Ψ±⟩ = (|01⟩ ± |10⟩)/√2; circuit H⊗I then CNOT, with X/Z on qubit 1 to select.
- INTERFACE: `bell_circuit(kind: Literal["phi+","phi-","psi+","psi-"]) -> QuantumCircuit`; `bell_state(kind) -> Statevector`; `bell_stim(kind) -> stim.Circuit`.
- REFERENCES: [nielsen2010, einstein1935, bohm1951].
- TEST: Schmidt coefficients (1/√2, 1/√2); reduced state = I/2; concurrence 1 [wootters1998].

### `ghz.py`
- IDEA: Genuine n-party entanglement that a single measurement can destroy.
- EQUATIONS: |GHZ_n⟩ = (|0…0⟩ + |1…1⟩)/√2; Mermin operator expectation 2^{(n−1)/2} beats the local bound of 1 for odd n... (use the exact bound table in [mermin1990]).
- INTERFACE: `ghz_circuit(n)`, `ghz_stim(n)` for n up to 10^4.
- TEST: Stim sampling of n = 1000 gives all-equal bitstrings; tracing one qubit leaves a separable mixture.
- REFERENCES: [greenberger1989, mermin1990, gidney2021stim].

### `teleportation.py`
- IDEA: Move an unknown qubit with one Bell pair and two classical bits.
- EQUATIONS: |ψ⟩⊗|Φ+⟩ = ½ Σ_{ij} |β_ij⟩ ⊗ X^j Z^i |ψ⟩; F_avg = ∫⟨ψ|ρ_out|ψ⟩dψ; classical bound F = 2/3 [massar1995]; with a Werner-state resource of singlet fraction f, F = (2f+1)/3 [horodecki1996].
- INTERFACE: `teleport(state, resource: BellPair, distance_m: float | None, noise: Channel | None) -> TeleportationRecord(output_qubit, classical_bits: tuple[int,int], message: ClassicalMessage, resource_consumed: int)`; `average_fidelity(record_fn, n_states=6 or Haar)`.
- INVARIANTS: INV-1 (the output is a `Deferred` that cannot be read before `message.earliest_arrival_s`), INV-3.
- REFERENCES: [bennett1993, bouwmeester1997, pfaff2014, hermans2022, ren2017].
- TEST: ideal F = 1 to 1e-12; F(f) = (2f+1)/3 on Werner states; six-state average matches Haar average within 1e-3.

### `superdense_coding.py`
- IDEA: One Bell pair plus one transmitted qubit carries two classical bits (the dual of teleportation).
- EQUATIONS: encode by {I, X, Z, XZ}; decode by CNOT, H, measure; capacity 2 bits per qubit at most [holevo1973].
- REFERENCES: [bennett1992, mattle1996].
- TEST: all four messages decode with probability 1; capacity ≤ 2 asserted.

### `entanglement_swapping.py`
- IDEA: A Bell measurement on two halves of two pairs entangles the two remaining halves.
- EQUATIONS: |Φ+⟩₁₂|Φ+⟩₃₄ = ½ Σ_k |β_k⟩₂₃|β_k⟩₁₄; fidelity of the swapped pair F₁₄ from two Werner inputs F₁₂, F₃₄ [briegel1998 eq. 6].
- INTERFACE: `swap(pair_a, pair_b, bsm: BellMeasurement) -> SwapRecord(pair_out, herald_bits, message)`.
- REFERENCES: [zukowski1993, pan1998, pompili2021].
- TEST: ideal output is a Bell state; two Werner inputs reproduce the analytic fidelity formula.

### `bell_measurement.py` (new; split from teleportation because it is its own physical idea)
- IDEA: Projecting two qubits onto the Bell basis, deterministically (matter qubits) or probabilistically (linear optics, ≤ 50%).
- EQUATIONS: linear-optics BSM identifies |Ψ±⟩ only, success ≤ 1/2 without ancillas [calsamiglia2001]; two-photon Hong-Ou-Mandel interference visibility sets fidelity [hong1987].
- INTERFACE: `BellMeasurement(kind="deterministic"|"linear_optics", visibility=1.0)`.
- TEST: linear-optics success probability = 0.5; deterministic = 1.

### `chsh.py`
- IDEA: A correlation function that no local hidden-variable model can push above 2.
- EQUATIONS: S = |E(a,b) − E(a,b') + E(a',b) + E(a',b')| ≤ 2 (local); ≤ 2√2 (quantum, Tsirelson); optimal angles 0, π/4, π/8, 3π/8; with detection efficiency η the loophole-free threshold is η > 2/(1+√2) ≈ 0.83 [garg1987, eberhard1993].
- INTERFACE: `chsh_value(state, settings)`; `chsh_sampled_stim(n_shots, entropy: EntropySource)`.
- INVARIANTS: INV-7 (settings drawn from a declared `EntropySource`).
- REFERENCES: [bell1964, clauser1969, cirelson1980, brunner2014, hensen2015, bigbell2018].
- TEST: Aer gives 2√2 ± 1e-6; Stim estimate within 3σ of 2√2 for 10^5 shots; Werner state gives S = 2√2·(4f−1)/3.

### `fidelity.py`
- IDEA: How close two states are.
- EQUATIONS: F(ψ,ρ) = ⟨ψ|ρ|ψ⟩; Uhlmann F(ρ,σ) = (Tr√(√ρ σ √ρ))² [uhlmann1976, jozsa1994]; Fuchs-van de Graaf ½‖ρ−σ‖₁ ≤ √(1−F) ≤ ... [fuchs1999].
- TEST: F(ρ,ρ) = 1; F(|0⟩,|1⟩) = 0; F(|0⟩, I/2) = 1/2; inequality holds on 100 random pairs.

### `tomography.py`
- IDEA: Reconstruct a density matrix from Pauli-basis measurements, then enforce physicality.
- EQUATIONS: ρ = ¼ Σ_{ij} ⟨σ_i⊗σ_j⟩ σ_i⊗σ_j; maximum-likelihood projection onto positive semidefinite trace-1 matrices [james2001, smolin2012].
- TEST: 10^5 shots on |Φ+⟩ reconstruct F > 0.99; output is PSD with trace 1.

### `process_tomography.py` (Phase 2 optional)
- IDEA: Characterize a channel by its χ matrix from a spanning set of inputs.
- REFERENCES: [chuang1997].
- TEST: identity channel gives χ with a single unit entry.

### `noise/_kraus_base.py`
- IDEA: Every noise process is a list of Kraus operators; nothing else.
- INTERFACE: `KrausChannel(ops).apply(rho)`, `.to_aer()`, `.to_qutip_superop()`.
- INVARIANTS: INV-4 on construction.
- REFERENCES: [kraus1983, nielsen2010 ch. 8].

### `noise/depolarizing.py`
- IDEA: With probability p the qubit is replaced by I/2.
- EQUATIONS: ρ → (1−p)ρ + p I/2; Kraus {√(1−3p/4) I, √(p/4) X, √(p/4) Y, √(p/4) Z}. A Bell pair through two such channels becomes Werner with f = (1−p)² + ... (derive symbolically in the test).
- TEST: p = 1 gives I/2; average gate fidelity 1 − p/2 [nielsen2002].

### `noise/amplitude_damping.py`
- IDEA: Energy relaxation toward |0⟩ at rate 1/T1 (zero temperature).
- EQUATIONS: γ = 1 − e^{−t/T1}; E₀ = [[1,0],[0,√(1−γ)]], E₁ = [[0,√γ],[0,0]].
- TEST: t → ∞ gives |0⟩; QuTiP Lindblad with c = √(1/T1) σ₋ matches the Kraus map at t = T1 to 1e-6.

### `noise/phase_damping.py`
- IDEA: Loss of coherence without energy exchange at rate 1/T_φ, with 1/T2 = 1/(2T1) + 1/T_φ.
- EQUATIONS: λ = 1 − e^{−t/T_φ}; E₀ = [[1,0],[0,√(1−λ)]], E₁ = [[0,0],[0,√λ]] (equivalently a Z-flip with probability (1−e^{−t/T_φ})/2).
- TEST: T2 ≤ 2T1 asserted; off-diagonal decays as e^{−t/T2}.
- REFERENCES: [nielsen2010, krantz2019].

### `noise/thermal.py` (exists)
- IDEA: A bath at temperature T sets both the relaxation rate and the equilibrium excited-state population.
- EQUATIONS: n̄ = 1/(e^{ħω/k_BT} − 1); T1(T) = T1(0)/(2n̄+1); p_exc = n̄/(2n̄+1); generalized amplitude damping with p_ground = (n̄+1)/(2n̄+1).
- REFERENCES: [clerk2010, krantz2019, nielsen2010 §8.3.5].
- TEST: as in Phase 1.

### `noise/spin_bath.py` (Phase 4, new)
- IDEA: Decoherence of an NV electron spin from the surrounding nuclear/paramagnetic spin bath, and its suppression by dynamical decoupling.
- EQUATIONS: T2 scaling with number of CPMG pulses N: T2(N) ∝ N^{2/3} in the P1-bath regime [delange2010]; T2* limited by C-13 Overhauser field; isotopic purification lengthens T2 [balasubramanian2009].
- TEST: monotone increase of T2 with N; fitted exponent 0.6-0.75.
- REFERENCES: [doherty2013, delange2010, balasubramanian2009, bradley2019].

### `no_cloning_guard.py` (test-only helper)
- IDEA: A universal cloner has fidelity at most 5/6 [buzek1996]; any function returning two copies is a bug.
- TEST: attempt a "cloning circuit" (CNOT from input to |0⟩) on |+⟩ and show the two outputs are not both |+⟩; reflection test over `qll.circuits`.

---

## 4. `qll/qkd/` — from correlations to secret bits

### `binary_entropy.py`
- EQUATIONS: h₂(x) = −x log₂x − (1−x)log₂(1−x), h₂(0) = h₂(1) = 0.

### `key_rate.py`
- IDEA: Secret key = information Bob has minus information Eve can have.
- EQUATIONS: BB84 asymptotic r = 1 − 2h₂(Q) [shor2000]; general Devetak-Winter r = I(A:B) − χ(A:E) [devetak2005]; threshold Q = 11.0%; with finite-key corrections [scarani2008]; INV-5 vs PLOB.
- INTERFACE: `bb84_rate_per_sifted_bit(Q)`; `bb84_qber_threshold()`; `finite_key_rate(n, Q, eps)`.
- TEST: threshold 0.1100 ± 5e-4; finite-key rate → asymptotic rate as n → ∞.
- REFERENCES: [shor2000, devetak2005, scarani2008, scarani2009, xu2020, pirandola2020].

### `plob_bound.py`
- EQUATIONS: K ≤ −log₂(1−η) [pirandola2017]; ~1.44 η for η ≪ 1.
- TEST: as Phase 1.

### `bb84.py`
- IDEA: Prepare-and-measure QKD with two conjugate bases.
- EQUATIONS: sifting keeps 1/2 (or nearly all with biased bases [lo2005efficient]); QBER from state error + background.
- INTERFACE: `Bb84Session(source, channel, detector, entropy: EntropySource).run(n_pulses)` returning sifted key, QBER, and a `ClassicalMessage` transcript (all basis reconciliation goes through `light_time_delay`).
- TEST: ideal channel QBER = 0; intercept-resend attack gives QBER = 25% [bennett1984, nielsen2010].

### `e91.py`
- IDEA: Entanglement-based QKD where a CHSH test certifies the key.
- EQUATIONS: security via S > 2; key from the matched bases; device-independent rate from S alone: r ≥ 1 − h₂((1+√(S²/4−1))/2) − h₂(Q) [acin2007, pironio2009].
- REFERENCES: [ekert1991, bennett1992bbm, yin2020].
- TEST: S = 2√2, Q = 0 gives r = 1.

### `decoy_state.py`
- IDEA: Randomly varied pulse intensities expose photon-number-splitting attacks on weak coherent sources.
- EQUATIONS: Poisson photon-number statistics; single-photon yield Y₁ and error e₁ bounds from vacuum+weak decoy [lo2005, ma2005]; rate r = q{−Q_μ f h₂(E_μ) + Q₁[1 − h₂(e₁)]}.
- REFERENCES: [hwang2003, lo2005, ma2005, liao2017, li2025jinan].
- TEST: with a perfect single-photon source the decoy rate reduces to the BB84 rate; PNS attack detected when Y₁ estimate collapses.

### `mdi.py`
- IDEA: Measurement-device-independent QKD removes all detector side channels by making an untrusted middle node do the Bell measurement.
- REFERENCES: [lo2012, braunstein2012].
- TEST: rate scales as η (not η²... actually as η for the two-arm product with a symmetric midpoint; assert the η_total exponent numerically).

### `twin_field.py` (new, Phase 3)
- IDEA: Single-photon interference at a midpoint gives a rate scaling as √η, beating PLOB without a memory.
- EQUATIONS: r ∝ √η [lucamarini2018]; demonstrated over 833 km [wang2022tf] and 1002 km [liu2023tf] (**TODO: verify**).
- TEST: log-log slope 1/2 vs. 1 for BB84.

### `sifting.py`, `error_correction.py`, `privacy_amplification.py`
- IDEAS: basis reconciliation; Cascade or LDPC reconciliation with leak f·h₂(Q), f ≈ 1.1-1.2 [brassard1994]; two-universal hashing compresses to the secure length [bennett1995pa, renner2005].
- INVARIANTS: every classical exchange is a `ClassicalMessage` (INV-1), so the *number of rounds* of Cascade becomes a latency cost that matters at Mars distances (this is why one-way LDPC is the CONOPS default [elkouss2009]).
- TEST: reconciled keys match; final length = n(1 − f h₂(Q)) − leak − 2log₂(1/ε).

---

## 5. `qll/hardware/` — models of the physical components (Phase 3)

### `photon_source.py`
- IDEA: SPDC produces pairs with thermal photon-number statistics per mode; weak coherent pulses produce Poisson statistics.
- EQUATIONS: SPDC pair probability per pulse p; multi-pair probability ~p²; heralded g^(2)(0) ≈ 2p... (use the exact two-mode-squeezed-vacuum expressions [kwiat1995, kwiat1999]); coherent state P(n) = e^{−μ} μⁿ/n!.
- INTERFACE: `SpdcSource(pair_rate_hz, brightness, heralding_eff)`, `WeakCoherentSource(mu, rep_rate_hz)`, `SingleEmitterSource(nv: NvNode)`.
- REFERENCES: [burnham1970, hong1985, kwiat1995, kwiat1999, dehlinger2002a].
- TEST: g^(2)(0) < 0.5 for heralded SPDC at p = 0.01; coherent P(0) = e^{−μ}.

### `nv_node.py` (new)
- IDEA: An NV center as a spin-photon interface: ground-state triplet, spin-dependent optical cycling, zero-phonon-line fraction, and the herald probability per attempt.
- EQUATIONS: D = 2.87 GHz zero-field splitting; Zeeman shift γ_e B with γ_e = 2.8 MHz/G; Debye-Waller factor ≈ 0.03 at 4 K (only ~3% of emission is in the zero-phonon line, the root cause of ~10^-4 herald rates) [doherty2013]; entanglement rate per attempt p_succ ≈ (η_zpl η_coll η_det)² /2 for two-photon schemes, ∝ single-photon efficiency for single-click schemes [barrett2005, humphreys2018].
- INTERFACE: `NvNode(T_kelvin, B_gauss, zpl_fraction, collection_eff, T1_s, T2_s)` with `.entangle_attempt(other, scheme)`.
- REFERENCES: [doherty2013, bernien2013, humphreys2018, pompili2021].
- TEST: p_succ at Delft-class efficiencies ≈ 10^-4 to 10^-5 (matches the reported seconds-to-minutes time per pair).

### `detector.py`
- IDEA: A single-photon detector is an efficiency, a dark-count rate, a dead time, and a timing jitter.
- EQUATIONS: click probability 1 − (1−η)ⁿ·(1−p_dark); afterpulsing as a probability per click; SNSPD vs. Si-SPAD vs. InGaAs parameter table.
- REFERENCES: [hadfield2009, eisaman2011].
- TEST: dark counts alone give QBER 50%; η = 1, p_dark = 0 gives ideal.

### `beam_splitter.py`, `perceval_adapter.py`
- IDEA: Linear optics as unitary transformations on modes; Hong-Ou-Mandel bunching.
- EQUATIONS: 50:50 BS unitary; HOM coincidence dip visibility V = (1 − indistinguishability)... = overlap |⟨φ₁|φ₂⟩|².
- REFERENCES: [hong1987, kok2007, heurtel2023perceval].
- TEST: identical photons never leave the BS in different ports.

### `randomness.py` (new; ties to the owner's QRNG board)
- IDEA: A declared entropy source with a min-entropy estimate.
- INTERFACE: `EntropySource` protocol `.bits(n)`, `.min_entropy_per_bit()`; implementations `NumpyPRNG` (labelled *not quantum*), `SerialQrng(port)` for the FPGA board, `PhaseDiffusionQrng` model [abellan2014].
- INVARIANTS: INV-7; BB84 and CHSH refuse a source labelled non-quantum unless `allow_pseudo=True`.
- REFERENCES: [herrero2017, abellan2014, nist800-90b].
- TEST: NIST SP 800-90B-style monobit and runs checks pass on 10^6 bits from any real source.

### `transduction.py` (Phase 4 placeholder)
- IDEA: Converting a microwave qubit (superconducting or spin ensemble) to an optical photon; efficiency, added noise, bandwidth.
- REFERENCES: [lauk2020, mirhosseini2020].
- TEST: state fidelity bound vs. added noise n_add.

---

## 6. `qll/network/` — memories, repeaters, and scheduling (Phase 4)

### `memory_decoherence.py`
- IDEA: A stored qubit decays; the stored *entanglement* decays faster than the qubit fidelity suggests.
- EQUATIONS: Werner fidelity of a stored pair F(t) = ¼ + (F₀ − ¼)e^{−t/T2_eff} for a depolarizing memory; entanglement lost when F < 1/2; teleportation useless when F < ... via (2f+1)/3 < 2/3, i.e., f < 1/2.
- INTERFACE: `Memory(platform, T_kelvin)` with a platform table: NV C-13 (T2 up to ~min at 4 K [bradley2019]), SiV C-13 (~s [knaut2024]), Eu:YSO (6-13 h at ~2 K with ZEFOZ+DD [zhong2015, wang2025memory]), Yb+ ion (>1 h [wang2021ion]), atomic ensemble (ms [liu2024]).
- TEST: the crossover time t* where F drops to 1/2, compared against `light_time_delay` for LEO, GEO, lunar, Mars min, Mars max; this is `REQ-CAP-001`.

### `purification.py`
- IDEA: Trade several noisy pairs for one better pair using only local operations and classical communication.
- EQUATIONS: BBPSSW recurrence F' = [F² + ((1−F)/3)²] / [F² + 2F(1−F)/3 + 5((1−F)/3)²], success p = denominator [bennett1996]; DEJMPS variant [deutsch1996].
- INVARIANTS: each round costs one `ClassicalMessage` round trip (INV-1), so at Mars distances the number of rounds is a first-class cost.
- TEST: F > 1/2 increases; F = 1/2 is a fixed point; fixed point at 1.

### `swapping_scheduler.py`
- IDEA: When to swap and when to purify along a chain, given memory decay and classical latency.
- EQUATIONS: nested scheme rate ~ (p_gen p_swap^{levels}) / t_cycle with t_cycle ≥ L_segment/c [briegel1998, sangouard2011]; three repeater generations [muralidharan2016, azuma2023].
- TEST: chain beats direct transmission beyond a crossover distance (`REQ-NET-001`), reproducing Fig. 2 of [muralidharan2016] qualitatively.

### `repeater_chain.py`
- IDEA: A chain of N segments each generating entanglement with probability p per attempt, memories that decay, and swaps that succeed with probability q.
- EQUATIONS: expected time to end-to-end pair; rate vs. N; the memory-time requirement t_mem ≳ (3/2)^{levels}·L/c.
- REFERENCES: [briegel1998, duan2001, sangouard2011, azuma2023, bhaskar2020].

### `routing.py`
- IDEA: Pick a path through a graph of links maximizing end-to-end entanglement rate subject to fidelity.
- REFERENCES: [pant2019, chakraborty2019] (**TODO: verify**).

### `relay_constellation.py`
- IDEA: Orbiting nodes carry entanglement and keys; pass geometry sets availability.
- EQUATIONS: pass duration and elevation from two-line elements; per-pass key from the Jinan-1 empirical table; single-satellite time-delayed repeater [gundogan2024].
- REFERENCES: [vergoossen2020, polnik2020, khatri2021, gundogan2024, li2025jinan].
- TEST: constellation availability vs. number of satellites reproduces the trend in [khatri2021].

### `sequence_adapter.py`
- IDEA: Delegate discrete-event network simulation to SeQUeNCe; the adapter only translates our `Memory`, `Link`, and `ClassicalMessage` objects and asserts INV-1 on the timeline.
- REFERENCES: [wu2021sequence].

---

## 7. `qll/space/` (Phase 5, new package)

### `ephemeris.py` — Horizons-derived Earth-Mars range and Sun-Earth-probe angle vs. time.
### `conjunction.py` — solar conjunction outage windows (Sun-Earth-Mars angle < ~3°) [dsn2020].
### `platform_thermal.py` — radiator-limited cryogenic budget for a spacecraft memory (R-2); passive cooling floor vs. dilution refrigerators in orbit [jpl_cryo] (**TODO: reference**).
### `mission_trl.py` — maps each module to the DSQL technology list [mohageg2022, mohageg2025].

---

## 8. `qll/app/` (Phase 6)

### `hybrid_kem.py` — ML-KEM (FIPS 203) key encapsulation combined with QKD key via a key-derivation function; hybrid security holds if either is secure [nist2024fips203, bindel2019].
### `aes_gcm_layer.py` — AES-256-GCM with per-message nonces from `randomness.py` [nist2007sp800-38d].
### `messenger.py` — store-and-forward with acknowledgments that respect `light_time_delay`; **fail-closed** on key exhaustion (`REQ-APP-001`); key-buffer sizing from arrival statistics of `relay_constellation`.
### `benchmark.py` — the "California-to-New-York" experience metric: perceived latency vs. physical latency under pre-shared keys and pre-distributed entanglement; the honest result is that *throughput* can look terrestrial while *round-trip* never can.

---

## 9. `qll/systems/`

### `traceability.py` — adds `check_import_dag()` and `check_module_cards()` (every file has the seven fields in its docstring).
### `trl.py` — NASA TRL table [nasa2016seh].
### `requirements.md` — append REQ-CAP-002 (teleportation completes after a light-time-delayed classical channel) and REQ-CHN-003 (background prefactor validated on hardware).

---

## 10. Reference map by physical idea (for the thesis literature review)

| Idea | Foundational | Review | Best experiment |
|---|---|---|---|
| No-signaling | [ghirardi1980] | [peres2004] | every teleportation paper's timing |
| No-cloning | [wootters1982, dieks1982] | [scarani2005] | [buzek1996] bound |
| Bell nonlocality | [bell1964, clauser1969] | [brunner2014] | [hensen2015, bigbell2018] |
| Teleportation | [bennett1993] | [pirandola2015tele] | [hermans2022, ren2017] |
| Entanglement swapping | [zukowski1993] | [azuma2023] | [pompili2021] |
| SPDC sources | [burnham1970, hong1985] | [anwar2021] | [kwiat1999] |
| Single-photon detectors | — | [hadfield2009, eisaman2011] | — |
| NV centers | [gruber1997] | [doherty2013, childress2013] | [bernien2013, stolk2024] |
| SiV centers and cavities | — | [bradac2019] | [bhaskar2020, knaut2024] |
| Rare-earth memories | — | [lvovsky2009, heshami2016] | [zhong2015, ma2021, wang2025memory] |
| Quantum repeaters | [briegel1998, duan2001] | [sangouard2011, muralidharan2016, azuma2023] | [bhaskar2020, liu2024] |
| QKD security | [bennett1984, ekert1991, shor2000] | [scarani2009, xu2020, pirandola2020] | [yin2020, li2025jinan] |
| Rate limits | [pirandola2017, takeoka2014] | [pirandola2020] | [wang2022tf] |
| Satellite links | [bourgoin2013] | [bedington2017, sidhu2021] | [yin2017, liao2017, li2025jinan] |
| Deep space | [mohageg2022] | [mohageg2025] | none yet (TRL 1-2) |
| Thermal noise in qubits and channels | [clerk2010] | [krantz2019] | [avesani2021] |
| Transduction | — | [lauk2020] | [mirhosseini2020] |
| Randomness | [abellan2014] | [herrero2017] | [bigbell2018] |
| Post-quantum hybrid | [nist2024fips203] | [bindel2019] | — |

---

## 11. Phase 2 file order (so every commit passes)

1. `noise/_kraus_base.py` + test (INV-4)
2. `fidelity.py` + test
3. `bell.py` + test
4. `bell_measurement.py` + test
5. `teleportation.py` + test (uses `light_time_delay`, INV-1, INV-3)
6. `noise/depolarizing.py`, `amplitude_damping.py`, `phase_damping.py` + QuTiP cross-checks
7. `chsh.py` + `hardware/randomness.py` (INV-7)
8. `entanglement_swapping.py`, `superdense_coding.py`, `ghz.py`, `tomography.py`
9. `tests/test_phase2_no_cloning.py`
10. traceability rows, notebook, CHANGELOG 0.2.0, commit "Phase 2: circuits"
