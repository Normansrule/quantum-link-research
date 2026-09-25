# Furusawa 1998: unconditional continuous-variable teleportation

**Original.** Furusawa, Kimble, Polzik, and colleagues teleported a coherent state of light using two-mode squeezed vacuum as the shared resource, homodyne detection of the input against one half of the squeezed pair, and a classical feed-forward of the two quadrature results to displace the other half. Every input state was teleported ("unconditional": no post-selection), with fidelity $F=0.58\pm0.02$ against the classical limit of 0.5 for coherent states [furusawa1998].

**Physics.** The continuous-variable analogue of Bennett's protocol: the two classical bits become two real numbers (the homodyne outcomes), the Bell pair becomes an Einstein–Podolsky–Rosen (EPR) state approximated by finite squeezing $r$, and the fidelity for coherent inputs is $F=1/(1+e^{-2r})$, so 3 dB of squeezing gives 0.67 and infinite squeezing 1 [braunstein1998]. The classical limit is 1/2 (measure-and-prepare with no entanglement). Later work reached $F\approx0.83$ with 8–10 dB of squeezing.

**Simple recreation (Tier 3, graduate optics).** A 1064 nm laser, two optical parametric amplifiers for squeezing, three homodyne detectors, and an electro-optic modulator for the displacement: a $50–100k table. A classroom substitute is the simulation: `qll/circuits/oscillator_states.py` builds the squeezed vacuum in QuTiP and the fidelity formula above is one line; the P03 bench cannot squeeze.

**What went wrong historically.** The original fidelity was modest and the "quantum" threshold of 0.5 was debated (a no-cloning threshold of 2/3 applies if one asks that the output be the *best* copy); both thresholds have since been passed.

**Repo hook.** `qll/circuits/oscillator_states.squeezed_vacuum_stats`; the CV analogue of `teleportation.analytic_average_fidelity`; T03 (bosonic codes) and T09 (CV-QKD) for why CV states matter for the link.

- Furusawa, A., Sørensen, J. L., Braunstein, S. L., Fuchs, C. A., Kimble, H. J., & Polzik, E. S. (1998). Unconditional quantum teleportation. *Science*, 282, 706. https://doi.org/10.1126/science.282.5389.706
- Braunstein, S. L., & Kimble, H. J. (1998). Teleportation of continuous quantum variables. *Physical Review Letters*, 80, 869. https://doi.org/10.1103/PhysRevLett.80.869
- Yukawa, M., Benichi, H., & Furusawa, A. (2008). High-fidelity continuous-variable quantum teleportation toward multistep quantum operations. *Physical Review A*, 77, 022314. https://doi.org/10.1103/PhysRevA.77.022314
