# T01 — A layered quantum-network stack

**The idea.** Classical networks scaled because of layering (physical → link → network → transport → application). The quantum analogue: a *physical* layer that attempts entanglement, a *link* layer that turns probabilistic attempts into a robust "entanglement delivered" service with quality (fidelity, time), a *network* layer that concatenates links by swapping, and a *transport* layer that turns entanglement into teleportation or key. Dahlberg et al. (2019) specified and ran a link layer on NV hardware; Pompili et al. (2022) ran a full stack on a three-node network.

**Equations.** Link-layer service: deliver a pair with fidelity $\ge F_{\min}$ within time $t_{\max}$; the physical layer offers success probability $p$ per attempt at rate $r$, so the delivery-time distribution is geometric with mean $1/(pr)$; memory decoherence bounds $t_{\max}$ by the $F(t)$ curve in `learn/03_quantum_communication/03`.

**Status.** Link and network layers demonstrated in the lab (2019–2022); standardization in IETF QIRG; no deployed multi-hop network with error-corrected links.

**What it would change.** The Mars link's protocols (E3, E5, E10) become instances of a stack with defined interfaces; scheduling with 20-minute heralds becomes a link-layer design problem with clear metrics.

**Key papers.** Wehner, S., Elkouss, D., & Hanson, R. (2018). *Science*, 362, eaam9288. Dahlberg, A., et al. (2019). A link layer protocol for quantum networks. *Proc. ACM SIGCOMM*, 159. https://doi.org/10.1145/3341302.3342070 Pompili, M., et al. (2022). Experimental demonstration of entanglement delivery using a quantum network stack. *npj Quantum Inf.*, 8, 121. Kozlowski, W., et al. (2023). Architectural principles for a quantum internet. IETF RFC 9340.

**Repo hook.** `qll/network/swapping_scheduler.py`, `sequence_adapter.py`; SeQUeNCe implements a stack-like model.
