# Continuous-Variable QKD

## The protocol (GG02)
Alice draws two quadratures from a Gaussian of variance $V_A$ (shot-noise units) and sends the coherent state; Bob homodynes a random quadrature; they reconcile in reverse (Bob's data are the reference) [grosshans2002]. No single-photon detectors: a telecom homodyne receiver at room temperature, which is why CV-QKD fits existing coherent-optical hardware and why satellite CV links are studied [dequal2021].

## The rate
$$K=\beta I_{AB}-\chi_{BE},\qquad I_{AB}=\tfrac12\log_2\frac{V+\chi_{\rm tot}}{1+\chi_{\rm tot}},$$
with $V=V_A+1$, $\chi_{\rm line}=1/T-1+\xi$, $\chi_{\rm hom}=(1+v_{\rm el})/\eta-1$, $\chi_{\rm tot}=\chi_{\rm line}+\chi_{\rm hom}/T$, and $\chi_{BE}$ the Holevo information from the symplectic eigenvalues of the covariance matrices [weedbrook2012] [laudenbach2018]. `qll/qkd/cv_qkd.py` implements the standard expressions. Two facts the code reproduces: the rate is below the PLOB bound at every transmittance, and the tolerance is to *excess noise*, not loss: with input-referred $\xi=1\%$ the asymptotic rate stays positive (scaling as $T$) at any loss, while $\xi=10\%$ kills it beyond ~10 dB. In practice finite-size effects, untrusted detector noise, and the phase reference (local oscillator transmitted or locally generated) set the loss limit at a few hundred kilometres of fiber [zhang2020cv].

## Why it matters for the link
Because excess noise referred to the channel input is what counts, a very lossy channel with quiet optics can still yield key; that is the argument for CV over free-space satellite paths in daylight where single-photon detectors saturate with background (T09 in `research/theories/`). The homodyne receiver's mode selectivity rejects background that a photon counter integrates.

## Key papers
- Grosshans, F., & Grangier, P. (2002). *Physical Review Letters*, 88, 057902. https://doi.org/10.1103/PhysRevLett.88.057902
- Weedbrook, C., et al. (2012). Gaussian quantum information. *Reviews of Modern Physics*, 84, 621. https://doi.org/10.1103/RevModPhys.84.621
- Laudenbach, F., et al. (2018). Continuous-variable quantum key distribution with Gaussian modulation: the theory of practical implementations. *Advanced Quantum Technologies*, 1, 1800011. https://doi.org/10.1002/qute.201800011
- Zhang, Y., et al. (2020). Long-distance continuous-variable quantum key distribution over 202.81 km of fiber. *Physical Review Letters*, 125, 010502. https://doi.org/10.1103/PhysRevLett.125.010502
- Dequal, D., et al. (2021). Feasibility of satellite-to-ground continuous-variable quantum key distribution. *npj Quantum Information*, 7, 3. https://doi.org/10.1038/s41534-020-00336-4

## In this repo
`qll/qkd/cv_qkd.py`; T09; the protocol figure `qkd_protocols_explorer` gains a CV curve in the next revision.
