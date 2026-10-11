"""Superdense coding through the hallway with polarization-entangled photons (experiment E19, milestone M2.6): the
photon that crosses the quantum channel carries more than one bit, because the pair was shared beforehand.

Physics
-------
The source shares |Phi+> = (|HH> + |VV>)/sqrt 2 between Alice and Bob. Alice turns it into any of the four Bell
states with waveplates on her photon (I, X, Z, XZ) and sends that photon across the hallway; Bob interferes it with
his photon on a 50/50 beamsplitter followed by a polarizing beamsplitter in each output. Linear optics separates
only three classes [mattle1996]:
    Psi-  : the photons leave by different beamsplitter outputs, with orthogonal polarizations,
    Psi+  : the same output, orthogonal polarizations,
    Phi+- : the same polarization (both Phi states give the same pattern),
so with three messages {Psi-, Psi+, Phi+} the ideal channel carries log2 3 = 1.585 bits per transmitted photon,
more than the 1 bit any single qubit can carry without prior entanglement [holevo1973] [bennett1992].

Two imperfections enter. A pair of visibility V is the Werner state V |Phi+><Phi+| + (1 - V) I/4, so after Alice's
encoding the intended Bell state has weight (1 + 3V)/4 and each other one (1 - V)/4. Two-photon interference of
visibility V_HOM [hong1987]: with probability V_HOM the photons are indistinguishable and the patterns above hold;
otherwise they leave the beamsplitter independently, so each Psi state gives the "different outputs" and "same
output" patterns half the time each (Psi+ and Psi- are then confused with each other half the time), while the
polarization correlation still marks Phi. The information per detected pair is the mutual information of that
confusion matrix with equally likely messages. Detection is post-selected, as in every linear-optics experiment,
so the comparison with the one-bit limit assumes fair sampling (losses that do not depend on the message).
"""
from __future__ import annotations

import numpy as np

BELL = ("Psi-", "Psi+", "Phi+", "Phi-")
CLASSES = ("Psi-", "Psi+", "Phi")


def decoder_matrix(v_hom: float) -> np.ndarray:
    """P(class | Bell state), rows Psi-, Psi+, Phi+, Phi-; columns Psi-, Psi+, Phi."""
    if not 0 <= v_hom <= 1:
        raise ValueError("v_hom in [0, 1]")
    d = 1 - v_hom
    return np.array([[1 - d / 2, d / 2, 0.0], [d / 2, 1 - d / 2, 0.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])


def bell_populations(message: str, visibility: float) -> np.ndarray:
    """After encoding `message` onto a Werner pair of visibility V."""
    p = np.full(4, (1 - visibility) / 4)
    p[BELL.index(message)] = (1 + 3 * visibility) / 4
    return p


def confusion(visibility: float, v_hom: float, messages=("Psi-", "Psi+", "Phi+")) -> np.ndarray:
    D = decoder_matrix(v_hom)
    return np.array([bell_populations(m, visibility) @ D for m in messages])


def bits_per_photon(visibility: float, v_hom: float, messages=("Psi-", "Psi+", "Phi+")) -> float:
    """I(message; class) with equally likely messages."""
    C = confusion(visibility, v_hom, messages)
    H = lambda q: float(-np.sum(q[q > 0] * np.log2(q[q > 0])))
    return H(C.mean(axis=0)) - float(np.mean([H(r) for r in C]))


def success(visibility: float, v_hom: float, messages=("Psi-", "Psi+", "Phi+")) -> float:
    C = confusion(visibility, v_hom, messages)
    return float(np.mean([C[i, CLASSES.index("Phi" if m.startswith("Phi") else m)] for i, m in enumerate(messages)]))
