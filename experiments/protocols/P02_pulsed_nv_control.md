# P02 — Pulsed control of an NV ensemble: Rabi, Ramsey, Hahn echo, $T_1$

## Safety
Same as P01; pulsed microwaves at up to a few watts peak need a proper 50 Ω chain and a terminated antenna.

## Parts (adds to P01; full list in Sewani et al. 2020, arXiv:2004.02643)
Microwave switch (e.g., a reflective SPDT with ~10 ns rise) · pulse generator: FPGA or a microcontroller with deterministic timing (≥ 10 ns resolution; a Raspberry Pi Pico PIO or an FPGA dev board works) · faster photodetector (bandwidth ≥ 1 MHz) with gated integration · acousto-optic modulator (AOM) or a directly modulated laser diode for optical pulses · permanent magnet with a mount to set $B_\parallel$ ~ 20–50 G.

## Build and align
1. Add the switch between the ADF4351 and amplifier; verify pulse shape on an oscilloscope.
2. Add laser gating; verify a 3 µs initialization pulse and a 300 ns readout window.
3. Set the magnet so ODMR shows a well-resolved single $m_s=0\to-1$ line; tune the microwave to it.

## Measure
4. **Rabi**: initialize (3 µs green) → microwave pulse of length $t$ (0–2 µs, 20 ns steps) → readout. Plot $P_1(t)$; fit $\sin^2(\Omega t/2)$; note the $\pi$ time.
5. **Ramsey**: $\pi/2$ – wait $\tau$ – $\pi/2$; scan $\tau$ 0–5 µs; fit $e^{-\tau/T_2^*}\cos(\Delta\tau)$; deliberately detune by 1 MHz to see fringes.
6. **Hahn echo**: $\pi/2$ – $\tau/2$ – $\pi$ – $\tau/2$ – $\pi/2$; scan $\tau$ to 200 µs; fit $e^{-(\tau/T_2)^n}$.
7. **$T_1$**: initialize → wait $\tau$ → readout, up to 10 ms; fit exponential.
8. Repeat 7 at 77 K (diamond in a small liquid-nitrogen bath, optics outside) and near 350 K (heater) for proposal E2.

## Analyze
Save each dataset as `data/pulsed/YYYY-MM-DD_<setup>_<experiment>.csv` with columns `time_s,signal`. Fit with `qll.analysis.relaxation_fit` (`fit_rabi`, `fit_ramsey`, `fit_echo`, `fit_t1`); for step 8 collect $T_1$ at each temperature and run `fit_t1_vs_temperature`, which fits the Orbach + Raman phonon model of Jarmola et al. (2012), and plot it against `thermal_model_prediction`, the Phase 1 bath-occupation law. The two differ by orders of magnitude between 77 K and 350 K; the data decide, and that closes REQ-THM-003. The pipeline is tested on synthetic data (`tests/test_analysis_relaxation.py`).

## Expected numbers
Ensemble in commercial microdiamond: $T_2^*$ 0.3–2 µs, echo $T_2$ 5–100 µs, $T_1$ ~ 1–5 ms at 300 K; contrast 1–3%.

## If it does not work
Rabi oscillations wash out: microwave inhomogeneity across the ensemble (smaller diamond, closer antenna) or too much laser during the pulse (check gating). Echo shorter than Ramsey: timing jitter; check the pulse generator.

## References
Sewani et al. (2020) *Am. J. Phys.* 88, 1156 · Jelezko et al. (2004) *PRL* 92, 076401 · de Lange et al. (2010) *Science* 330, 60 · Jarmola et al. (2012) *PRL* 108, 197601.
