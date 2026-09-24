# Relativistic Effects on the Link

## Definitions
- **Gravitational redshift**: clocks at different potentials tick at different rates, $\Delta f/f=\Delta\Phi/c^2$. Between Earth's and Mars's surfaces, with the Sun's potential included, about $+3.5\times10^{-9}$: the Mars clock runs fast by 0.3 ms per day.
- **Doppler shift**: the Earth–Mars range rate reaches about 17 km/s, a fractional shift of $6\times10^{-5}$; a 193 THz carrier moves by 11 GHz, far more than any filter bandwidth, so the receiver must track it.
- **Shapiro delay**: extra light time from the Sun's potential, $\Delta t=\frac{2GM}{c^3}\ln\frac{r_E+r_M+d}{r_E+r_M-d}$, about 150–250 µs near conjunction and a few µs at opposition [shapiro1964].
- **Second-order Doppler (time dilation)**: $v^2/2c^2\sim2\times10^{-9}$, comparable to the redshift.

## Why a quantum link cares
A time-bin qubit's early and late bins are nanoseconds apart; the shape survives all of the above because they act as smooth stretches and shifts. What does not survive is the *prediction* of arrival time: a coincidence window of 1 ns after 20 minutes of flight demands the clocks agree to $10^{-12}$ and the path to 30 cm. The Doppler term alone moves an arrival by 0.4 ms per minute of uncorrected clock (`timing_budget_ns`), so the ephemeris drives the coincidence logic, as it does for the Deep Space Network's ranging [ashby2003]. Entangled-clock networks would turn this cost into a resource [komar2014].

## In this repo
`qll/space/relativity.py` computes all four terms from the Kepler ephemeris; the test pins them to their textbook magnitudes (Earth-surface potential $6.95\times10^{-10}$, Shapiro at conjunction 100–300 µs). `learn/03/07` covers the synchronization methods.

## Key papers
- Ashby, N. (2003). Relativity in the Global Positioning System. *Living Reviews in Relativity*, 6, 1. https://doi.org/10.12942/lrr-2003-1
- Shapiro, I. I. (1964). Fourth test of general relativity. *Physical Review Letters*, 13, 789. https://doi.org/10.1103/PhysRevLett.13.789
- Kómár, P., et al. (2014). A quantum network of clocks. *Nature Physics*, 10, 582. https://doi.org/10.1038/nphys3000

## Exercises
1. How far off is the Mars clock after one synodic period if never corrected for the redshift?
2. At what range rate does the Doppler shift of a 1550 nm carrier equal the 1 GHz bandwidth of a typical filter?
