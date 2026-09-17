# Architecture

```mermaid
flowchart TB
  subgraph Layers
    A[app: messenger, hybrid KEM, AES-GCM] --> B[network: memories, repeaters, scheduling]
    B --> C[qkd: BB84, E91, decoy, MDI]
    C --> D[circuits: Bell, teleportation, CHSH, noise]
    D --> E[channels: fiber, free space, delay, background]
    E --> F[constants]
  end
```

Simulator responsibilities: Qiskit Aer (density-matrix and noisy circuits), Stim (large Clifford circuits and sampling), QuTiP (Lindblad cross-checks for T1/T2 and thermal baths), SeQUeNCe (discrete-event network simulation), Perceval (linear optics), kyber-py + cryptography (post-quantum hybrid application layer).

```mermaid
sequenceDiagram
  participant E as Earth node
  participant R as Relay
  participant M as Mars node
  E->>R: entangled photon (optical)
  R->>M: entangled photon (optical)
  R-->>E: swap herald (classical, at c)
  R-->>M: swap herald (classical, at c)
  E-->>M: 2 teleportation bits (classical, at c)
```

Three invariants enforced in code: no early classical reads (`light_time_delay.ClassicalMessage`), no cloning (Phase 2 guard), 2 bits per teleported qubit (Phase 2 record).
