# Security Proofs 101

## Definitions
- **Information-theoretic security**: Eve's information about the final key is bounded by ε regardless of her computing power; contrast with computational security (RSA, ML-KEM), where it is bounded only if a problem is hard.
- **Entropic uncertainty relation**: for two incompatible measurements $X$ and $Z$ on a system correlated with Bob (B) and Eve (E), $H(X|E)+H(Z|B)\ge q$, with $q=\log_2(1/c)$ and $c$ the maximum overlap of the bases ($c=1/2$ for BB84, so $q=1$) [berta2010]. Read: the more Bob can predict Alice's $Z$ outcomes, the less Eve can know about her $X$ outcomes.
- **Smooth min-entropy** $H_{\min}^\varepsilon(X|E)$: the operational quantity that privacy amplification converts into secret key (leftover hash lemma) [renner2005].
- **Composable security**: the key is ε-close to an ideal key that is uniform and independent of Eve, so it can be used in any later protocol with the ε's adding.
- **Collective vs coherent attacks**: Eve interacts identically and independently with each signal (collective) or arbitrarily with all of them (coherent); the entropy accumulation theorem extends collective-attack bounds to coherent attacks [arnon2018].
- **Finite-key effects**: with $n$ signals the parameter estimation has statistical error, so the rate carries corrections that vanish as $n\to\infty$ [scarani2008] [tomamichel2012].

## The chain of reasoning, as the code implements it
1. Alice and Bob measure; sifting keeps matched bases (`qll/qkd/sifting.py`).
2. They sacrifice a sample to estimate the error rate $Q$; with $n$ bits the estimate has error $\mu\sim\sqrt{\ln(1/\varepsilon)/n}$.
3. The uncertainty relation bounds Eve: $H_{\min}(X|E)\ge n(1-h_2(Q+\mu))$.
4. Error correction leaks $\text{leak}_{EC}=f\,n\,h_2(Q)$ bits (`error_correction.py`).
5. Privacy amplification compresses to $\ell=n(1-h_2(Q+\mu))-\text{leak}_{EC}-2\log_2(1/\varepsilon)$ bits (`privacy_amplification.py`); asymptotically $\ell/n\to1-2h_2(Q)$, the Shor–Preskill rate [shor2000] (`key_rate.py`).
6. Every classical message in steps 1–5 is authenticated with a pre-shared key: QKD *grows* keys; it cannot create the first one.

## Equations
$$\ell=n\left[1-h_2(Q+\mu)\right]-f\,n\,h_2(Q)-2\log_2\frac1\varepsilon,\qquad \mu=\sqrt{\frac{n+k}{nk}\cdot\frac{k+1}{k}\ln\frac{4}{\varepsilon}}$$
(the second expression is one standard finite-size correction for a sample of $k$ test bits [scarani2008]; the exact form differs between proofs). Device-independent: $H_{\min}\ge1-h_2\big(\tfrac{1+\sqrt{S^2/4-1}}{2}\big)$ per round from the CHSH value alone [acin2007] (`e91.py`).

## Visual
```mermaid
flowchart LR
  M[measure] --> S[sift] --> E[estimate Q from a sample] --> B["bound Eve: H_min ≥ n(1−h₂(Q+μ))"]
  B --> EC[error correction: leak f·n·h₂(Q)] --> PA["privacy amplification: ℓ = H_min − leak − 2log(1/ε)"]
  A[pre-shared authentication key] -.-> S & E & EC
```

## Key papers
- Shor, P. W., & Preskill, J. (2000). *Physical Review Letters*, 85, 441. https://doi.org/10.1103/PhysRevLett.85.441
- Renner, R. (2005). Security of quantum key distribution. PhD thesis, ETH Zurich. arXiv:quant-ph/0512258
- Berta, M., Christandl, M., Colbeck, R., Renes, J. M., & Renner, R. (2010). The uncertainty principle in the presence of quantum memory. *Nature Physics*, 6, 659. https://doi.org/10.1038/nphys1734
- Tomamichel, M., Lim, C. C. W., Gisin, N., & Renner, R. (2012). Tight finite-key analysis for quantum cryptography. *Nature Communications*, 3, 634. https://doi.org/10.1038/ncomms1631
- Scarani, V., & Renner, R. (2008). *Physical Review Letters*, 100, 200501. https://doi.org/10.1103/PhysRevLett.100.200501
- Arnon-Friedman, R., Dupuis, F., Fawzi, O., Renner, R., & Vidick, T. (2018). Practical device-independent quantum cryptography via entropy accumulation. *Nature Communications*, 9, 459. https://doi.org/10.1038/s41467-017-02307-4
- Portmann, C., & Renner, R. (2022). Security in quantum cryptography. *Reviews of Modern Physics*, 94, 025008. https://doi.org/10.1103/RevModPhys.94.025008

## In this repo
`qll/qkd/{key_rate,privacy_amplification,e91}.py`; `run_bb84` executes steps 1–5 end to end; `notebooks/02_qkd_session.ipynb` walks through a session with the numbers printed at each step.

## Exercises
1. With $n=10^5$ sifted bits, $Q=0.03$, $k=10^4$ test bits, $\varepsilon=10^{-10}$, compute $\mu$ and $\ell$; compare with the asymptotic $n(1-2h_2(Q))$.
2. Why does the intercept-resend attack leave $H_{\min}=0$ although Eve learns only half the bits on average?
