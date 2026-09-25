# Cryogenic Wiring Budget

## The problem
A superconducting processor needs at least one microwave line per qubit (drive), often a flux line, and readout lines shared by multiplexing. Each line is a coaxial cable from 300 K to 10 mK with attenuators at the cold stages so that room-temperature thermal noise is reduced below the qubit's own thermal occupation. Every cable conducts heat and every attenuator dissipates microwave power, and the coldest stage of a dilution refrigerator has tens of microwatts to spend [krinner2019].

## The budget
Passive load per stage: $Q=\frac{A}{L}\int_{T_1}^{T_2}k(T)\,dT$ for the cable's cross-section, length, and conductivity integral (stainless steel or cupronickel for drive lines, niobium-titanium for readout lines, whose superconducting inner conductor carries almost no heat). Active load: $P_{\rm in}(1-10^{-A/10})$ at each attenuator, so a 20 dB pad at 4 K dissipates 99 % of what reaches it. `qll/hardware/cryo_wiring.py` sums both per stage for a list of lines and finds the limiting stage: with representative conductivity integrals a −30 dBm-average drive line with 20 dB at 4 K and 20 dB at the mixing chamber is limited by the cold-plate stage, niobium-titanium raises the count, and a 0 dBm drive line lowers it. The absolute count in the model (of order 50–100 identical lines per unit at 50 % margin) is more conservative than the ~1000 lines Krinner et al. reach with optimized cable diameters and attenuator placement; the conductivity integrals in the module are flagged for calibration against their Table 2.

## Why it matters for the link
A network node with a microwave processor pays this budget in addition to the optical interface, which is another reason (besides transduction, E7) that the baseline node in this thesis speaks optics natively. For flown hardware, the coolers in `qll/space/platform_thermal.py` have milliwatts at 4 K and microwatts at 100 mK, so the same arithmetic decides that a millikelvin processor does not fly.

## Key papers
- Krinner, S., et al. (2019). Engineering cryogenic setups for 100-qubit scale superconducting circuit systems. *EPJ Quantum Technology*, 6, 2. https://doi.org/10.1140/epjqt/s40507-019-0072-0
- Pobell, F. (2007). *Matter and Methods at Low Temperatures* (3rd ed.). Springer. https://doi.org/10.1007/978-3-540-46360-3
- Yeh, J.-H., LeFebvre, J., Premaratne, S., Wellstood, F. C., & Palmer, B. S. (2017). Microwave attenuators for use with quantum devices below 100 mK. *Journal of Applied Physics*, 121, 224501. https://doi.org/10.1063/1.4984894

## In this repo
`qll/hardware/cryo_wiring.py`; `learn/02/10`; `qll/space/platform_thermal.py`.
