# Randomized Benchmarking in Practice

## The protocol
Apply $m$ random Clifford gates and then the single Clifford that inverts them; measure; repeat over sequences and lengths. The survival probability decays as $Ap^m+B$, and the average error per Clifford is $r=(1-p)(1-1/d)$ with $d=2$ for one qubit [magesan2011] [magesan2012]. State-preparation and measurement errors land in $A$ and $B$, not in $p$; that insensitivity is the reason RB became the standard gate benchmark and why a "99.9 % gate" claim means an RB number unless stated otherwise.

## What the model shows
`qll/circuits/benchmarking.py` implements one-qubit RB in Qiskit Aer with the 24-element Clifford group written as sequences of $H,S,S^\dagger,X,Y,Z$; with 1 % depolarizing error on every gate the fit gives $p\approx0.98$, i.e. about 2 gates per Clifford, and $r\approx0.9\%$ per Clifford; with no noise the survival stays above 99 % at $m=40$. Interleaved RB (insert the gate under test between random Cliffords) isolates one gate's error; simultaneous RB reveals crosstalk; cycle benchmarking extends to multi-qubit layers. What RB does *not* measure: coherent errors are averaged into an effective depolarizing rate by the randomization (the same twirling as `learn/01/09`), so an RB number can flatter a device whose errors are coherent, and leakage out of the qubit subspace needs its own protocol.

## Key papers
- Magesan, E., Gambetta, J. M., & Emerson, J. (2011). *Physical Review Letters*, 106, 180504. https://doi.org/10.1103/PhysRevLett.106.180504
- Magesan, E., Gambetta, J. M., & Emerson, J. (2012). Characterizing quantum gates via randomized benchmarking. *Physical Review A*, 85, 042311. https://doi.org/10.1103/PhysRevA.85.042311
- Magesan, E., et al. (2012). Efficient measurement of quantum gate error by interleaved randomized benchmarking. *Physical Review Letters*, 109, 080505. https://doi.org/10.1103/PhysRevLett.109.080505
- Proctor, T., et al. (2019). Direct randomized benchmarking for multiqubit devices. *Physical Review Letters*, 123, 030503. https://doi.org/10.1103/PhysRevLett.123.030503

## In this repo
`qll/circuits/benchmarking.py` (slow test); `learn/01/04`; the 99.9 % claims in `learn/02/04` and `02/05` are RB numbers.
