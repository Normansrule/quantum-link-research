# Quantum simulation and chemistry

## Definitions
- **Feynman's argument (1982)**: simulating $n$ interacting quantum particles classically costs $2^n$; a quantum system can simulate another with polynomial resources.
- **Digital simulation**: Trotter–Suzuki product formulas $e^{-i(A+B)t}\approx(e^{-iAt/r}e^{-iBt/r})^r$; qubitization and linear-combination-of-unitaries give better scaling.
- **Analog simulation**: engineer a controllable system whose Hamiltonian *is* the model (optical lattices for Hubbard models, Rydberg arrays for spin models, trapped ions for long-range Ising); no error correction, but already at 100–1000 particles beyond exact classical simulation for dynamics.
- **Electronic structure**: second-quantized Hamiltonian $H=\sum h_{pq}a_p^\dagger a_q+\frac12\sum h_{pqrs}a_p^\dagger a_q^\dagger a_ra_s$, mapped to qubits by Jordan–Wigner or Bravyi–Kitaev; phase estimation gives energies to chemical accuracy (1.6 mHa) with fault tolerance; VQE is the NISQ heuristic.
- **Resource estimates**: FeMoco (nitrogenase cofactor) needs ~$10^6$ physical qubits and hours in surface-code estimates (Lee et al. 2021), which is the benchmark that sets scale for "useful."

## Equations
Trotter error $\lVert e^{-i(A+B)t}-(e^{-iAt/r}e^{-iBt/r})^r\rVert\le\frac{t^2}{2r}\lVert[A,B]\rVert$. Phase estimation cost $\tilde O(1/\epsilon)$ controlled evolutions for precision $\epsilon$.

## Key papers
- Feynman, R. P. (1982). Simulating physics with computers. *Int. J. Theor. Phys.*, 21, 467. https://doi.org/10.1007/BF02650179
- Lloyd, S. (1996). Universal quantum simulators. *Science*, 273, 1073. https://doi.org/10.1126/science.273.5278.1073
- Aspuru-Guzik, A., Dutoi, A. D., Love, P. J., & Head-Gordon, M. (2005). Simulated quantum computation of molecular energies. *Science*, 309, 1704. https://doi.org/10.1126/science.1113479
- Georgescu, I. M., Ashhab, S., & Nori, F. (2014). Quantum simulation. *Rev. Mod. Phys.*, 86, 153. https://doi.org/10.1103/RevModPhys.86.153
- McArdle, S., Endo, S., Aspuru-Guzik, A., Benjamin, S. C., & Yuan, X. (2020). Quantum computational chemistry. *Rev. Mod. Phys.*, 92, 015003. https://doi.org/10.1103/RevModPhys.92.015003
- Lee, J., et al. (2021). Even more efficient quantum computations of chemistry through tensor hypercontraction. *PRX Quantum*, 2, 030305.
- Ebadi, S., et al. (2021). Quantum phases of matter on a 256-atom programmable quantum simulator. *Nature*, 595, 227.

## In this repo
QuTiP is the small-system analog simulator we use for noise cross-checks; the repeater-chain rate model is itself a (classical) simulation of a quantum network.
