# The Earth–Mars Link Budget, Stage by Stage

## Why a budget
A systems engineer does not ask whether a link "works"; they ask how many units of the product arrive per day, and which stage decides it. For an entanglement link the product is a pair good enough to teleport with (fidelity above 2/3), and the stages multiply. `qll/systems/mars_budget.py` composes the tested models of the lower layers into that multiplication for three architectures, and the [link budget page](https://normansrule.github.io/quantum-link-research/budget/) draws it as a stream that narrows at every stage.## The stages
For a pair source on a spacecraft at the lunar distance from Earth, one photon stored locally and the other sent to Mars, on the day of closest approach (0.45 au). Why the source is not on the ground is the subject of the section after next.

| stage | factor | dB |
|---|---|---|
| source: 1000 modes × 10⁹ pairs/s | 10¹² pairs/s | |
| transmit optics | 0.8 | −1.0 |
| diffraction: Gaussian beam, waist 0.5 m, onto a 4 m receiver | 1.8 × 10⁻⁹ | **−87.4** |
| pointing jitter, 100 nrad per axis | 0.96 | −0.2 |
| receiver optics and heralding detector | 0.63 | −2.0 |
| memories, write and read at both ends (¹⁷¹Yb⁺, 99 %) | 0.98 | −0.1 |
| availability: no conjunction, 50 % operations | 0.5 | −3.0 |
| **total** | | **−93.7** |

That leaves 431 pairs per second, or 3.7 × 10⁷ per day. One stage, diffraction, is 93 % of the loss in decibels: a beam with a 0.5 m waist is about 130 km across when it reaches Mars at closest approach and nearly 800 km at the farthest, against a 4 m mirror [siegman1986]. Everything else is engineering margin. Pointing at 100 nrad is demanding but has been approached by deep-space optical terminals [bourgoin2013]; multiplexing a thousand modes needs a multimode memory [sinclair2014].



## Then the pair must wait
Mars keeps its half in a memory until Earth's two classical bits arrive. Taking one round trip, as requirement REQ-CAP-001 does, that is 7.5 minutes at closest approach and 44 minutes at the farthest (2.6 au). Over that wait the pair decays toward the useless mixture: with the trapped-ion memory and the background light of the next section, the teleportation fidelity is 0.91 at closest approach and 0.72 at the farthest, still useful. If those stored pairs were used for key (BBM92 [bennett1992bbm92], with the error rate $Q=2(1-f)/3$ of a Werner pair against the 11 % threshold [shor2000]), $Q$ would reach 28 % at the farthest point and no key would survive. Key does not have to wait, though. Each end can measure its photon in a random basis the moment it has it and compare bases later over the classical channel, so the key sees $f_0$ reduced only by the background light: $Q$ is 3.3 % at closest approach and 5.1 % at the farthest, giving 2.2 × 10⁷ and 4.9 × 10⁵ secret bits per day, with no memory at all. (Through 0.40 this budget charged key for the memory wait, which wrongly confined key to the months near closest approach.) Lesson [03/22](22_the_key_bank.md) follows that key through a whole synodic period.

## The light that is not the signal
A photon counter cannot tell a signal photon from sunlight of the same colour, and the receiver at Mars is pointed at Earth, which is lit by the Sun. How much of that light gets in depends on whether Earth looks like a point or a disk. A diffraction-limited receiver accepts a single spatial mode, a patch of sky λ/D = 0.39 microradian across for 4 m at 1550 nm, while Earth's disk is 190 microradians across at closest approach and 32 at the farthest. The receiver resolves Earth, and its one mode sees only the patch around the transmitter. The photons per second it collects from an extended source of spectral radiance $L_\lambda$, in a filter of bandwidth $B$, are

$$N = \frac{L_\lambda\,\Delta\lambda\,\lambda^2}{hc/\lambda}, \qquad \Delta\lambda = \frac{\lambda^2 B}{c},$$

because one mode has étendue $A\Omega = \lambda^2$ [siegman1986]. The aperture area has dropped out; the test suite checks the formula against the blackbody result of $1/(e^{h\nu/kT}-1)$ photons per second per hertz per mode. Sunlit ground of albedo 0.3 has $L_\lambda = A E_\odot \cos z/\pi \approx 0.025$ W m⁻² sr⁻¹ nm⁻¹ at 1550 nm with the Sun overhead [hapke2012] [gueymard2004], which puts about 370 photons per second into each 100 MHz mode, and about 190 with the Sun 60° from the zenith. The signal in that mode is 1.4 per second at closest approach and 0.04 at the farthest. **A transmitter on the ground in daylight produces heralds that are more than 99 % sunlight.** A noise herald stores a maximally mixed state, so the delivered Werner fraction becomes $1/4 + w(f - 1/4)$ with $w$ the fraction of heralds that are signal.

At night the patch glows only with airglow, roughly 10⁻⁷ W m⁻² sr⁻¹ nm⁻¹ near 1.5 µm [rousselot2000], about 0.0015 photons per second per mode, and 99.9 % of heralds are signal. But a ground station sees Mars in a dark sky only when Mars is far enough from the Sun: with Mars at least 40° up and the Sun at least 12° down, the window is $\max(0, \varepsilon - 52°)$ of hour angle per day, capped at 100°, for an equatorial station, with $\varepsilon$ the solar elongation of Mars [meeus1998]. It is 28 % of the day at opposition and zero for 333 days of each 780-day synodic period. The ground source delivers 8 × 10⁶ pairs per day at closest approach and nothing at all for about eleven months around each conjunction, so it fails REQ-CAP-003.

Moving the source off Earth's disk changes the geometry. From the lunar distance, the transmitter sits 1 to 6 milliradians from Earth as seen from Mars, so Earth becomes an off-axis, unresolved source of flux $E_\odot\,p\,(R/d)^2\,\Phi(\alpha)$, with the Lambert-sphere phase function $\Phi(\alpha) = (\sin\alpha + (\pi-\alpha)\cos\alpha)/\pi$ [russell1916]. Only a fraction of it reaches the on-axis mode: the Airy wing $8/(\pi x^3)$, $x = \pi D\theta/\lambda$, for a clear aperture [born1999], and never less than the telescope's stray-light floor. With a floor of 10⁻⁹, 96 % of heralds are signal at the farthest point, where Mars sees a full Earth, and 99.997 % at closest approach, where Mars sees Earth's night side. A floor of 2.6 × 10⁻¹⁰ would reach 99 %: coronagraph-grade optics, and a real requirement on the Mars receiver (REQ-CAP-005, trade TS-6). From geostationary orbit the offset is only 0.1 mrad at maximum range and the diffraction wing alone leaks 4 × 10⁻⁹, which is why the baseline goes as far as the Moon.

## The memory trade, again
With the same link at the farthest point:

| memory | pairs per day | fidelity after 44 min, with background |
|---|---|---|
| ¹⁷¹Yb⁺ hyperfine (1 h, 99 %) | 1.1 × 10⁶ | 0.72 |
| Eu:YSO, 6 h (1 %) | 112 | 0.90 |
| Eu:YSO, 13.1 h (0.5 %) | 28 | 0.92 |
| NV ¹³C, SiV, Rb/Cs ensembles | 10⁵–10⁶ | 0.50 (useless) |

Retrieval efficiency is paid at both ends, so the long-lived crystals deliver ten thousand times fewer pairs, but better ones. The ion is the only memory in the table that is both fast and useful at every point of the orbit. Compare lesson [03/20](20_where_a_fiber_repeater_is_worth_building.md), where the same retrieval penalty ruled the crystals out of fiber chains entirely.

## Architecture decides first
A relay at Sun–Earth L4 that sends one photon to each planet (the Micius two-downlink pattern [yin2017]) keeps a line of sight during conjunction, but both photons now cross astronomical distances and diffraction is paid twice: about 2 × 10⁻⁵ pairs per day at closest approach with the same hardware, 10⁻¹² of the baseline rate, and its Earth receiver on the ground needs a dark sky too. That relay is useful as a store-and-forward node with its own memory, not as a two-downlink source. The first design decision is how many times a photon crosses an astronomical unit; the hardware only moves the result by decibels after that.

## On a table
Protocol [P09](../../experiments/protocols/P09_mars_link_on_a_table.md) builds this lesson's background physics on a bench, a lamp for the Sun and a white ball for Earth, with a digital twin (`qll/systems/bench_twin.py`) that predicts each reading: the ground transmitter in daylight is swamped, the one beside the ball is clean, and a single-mode receiver collects a λ² étendue of the ball's radiance whatever its distance.

## Key papers
- Siegman, A. E. (1986). *Lasers*. University Science Books.
- Bourgoin, J.-P., et al. (2013). A comprehensive design and performance analysis of low Earth orbit satellite quantum communication. *New Journal of Physics*, 15, 023006. https://doi.org/10.1088/1367-2630/15/2/023006
- Yin, J., et al. (2017). Satellite-based entanglement distribution over 1200 kilometers. *Science*, 356, 1140–1144. https://doi.org/10.1126/science.aan3211
- Sinclair, N., et al. (2014). Spectral multiplexing for scalable quantum photonics using an atomic frequency comb quantum memory and feed-forward control. *Physical Review Letters*, 113, 053603. https://doi.org/10.1103/PhysRevLett.113.053603
- Bennett, C. H., Brassard, G., & Mermin, N. D. (1992). Quantum cryptography without Bell's theorem. *Physical Review Letters*, 68, 557–559. https://doi.org/10.1103/PhysRevLett.68.557
- Gueymard, C. A. (2004). The sun's total and spectral irradiance for solar energy applications and solar radiation models. *Solar Energy*, 76, 423–453. https://doi.org/10.1016/j.solener.2003.08.039
- Russell, H. N. (1916). On the albedo of the planets and their satellites. *The Astrophysical Journal*, 43, 173–196.
- Hapke, B. (2012). *Theory of reflectance and emittance spectroscopy* (2nd ed.). Cambridge University Press.
- Born, M., & Wolf, E. (1999). *Principles of optics* (7th ed.). Cambridge University Press.
- Rousselot, P., Lidman, C., Cuby, J.-G., Moreels, G., & Monnet, G. (2000). Night-sky spectral atlas of OH emission lines in the near-infrared. *Astronomy and Astrophysics*, 354, 1134–1150.
- Meeus, J. (1998). *Astronomical algorithms* (2nd ed.). Willmann-Bell.

## In this repo
`qll/systems/mars_budget.py` (`MarsLinkDesign`, `budget`, `compare_memories`, `required_rejection`); `qll/channels/planetshine.py` (sunlit radiance, single-mode photon rate, Lambert phase, Airy wing); `qll/space/dark_window.py`; `docs/js/budget_core.js` and `docs/budget/`; tests `test_mars_budget.py`, `test_background_light.py`, `test_site.py::test_js_mars_budget_matches_python`, and the page test.

## Exercises
1. Find the smallest Mars receiver that keeps 10⁵ useful pairs per day at the farthest point with the default design. How does it scale with the transmit waist?
2. Set the storage factor to 1 (the bits need only one light time). How much does the teleportation fidelity at the farthest point improve, and why does the secret key per day not change at all?
3. Keep everything else and switch the wavelength to 810 nm. Diffraction improves and the Sun is 4.3 times brighter per nanometre; why does the Earthshine per 100 MHz mode still go down?
4. Put the space source at geostationary distance. On which days does the Airy wing, rather than the stray-light floor, set the background, and what receiver diameter would push it back under the floor?
5. Widen the filter to 10 GHz per mode. How does the herald purity change at the farthest point, and why does the receiver diameter not help?
