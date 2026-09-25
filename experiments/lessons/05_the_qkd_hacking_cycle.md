# Lessons 05 — The QKD Hacking–Countermeasure Cycle as a Case Study

## The pattern
1. **2000–2004**: photon-number-splitting attacks on weak-laser BB84 are analysed; the fix, decoy states, is theoretical (2003) and demonstrated (2006) [hwang2003] [lo2005].
2. **2006–2010**: time-shift and detector-efficiency-mismatch attacks exploit the assumption that Bob's detectors are identical [qi2007]; the fix is random detector assignment and, structurally, measurement-device independence (2012) [lo2012].
3. **2010**: detector blinding by bright illumination controls the clicks of commercial systems [lydersen2010]; vendors add watchdog detectors and randomized efficiency; the structural fix is again MDI.
4. **2011–2016**: Trojan-horse, laser-seeding, and wavelength-dependent attacks probe the transmitter [jain2016]; isolators, filters, and power monitors follow.
5. **2018–2022**: device-independent QKD is demonstrated with loophole-free Bell tests [nadlinger2022] [zhang2022di], removing every device assumption at the price of rate.

## The three regularities
- **Every attack broke an assumption that was stated in the proof.** None broke the physics. The engineering lesson is to list the assumptions as requirements and test each one (this repository's `VERIFICATION_PLAN.md` does this for the models).
- **Point fixes precede structural fixes by about five years.** Watchdog detectors were sold in 2011; MDI systems in commercial form arrived around 2018.
- **The structural fix costs rate.** MDI halves the range per arm; DI costs orders of magnitude; twin-field recovers some of it. A Mars link that chooses DI (E10) accepts that cost knowingly.

## What this means for the thesis
The messenger fails closed rather than falling back to a computational key (REQ-APP-001) because the history says the hardware will be attacked and the safe response is refusal, not degradation. The hybrid with ML-KEM exists so that a broken QKD layer does not leave the channel *less* secure than a classical one.

## Sources
- Hwang, W.-Y. (2003). *Physical Review Letters*, 91, 057901. https://doi.org/10.1103/PhysRevLett.91.057901
- Qi, B., Fung, C.-H. F., Lo, H.-K., & Ma, X. (2007). Time-shift attack in practical quantum cryptosystems. *Quantum Information & Computation*, 7, 73.
- Lydersen, L., et al. (2010). *Nature Photonics*, 4, 686. https://doi.org/10.1038/nphoton.2010.214
- Jain, N., et al. (2016). *Contemporary Physics*, 57, 366. https://doi.org/10.1080/00107514.2016.1148333
- Nadlinger, D. P., et al. (2022). *Nature*, 607, 682. Zhang, W., et al. (2022). *Nature*, 607, 687.
