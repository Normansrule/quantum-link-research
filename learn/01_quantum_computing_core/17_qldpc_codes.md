# Quantum LDPC Codes

## The surface code's weakness
The surface code stores one logical qubit per patch: a distance-7 unrotated patch uses 85 data qubits plus 84 measurement qubits (the rotated layout, 49 + 48), and a thousand logical qubits need tens of thousands of physical ones. Its virtue is locality, every check touching four neighbours on a plane.

## Hypergraph products
Take two classical codes with parity-check matrices $H_1,H_2$. The hypergraph product [tillich2014] is the CSS code
$$H_X=[H_1\otimes I\;|\;I\otimes H_2^T],\qquad H_Z=[I\otimes H_2\;|\;H_1^T\otimes I],$$
which commutes automatically and has $n=n_1n_2+m_1m_2$, $k=k_1k_2+k_1^Tk_2^T$. With two repetition codes it *is* the surface code ($k=1$); with two [7,4,3] Hamming codes it stores **16 logical qubits in 58 physical qubits** at distance 3, against $16\times13=208$ data qubits for sixteen distance-3 unrotated surface patches (counts here are data qubits in both cases). `qll/circuits/qldpc.py` builds both, checks $H_XH_Z^T=0$ over GF(2), and counts $k$ by rank; the tests pin (13, 1), (41, 1), (85, 1) and (58, 16).

## The price
Checks stay sparse (low-density parity check), but they are no longer local on a plane: the Hamming product needs weight-7 checks connecting distant qubits. Neutral atoms that move (`learn/02/16`) and ions with all-to-all gates can provide that connectivity; superconducting chips need long-range couplers. The 2024 bivariate-bicycle "gross" code stores 12 logical qubits in 144 data qubits at distance 12 with weight-6 checks laid out on two planar layers, about ten times more efficient than the surface code at that distance [bravyi2024]. Decoding needs belief propagation plus ordered-statistics post-processing rather than matching [panteleev2021] [roffe2020].

## Why it matters for the link
T14 estimated a surface-code memory of ~1 250 qubits for one logical qubit held through a Mars round trip. A qLDPC memory holding many pairs at once would cut that per-pair cost by an order of magnitude, which is the difference between a node that stores one entangled pair and one that stores a multiplexed buffer (S08).

## Key papers
- Tillich, J.-P., & Zémor, G. (2014). Quantum LDPC codes with positive rate and minimum distance proportional to the square root of the blocklength. *IEEE Transactions on Information Theory*, 60, 1193. https://doi.org/10.1109/TIT.2013.2292061
- Breuckmann, N. P., & Eberhardt, J. N. (2021). Quantum low-density parity-check codes. *PRX Quantum*, 2, 040101. https://doi.org/10.1103/PRXQuantum.2.040101
- Bravyi, S., et al. (2024). High-threshold and low-overhead fault-tolerant quantum memory. *Nature*, 627, 778. https://doi.org/10.1038/s41586-024-07107-7
- Panteleev, P., & Kalachev, G. (2021). Degenerate quantum LDPC codes with good finite length performance. *Quantum*, 5, 585. https://doi.org/10.22331/q-2021-11-22-585

## In this repo
`qll/circuits/qldpc.py`; `learn/01/11` (stabilizer codes); T14.
