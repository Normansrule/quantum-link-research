# Aspect 1982: Bell test with time-varying analyzers

**Original.** Aspect, Dalibard, and Roger placed acousto-optic switches in each arm of a calcium-cascade photon-pair source so that the analyzer setting was changed every 10 ns while the photons were in flight over 6 m; a setting could not have been known at the source when the pair was emitted. The result $S=2.697\pm0.015$ violated the CHSH bound by 5 standard deviations and addressed the locality loophole for the first time [aspect1982]. The 2022 Nobel Prize recognized this line of work.

**Physics.** The locality loophole: if the settings are fixed before emission, a local model could in principle let the source "know" them. Switching faster than $L/c$ closes it in spirit; the 2015 loophole-free tests used quantum random number generators and space-like separation of the choices, closing it rigorously [hensen2015] [giustina2015] [shalm2015].

**Simple recreation (Tier 2).** The P03 bench with the basis chosen by the QRNG board on each shot and the choice time-tagged: with 5 m arms the light time is 17 ns, so the switching cannot be faster than the flight in a classroom, but the *record* of choice times versus detection times demonstrates the logic exactly (E6). Use liquid-crystal retarders or a fast Pockels cell as the switch (~$1–3k) and the FPGA time-tagger to prove that each choice was made after the pair was created. Expect $S\approx2.3$–2.6.

**What went wrong historically.** The switches were periodic, not random, so a determined local model could exploit the pattern; and detector efficiency left the fair-sampling assumption in place. Both were closed only in 2015.

**Repo hook.** `qll/circuits/chsh.chsh_sampled_stim` refuses a non-quantum entropy source (INV-7); `hardware/randomness.SerialQrng` reads the board; the pass/fail number is the CHSH value with settings verified random by `health_check`.

- Aspect, A., Dalibard, J., & Roger, G. (1982). *Physical Review Letters*, 49, 1804. https://doi.org/10.1103/PhysRevLett.49.1804
- Hensen, B., et al. (2015). *Nature*, 526, 682. https://doi.org/10.1038/nature15759
- Giustina, M., et al. (2015). *Physical Review Letters*, 115, 250401. https://doi.org/10.1103/PhysRevLett.115.250401
- Shalm, L. K., et al. (2015). *Physical Review Letters*, 115, 250402. https://doi.org/10.1103/PhysRevLett.115.250402
