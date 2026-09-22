# E9 — Herald-rate multiplexing at AU-scale loss

**Gap.** At $\eta\sim10^{-9}$–$10^{-11}$ a single-mode source gives pairs per hour. Temporal, spectral, and spatial multiplexing by $10^3$–$10^6$ is required and is well studied for fiber repeaters (multimode AFC memories) but not for a free-space link with a 20-minute herald delay, where the memory must hold *all* multiplexed modes until the herald returns.

**Cheapest version.** Simulation: multimode memory capacity $M$ vs required rate at Mars loss, using `link_budget.py` and `memory_decoherence.py`; then a bench analogue on the SPDC source with time-bin multiplexing (fiber delay loops) and software-delayed heralds.

**Cheapest version implemented (0.17.0).** `simulations/s08_multiplexing_at_au_scale.py`: at Mars maximum with a 1 m transmitter and a 10 m receiver, one pair per second needs a multiplexing factor M ≈ 2×10³ (about 50 for a 1 kbit/day key); with 30 cm optics on both ends M ≈ 2×10⁶. Apertures enter as D²w₀², multiplexing linearly; 10³ is demonstrated in multimode memories, 10⁶ is not. This replaces the unquantified "10³–10⁶" in the earlier text.

**Verifies.** REQ-NET-001 at planetary scale; quantifies the multimode capacity a Mars memory needs (AFC memories have shown > 1000 temporal modes).

**Key references.** Sinclair, N., et al. (2014). Spectral multiplexing for scalable quantum photonics using an atomic frequency comb quantum memory and feed-forward control. *Physical Review Letters*, 113, 053603. Businger, M., et al. (2022). Non-classical correlations over 1250 modes between telecom photons and 979-nm photons stored in ¹⁷¹Yb³⁺:Y₂SiO₅. *Nat. Commun.*, 13, 6438. **TODO: verify.**
