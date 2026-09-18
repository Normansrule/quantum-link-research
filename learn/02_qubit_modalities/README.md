# Qubit modalities: how people actually build qubits

Every platform below is a real two-level system that satisfies, to some degree, the DiVincenzo criteria: (1) well-characterized scalable qubits, (2) initialization, (3) coherence long compared with gate time, (4) a universal gate set, (5) qubit-specific readout, plus for networks (6) conversion between stationary and flying qubits and (7) faithful transmission of flying qubits. The two network criteria are why this repository exists: a computer does not need them; a link does.

## The comparison that matters (order-of-magnitude, 2024–2026 public results; re-verify before citing)

| Platform | What the qubit *is* | Operating T | T1 / T2 | 2-qubit gate time | Best 2-qubit fidelity | Qubits in one device | Native photon interface | Maturity |
|---|---|---|---|---|---|---|---|---|
| Superconducting transmon | lowest two levels of a nonlinear LC oscillator (Josephson junction) | 10–20 mK | 0.1–1 ms / 0.1–0.5 ms | 20–100 ns | 99.5–99.9% | 100–1000 | none (microwave) → needs transduction | highest: below-threshold surface code (2024) |
| Silicon spin (quantum dot) | electron or hole spin in a gate-defined dot in ²⁸Si | 0.1–1 K | s / ms (nuclear: min) | 10–100 ns | 99.5–99.8% | ~10 | none | foundry-compatible; small arrays |
| Diamond NV / SiV | electron spin of a color center, with ¹³C nuclear registers | 4 K (NV network), 0.1 K (SiV cavities) | ms–s / ms; nuclear up to min | µs | ~99% | ~10 per node | **yes**, optical 637/737 nm | best *network* record: 3-node teleportation, metropolitan links |
| Trapped ion (Yb⁺, Ca⁺, Ba⁺) | hyperfine or optical levels of a single ion in an RF trap | room-temperature trap, laser-cooled ion | > 1 h / s–min | 10–100 µs | 99.9% (best of any platform) | 30–60 fully connected | **yes**, UV/visible photons | highest gate fidelity; slow |
| Neutral atom (Rb, Cs, Sr, Yb) | hyperfine levels, entangled via Rydberg blockade | µK atoms, room-temp apparatus | s / ms | ~1 µs | 99.5% | 1000+ | yes, in principle | fastest-growing; logical processor (2024) |
| Photonic | polarization / path / time-bin of one photon; or squeezed modes | room temperature (sources); detectors at 1–4 K | no decoherence in flight; loss instead | fusion measurements, probabilistic | — | 200+ modes (Gaussian boson sampling) | **is** the flying qubit | native to communication; computing needs fusion networks |
| Topological (Majorana) | parity of a pair of Majorana zero modes in a superconductor–semiconductor wire | 10–50 mK | topologically protected in theory | — | not demonstrated | 0 verified logical qubits | none | contested: see `../../experiments/lessons/` |
| Bosonic (cat, GKP) | encoded state of a microwave cavity mode | 10–20 mK | ms | ~µs | bias-preserving | 1–10 | none | beyond-break-even QEC (2023) |

## How to read the modality files
Each file has the same sections: the physics of the two levels, the Hamiltonian, how the qubit is **built** (materials, fabrication, cryogenics, control chain), how it is **modeled** (what simulator, what noise model), what the **best published results** are, **what has failed** or is contested, and **what it means for a link** (photon interface, memory time versus light time).

For a bench-scale build the only affordable modality is the diamond NV ensemble (about $100–$500, `experiments/bench/hardware_guide.md`); the photonic bench (SPDC, ~$5k+) is the affordable *flying*-qubit platform.

## Reviews to read first
- Ladd, T. D., et al. (2010). Quantum computers. *Nature*, 464, 45. https://doi.org/10.1038/nature08812
- Kjaergaard, M., et al. (2020). Superconducting qubits: current state of play. *Annu. Rev. Condens. Matter Phys.*, 11, 369.
- Burkard, G., Ladd, T. D., Pan, A., Nichol, J. M., & Petta, J. R. (2023). Semiconductor spin qubits. *Rev. Mod. Phys.*, 95, 025003. https://doi.org/10.1103/RevModPhys.95.025003
- Bruzewicz, C. D., Chiaverini, J., McConnell, R., & Sage, J. M. (2019). Trapped-ion quantum computing: progress and challenges. *Appl. Phys. Rev.*, 6, 021314. https://doi.org/10.1063/1.5088164
- Henriet, L., et al. (2020). Quantum computing with neutral atoms. *Quantum*, 4, 327.
- Flamini, F., Spagnolo, N., & Sciarrino, F. (2019). Photonic quantum information processing: a review. *Rep. Prog. Phys.*, 82, 016001.
- Doherty, M. W., et al. (2013). The nitrogen-vacancy colour centre in diamond. *Phys. Rep.*, 528, 1. https://doi.org/10.1016/j.physrep.2013.02.001
