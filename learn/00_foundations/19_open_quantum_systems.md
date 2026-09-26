# Open Quantum Systems: from a Bath to T₁

## The derivation in one paragraph
Couple a qubit $H_S=\tfrac\omega2\sigma_z$ to a bath through $\sigma_x\otimes B$, assume the bath forgets quickly compared with the qubit's relaxation (Born–Markov) and average over fast oscillations (secular approximation). The qubit's reduced density matrix then obeys a Lindblad equation whose rates are the bath's noise spectrum at the transition frequency: emission at $J(\omega)(\bar n+1)$, absorption at $J(\omega)\bar n$ [breuer2002]. The total population relaxation rate is $\Gamma_1=J(\omega)(2\bar n+1)$ and the steady state satisfies detailed balance, $\langle\sigma_z\rangle=-1/(2\bar n+1)=-\tanh(\hbar\omega/2k_BT)$.

## Checked independently
`qll/circuits/bloch_redfield.py` hands QuTiP's Bloch–Redfield solver an ohmic thermal spectrum and fits $T_1$ from the evolution; it reproduces $T_1(T)=T_1(0)/(2\bar n+1)$ to 10⁻³ at 20, 100 and 300 mK. That law is what Phase 1's generalized amplitude damping channel (`qll/circuits/noise/thermal.py`) assumes, so the thermal model at the base of the whole repository now has two independent derivations in code: the Kraus map and the master equation.

## Where it stops
Born–Markov fails for structured baths with long memory (two-level systems in amorphous oxides, the phonon bottleneck), for strong coupling, and when the qubit's own dynamics are as fast as the bath's correlation time. The phonon-driven $T_1(T)$ of the NV centre (P02, `qll/analysis/relaxation_fit.py`) is a case where a different bath (lattice phonons with an Orbach and a Raman channel) sets the temperature dependence, which is exactly the comparison REQ-THM-003 will make with data.

## Key papers
- Breuer, H.-P., & Petruccione, F. (2002). *The Theory of Open Quantum Systems*. Oxford University Press. https://doi.org/10.1093/acprof:oso/9780199213900.001.0001
- Lindblad, G. (1976). On the generators of quantum dynamical semigroups. *Communications in Mathematical Physics*, 48, 119. https://doi.org/10.1007/BF01608499
- Johansson, J. R., Nation, P. D., & Nori, F. (2012). QuTiP: an open-source Python framework for the dynamics of open quantum systems. *Computer Physics Communications*, 183, 1760. https://doi.org/10.1016/j.cpc.2012.02.021

## In this repo
`qll/circuits/bloch_redfield.py`, `qll/circuits/noise/thermal.py`; REQ-THM-001, REQ-THM-003.
