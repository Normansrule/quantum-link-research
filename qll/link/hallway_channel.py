"""The two-room link seen as a quantum channel: what happens to the polarization qubit of one photon between the
source in room A and the detectors in room B, from the same parts as qll/link/two_room.py.

Model
-----
A single photon reaches a click with probability eta = T eta_det (transmission times detection); otherwise it is
lost, and Bob knows it, because no detector fired: a heralded erasure of probability 1 - eta. Given a click, the
qubit has passed an intercept-resend station on a fraction f of pulses (if one is present) and the optics, whose
misalignment e_mis flips it in every basis (a depolarizing channel with Bloch shrink 1 - 2 e_mis), unless the click
came from a dark count or afterpulse, which carries a random bit. A dark click wins a gate with probability
w = (1 - eta) p_bg / Q, Q = eta + (1 - eta) p_bg, so the click-conditioned channel is
    R = (1 - w) R_optics R_station + w R_random,
whose Z and X error rate e = [eta e_s + (1 - eta) p_bg / 2] / Q, e_s = e_mis + (f/4)(1 - 2 e_mis), is the
single-photon error rate of the twin [ma2005] [bennett1984]. The figures of merit and capacities follow from
qll/circuits/qubit_channel.py; the heralded two-way quantum rate uses the erasure result [bennett1997erasure]
with the hashing bound on the heralded qubits [bennett1996mixed], and the repeaterless bound caps it
[pirandola2017]. For a laser source the decoy-state analysis bounds the single-photon error e_1, and
F_e >= 1 - 2 e_1 then certifies the single-photon channel, which is what a quantum network would use.
"""
from __future__ import annotations

import numpy as np

from qll.circuits import qubit_channel as Q
from qll.link import models
from qll.link.expected_session import expected_session
from qll.link.two_room import TwoRoomParts, config
from qll.qkd.plob_bound import plob_bits_per_use


def hallway_channel(parts: TwoRoomParts = TwoRoomParts(), eve_fraction: float = 0.0) -> dict:
    c = config(parts).with_(eve_fraction=eve_fraction)
    eta = models.signal_click_prob(c.with_(source_model="single_photon"))
    pb = models.background_click_prob(c)
    q = eta + (1 - eta) * pb
    w = (1 - eta) * pb / q
    R_sig = Q.compose(Q.intercept_resend_ptm(eve_fraction), Q.depolarizing_ptm(2 * c.misalignment_error))
    R = (1 - w) * R_sig + w * np.diag([1.0, 0.0, 0.0, 0.0])
    err = Q.basis_errors(R)
    s = expected_session(c)
    hashing = Q.hashing_bound(R)
    return {
        "eta": eta, "erasure": 1 - eta, "background_share": w, "ptm": R,
        "error_zx": err["z"], "error_y": err["y"],
        "entanglement_fidelity": Q.entanglement_fidelity(R), "average_fidelity": Q.average_fidelity(R),
        "entanglement_breaking": Q.is_entanglement_breaking(R),
        "decoy_e1_upper": s["e1_upper"],
        "certified_single_photon_fe": Q.certified_entanglement_fidelity(s["e1_upper"], s["e1_upper"]),
        "quantum_one_way": max(0.0, eta * hashing - (1 - eta)),
        "quantum_heralded": eta * hashing,
        "plob": plob_bits_per_use(eta),
        "classical_holevo_clicked": Q.holevo_capacity_unital(R),
        "private_bb84_clicked": Q.private_capacity_bb84(err["z"], err["x"]),
    }
