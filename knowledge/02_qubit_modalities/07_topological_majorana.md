# Topological qubits and Majorana zero modes

## The idea
A pair of Majorana zero modes (MZMs) at the ends of a one-dimensional topological superconductor shares one fermionic parity; the qubit is stored non-locally in that parity, so local noise cannot dephase it, and gates are performed by braiding (exchanging) modes, which is topologically protected. The Kitaev chain (2001) is the toy model; the physical proposal is a semiconductor nanowire (InAs, InSb) with strong spin–orbit coupling, proximitized by a superconductor (Al), in a magnetic field [Lutchyn 2010; Oreg 2010].

## Equations
Kitaev chain $H=-\mu\sum_jc_j^\dagger c_j-\sum_j\left(t\,c_j^\dagger c_{j+1}+\Delta\,c_jc_{j+1}+\text{h.c.}\right)$ is topological for $\lvert\mu\rvert<2t$, $\Delta\ne0$; Majorana operators $\gamma=\gamma^\dagger$, $\gamma^2=1$, with $c=(\gamma_1+i\gamma_2)/2$. Braiding two MZMs applies $\exp(\pm\frac\pi4\gamma_i\gamma_j)$, a Clifford gate; Majorana braiding alone is not universal (a $T$ gate needs a non-topological operation).

## Status: contested, and a lesson in evidence
- The 2012 "signatures" (zero-bias conductance peaks) turned out to be reproducible by trivial Andreev bound states from disorder.
- The 2018 *Nature* report of a quantized Majorana conductance was **retracted in 2021** after reanalysis of the data.
- Microsoft's 2025 "Majorana 1" paper reports interferometric single-shot parity measurements in a topological-gap-protocol device; the measurement is real, but whether the modes are topological Majoranas remains disputed by independent groups (2025–2026). **TODO: track the literature before citing any topological-qubit claim.**

This modality is included because the thesis is about learning from failed iterations: it is the clearest case in the field where a compelling theory outran the evidence, and where the corrective mechanism (data sharing, replication, retraction) worked.

## What it means for a link
Nothing yet: no photon interface, no demonstrated logical qubit, dilution-refrigerator temperatures.

## Key papers
- Kitaev, A. Y. (2001). Unpaired Majorana fermions in quantum wires. *Physics-Uspekhi*, 44, 131. arXiv:cond-mat/0010440
- Nayak, C., et al. (2008). Non-Abelian anyons and topological quantum computation. *Rev. Mod. Phys.*, 80, 1083. https://doi.org/10.1103/RevModPhys.80.1083
- Lutchyn, R. M., Sau, J. D., & Das Sarma, S. (2010). *Physical Review Letters*, 105, 077001. Oreg, Y., Refael, G., & von Oppen, F. (2010). *Physical Review Letters*, 105, 177002.
- Mourik, V., et al. (2012). Signatures of Majorana fermions in hybrid superconductor-semiconductor nanowire devices. *Science*, 336, 1003. https://doi.org/10.1126/science.1222360
- Zhang, H., et al. (2018). Quantized Majorana conductance. *Nature*, 556, 74. **Retracted 2021.**
- Frolov, S. (2021). Quantum computing's reproducibility crisis: Majorana fermions. *Nature*, 592, 350. (Commentary on the retraction.)
- Microsoft Azure Quantum, et al. (2025). Interferometric single-shot parity measurement in InAs–Al hybrid devices. *Nature*, 638, 651. **TODO: verify DOI and subsequent critiques.**

## Exercises
1. Show that $\gamma_1\gamma_2$ has eigenvalues $\pm i$ and relate them to the fermion parity $(-1)^{c^\dagger c}$.
2. List three non-topological mechanisms that produce a zero-bias conductance peak.
