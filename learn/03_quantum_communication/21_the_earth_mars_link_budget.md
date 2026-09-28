# The Earth–Mars Link Budget, Stage by Stage

## Why a budget
A systems engineer does not ask whether a link "works"; they ask how many units of the product arrive per day, and which stage decides it. For an entanglement link the product is a pair good enough to teleport with (fidelity above 2/3), and the stages multiply. `qll/systems/mars_budget.py` composes the tested models of the lower layers into that multiplication for two architectures, and the [link budget page](https://normansrule.github.io/quantum-link-research/budget/) draws it as a stream that narrows at every stage.

## The stages
For a pair source at the Earth station, one photon stored locally and the other sent to Mars, on the day of closest approach (0.45 au):

| stage | factor | dB |
|---|---|---|
| source: 1000 modes × 10⁹ pairs/s | 10¹² pairs/s | |
| transmit optics | 0.8 | −1.0 |
| Earth atmosphere at 40° elevation, 1550 nm | 0.79 | −1.0 |
| diffraction: Gaussian beam, waist 0.5 m, onto a 4 m receiver | 1.8 × 10⁻⁹ | **−87.4** |
| pointing jitter, 100 nrad per axis | 0.96 | −0.2 |
| receiver optics and heralding detector | 0.63 | −2.0 |
| memories, write and read at both ends (¹⁷¹Yb⁺, 99 %) | 0.98 | −0.1 |
| availability: no conjunction, 50 % weather and operations | 0.5 | −3.0 |
| **total** | | **−94.7** |

That leaves 341 pairs per second, or 2.9 × 10⁷ per day. One stage, diffraction, is 92 % of the loss in decibels: a beam with a 0.5 m waist is about 130 km across when it reaches Mars at closest approach and nearly 800 km at the farthest, against a 4 m mirror [siegman1986]. Everything else is engineering margin. Pointing at 100 nrad is demanding but has been approached by deep-space optical terminals [bourgoin2013]; multiplexing a thousand modes needs a multimode memory [sinclair2014].

## Then the pair must wait
Mars keeps its half in a memory until Earth's two classical bits arrive. Taking one round trip, as requirement REQ-CAP-001 does, that is 7.5 minutes at closest approach and 44 minutes at the farthest (2.6 au). Over that wait the pair decays toward the useless mixture: with the trapped-ion memory the teleportation fidelity is 0.91 at closest approach and 0.73 at the farthest, still useful. Secret key (BBM92 [bennett1992bbm92], with the error rate $Q=2(1-f)/3$ of a Werner pair against the 11 % threshold [shor2000]) survives only near closest approach: 4 × 10⁶ bits per day there, none at the farthest, where $Q$ is 27 %.

## The memory trade, again
With the same link at the farthest point:

| memory | pairs per day | fidelity after 44 min |
|---|---|---|
| ¹⁷¹Yb⁺ hyperfine (1 h, 99 %) | 8.7 × 10⁵ | 0.73 |
| Eu:YSO, 6 h (1 %) | 88 | 0.91 |
| Eu:YSO, 13.1 h (0.5 %) | 22 | 0.94 |
| NV ¹³C, SiV, Rb/Cs ensembles | 10⁵–10⁶ | 0.50 (useless) |

Retrieval efficiency is paid at both ends, so the long-lived crystals deliver ten thousand times fewer pairs, but better ones. The ion is the only memory in the table that is both fast and useful at every point of the orbit. Compare lesson [03/20](20_where_a_fiber_repeater_is_worth_building.md), where the same retrieval penalty ruled the crystals out of fiber chains entirely.

## Architecture decides first
A relay at Sun–Earth L4 that sends one photon to each planet (the Micius two-downlink pattern [yin2017]) keeps a line of sight during conjunction, but both photons now cross astronomical distances and diffraction is paid twice: about 7 × 10⁻⁴ pairs per day at closest approach with the same hardware, 10⁻¹¹ of the Earth-source rate. That relay is useful as a store-and-forward node with its own memory, not as a two-downlink source. The first design decision is how many times a photon crosses an astronomical unit; the hardware only moves the result by decibels after that.

## Key papers
- Siegman, A. E. (1986). *Lasers*. University Science Books.
- Bourgoin, J.-P., et al. (2013). A comprehensive design and performance analysis of low Earth orbit satellite quantum communication. *New Journal of Physics*, 15, 023006. https://doi.org/10.1088/1367-2630/15/2/023006
- Yin, J., et al. (2017). Satellite-based entanglement distribution over 1200 kilometers. *Science*, 356, 1140–1144. https://doi.org/10.1126/science.aan3211
- Sinclair, N., et al. (2014). Spectral multiplexing for scalable quantum photonics using an atomic frequency comb quantum memory and feed-forward control. *Physical Review Letters*, 113, 053603. https://doi.org/10.1103/PhysRevLett.113.053603
- Bennett, C. H., Brassard, G., & Mermin, N. D. (1992). Quantum cryptography without Bell's theorem. *Physical Review Letters*, 68, 557–559. https://doi.org/10.1103/PhysRevLett.68.557

## In this repo
`qll/systems/mars_budget.py` (`MarsLinkDesign`, `budget`, `compare_memories`); `docs/js/budget_core.js` and `docs/budget/`; tests `test_mars_budget.py`, `test_site.py::test_js_mars_budget_matches_python`, and the page test.

## Exercises
1. Find the smallest Mars receiver that keeps 10⁵ useful pairs per day at the farthest point with the default design. How does it scale with the transmit waist?
2. Set the storage factor to 1 (the bits need only one light time). Does secret key now survive at the farthest point?
3. Keep everything else and switch the wavelength to 810 nm. Diffraction improves; what gets worse, and is the net change favourable?
