# Noise Spectroscopy and Dynamical Decoupling

## The filter-function picture
Pure dephasing by classical noise with spectral density $S(\omega)$ makes coherence decay as $e^{-\chi(T)}$ with $\chi=\frac{1}{2\pi}\int S(\omega)\frac{F(\omega T)}{\omega^2}d\omega$, where the filter function $F$ depends only on where the $\pi$ pulses sit [cywinski2008] [biercuk2011]. Free induction passes low frequencies ($F=4\sin^2\omega T/2$), which is why $T_2^*$ is short; a Hahn echo blocks DC ($F=16\sin^4\omega T/4$); an $n$-pulse CPMG sequence is a band-pass centred at $\omega=\pi n/T$. `qll/circuits/noise/filter_functions.py` computes $F$ for any pulse times and integrates $\chi$ against a spectrum; the tests confirm the two closed forms and that for $1/f$ noise more pulses give more coherence.

## Using the qubit as a spectrum analyser
Scan $n$ at fixed $T$ and $\chi$ samples $S(\pi n/T)$: the qubit reports its own environment's spectrum. Superconducting qubits see $1/f$ flux and charge noise plus discrete two-level-system peaks [bylander2011]; NV centres see the ¹³C bath's Larmor frequency and its harmonics; silicon spins see residual ²⁹Si. Every extension of $T_2$ by decoupling in the modality table (`learn/02`) is this filter moved away from where the noise is, and the P02 echo and CPMG measurements are the bench version.

## Limits
Pulses are imperfect (finite length, rotation errors accumulate as $n$ grows) and decoupling does nothing against $T_1$: the ceiling is $2T_1$. Decoupling also does not protect a *gate*; it protects idle qubits, which is why memories (idle by definition) benefit most — the 13-hour rare-earth coherence of the memory table is ZEFOZ plus decoupling (`learn/03/16`).

## Key papers
- Cywiński, Ł., Lutchyn, R. M., Nave, C. P., & Das Sarma, S. (2008). How to enhance dephasing time in superconducting qubits. *Physical Review B*, 77, 174509. https://doi.org/10.1103/PhysRevB.77.174509
- Biercuk, M. J., Doherty, A. C., & Uys, H. (2011). Dynamical decoupling sequence construction as a filter-design problem. *Journal of Physics B*, 44, 154002. https://doi.org/10.1088/0953-4075/44/15/154002
- Bylander, J., et al. (2011). Noise spectroscopy through dynamical decoupling with a superconducting flux qubit. *Nature Physics*, 7, 565. https://doi.org/10.1038/nphys1994
- Medford, J., et al. (2012). Scaling of dynamical decoupling for spin qubits. *Physical Review Letters*, 108, 086802. https://doi.org/10.1103/PhysRevLett.108.086802

## In this repo
`qll/circuits/noise/filter_functions.py`; `learn/00/04` (echo); P02 steps 6–7; the memory table.
