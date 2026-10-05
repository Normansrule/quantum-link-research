"""Monitoring: the metrics of a session, the status indicators an operator watches, and the per-run summary.

Every metric the handoff lists as required is a field of SessionMetrics and is filled by every session; the future
metrics (latency, availability, finite-key composable bounds, decoy-state yields) are listed in
systems/see510/04_inputs_and_outputs.md as not implemented. Status follows the CONOPS: READY, then RUNNING, then one of
ACCEPTED or REJECTED with a reason. A rejection never claims to know why errors appeared: an error rate above the
threshold is "consistent with interception or excessive noise", because error counts alone cannot separate the two.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

REJECT_REASONS = {
    "auth": "classical message failed authentication (possible active tampering)",
    "insufficient": "too few detections to estimate the error rate and form a key block",
    "qber": "estimated error rate above threshold (consistent with interception or excessive noise)",
    "single_photon": "too few detections can be guaranteed to come from single photons (multi-photon pulses, or decoy statistics inconsistent with an honest channel)",
    "verify": "keys still differ after reconciliation",
    "no_key": "no secret key remains after the finite-size and leakage deductions",
}


@dataclass
class SessionMetrics:
    run_id: str
    scenario: str
    protocol: str
    seed: int
    distance_km: float
    channel_loss_db: float
    channel_transmittance: float
    adversary: str
    states_sent: int
    states_detected: int = 0
    detection_probability: float = 0.0
    sifted_bits: int = 0
    sample_bits: int = 0
    sample_errors: int = 0
    qber_estimate: float = 0.5
    qber_upper_bound: float = 1.0
    qber_true: float = 0.5               # simulation-only: error rate over all sifted bits (an operator never sees this)
    key_block_bits: int = 0
    ec_leaked_bits: int = 0
    ec_corrected_bits: int = 0
    residual_errors_before_verify: int = 0  # simulation-only
    source_model: str = "single_photon"
    gain_signal: float = 0.0             # detections per signal pulse (weak-coherent sources)
    gain_decoy: float = 0.0
    gain_vacuum: float = 0.0
    single_photon_fraction: float = 1.0  # lower bound on the single-photon share of signal detections
    e1_upper: float = 0.0                # upper bound on the single-photon error rate
    y1_lower: float = float("nan")       # decoy-state lower bound on the single-photon yield
    decoy_gain_deviation_sd: float = 0.0 # decoy gain against the honest prediction from the signal gain, in standard deviations
    naive_key_bits: int = 0              # simulation-only: key kept by an analysis that ignored multi-photon pulses
    alert: bool = False                  # error rate above the operator's alert level (key may still be accepted)
    verified: bool = False
    accepted: bool = False
    reject_reason: str = ""
    final_key_bits: int = 0              # output of privacy amplification (gross)
    secret_key_rate_bps: float = 0.0
    auth_mode: str = ""
    auth_bits_consumed: int = 0          # authentication key spent on this session (Wegman-Carter pads and hash key)
    auth_bits_refilled: int = 0          # final-key bits used to top the authentication pool back up
    net_key_bits: int = 0                # final key minus the authentication key this session spent (may be negative)
    key_delivered_bits: int = 0          # final key left for applications after topping the pool back up
    net_key_rate_bps: float = 0.0
    forgery_probability: float = 0.0     # chance a substituted transcript passes authentication
    keys_delivered_256: int = 0
    classical_messages: int = 0
    classical_bytes: int = 0
    eve_touched: int = 0
    eve_known_key_bits: int = 0          # simulation-only: key-block bits the adversary measured in the right basis
    pa_removed_bits: int = 0             # key-block bits removed by privacy amplification (block minus final key)
    execution_time_s: float = 0.0
    timestamp_utc: str = ""
    events: list = field(default_factory=list)

    def to_dict(self, with_events: bool = True) -> dict:
        d = asdict(self)
        if not with_events:
            d.pop("events")
        return d

    def event(self, step: str, level: str, message: str) -> None:
        self.events.append({"step": step, "level": level, "message": message})

    @property
    def status(self) -> str:
        return "ACCEPTED" if self.accepted else f"REJECTED ({self.reject_reason})"


def summary(m: SessionMetrics) -> str:
    """The per-run summary block of systems/see510/04_inputs_and_outputs.md."""
    rows = [
        ("Simulation Run ID", m.run_id), ("Scenario", m.scenario), ("Protocol", m.protocol),
        ("Distance", f"{m.distance_km:g} km"), ("Loss", f"{m.channel_loss_db:.2f} dB (transmittance {m.channel_transmittance:.4g})"),
        ("States Sent", f"{m.states_sent:,}"), ("States Detected", f"{m.states_detected:,} (p = {m.detection_probability:.3e})"),
        ("Sifted Key Bits", f"{m.sifted_bits:,}"), ("Errors", f"{m.sample_errors} of {m.sample_bits} sampled bits"),
        ("QBER", f"{100 * m.qber_estimate:.2f} % estimated (upper bound {100 * m.qber_upper_bound:.2f} %)"),
        ("Adversary", m.adversary), ("Key Accepted", "yes" if m.accepted else f"no: {REJECT_REASONS.get(m.reject_reason, m.reject_reason)}"),
        ("Final Usable Key Length", f"{m.final_key_bits:,} bits ({m.secret_key_rate_bps:,.1f} bit/s at the pulse rate)"),
        ("Authentication", f"{m.auth_mode}: {m.auth_bits_consumed} key bits spent; net key {m.net_key_bits:,} bits"
                           + (f" (forgery probability below {m.forgery_probability:.1e})" if m.forgery_probability else "")),
        ("Random Seed", str(m.seed)), ("Execution Time", f"{m.execution_time_s:.3f} s"),
    ]
    w = max(len(k) for k, _ in rows)
    return "\n".join(f"{k + ':':<{w + 1}} {v}" for k, v in rows)
