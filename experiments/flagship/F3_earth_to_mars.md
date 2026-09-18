# F3 — Earth to Mars

## The question
With F1's node protocol and F2's link model, what architecture delivers a physics-secured message channel between Earth and Mars, and what is the honest end-to-end performance (pairs per day, secret bits per day, message latency at a target fidelity)?

## Physics that changes at AU scale
- Light time 3–22 min one way; every herald, correction, and reconciliation round costs 6–45 min ([03/02](../../learn/03_quantum_communication/02_teleportation_and_swapping.md)).
- Memory must hold the pair across the round trip: $F(t)=\frac14+(F_0-\frac14)e^{-t/T_2}$ must stay above the $f>1/2$ (teleportation $F>2/3$) line ([03/03](../../learn/03_quantum_communication/03_repeaters_and_memories.md)); only rare-earth nuclear spins (6–13 h) and trapped ions (> 1 h) qualify today.
- Diffraction $\sim10^{-9}$–$10^{-11}$ even with 10 m apertures; pairs per hour at best without multiplexing by $10^3$–$10^6$ ([E9](../proposed/E09_multiplexing_at_au_scale_loss.md)).
- Solar conjunction blocks the line of sight for weeks every 26 months (figure below); relays at Sun–Earth L4/L5 or Mars orbit are the only way around it.
- The classical half is itself photon-starved: DSOC-class optical terminals and quantum-limited receivers ([T06](../../research/theories/T06_quantum_limited_optical_receivers.md)).

![mars](../../docs/figures/mars_light_time_cycle.svg)

## Architecture under study (baseline vs alternative)
| | Baseline: memory-based relay chain | Alternative: all-photonic |
|---|---|---|
| Relay carries | entangled-photon source + rare-earth or ion memory | source + photonic cluster-state generator, no memory |
| Cryogenics in space | 2–4 K (flown class) | detectors only |
| Herald delay handled by | memory holding across 2d/c | nothing to hold; enormous photon budget |
| Trade study | [E8](../proposed/E08_modality_trade_study_mars_memory_node.md) | [T02](../../research/theories/T02_all_photonic_repeaters.md) |

## Stages (all software or bench analogues; nothing flies)
| Stage | What | Pass | Files |
|---|---|---|---|
| S1 delayed bits on the bench | F1's CHSH/teleportation bench with heralds released after a software delay equal to the Mars light time | correlations identical at any delay; the `NotYetArrived` guard never bypassed | [E1](../proposed/E01_delayed_classical_channel_teleportation.md) |
| S2 memory crossover | $F(t)$ for each memory platform vs the light-time baselines; owner's NV $T_1(T)$ data added | figure with the crossover per platform; REQ-CAP-001 verified | [E2](../proposed/E02_memory_vs_temperature_vs_light_time.md), `network/memory_decoherence.py` |
| S3 relay scheduling | SeQUeNCe model with ephemeris ranges, conjunction outages, Jinan-1 per-pass statistics, 1–5 relays | pairs per day vs relay count and placement | [E3](../proposed/E03_constellation_scheduling_on_real_pass_data.md), Phase 5 `qll/space/` |
| S4 messenger | hybrid ML-KEM + QKD keys, AES-GCM, every message through `DelayQueue`; key-buffer sizing; fail closed | never blocks, never sends unkeyed; latency at target fidelity reported | [E5](../proposed/E05_fail_closed_messaging_20min_latency.md), Phase 6 |
| S5 certification | DI key rate with settings and outcomes buffered for the light time | finite-key rate > 0 for a stated buffer | [E10](../proposed/E10_device_independent_certification_under_latency.md) |

## The honest metric
Report three numbers, not one: **pairs per day** (physics), **secret bits per day** (security), and **message latency at $F\ge0.9$** (experience). The last can look terrestrial for throughput and never for round trip; the thesis says so plainly ([lessons/02](../lessons/02_what_scaled_and_why.md)).

## Requirements verified
REQ-CAP-001, REQ-CAP-002 (new: teleportation completes after a light-time-delayed classical channel), REQ-NET-001 at planetary scale, REQ-APP-001, REQ-SEC-001 (new).

## Key references
Mohageg et al. (2022) *EPJ Quantum Technol.* 9, 25 and (2025) update · Zhong et al. (2015) *Nature* 517, 177 · Wang et al. (2025) *PRX Quantum* 6, 010302 · Gündoğan et al. (2024) *Optica Quantum* 2, 140 · Azuma et al. (2015) *Nat. Commun.* 6, 6787 · Khatri et al. (2021) *npj QI* 7, 4 · Bennett et al. (1993) *PRL* 70, 1895.
