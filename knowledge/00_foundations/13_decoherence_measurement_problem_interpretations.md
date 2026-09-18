# Decoherence, the measurement problem, and what interpretations do and do not change

## Definitions
- **Decoherence**: entanglement of a system with its environment; tracing out the environment turns superpositions into mixtures in a preferred (pointer) basis. It explains why we do not see macroscopic superpositions and why $T_2$ exists; it does not by itself select one outcome.
- **Measurement problem**: the postulates give unitary evolution *and* collapse; when does one become the other? Decoherence answers "when interference becomes unobservable in practice," not "which outcome."
- **Interpretations** (Copenhagen, many-worlds, Bohmian, QBism, objective collapse): agree on every prediction in this repository; they differ on what the state *is*. Objective-collapse models (GRW, CSL) are the only ones that predict deviations, and experiments (matter-wave interferometry, LIGO-class mechanics) bound them.
- **Quantum Darwinism / einselection**: the environment redundantly records pointer-basis information; the reason classical records are robust.
- **Weak measurement, quantum non-demolition (QND)**: measuring an observable that commutes with the Hamiltonian so repeated measurements agree (dispersive readout of a transmon is QND for $Z$).

## Why it matters for engineering
Every noise channel in `docs/physics_module_design.md` is a decoherence model; every readout design decides which basis the environment (the amplifier chain) is allowed to learn. The Bell tests in `05_experiments/` are the empirical fact that no local classical story replaces the state.

## Key papers and texts
- Zurek, W. H. (2003). Decoherence, einselection, and the quantum origins of the classical. *Rev. Mod. Phys.*, 75, 715. https://doi.org/10.1103/RevModPhys.75.715
- Schlosshauer, M. (2007). *Decoherence and the Quantum-to-Classical Transition*. Springer.
- Ghirardi, G. C., Rimini, A., & Weber, T. (1986). Unified dynamics for microscopic and macroscopic systems. *Physical Review D*, 34, 470. https://doi.org/10.1103/PhysRevD.34.470
- Bassi, A., et al. (2013). Models of wave-function collapse, underlying theories, and experimental tests. *Rev. Mod. Phys.*, 85, 471.
- Braginsky, V. B., & Khalili, F. Ya. (1992). *Quantum Measurement*. Cambridge University Press. (QND.)
- Mermin, N. D. (1985). Is the moon there when nobody looks? Reality and the quantum theory. *Physics Today*, 38(4), 38.
