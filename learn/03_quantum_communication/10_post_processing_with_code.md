# Post-Processing With Code

The classical half of QKD, step by step, with the repository's functions. Run the cells in `notebooks/02_qkd_session.ipynb` to see every number.

## 1. Sifting (`qll.qkd.sifting.sift`)
Alice and Bob announce bases over an authenticated channel (two `ClassicalMessage`s, each ≥ d/c). Keep the matched rounds: half for unbiased bases; $p^2+(1-p)^2$ for biased ones, which approaches 1 [lo2005efficient].

## 2. Parameter estimation
Reveal a random sample, compute $Q$, discard the sample. The sample size is a trade: more test bits give a tighter $\mu$ but fewer key bits.

## 3. Information reconciliation (`qll.qkd.error_correction.reconcile`)
Two families:
- **Cascade** [brassard1994]: interactive binary search on parity blocks; efficiency $f\approx1.05$–1.1 but ~4 passes of two-way messages. At Mars that is 4 × (6–45 min).
- **LDPC** (low-density parity-check) one-way [elkouss2009]: Alice sends a syndrome once; $f\approx1.1$–1.2; one light time. The repository defaults to LDPC for exactly this reason, and the test `test_bb84_classical_time_respects_light_time` shows Cascade costing more than three extra round trips.

The leak is $f\,n\,h_2(Q)$; the Slepian–Wolf lower bound is $n\,h_2(Q)$ (`minimum_leak_bits`).

## 4. Error verification
Compare a short hash of the corrected keys; abort on mismatch (folded into `reconcile` as oracle correction in this model; a real implementation exchanges a 64-bit tag).

## 5. Privacy amplification (`qll.qkd.privacy_amplification`)
Choose a random Toeplitz matrix (two-universal family) over GF(2), publicly, and multiply: $\ell$ output bits from $n$ input bits with $\ell=H_{\min}-\text{leak}_{EC}-2\log_2(1/\varepsilon)$ [bennett1995pa]. `toeplitz_hash` implements it; `final_key_length` computes $\ell$.

## 6. Authentication
Every message above is tagged with a Wegman–Carter MAC keyed from a previous round's key (~64 bits per message) [wegman1981]; the messenger in `qll/app` then uses the key for AES-GCM and rotates it by budget.

## Worked numbers (from `run_bb84(40000, channel_error=0.05, allow_pseudo=True)`)
About 20 000 sifted bits, $Q\approx0.05$, secret fraction $1-2h_2(0.05)=0.427$ per sifted bit, leak $1.1\cdot n\cdot h_2(0.05)$, final key ≈ 0.4 × 20 000 minus the ε term. At Mars distance the same session takes at least one round trip for sifting plus one light time for the LDPC syndrome: 6–45 minutes before a single key bit exists, independent of the photon rate.

## Key papers
- Brassard, G., & Salvail, L. (1994). Secret-key reconciliation by public discussion. *EUROCRYPT '93*, LNCS 765, 410.
- Elkouss, D., Leverrier, A., Alléaume, R., & Boutros, J. J. (2009). Efficient reconciliation protocol for discrete-variable quantum key distribution. *IEEE ISIT*.
- Bennett, C. H., Brassard, G., Crépeau, C., & Maurer, U. M. (1995). Generalized privacy amplification. *IEEE Trans. Inf. Theory*, 41, 1915. https://doi.org/10.1109/18.476316
- Wegman, M. N., & Carter, J. L. (1981). New hash functions and their use in authentication and set equality. *J. Comput. Syst. Sci.*, 22, 265. https://doi.org/10.1016/0022-0000(81)90033-7
- Fung, C.-H. F., Ma, X., & Chau, H. F. (2010). Practical issues in quantum-key-distribution postprocessing. *Physical Review A*, 81, 012318. https://doi.org/10.1103/PhysRevA.81.012318
