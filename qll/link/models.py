"""Closed-form expectations for the two-site BB84 link, used to validate the Monte Carlo simulation and to draw the
analytic curves on every plot.

Physics
-------
Channel transmittance T_ch = 10^(-(alpha L + loss_extra)/10) [qll/channels/fiber_loss.py]; the probability that a
pulse produces a signal click at Site B is mu_s = T_ch 10^(-loss_rx/10) eta_det. A gate with no signal click fires on
background with probability p_bg = p_dark + p_xt (a random bit), so the detection probability per pulse is
    p_det = mu_s + (1 - mu_s) p_bg.
After sifting (1/2 of detections with matched bases, [bennett1984]) the expected error rate is
    Q = [mu_s e_s + (1 - mu_s) p_bg / 2] / p_det,   e_s = q (1 - e_mis) + (1 - q) e_mis,  q = f_E / 4,
because an intercept-resend adversary acting on a fraction f_E of pulses measures in the wrong basis half the time
and then causes an error half the time at Site B [bennett1984] [nielsen2010]; e_mis is the misalignment error. With
an ideal single-photon source the asymptotic secret fraction per sifted bit is r = 1 - 2 h(Q) [shor2000], positive
below Q of about 11 %. These are expectations; a session of N pulses fluctuates around them.
"""
from __future__ import annotations

import math

from qll.channels.fiber_loss import transmittance
from qll.link.config import LinkConfig
from qll.qkd.binary_entropy import h2


def channel_transmittance(c: LinkConfig) -> float:
    return transmittance(c.distance_km, c.attenuation_db_per_km) * 10 ** (-c.extra_loss_db / 10)


def channel_loss_db(c: LinkConfig) -> float:
    return c.attenuation_db_per_km * c.distance_km + c.extra_loss_db


def signal_click_prob(c: LinkConfig) -> float:
    return channel_transmittance(c) * 10 ** (-c.receiver_loss_db / 10) * c.detector_efficiency


def background_click_prob(c: LinkConfig) -> float:
    return min(1.0, c.dark_count_prob + c.crosstalk_click_prob)


def detection_prob(c: LinkConfig) -> float:
    mu, pb = signal_click_prob(c), background_click_prob(c)
    return mu + (1 - mu) * pb


def signal_error(c: LinkConfig) -> float:
    q = c.eve_fraction / 4
    return q * (1 - c.misalignment_error) + (1 - q) * c.misalignment_error


def expected_qber(c: LinkConfig) -> float:
    mu, pb, pd = signal_click_prob(c), background_click_prob(c), detection_prob(c)
    return (mu * signal_error(c) + (1 - mu) * pb / 2) / pd if pd > 0 else 0.5


def expected_sifted(c: LinkConfig) -> float:
    return 0.5 * c.n_pulses * detection_prob(c)


def asymptotic_secret_fraction(qber: float) -> float:
    return max(0.0, 1 - 2 * h2(qber)) if qber < 0.5 else 0.0


def asymptotic_secret_bits(c: LinkConfig) -> float:
    """Reference upper estimate: sifted bits after sampling times 1 - 2 h(Q); no finite-size or reconciliation cost."""
    return expected_sifted(c) * (1 - c.sample_fraction) * asymptotic_secret_fraction(expected_qber(c))


def max_distance_km(c: LinkConfig, step_km: float = 0.5, limit_km: float = 500.0) -> float:
    """Largest distance (on a step_km grid) at which the expected error rate stays at or below the threshold."""
    d = 0.0
    while d <= limit_km and expected_qber(c.with_(distance_km=d)) <= c.qber_threshold:
        d += step_km
    return d - step_km


def hoeffding_margin(n_sample: int, eps: float) -> float:
    """Upper confidence margin on a sampled error rate: sqrt(ln(1/eps) / (2 n)) [hoeffding1963]."""
    return math.sqrt(math.log(1 / eps) / (2 * n_sample)) if n_sample > 0 else 1.0
