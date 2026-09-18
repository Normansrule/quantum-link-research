# Clock synchronization for quantum networks

## Why it is physics, not plumbing
Coincidence windows are nanoseconds; a herald that arrives "now" is only meaningful if both nodes agree what "now" is to better than the window. F1 needs ~1 ns across a city, F2 needs ~1 ns between a ground station and a satellite moving at 7.6 km/s, F3 needs relativistic corrections of parts in $10^{-8}$ over minutes of light time.

## Methods, best to cheapest
| Method | Accuracy | Where used |
|---|---|---|
| Optical two-way time transfer (frequency combs) | fs–ps | clock networks, T05 |
| White Rabbit (Ethernet + PTP + phase) | sub-ns | accelerator labs, some QKD testbeds |
| GPS-disciplined oscillators (GPSDO) | ~10–50 ns absolute, better relative with common-view | F1 campus links, P03/P04 |
| Pulsed laser beacon + coincidence peak search | ~ns after correlation | Micius: a 10 kHz pulsed laser synchronized the satellite and ground clocks |
| Cross-correlation of photon arrival times | ns; needs high rates | entanglement-based sync |

## Relativity at F3 scale
Gravitational redshift between Earth and Mars surfaces $\sim(\Phi_{\rm Earth}-\Phi_{\rm Mars})/c^2\approx6\times10^{-10}$; Doppler from relative velocity up to ~40 km/s gives $10^{-4}$; Shapiro delay near conjunction up to ~250 µs. A time-bin qubit's early/late separation (ns) is unaffected in shape but its arrival must be predicted to the window, so the ephemeris drives the coincidence logic ([T05](../../research/theories/T05_quantum_clock_networks_and_relativity.md)).

## Key references
Lu, C.-Y., et al. (2022). *Rev. Mod. Phys.*, 94, 035001 (Micius synchronization). Deschênes, J.-D., et al. (2016). Synchronization of distant optical clocks at the femtosecond level. *Physical Review X*, 6, 021016. Ho, C., Lamas-Linares, A., & Kurtsiefer, C. (2009). Clock synchronization by remote detection of correlated photon pairs. *New J. Phys.*, 11, 045011. Kómár, P., et al. (2014). *Nature Physics*, 10, 582. https://doi.org/10.1038/nphys3000 Ashby, N. (2003). Relativity in the Global Positioning System. *Living Rev. Relativ.*, 6, 1.

## In this repo
P03/P04 use GPS-disciplined clocks; Phase 5 `qll/space/ephemeris.py` adds relativistic corrections to `light_time_delay.py`.
