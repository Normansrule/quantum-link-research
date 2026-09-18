# T07 — Blind and delegated quantum computing over a network

**The idea.** A client with minimal quantum ability (prepare single qubits, or none at all) delegates a computation to a remote quantum server such that the server learns nothing about the input, the program, or the output (universal blind quantum computation, UBQC); verification protocols let the client check the server did it right. This is the "application layer" of a quantum internet beyond key distribution.

**Equations.** Measurement-based computation on a brickwork state with client-chosen measurement angles $\phi_j+\theta_j+r_j\pi$ hiding $\phi_j$ by one-time-pad rotations $\theta_j$ and bit flips $r_j$; the server sees uniformly random angles.

**Status.** Photonic demonstrations (Barz et al. 2012); verification and classical-client proposals (Fitzsimons & Kashefi 2017; Mahadev 2018 classical verification under computational assumptions).

**What it would change.** A Mars crew could use Earth's error-corrected machines privately; but every measurement round needs a classical message, so the round-trip latency makes MBQC-style delegation impractical at 20 minutes per round unless rounds are batched; a research question in its own right (candidate E11).

**Key papers.** Broadbent, A., Fitzsimons, J., & Kashefi, E. (2009). Universal blind quantum computation. *Proc. FOCS*, 517. https://doi.org/10.1109/FOCS.2009.36 Barz, S., et al. (2012). Demonstration of blind quantum computing. *Science*, 335, 303. Fitzsimons, J. F., & Kashefi, E. (2017). Unconditionally verifiable blind quantum computation. *PRA*, 96, 012303. Mahadev, U. (2018). Classical verification of quantum computations. *Proc. FOCS*. arXiv:1804.01082

**Repo hook.** None yet; a Phase 6 stretch goal for `qll/app/`.
