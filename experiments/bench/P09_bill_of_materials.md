# P09 Bill of Materials — The Mars Link on a Table

Planning prices in US dollars are ranges for new hobby-grade or used lab parts; check current listings before ordering. Every part's measured value belongs in `data/bench/bench.json` (template: [`P09_bench.json`](P09_bench.json)), because the twin predicts with your numbers, not the defaults. A 3D printer covers the mounts, baffles, turntable arm, lever-arm stage, fiber receptacles, and ND wheel.

## Tier 1 — photodiodes (Stages 1–7, multimode receiver)
| # | Part | Qty | Planning price | Notes |
|---|---|---|---|---|
| 1 | 650 nm laser, class 2 (≤ 1 mW), ideally fiber-pigtailed to single-mode fiber | 1 | $10–150 | a pigtailed module gives a clean point source; the budget route is a bare module behind item 2 |
| 2 | Precision pinhole, 25–50 µm | 1 | $10–40 | the budget point source; skip if item 1 is pigtailed |
| 3 | Neutral Density (ND) filters, OD 0.5–3, stackable, 25 mm | 1 set | $15–60 | photographic ND film works for the source side; note each OD |
| 4 | Halogen lamp, 12 V, 20–50 W (MR16 or desk lamp) and its supply | 1 | $10–30 | a smooth spectrum; a stable supply matters more than power |
| 5 | Ping-pong balls, 40 mm, and matte white primer | 3 | $8 | two coats, matte; keep a spare |
| 6 | Bandpass filter 650 nm, 10 nm full width, 12.5 or 25 mm | 1 | $25–80 | a second width (3 or 40 nm) enables the filter-width law |
| 7 | Fiber collimator, FC/PC, f ≈ 11 mm, visible coating | 1 | $20–120 | record focal length and clear aperture |
| 8 | Multimode Fiber (MMF) patch cable, 50 µm core, 0.22 NA, FC/PC, 1–2 m | 1 | $15–50 | |
| 9 | Silicon photodiodes, BPW34 class | 3 | $3–10 | one bare with the filter (Stages 1–2), one in an FC receptacle, one spare |
| 10 | Transimpedance Amplifier (TIA): picoamp-bias op-amp, 10 MΩ–1 GΩ feedback resistors, shielded box | 2 | $10–30 | 1 GΩ for the ~10⁻¹⁰ W of Stage 3 |
| 11 | Controller: Arduino or RP2040 board with a 16-bit ADC (ADS1115 class), hobby servo | 1 | $15–35 | logs readings, turns the ND wheel |
| 12 | Linear polarizer film | 1 sheet | $8–15 | two pieces: transmitter and receiver analyzer |
| 13 | Turntable bearing (lazy Susan), M3 screws, 200 mm aluminium bar | 1 | $10–20 | lamp arm and lever-arm stage |
| 14 | Black felt or foam board, flat black paint | — | $10–20 | backdrop and baffles |
| **Tier 1 total** | | | **$150–400** | |

## Tier 2 — photon counting (adds Stage 3 SMF, Stage 5 SMF, Stage 7 in counts)
| # | Part | Qty | Planning price | Notes |
|---|---|---|---|---|
| 15 | Single-Mode Fiber (SMF) patch cable for 630–680 nm (630HP / SM600 class), FC/PC | 1 | $40–100 | record the mode-field diameter at 650 nm |
| 16 | Silicon Photomultiplier (SiPM), 1–1.3 mm, on a carrier board | 1 | $40–150 | small area keeps dark counts near 10⁵ per second; cool it if you can |
| 17 | SiPM bias supply, 25–55 V adjustable, low noise | 1 | $15–60 | or a bench supply |
| 18 | Fast comparator board and an RP2040 counting pulses with its PIO | 1 | $15–40 | or a used single-photon counting module ($$) |
| 19 | Extra ND, OD 3–4 | 1 | $15–40 | photon counters saturate near 10⁶–10⁷ per second |
| 20 | Polarizing Beamsplitter (PBS) cube, visible, 10–12.7 mm, and a second counter | 1 | $30–120 | optional: both error ports at once |
| **Tier 2 added** | | | **$150–400** | |

## Tier 3 — entanglement (true measure-on-arrival BBM92)
The P03 spontaneous parametric down-conversion source, polarization analyzers at both ends, and a time tagger: see `P03_spdc_bell_test.md` and `P07_bb84_over_a_fiber_spool.md`. Planning cost $3,000–15,000, mostly the pump laser, crystal, and single-photon detectors; many universities lend these for a semester project.

## Order of assembly
Stage 0 costs nothing; buy Tier 1 items 4, 5, 6, 9, 10, 11, 13, 14 first (Stages 1–2), then 7, 8 (Stage 3), then 1–3 (Stages 4–5), then 12 (Stage 6). Tier 2 is worth buying only after Stage 5 works with the multimode receiver.

## Sources
- Hapke, B. (2012). *Theory of reflectance and emittance spectroscopy* (2nd ed.). Cambridge University Press. (Why a matte, Lambertian ball and card.)
- Siegman, A. E. (1986). *Lasers*. University Science Books. (Why single-mode fiber has étendue λ², and how a fiber collimator couples a Gaussian mode.)
- Dehlinger, D., & Mitchell, M. W. (2002). Entangled photons, nonlocality, and Bell inequalities in the undergraduate laboratory. *American Journal of Physics*, 70, 903. https://doi.org/10.1119/1.1498860 (Tier 3.)
