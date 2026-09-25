# Quantum Walks and Quantum Thermodynamics

## Quantum walks
A walker whose direction is set by a coin qubit that is put in superposition each step spreads ballistically: the position standard deviation grows as $\sim0.54t$ for the Hadamard walk against $\sqrt t$ for a classical random walk [aharonov2001] [kempe2003]. `qll/circuits/quantum_walk.py` runs both and the test checks the $t$ versus $\sqrt t$ scaling by quadrupling $t$. Quantum walks give quadratic speedups for search on graphs and are the natural description of a photon in a waveguide array (`learn/02/19`); they are one of the few algorithmic primitives demonstrated on photonic hardware at useful size.

## Landauer's bound
Erasing one bit costs at least $k_BT\ln2$ of heat [landauer1961]: $2.9\times10^{-21}$ J at 300 K, $10^{-25}$ J at 10 mK. A thousand qubits reset a million times per second at 10 mK dissipate at least $10^{-16}$ W, negligible against the microwatts of the coldest stage (`learn/02/17`); the real reset cost is the mechanism (measurement plus feedback or a leaky resonator), orders of magnitude above the bound. Measurement itself has no Landauer cost; erasing its record does [bennett1982]. Maxwell's demon is exorcised by the same accounting: the demon must erase its memory.

## Quantum thermal machines
A qubit coupled to two baths is the smallest heat engine; its efficiency is bounded by Carnot and its power by the quantum speed limit [alicki1979] [kosloff2014]. For this repository the relevant application is the opposite direction: the thermal occupation $\bar n$ of Phase 1 is the equilibrium the environment imposes, and every reset, cooling, and heralding step is a small thermodynamic transaction against it.

## Key papers
- Aharonov, D., Ambainis, A., Kempe, J., & Vazirani, U. (2001). Quantum walks on graphs. *STOC '01*, 50. https://doi.org/10.1145/380752.380758
- Kempe, J. (2003). Quantum random walks: an introductory overview. *Contemporary Physics*, 44, 307. https://doi.org/10.1080/00107151031000110776
- Landauer, R. (1961). Irreversibility and heat generation in the computing process. *IBM Journal of Research and Development*, 5, 183. https://doi.org/10.1147/rd.53.0183
- Bennett, C. H. (1982). The thermodynamics of computation—a review. *International Journal of Theoretical Physics*, 21, 905. https://doi.org/10.1007/BF02084158
- Kosloff, R., & Levy, A. (2014). Quantum heat engines and refrigerators: continuous devices. *Annual Review of Physical Chemistry*, 65, 365. https://doi.org/10.1146/annurev-physchem-040513-103724

## In this repo
`qll/circuits/{quantum_walk,thermodynamics}.py`; `learn/00/06`.
