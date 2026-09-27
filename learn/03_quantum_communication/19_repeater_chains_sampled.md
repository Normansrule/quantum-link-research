# Repeater Chains, Sampled: Why Rate Is Not Enough

## The protocol in one paragraph
A memory-based repeater [briegel1998] cuts a link of length $L$ into $2^n$ segments. Each segment tries to share an entangled pair: both nodes send a photon to a detector at the midpoint, and one attempt in $1/p_0$ succeeds, with $p_0=p_{\rm src}\,\eta(L_0/2)^2$ and $\eta=10^{-0.02L/{\rm km}}$ in fiber. Each success is announced by a classical herald, and the pair waits in quantum memories. When two neighbouring pairs both exist, the node between them performs a Bell measurement (entanglement swapping) and, with probability $P_s$, the two short pairs become one long one; otherwise both are lost and must be made again. After $n$ rounds of swapping one pair spans the whole link [sangouard2011].

## The closed form, and what sampling says about it
The usual summary [sangouard2011] replaces each level's waiting time by the expected maximum of two geometric waits,
$$E[\max(X,Y)]=\frac{2}{p}-\frac{1}{p(2-p)},$$
divides by $P_s$, and multiplies by the attempt period (one herald round trip). `qll/network/swapping_scheduler.py` implements it; `qll/network/repeater_chain.py` turns it into the rate $1/T_n$ and the crossover distance with direct transmission (the 393 km headline for 1 s memories and 8 segments).

Above the first level this is an approximation, because a level's waiting time is no longer geometric. `qll/network/repeater_montecarlo.py` samples the protocol exactly: geometric attempt counts per segment, the later of two children at each swap, and a restart of both subtrees after a failed swap. With 20 000 runs per case (standard error about 0.6 %):

| segments | length | sampled mean / closed form |
|---|---|---|
| 1 | 300 km | 0.993 ± 0.007 |
| 2 | 100 km | 0.989 ± 0.006 |
| 4 | 400 km | 0.964 ± 0.006 |
| 8 | 800 km | 0.919 ± 0.005 |

So the closed form is exact without nesting and conservative with it: for $P_s=0.5$ it overestimates the waiting time by about 4 % with two levels and 8 % with three, and the rates quoted from it are slightly low. The gap grows as swaps become reliable (19 % for 8 segments at $P_s=1$), because with frequent failed swaps a level's waiting time is dominated by restarts and is nearly geometric, which is what the closed form assumes. The distribution is also very wide: for 800 km and 8 segments the median run takes 18 s, the mean 24 s, and one run in a hundred takes more than 97 s. That tail is what a memory must survive.

![Sampled waiting times against the closed form](../../docs/figures/repeater_sampled.svg)

## Rate is not enough
A chain can beat direct transmission and still deliver useless pairs. Each swap of Werner pairs with fraction $f$ gives $f'=f^2+(1-f)^2/3$, and every second of storage pulls the fraction toward $1/4$ with the memory time $T$. At the 393 km crossover (8 segments, 1 s memories, $f_0=0.95$), the chain delivers 0.80 pairs per second against 0.69 for direct transmission, but the end-to-end teleportation fidelity is **0.58**, below the classical limit of 2/3. The headline crossover is a statement about rate only.

Two ways out. Purify between levels (learn [03/11](11_purification_and_repeater_generations.md)), paying pairs for fidelity; or improve the parts: with $f_0=0.99$, 100 s memories, and 16 segments, a 1000 km chain delivers 0.11 pairs per second at fidelity 0.87, while direct transmission manages $5\times10^{-13}$ per second. For Earth to Mars there is no fiber at all, which is why the thesis routes the link through free-space relays; but the same bookkeeping of rate, storage time, and fidelity decides whether those relays work.

## Try it
The [repeater lab](https://normansrule.github.io/quantum-link-research/repeater/) plays one sampled run at a time (segments heralding, stored pairs fading as they decay, swaps joining them, failed swaps in red) next to the average rate against distance. Its JavaScript model is a line-by-line port of `repeater_chain.py`, checked against it to $10^{-12}$ by `tests/test_site.py`, and its sampler matches the Python Monte Carlo to within 3 %.

## Key papers
- Briegel, H.-J., Dür, W., Cirac, J. I., & Zoller, P. (1998). Quantum repeaters: The role of imperfect local operations in quantum communication. *Physical Review Letters*, 81, 5932–5935. https://doi.org/10.1103/PhysRevLett.81.5932
- Sangouard, N., Simon, C., de Riedmatten, H., & Gisin, N. (2011). Quantum repeaters based on atomic ensembles and linear optics. *Reviews of Modern Physics*, 83, 33–80. https://doi.org/10.1103/RevModPhys.83.33
- Azuma, K., Tamaki, K., & Lo, H.-K. (2015). All-photonic quantum repeaters. *Nature Communications*, 6, 6787. https://doi.org/10.1038/ncomms7787
- Pirandola, S., Laurenza, R., Ottaviani, C., & Banchi, L. (2017). Fundamental limits of repeaterless quantum communications. *Nature Communications*, 8, 15043. https://doi.org/10.1038/ncomms15043

## In this repo
`qll/network/repeater_chain.py`, `swapping_scheduler.py`, `repeater_montecarlo.py`, `purification.py`; `qll/viz/repeater_sampled.py`; `docs/js/repeater_core.js` and `docs/repeater/`; tests `test_repeater_montecarlo.py` and `test_site.py::test_js_repeater_model_matches_python`.

## Exercises
1. With `mean_chain_time_s`, reproduce how the sampled-to-closed-form ratio falls from 0.94 at $P_s=0.3$ to 0.81 at $P_s=1$ for 8 segments. Plot the distribution of a level-1 waiting time for both and compare it with a geometric distribution of the same mean.
2. At 393 km with 1 s memories, what elementary fraction $f_0$ makes the end-to-end teleportation fidelity exceed 2/3? Is that more or less realistic than a memory ten times longer?
3. Add a memory cutoff to `sample_chain_time_s`: discard a stored pair older than $3T$. How much does the mean time grow for 1 s memories at 400 km?
