# Stabilizer Codes Hands-On

## Three codes in one framework
A stabilizer code is the joint +1 eigenspace of commuting Pauli operators [gottesman1997]. A single-qubit Pauli error anticommutes with some generators and flips their measured values; that syndrome names the error without revealing the logical state. `qll/circuits/stabilizer_codes.py` writes three codes as generator lists and uses Stim's Pauli-string algebra to compute every syndrome:

| Code | n | Generators | Corrects | Syndromes used |
|---|---|---|---|---|
| repetition [[3,1,1]] | 3 | ZZI, IZZ | one X error only | 4 of 4 |
| five-qubit [[5,1,3]] | 5 | XZZXI and cyclic shifts | any single-qubit error | 16 of 16 (perfect code) |
| Steane [[7,1,3]] | 7 | three X-type, three Z-type (Hamming) | any single-qubit error | 22 of 64 |

The five-qubit code is *perfect*: its 16 syndromes exactly cover the identity and 15 single errors [laflamme1996]. Steane's code wastes syndromes but is CSS (X and Z checks separate), which makes its Cliffords transversal [steane1996]; the surface code (`learn/01/03`) trades both for locality.

## A memory experiment
Prepare $|0\rangle_L$, flip each data qubit with probability $p$, measure the Z checks, correct by lookup, measure $Z_L$. For the repetition code the logical error is $3p^2$ (two of three flipped) and Stim reproduces it; the seven-qubit code is *worse* than the three-qubit code against pure bit flips at the same $p$ (21 two-error pairs against 3) — the price of protecting against Z errors too. The lesson generalizes: code distance sets the exponent, the number of ways to fail sets the prefactor, and below threshold the exponent wins.

## Key papers
- Gottesman, D. (1997). *Stabilizer codes and quantum error correction*. PhD thesis, Caltech. arXiv:quant-ph/9705052
- Laflamme, R., Miquel, C., Paz, J. P., & Zurek, W. H. (1996). Perfect quantum error correcting code. *Physical Review Letters*, 77, 198. https://doi.org/10.1103/PhysRevLett.77.198
- Steane, A. M. (1996). *Physical Review Letters*, 77, 793. https://doi.org/10.1103/PhysRevLett.77.793
- Gidney, C. (2021). Stim: a fast stabilizer circuit simulator. *Quantum*, 5, 497. https://doi.org/10.22331/q-2021-07-06-497

## In this repo
`qll/circuits/stabilizer_codes.py`; S04 (repetition code vs distance); `surface_code_lattice.svg`.

## Exercises
1. List the 15 single-qubit Paulis on five qubits and their syndromes; verify no two coincide.
2. Why does the Steane code need 6 syndrome bits for 21 errors while the five-qubit code needs 4 for 15?
