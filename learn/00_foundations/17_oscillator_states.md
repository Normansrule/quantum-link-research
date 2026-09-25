# Oscillator States: Coherent, Squeezed, Fock

## Three families
- **Fock** $|n\rangle$: definite photon number; antibunched, $g^{(2)}(0)=1-1/n$; the states single emitters produce one at a time.
- **Coherent** $|\alpha\rangle=D(\alpha)|0\rangle$: what a laser emits; Poissonian number with mean $|\alpha|^2$, $g^{(2)}(0)=1$, both quadrature variances at the vacuum value ($\tfrac14$ in the convention $x=(a+a^\dagger)/2$) [glauber1963]. Weak coherent pulses are the BB84 sources whose multiphoton tail decoy states protect.
- **Squeezed vacuum** $S(r)|0\rangle$: variances $e^{-2r}/4$ and $e^{2r}/4$, mean photon number $\sinh^2r$, made by parametric down-conversion below threshold [walls2008]. Squeezed light is the resource of continuous-variable QKD (`learn/03/17`), of gravitational-wave detectors, and, displaced onto a grid, of GKP codes (T03).

`qll/circuits/oscillator_states.py` computes the statistics with QuTiP and the tests pin them to the closed forms: for $\alpha=2$, $\bar n=4$ and $\mathrm{Var}x=\mathrm{Var}p=\tfrac14$; for $r=0.5$, $\mathrm{Var}x=e^{-1}/4$, $\mathrm{Var}p=e/4$, $\bar n=\sinh^20.5$.

## Why it matters for the link
The photon-number statistics of the source decide the security analysis (Poissonian: decoy states; heralded thermal from SPDC: `SpdcSource`), the homodyne receiver of CV-QKD measures exactly the quadratures whose variances appear here, and a memory that stores a squeezed or coherent state rather than a qubit is a different device (a bosonic memory, T03).

## Key papers
- Glauber, R. J. (1963). *Physical Review*, 131, 2766. https://doi.org/10.1103/PhysRev.131.2766
- Walls, D. F., & Milburn, G. J. (2008). *Quantum Optics* (2nd ed.). Springer. https://doi.org/10.1007/978-3-540-28574-8
- Lvovsky, A. I. (2015). Squeezed light. In *Photonics: Scientific Foundations, Technology and Applications* (Vol. 1). Wiley. arXiv:1401.4118

## In this repo
`qll/circuits/oscillator_states.py`; `learn/00/12`; `qll/qkd/cv_qkd.py`.
