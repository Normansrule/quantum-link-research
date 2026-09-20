# P01 Bill of Materials

The $100–500 ODMR bench, itemized. Links are the ones already verified in this project (`hardware_guide.md`); prices are planning ranges from September 2026, request quotes for exact figures. Two routes: **Uncut Gem** (order the PCB, populate it) or **Stegemann cubes** (3D-print the optics). Both use the same diamond, microwave source, and readout.

| # | Part | Qty | Route | Planning price | Where | Notes |
|---|---|---|---|---|---|---|
| 1 | Fluorescent microdiamond, ~150 µm, NV-rich | 1 vial (many stones) | both | $50–200 | [Adámas Nano fluorescent diamonds](https://www.adamasnano.com/fluorescent-diamonds); low-nitrogen grade for contrast: [details](https://www.adamasnano.com/low-nitrogen-information) | one stone is glued over the antenna; keep spares |
| 2 | Green laser module, 520–532 nm, < 1 mW (class 2) | 1 | both | $10–30 | any electronics distributor | class 2 keeps the first build eye-safe; a 5 mW module needs goggles |
| 2b | High-power green LED (alternative to the laser) | 1 | both | $5–15 | | works for ODMR at ~µT/√Hz [williams2025] |
| 3 | Long-pass filter ≥ 600 nm | 1 | both | $5–60 | photographic red filter film (cheap) or a 2 mm glass long-pass (better) | blocks the green; passes 637–800 nm fluorescence |
| 4 | Photodiode BPW34 + transimpedance amplifier (op-amp, 1–10 MΩ feedback) | 1 | both | $5–15 | | or a SiPM board (~$50–100) for more gain |
| 5 | ADF4351 evaluation board, 35–4400 MHz | 1 | both | $20–40 | common eval boards | the microwave source, SPI-controlled |
| 6 | Microcontroller (Arduino Uno/Nano or ESP32) | 1 | both | $5–25 | | drives the ADF4351 over SPI, reads the ADC |
| 7 | RF amplifier module, 1–2 W, 2–3 GHz | 1 | both | $15–40 | | keep the antenna short and the enclosure closed |
| 8 | Loop antenna (copper wire, ~5 mm loop) or PCB microstrip | 1 | both | $1 | | the Uncut Gem PCB includes the microstrip |
| 9 | Neodymium magnet on an M6 screw | 1 | both | $5 | | the Zeeman splitting demonstration |
| 10 | Uncut Gem PCB (JLCPCB/PCBWay from the repo's Gerbers) | 1 | Uncut Gem | $20–60 incl. shipping | [github.com/QuantumVillage/UncutGem](https://github.com/QuantumVillage/UncutGem) | reported total ~£115 [carney2025] |
| 11 | 3D-printed optics cubes and magnetic base plate | 1 set | Stegemann | $5–20 filament | STLs in the paper's supplement [stegemann2023] | needs a printer (any FDM) |
| 12 | Acrylic lens ~10–20 mm focal length | 1–2 | Stegemann | $5 | | |
| 13 | Coax pigtails (SMA), USB cables, breadboard, wire | — | both | $20 | | |
| 14 | Optional: USB oscilloscope or sound card for lock-in style readout | 1 | both | $30–100 | | improves the dip contrast at low signal |
| **Total** | | | | **$170–500** | | detectors are the only place money buys signal here |

## Order of assembly (P01 §Build)
1. Diamond glued over the antenna; 2. laser/LED → diamond → filter → photodiode aligned; 3. ADF4351 + amplifier verified with an SDR or a second board; 4. sweep 2.70–3.05 GHz; 5. magnet.

## What to record for `data/odmr/`
`frequency_hz, signal` CSV and the JSON sidecar (`diamond`, `laser_mw`, `microwave_dbm`, `dwell_ms`, `averages`, `magnet`, `temperature_k`, `photon_rate_hz`). Then `python -m qll.analysis.odmr_report data/odmr/<file>.csv`.

## Safety, once more
Laser class 2 or LED only for the first build; the RF chain in a closed metal box; no antenna left open at 1–2 W.

## Sources
- Stegemann, J., et al. (2023). Modular low-cost 3D printed setup for experiments with NV centers in diamond. *European Journal of Physics*, 44, 035402. https://doi.org/10.1088/1361-6404/acbe7b
- Carney, M. (2025). Uncut Gem: a DIY quantum sensing badge. DEF CON 33 Quantum Village. https://github.com/QuantumVillage/UncutGem
- Williams, T., et al. (2025). Low-cost, open-source diamond NV magnetometry for the classroom. arXiv (TODO: confirm identifier).
