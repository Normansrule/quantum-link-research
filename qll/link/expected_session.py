"""The session of qll/link/protocol_bb84.py with every count replaced by its expectation: what a twin can say about
the key before a single pulse is sent, and what the lab pages compute in the browser.

Method
------
For each intensity class k (signal mu, decoy nu, vacuum 0) sent with share p_k, a Poisson pulse gives a signal click
with probability p_k^sig = 1 - exp(-k T eta), otherwise background with p_bg, so the gain and error rate are
    Q_k = p_k^sig + (1 - p_k^sig) p_bg,      E_k Q_k = p_k^sig e_d + (1 - p_k^sig) p_bg / 2       [ma2005]
(for a single-photon source, one class with p^sig = T eta). Half the detections are sifted [bennett1984]; the session
samples max(m_min, f_s n) of the signal-class sifted bits to estimate Q, bounds the single-photon fraction and error
rate with the decoy (or GLLP) bounds of qll/link/decoy.py evaluated at the expected counts, and keeps
    l = n_key s_1 [1 - h(e_1)] - f_EC n_key h(Q) - t - 2 log2(1/eps_pa)
bits after reconciliation and privacy amplification [shor2000] [lo2005], with f_EC = 1.2 standing in for Cascade's
disclosed parities [brassard1994]. Real sessions fluctuate around this; the full Monte Carlo is protocol_bb84.
"""
from __future__ import annotations

import math

from qll.link import models
from qll.link.config import LinkConfig
from qll.link.decoy import SinglePhotonBound, decoy_bound, gllp_bound
from qll.qkd.binary_entropy import h2

EC_EFFICIENCY = 1.2


def _round(x: float) -> int:
    """Half up, as JavaScript's Math.round, so the browser twin gives the same counts (Python's round is half even)."""
    return math.floor(x + 0.5)


def classes(c: LinkConfig) -> list[tuple[float, float, float, float]]:
    """(share, gain Q_k, error rate E_k, signal-click probability) for each intensity class the source sends."""
    t_eta = models.signal_click_prob(c.with_(source_model="single_photon"))
    pb, e_d = models.background_click_prob(c), models.signal_error(c)
    if c.source_model == "single_photon":
        mix = [(1.0, None)]
    elif c.source_model == "weak_coherent":
        mix = [(1.0, c.mu_signal)]
    else:
        mix = [(c.p_signal, c.mu_signal), (c.p_decoy, c.mu_decoy), (1 - c.p_signal - c.p_decoy, 0.0)]
    out = []
    for share, k in mix:
        p_sig = t_eta if k is None else 1 - math.exp(-k * t_eta)
        q = p_sig + (1 - p_sig) * pb
        e = (p_sig * e_d + (1 - p_sig) * pb / 2) / q if q > 0 else 0.5
        out.append((share, q, e, p_sig))
    return out


def expected_session(c: LinkConfig) -> dict:
    cl = classes(c)
    p_det = sum(s * q for s, q, _, _ in cl)
    qber = sum(s * q * e for s, q, e, _ in cl) / p_det if p_det > 0 else 0.5
    share, q_mu, e_mu, _ = cl[0]
    n_sifted = 0.5 * c.n_pulses * share * q_mu                      # signal class only, as the session keeps
    n_sample = max(c.min_sample_bits, math.ceil(c.sample_fraction * n_sifted))
    n_key = max(0.0, n_sifted - n_sample)
    q_upper = min(0.5, e_mu + math.sqrt(math.log(1 / c.eps_pe) / (2 * n_sample)))
    if c.source_model == "single_photon":
        bound = SinglePhotonBound(1.0, q_upper)
    elif c.source_model == "weak_coherent":
        bound = gllp_bound(c.mu_signal, q_mu, q_upper)
    else:
        n = [_round(c.n_pulses * s) for s, _, _, _ in cl]
        k = [_round(c.n_pulses * s * q) for s, q, _, _ in cl]
        dsift = 0.5 * k[1]
        bound = decoy_bound(c.mu_signal, c.mu_decoy, tuple(n), tuple(k), _round(dsift * cl[1][2]), _round(dsift), c.eps_pe)
    key = n_key * bound.single_fraction * (1 - h2(bound.e1_upper)) - EC_EFFICIENCY * n_key * h2(e_mu) \
        - c.verify_tag_bits - 2 * math.log2(1 / c.eps_pa)
    ok = n_sifted >= n_sample + c.min_key_block_bits and e_mu <= c.qber_threshold and bound.usable and key > 0
    return {"click_prob_per_pulse": p_det, "qber": qber, "signal_qber": e_mu, "sifted_bits": n_sifted,
            "sample_bits": n_sample, "key_block_bits": n_key, "qber_upper": q_upper,
            "single_fraction": bound.single_fraction, "e1_upper": bound.e1_upper,
            "key_bits": max(0, math.floor(key)) if ok else 0, "accepted": ok}
