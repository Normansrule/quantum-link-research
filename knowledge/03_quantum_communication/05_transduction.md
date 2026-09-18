# Microwave-to-optical transduction

## Why it exists
Superconducting and spin processors speak microwaves (GHz); the only viable long-distance carrier is optical (hundreds of THz). A transducer must convert a single microwave photon to a single optical photon with high efficiency $\eta_t$, low added noise $n_{\rm add}$ (in photons), and enough bandwidth, while sitting at millikelvin next to the processor and being illuminated by an optical pump that heats it.

## Equations
$$\eta_t=\frac{4C_{\rm om}C_{\rm em}}{(1+C_{\rm om}+C_{\rm em})^2}\ \text{(for cavity electro-optomechanics at matched cooperativities)},\qquad F\lesssim\frac{\eta_t}{\eta_t+n_{\rm add}}$$
Useful for entanglement distribution only if $n_{\rm add}\lesssim\eta_t$ (roughly: the converted state must remain more signal than noise). Approaches: electro-optic (lithium niobate), piezo-optomechanical, magnonic, atomic (Rydberg) and rare-earth ensembles. Reported figures (2020–2025) span $\eta_t\sim10^{-3}$–$10^{-1}$ with $n_{\rm add}$ from ~1 to hundreds; entanglement-preserving transduction remains a milestone in progress (**TODO: verify current best**).

## What it means for a link
For the thesis the design stance is to avoid transduction entirely: use platforms with a native optical interface (color centers, ions, rare-earth memories) at the network nodes and keep microwave processors as end points behind a local optical interconnect. That stance is recorded as proposal E7 in `05_experiments/proposed/`.

## Key papers
- Lauk, N., et al. (2020). Perspectives on quantum transduction. *Quantum Sci. Technol.*, 5, 020501.
- Mirhosseini, M., Sipahigil, A., Kalaee, M., & Painter, O. (2020). Superconducting qubit to optical photon transduction. *Nature*, 588, 599. https://doi.org/10.1038/s41586-020-3038-6
- Higginbotham, A. P., et al. (2018). Harnessing electro-optic correlations in an efficient mechanical converter. *Nature Physics*, 14, 1038.
- Sahu, R., et al. (2023). Entangling microwaves with light. *Science*, 380, 718.
- Han, X., et al. (2021). Microwave-optical quantum frequency conversion. *Optica*, 8, 1050.
