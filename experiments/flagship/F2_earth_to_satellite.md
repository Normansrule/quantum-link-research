# F2 — A computer on Earth to a satellite

## The question
Given F1's source and detectors, what does it take to close a single-photon link to low Earth orbit, and how many entangled pairs and secret bits does one pass deliver?

## Physics
- Diffraction: $\theta=\lambda/\pi w_0$, $\eta_{\rm geo}=\min(1,(D_{\rm rx}/2\theta L)^2)$; at 1200 km with a 15 cm transmitter and 1 m receiver, ~0.06 geometric ([03/04](../../learn/03_quantum_communication/04_satellite_and_deep_space.md)).
- Atmosphere 3–10 dB, pointing $\eta_{\rm point}=w^2/(w^2+4\sigma_p^2L^2)$, optics and detectors ~10 dB: total 60–80 dB, i.e. $10^{-6}$–$10^{-8}$, which Micius measured.
- Background: $N=\bar nMB\eta$ from sky radiance; QBER floor $\approx N\tau/(2(R\eta+N\tau))$; this is why Micius flew at night and why sun angle matters.
- Timing: nanosecond synchronization from a pulsed beacon plus GPS-disciplined clocks; polarization reference frame compensation for a rotating satellite.

## Stages
| Stage | What | Pass | Cost / time | Files |
|---|---|---|---|---|
| S1 simulate | `link_budget.py` reproduces the Micius 2017 and Jinan-1 2025 budgets; pairs per pass from pass geometry | within ±3 dB of the published loss; pairs per pass within 3× | software, 3 weeks | Phase 3 `atmosphere.py`, `pointing_jitter.py`, `link_budget.py` |
| S2 rooftop | P04: the F1 source across campus (20–300 m), loss vs distance, background vs sun angle and filter | fit to the diffraction and background models; QBER < 5 % at 10° from the Sun | $1–2k above F1, two weeks | [P04](../protocols/P04_rooftop_free_space_link.md), [E4](../proposed/E04_sun_angle_background.md) |
| S3 ground-station design | a 30–50 cm telescope with fine-steering mirror, SNSPD or SPAD, tracking of a known LEO beacon (an ISS pass) | track to < 20 µrad; detect the beacon | ~$20–50k, one year | new protocol P06 |
| S4 real pass | partner with a mission (Jinan-1 successors, Eagle-1, QEYSSat) as a receiving station | received pairs/key from orbit | collaboration | [done/09](../done/09_satellite_qkd_micius_jinan.md) |

## What "a computer" on each end means
Not a photon counter: a node that holds its half of the pair in a memory long enough for the herald round trip (~8 ms), which NV/SiV or ion nodes do; the satellite carries only a source in this version. The upgrade path where the satellite carries a *memory* is the time-delayed single-satellite repeater ([Gündoğan 2024](../../learn/03_quantum_communication/04_satellite_and_deep_space.md)).

## Requirements verified
REQ-CHN-002 (tightened with exact Gaussian forms), REQ-CHN-003 (background prefactor), REQ-QKD-002 (rates ≤ PLOB); new REQ-F2-001: "the link-budget model reproduces two independent published satellite budgets within ±3 dB."

## Key references
Yin et al. (2017) *Science* 356, 1140 · Liao et al. (2017) *Nature* 549, 43 · Li et al. (2025) *Nature* 640, 47 · Bourgoin et al. (2013) *New J. Phys.* 15, 023006 · Bedington et al. (2017) *npj QI* 3, 30 · Sidhu et al. (2021) *IET Quantum Commun.* 2, 182.
