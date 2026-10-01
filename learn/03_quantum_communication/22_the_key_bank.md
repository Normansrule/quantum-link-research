# The Key Bank: Storing Secrets Through Conjunction

## Qubits cannot wait, key can
An entangled pair is perishable. The trapped-ion memory holds it for about an hour, and every minute of waiting costs fidelity (lesson [03/21](21_the_earth_mars_link_budget.md)). Secret key is different. Once both ends have measured their photons and distilled a key, it is classical bits, and classical bits keep for as long as the store that holds them stays secret. That difference turns the key supply of the Earth–Mars link into a storage problem, and storage problems have a mature theory.

## Key does not need a memory
In BBM92 [bennett1992bbm92] each end measures its half of the pair in a random basis as soon as it has it; the bases are compared later over the classical channel, whenever those bits arrive. Nothing is stored except the measurement results. The key therefore sees the source's pair fraction $f_0$ reduced only by the background light (lesson 03/21), $f = \tfrac14 + w(f_0 - \tfrac14)$, and the Werner error rate $Q = 2(1-f)/3$ stays between 3.3 % and 5.1 % over the whole orbit, well under the 11 % limit [shor2000]. It pays neither the 44-minute wait nor the memory's retrieval efficiency, so even a 0.5 %-efficient crystal memory would not cost the key a single bit.

## A synodic period of key
Evaluated day by day with the baseline design (`qll/systems/key_ledger.py`), the link makes

| | secret bits per day |
|---|---|
| closest approach (0.45 au) | 2.2 × 10⁷ |
| farthest point (2.6 au) | 4.9 × 10⁵ |
| the 21 days around conjunction | 0 |
| mean over the 780-day cycle | 4.1 × 10⁶ |

The supply swings by a factor of 45 with range and stops completely at conjunction. A messenger that fails closed (REQ-APP-001) and lives off each day's key would have to refuse on every conjunction day, and on most of the far half of the orbit too if it spends more than about 5 × 10⁵ bits a day.

## Sizing the bank: the sequent-peak rule
Hydrologists size reservoirs against rivers that flood and run dry. The sequent-peak rule [loucks2017] accumulates the deficit of demand $d_t$ over supply $s_t$,

$$S_t = \max(0,\; S_{t-1} + d_t - s_t), \qquad S_0 = 0,$$

over two repetitions of a periodic record, so that a dry season straddling the end of the first repetition is caught in the second. The capacity $K = \max_t S_t$ is the smallest store that, starting full, never runs dry. The proof is one line: a bank of capacity $C$ starting full has level $L_t = \min(C, L_{t-1} + s_t - d_t)$, so $K - L_t = S_t$ for as long as nothing is refused. The test suite checks that identity day by day, the square-wave case (supply $s$ for $n_\text{on}$ days, none for $n_\text{off}$: $K = d\,n_\text{off}$), and that a bank 1 % smaller than $K$ does refuse. No bank of any size can carry a demand above the mean supply.

## What the numbers say
For a steady 10⁶ key bits per day (125 kB of one-time pad, or about 3,900 256-bit session keys), with no bank the messenger would refuse on 341 of the 780 days. A bank of **16.7 MB** at each end, starting full, refuses on none. The level drains through conjunction and on through the far half of the orbit, touches zero about five months after conjunction, when the daily key finally climbs back above the demand, and refills over the following three and a half months as Mars approaches. The whole trade is in `systems/trade_studies.md` (TS-7):

| daily demand | one-time pad | bank needed |
|---|---|---|
| 10⁵ bits | 12 kB | 0.26 MB |
| 10⁶ bits (baseline) | 125 kB | 16.7 MB |
| 4.1 × 10⁶ bits (the mean supply) | 518 kB | 209 MB |

The bank is negligible as storage. As a target it is not: a copy of the bank is a copy of every message it will ever encrypt. A one-time pad is information-theoretically secure [vernam1926] [shannon1949] only while the pad stays secret, which is why the bank's protection, not its size, is the open risk (R-10).

## Try it
The [link budget page](https://normansrule.github.io/quantum-link-research/budget/) draws the key made each day across a synodic period, the demand you set, the days a messenger with no bank must refuse, and the level of the bank that removes every refusal. Every change to the telescope, filter, or source moves the curve.

## On a table
Stage 7 of protocol [P09](../../experiments/protocols/P09_mars_link_on_a_table.md) steps a bench transmitter through a synodic period in under seven minutes (`python -m qll.analysis.bench_report schedule`), turns the logged counts into key, and sizes the bank from your own data.

## Key papers
- Bennett, C. H., Brassard, G., & Mermin, N. D. (1992). Quantum cryptography without Bell's theorem. *Physical Review Letters*, 68, 557–559. https://doi.org/10.1103/PhysRevLett.68.557
- Shor, P. W., & Preskill, J. (2000). Simple proof of security of the BB84 quantum key distribution protocol. *Physical Review Letters*, 85, 441–444. https://doi.org/10.1103/PhysRevLett.85.441
- Loucks, D. P., & van Beek, E. (2017). *Water resource systems planning and management: An introduction to methods, models, and applications*. Springer. https://doi.org/10.1007/978-3-319-44234-1
- Vernam, G. S. (1926). Cipher printing telegraph systems for secret wire and radio telegraphic communications. *Journal of the American Institute of Electrical Engineers*, 45, 109–115.
- Shannon, C. E. (1949). Communication theory of secrecy systems. *Bell System Technical Journal*, 28, 656–715. https://doi.org/10.1002/j.1538-7305.1949.tb00928.x

## In this repo
`qll/app/key_bank.py` (`sequent_peak`, `simulate`, `max_demand_for_capacity`); `qll/systems/key_ledger.py` (`daily_key_bits`, `ledger`); `docs/js/key_bank.js` and the budget page; tests `test_key_bank.py` (including REQ-APP-003) and `test_site.py::test_js_key_bank_matches_python`.

## Exercises
1. Double the Mars receiver diameter. By how much does the mean key supply rise, and how much smaller does the baseline bank become?
2. Find the largest daily demand that a 1 MB bank carries through every day of the cycle (`demand_for_capacity`). Which days decide it?
3. Suppose the bank must also cover one lost week of operations anywhere in the cycle. Add that week to the record and resize the bank. Is it worst to lose the week before conjunction or after?
