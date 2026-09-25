# Entanglement Measures and Multipartite Bell Inequalities

## Mixed states
A pure state is entangled iff it is not a product; a mixed state is subtler. The Peres–Horodecki test: transpose one subsystem of $\rho$; if the result has a negative eigenvalue, the state is entangled, and for two qubits the converse holds too [peres1996] [horodecki1996sep]. The negativity $N=(\|\rho^{T_B}\|_1-1)/2$ measures how negative: for a Werner state of fully entangled fraction $f$, $N=\max(0,f-\tfrac12)$, zero exactly at the threshold where teleportation falls to 2/3 and CHSH stops being violated in the symmetric case. A witness $W=\tfrac12 I-|\Phi^+\rangle\langle\Phi^+|$ has $\mathrm{Tr}(W\rho)<0$ only for entangled states and needs three local measurement settings rather than full tomography, which is how experiments certify entanglement cheaply [guhne2009]. Concurrence, in `qll/circuits/bell.py`, is the third measure; all three agree on the Werner threshold.

## Three parties
For three qubits the Mermin combination $M=\langle XYY\rangle+\langle YXY\rangle+\langle YYX\rangle-\langle XXX\rangle$ obeys $|M|\le2$ for any local model, while the GHZ state gives $|M|=4$ *with certainty* — no statistics needed, every run of the four settings gives the same parity pattern [mermin1990] [greenberger1990]. For $n$ parties the violation grows as $2^{(n-1)/2}$. `qll/circuits/mermin.py` computes $M$ exactly and samples it in Stim (all four settings are Clifford), and the tests confirm $|M|=4$ for GHZ and $|M|\le2$ for a product state. Multipartite entanglement of this kind underlies conference key agreement and the entangled-clock network of T05.

## Key papers
- Peres, A. (1996). Separability criterion for density matrices. *Physical Review Letters*, 77, 1413. https://doi.org/10.1103/PhysRevLett.77.1413
- Horodecki, M., Horodecki, P., & Horodecki, R. (1996). Separability of mixed states: necessary and sufficient conditions. *Physics Letters A*, 223, 1. https://doi.org/10.1016/S0375-9601(96)00706-2
- Gühne, O., & Tóth, G. (2009). Entanglement detection. *Physics Reports*, 474, 1. https://doi.org/10.1016/j.physrep.2009.02.004
- Mermin, N. D. (1990). Extreme quantum entanglement in a superposition of macroscopically distinct states. *Physical Review Letters*, 65, 1838. https://doi.org/10.1103/PhysRevLett.65.1838
- Greenberger, D. M., Horne, M. A., Shimony, A., & Zeilinger, A. (1990). Bell's theorem without inequalities. *American Journal of Physics*, 58, 1131. https://doi.org/10.1119/1.16243

## In this repo
`qll/circuits/{entanglement_measures,mermin,bell}.py`; `learn/00/05`.

## Exercises
1. Show that the partial transpose of |Φ⁺⟩⟨Φ⁺| has eigenvalue −½ and that its negativity is ½.
2. Which single-setting expectation values does the witness $W$ need? Design the three measurements.
