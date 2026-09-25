# Twin-Field QKD: Where the √η Comes From

## The idea
In every point-to-point protocol a key bit needs a photon to cross the *whole* channel: rate $\propto\eta$. In measurement-device-independent QKD two photons must meet at a midpoint: $\propto\eta_A\eta_B=\eta$ for a symmetric link, no better. Twin-field QKD [lucamarini2018] has the midpoint detect a *single* photon that could have come from either side: the click probability is $\propto\sqrt{\eta_A}+\sqrt{\eta_B}\sim\sqrt\eta$ in amplitude terms, and the key is encoded in the *phase* between Alice's and Bob's weak coherent pulses, which the single-photon interference reveals only as a parity.

## The derivation in three lines
Alice and Bob send $|\sqrt{\mu}e^{i\phi_A}\rangle$ and $|\sqrt{\mu}e^{i\phi_B}\rangle$; after the channels the amplitudes are $\sqrt{\eta\mu}$ each; at the 50:50 midpoint splitter the output amplitudes are $\sqrt{\eta\mu/2}\,(e^{i\phi_A}\pm e^{i\phi_B})$, so detector D₀ clicks with probability $\approx\eta\mu(1+\cos(\phi_A-\phi_B))$ and D₁ with $\eta\mu(1-\cos(\phi_A-\phi_B))$ (small $\eta\mu$). A click therefore reveals the parity of the phase difference, which Alice and Bob turn into a bit, with a gain $\propto\eta\mu$ per *arm* where $\eta$ here is the half-channel transmittance $\sqrt{\eta_{\rm total}}$. The rate is $R\sim c\,\mu\sqrt{\eta_{\rm total}}$ with a prefactor $c$ of order 0.1 from sifting, decoy estimation, and the phase-matching probability [curty2019].

## What it costs
The two lasers must be phase-locked at the midpoint to a fraction of a wavelength over hundreds of kilometres of fibre: a reference tone, fast phase tracking, and either a shared laser or an optical frequency comb. Demonstrations reached 830 km (2022) and 1 000 km (2023) of ultra-low-loss fibre [wang2022tf] [liu2023tf]. The PLOB bound $-\log_2(1-\eta)\approx1.44\eta$ is beaten when $c\mu\sqrt\eta>1.44\eta$, i.e. $\eta<(c\mu/1.44)^2$, about $5\times10^{-5}$ (43 dB, ~215 km of fibre) for $c\mu=0.01$ (`qll/qkd/twin_field.py`, `crossover_transmittance`).

## Why it is not a repeater
It is a single-node scheme: the midpoint must be trusted-free but must exist, and the √η scaling does not compound. Two twin-field links in series give √η each, i.e. η^{1/2}·η^{1/2} = η overall unless a memory joins them, which returns to Chapter 4's repeater problem.

## Key papers
- Lucamarini, M., Yuan, Z. L., Dynes, J. F., & Shields, A. J. (2018). Overcoming the rate–distance limit of quantum key distribution without quantum repeaters. *Nature*, 557, 400. https://doi.org/10.1038/s41586-018-0066-6
- Curty, M., Azuma, K., & Lo, H.-K. (2019). Simple security proof of twin-field type quantum key distribution protocol. *npj Quantum Information*, 5, 64. https://doi.org/10.1038/s41534-019-0175-6
- Wang, S., et al. (2022). Twin-field quantum key distribution over 830-km fibre. *Nature Photonics*, 16, 154. https://doi.org/10.1038/s41566-021-00928-2
- Liu, Y., et al. (2023). Experimental twin-field quantum key distribution over 1000 km fiber distance. *Physical Review Letters*, 130, 210801. https://doi.org/10.1103/PhysRevLett.130.210801

## In this repo
`qll/qkd/twin_field.py`; the protocol figure; `learn/03/01`.
