# P01 — Optically detected magnetic resonance (ODMR) on a $100–500 NV bench

## Safety
- Green lasers above 1 mW (class 3R/3B) can damage eyes in a fraction of a second. Use a **class 2 (< 1 mW) 520–532 nm module** or a high-power green LED for a first build; if you later use a 50–100 mW DPSS laser, wear OD 4+ 532 nm goggles, enclose the beam path, and never align at eye level.
- The ADF4351 board with a 1–2 W amplifier is a radio transmitter at 2.87 GHz: keep the antenna loop small, do not run it open-ended, and check local rules on unlicensed emission (a shielded enclosure solves this).

## Parts (links in [`../bench/hardware_guide.md`](../bench/hardware_guide.md) §2.2)
Fluorescent microdiamond (Adámas, ~150 µm, NV-rich) · green laser module or LED · long-pass film or dichroic (> 600 nm) · BPW34 photodiode + transimpedance amplifier or a cheap SiPM board · ADF4351 evaluation board + Arduino/ESP32 · 1–2 W 2.4–3 GHz amplifier · copper wire loop or microstrip antenna · small neodymium magnet on a screw · 3D-printed cubes (Stegemann) or the Uncut Gem PCB.

## Build
1. Print or assemble the optical path: laser → diamond → long-pass filter → photodiode, with the diamond glued over the antenna loop (or on the PCB's microstrip).
2. Wire the ADF4351 to the microcontroller (SPI), set output −4 dBm, feed the amplifier, connect the antenna.
3. Wire the photodiode amplifier to the microcontroller ADC (or a sound card / USB oscilloscope).

## Align
4. With the laser on, maximize the photodiode signal by moving the diamond; verify the long-pass filter blocks the green (signal drops to near zero when the diamond is removed).
5. Confirm the microwave chain: a cheap SDR or a second ADF4351 as a receiver should hear the tone.

## Measure
6. Sweep the microwave frequency 2.70–3.05 GHz in 1 MHz steps, dwell 20–50 ms per step, average 10–50 sweeps, record fluorescence vs frequency.
7. Expect a dip at 2.87 GHz of 0.5–3% depth (ensemble). If two dips appear at zero field, strain splitting is visible.
8. Bring the magnet within a few centimetres; the dip splits into up to eight lines (four NV orientations × two transitions).

## Analyze
9. Fit dips to Lorentzians; extract centre frequencies $f_\pm$. With the field along one NV axis, $f_\pm=D\pm\gamma_eB_\parallel$ with $\gamma_e/2\pi=2.8$ MHz/G, so $B_\parallel=(f_+-f_-)/(2\gamma_e)$.
10. Record contrast $C$, photon rate $R$, linewidth; compute the DC magnetometer sensitivity $\eta_B\approx\frac{\Delta f}{\gamma_eC\sqrt R}$ (`learn/01_quantum_computing_core/06`).
11. Compare with `qll/hardware/nv_node.py` parameters (Phase 3) and log the run.

## Expected numbers
Ensemble contrast 1–3%; linewidth 5–15 MHz (power-broadened); sensitivity ~1–10 µT/√Hz on the LED build [Williams et al. 2025].

## If it does not work
- No dip: microwave not reaching the diamond (check amplifier output with an SDR), laser too weak, or the photodiode saturated. Reduce laser, increase averaging.
- Dip in the wrong place: an ADF4351 reference-clock error; verify against a known 2.87 GHz.
- Huge noise: 50/60 Hz pickup; use a lock-in style modulation (chop the microwaves at 1 kHz and demodulate in software).

## References
Stegemann et al. (2023) *Eur. J. Phys.* 44, 035402 https://doi.org/10.1088/1361-6404/acbe7c · Carney & Kumaran (2025) arXiv:2509.18329 · Williams et al. (2025) arXiv:2512.03106 · Doherty et al. (2013) *Phys. Rep.* 528, 1.
