"""One BB84 session between Site A and Site B, following the concept of operations step by step.

Steps (CONOPS 1-10)
-------------------
1. Configure: one LinkConfig; independent random streams for Site A, the adversary, the channel, Site B, and the
   protocol's public choices, all spawned in a fixed order from the seed, so a run reproduces bit for bit.
2. Verify readiness: the configuration validates; the sites exchange an authenticated session-start message.
3-4. Quantum transmission: Site A prepares N states [bennett1984]; the channel (and any adversary) acts; Site B
   measures.
5. Sifting: Site B announces which gates clicked and its bases; Site A announces its bases on those; both keep the
   matches.
6. Parameter estimation: a public random sample of the sifted bits is disclosed and compared; the estimate Q and its
   upper bound Q_U = Q + sqrt(ln(1/eps_pe)/(2m)) [hoeffding1963] are computed. Abort if too few bits remain or Q
   exceeds the threshold.
7. Reconciliation and verification [qll/link/reconciliation.py]; abort if the keys differ.
8. Privacy amplification by Toeplitz hashing to l = floor(n (1 - h(Q_U)) - leak_EC - t - 2 log2(1/eps_pa)) bits
   [renner2005] [qll/qkd/privacy_amplification.py]; abort if l <= 0. With Q_U in place of Q this is the Shor-Preskill
   rate with a statistical margin, not a composable finite-key proof [shor2000].
9. Deliver: only an accepted key is deposited in both sites' key stores, in 256-bit keys with shared identifiers.
10. Record: every metric and event goes into SessionMetrics for the logger.
Any authentication failure on the classical channel aborts the session at the step where it occurs.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import math
import time
from dataclasses import dataclass

import numpy as np

from qll.link.adversary import AdversaryRecord, InterceptResend, PhotonNumberSplitting
from qll.link.decoy import SinglePhotonBound, decoy_bound, gllp_bound
from qll.link.authentication import AuthKeyPool
from qll.link.classical_channel import AuthenticatedChannel, AuthenticationFailure
from qll.link.codec import pack, pack_indices, unpack, unpack_indices
from qll.link.config import LinkConfig
from qll.link.key_store import SiteKeyManager
from qll.link.models import channel_loss_db, channel_transmittance, hoeffding_margin
from qll.link.monitor import SessionMetrics
from qll.link.quantum_channel import FiberChannel
from qll.link.reconciliation import reconcile, verify
from qll.link.site_a import DECOY, SIGNAL, VACUUM, PreparedStates, SiteA
from qll.link.site_b import Detections, SiteB
from qll.qkd.binary_entropy import h2
from qll.qkd.privacy_amplification import toeplitz_hash

PROTOCOL = {"single_photon": "BB84 (ideal single-photon source, prepare and measure)",
            "weak_coherent": "BB84 (attenuated laser without decoys, prepare and measure)",
            "weak_coherent_decoy": "BB84 with decoy states (attenuated laser, prepare and measure)"}
STREAMS = ("site_a", "adversary", "channel", "site_b", "protocol")


@dataclass(frozen=True)
class QuantumRecord:
    """What the quantum part of a session produced: Site A's states, Site B's detections, and any adversary record.
    Simulated by default; read from an experiment's log by qll/link/hardware_log.py."""
    states: PreparedStates
    det: Detections
    adversary: AdversaryRecord | None = None


@dataclass
class SessionResult:
    config: LinkConfig
    metrics: SessionMetrics
    key_a: np.ndarray                 # Site A's final key (empty if rejected)
    key_b: np.ndarray                 # Site B's final key
    channel: AuthenticatedChannel
    adversary: AdversaryRecord | None
    delivered_ids: list


def auth_key_for(c: LinkConfig) -> bytes:
    """The pre-shared authentication key of the simulation (a stand-in for one exchanged when the sites were set up)."""
    return hashlib.sha256(f"qll-link-psk/{c.seed}".encode()).digest()


def make_adversary(c: LinkConfig, rng: np.random.Generator):
    if c.eve_fraction <= 0:
        return None
    if c.eve_attack == "pns":
        eta_b = 10 ** (-c.receiver_loss_db / 10) * c.detector_efficiency
        return PhotonNumberSplitting(c.eve_fraction, rng, c.mu_signal, channel_transmittance(c), eta_b)
    return InterceptResend(c.eve_fraction, rng)


def adversary_label(c: LinkConfig) -> str:
    if c.eve_fraction <= 0:
        return "none"
    name = "photon-number splitting" if c.eve_attack == "pns" else "intercept-resend"
    return f"{name} on {100 * c.eve_fraction:g} % of pulses"


def simulate_quantum(c: LinkConfig) -> QuantumRecord:
    """Steps 3-4 alone: the simulated quantum transmission, from the same seeded streams run_session uses."""
    rngs = dict(zip(STREAMS, (np.random.default_rng(s) for s in np.random.SeedSequence(c.seed).spawn(len(STREAMS)))))
    adversary = make_adversary(c, rngs["adversary"])
    states = SiteA(rngs["site_a"]).prepare(c.n_pulses, c)
    out = FiberChannel(c, rngs["channel"], adversary).transmit(states)
    return QuantumRecord(states, SiteB(c, rngs["site_b"]).measure(out), out.adversary)


def new_auth_pool(c: LinkConfig) -> AuthKeyPool:
    """The pre-shared authentication key the sites hold before their first session."""
    return AuthKeyPool(c.auth_pool_bits, hashlib.sha256(b"wc-pool/" + auth_key_for(c)).digest())


def run_session(c: LinkConfig, managers: dict[str, SiteKeyManager] | None = None, site_a: str = "A",
                site_b: str = "B", record: QuantumRecord | None = None, pool: AuthKeyPool | None = None) -> SessionResult:
    """One session. With `record`, the quantum part comes from an experiment instead of the simulation and every later
    step (sifting, estimation, Cascade, verification, amplification, delivery) runs unchanged. `pool` carries the
    Wegman-Carter key from session to session; a fresh pre-shared pool is used if none is given."""
    t0 = time.perf_counter()
    rngs = dict(zip(STREAMS, (np.random.default_rng(s) for s in np.random.SeedSequence(c.seed).spawn(len(STREAMS)))))
    adversary = make_adversary(c, rngs["adversary"])
    m = SessionMetrics(c.run_id(), c.scenario, PROTOCOL[c.source_model], c.seed, c.distance_km, channel_loss_db(c), channel_transmittance(c),
                       adversary_label(c), c.n_pulses,
                       timestamp_utc=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"))
    if c.auth_mode == "wegman_carter" and pool is None:
        pool = new_auth_pool(c)
    cc = AuthenticatedChannel(auth_key_for(c), tamper_kind="sifting_bases_b" if c.tamper_classical else None,
                              mode=c.auth_mode, pool=pool if c.auth_mode == "wegman_carter" else None)
    m.auth_mode = c.auth_mode
    empty = np.zeros(0, dtype=np.int8)
    rec: AdversaryRecord | None = None
    result_ids: list = []

    def done(reason: str = "", key_a=empty, key_b=empty) -> SessionResult:
        # authenticate only a session that would otherwise be accepted: a rejected session uses no key, so an adversary
        # who forces rejections cannot drain the pool (she can still stop the key: denial of service is not prevented)
        if reason == "" and cc.mode == "wegman_carter":
            spent = cc.pool.consumed
            try:
                cc.finalize()                                   # authenticate the transcript before any decision
                m.event("authenticate", "info", f"transcript tags agree (forgery probability below {cc.forgery_probability:.1e})")
            except AuthenticationFailure as err:
                m.event("authenticate", "alarm", str(err))
                reason, key_a, key_b = "auth", empty, empty
            except RuntimeError as err:                         # pool exhausted
                m.event("authenticate", "alarm", str(err))
                reason, key_a, key_b = "auth", empty, empty
            m.auth_bits_consumed = cc.pool.consumed - spent
            m.forgery_probability = cc.forgery_probability
        if reason == "" and len(key_a):
            # top the authentication pool back up from this session's output (its own spend plus any earlier deficit),
            # then deliver the rest; the net key is the session's output minus what it spent
            m.net_key_bits = len(key_a) - m.auth_bits_consumed
            if cc.mode == "wegman_carter":
                topped = min(len(key_a), max(0, c.auth_pool_bits - cc.pool.bits))
                cc.pool.refill(topped)
                m.auth_bits_refilled = topped
                key_a, key_b = key_a[topped:], key_b[topped:]
            m.key_delivered_bits = len(key_a)
            m.net_key_rate_bps = max(0, m.net_key_bits) / (m.states_sent / c.pulse_rate_hz) if c.pulse_rate_hz > 0 else 0.0
            if m.net_key_bits <= 0:
                m.event("deliver", "warning", "the session made less key than its authentication consumed: no net key")
            if len(key_a) and managers is not None:
                ids = managers[site_a].store_for(site_b, c.key_size_bits).deposit(m.run_id, key_a)
                ids_b = managers[site_b].store_for(site_a, c.key_size_bits).deposit(m.run_id, key_b)
                assert ids == ids_b
                m.keys_delivered_256 = len(ids)
                m.event("deliver", "info", f"{len(ids)} keys of {c.key_size_bits} bits deposited at both sites")
                result_ids.extend(ids)
        m.reject_reason = reason
        m.accepted = reason == ""
        m.event("decide", "info" if m.accepted else "alarm", m.status)
        m.classical_messages, m.classical_bytes = cc.n_messages, cc.bytes_sent
        m.execution_time_s = time.perf_counter() - t0
        return SessionResult(c, m, key_a, key_b, cc, rec, result_ids)

    try:
        # 1-2 configure and verify readiness
        cc.send("A", "session_start", {"run_id": m.run_id, "n_pulses": c.n_pulses, "protocol": "BB84"})
        cc.send("B", "session_ready", {"run_id": m.run_id})
        m.event("ready", "info", f"session {m.run_id} established; channel loss {m.channel_loss_db:.2f} dB")
        # 3-4 quantum transmission (simulated, or recorded by an experiment)
        if record is None:
            states = SiteA(rngs["site_a"]).prepare(c.n_pulses, c)
            out = FiberChannel(c, rngs["channel"], adversary).transmit(states)
            rec = out.adversary
            det = SiteB(c, rngs["site_b"]).measure(out)
        else:
            states, det, rec = record.states, record.det, record.adversary
            m.states_sent = len(states.bits)
            m.protocol = "BB84 post-processing of an experiment log (source and detectors as recorded)"
            m.event("transmit", "info", "quantum record supplied by an experiment log")
        m.states_detected = int(det.detected.sum())
        m.detection_probability = m.states_detected / m.states_sent
        m.eve_touched = rec.n_touched if rec else 0
        m.event("transmit", "info", f"{m.states_sent:,} states sent, {m.states_detected:,} detected")
        # 5 sifting over the authenticated public channel
        idx = np.nonzero(det.detected)[0]
        payload = cc.send("B", "sifting_bases_b", {"idx": pack_indices(idx), "bases": pack(det.bases[idx])})
        idx_rx, bases_b = unpack_indices(payload["idx"]), unpack(payload["bases"])
        bases_a = unpack(cc.send("A", "sifting_bases_a", pack(states.bases[idx_rx])))
        match = bases_a == bases_b
        keep = idx_rx[match]
        ka, kb = states.bits[keep].astype(np.int8), det.bits[keep].astype(np.int8)
        m.source_model = c.source_model
        decoy_counts = None
        if states.intensity is not None:
            # Site A announces each detected pulse's intensity class and how many pulses of each class it sent
            totals = [int(np.sum(states.intensity == k)) for k in (SIGNAL, DECOY, VACUUM)]
            cls_rx = unpack_indices(cc.send("A", "intensity_classes", {"classes": pack_indices(states.intensity[idx_rx]),
                                                                       "totals": totals})["classes"])
            detected_per_class = [int(np.sum(cls_rx == k)) for k in (SIGNAL, DECOY, VACUUM)]
            cls_keep = cls_rx[match]
            dec = cls_keep == DECOY
            da = unpack(cc.send("A", "decoy_bits_a", pack(ka[dec])))           # decoy bits are disclosed, never key
            db = unpack(cc.send("B", "decoy_bits_b", pack(kb[dec])))
            decoy_counts = (totals, detected_per_class, int(np.sum(da != db)), int(dec.sum()))
            m.gain_signal = detected_per_class[0] / max(totals[0], 1)
            m.gain_decoy = detected_per_class[1] / max(totals[1], 1)
            m.gain_vacuum = detected_per_class[2] / max(totals[2], 1)
            sig = cls_keep == SIGNAL
            keep, ka, kb = keep[sig], ka[sig], kb[sig]
        elif c.source_model == "weak_coherent":
            m.gain_signal = m.detection_probability
        m.sifted_bits = len(keep)
        m.qber_true = float(np.mean(ka != kb)) if len(keep) else 0.5
        m.event("sift", "info", f"{m.sifted_bits:,} sifted bits")
        # 6 parameter estimation
        n_s = m.sifted_bits
        n_sample = max(c.min_sample_bits, math.ceil(c.sample_fraction * n_s))
        if n_s < n_sample + c.min_key_block_bits:
            m.event("estimate", "warning", f"only {n_s} sifted bits; need {n_sample + c.min_key_block_bits}")
            return done("insufficient")
        sample = np.sort(rngs["protocol"].choice(n_s, n_sample, replace=False))
        cc.send("A", "sample_positions", pack_indices(sample))
        sa = unpack(cc.send("A", "sample_bits_a", pack(ka[sample])))
        sb = unpack(cc.send("B", "sample_bits_b", pack(kb[sample])))
        m.sample_bits, m.sample_errors = n_sample, int(np.sum(sa != sb))
        m.qber_estimate = m.sample_errors / n_sample
        m.qber_upper_bound = min(0.5, m.qber_estimate + hoeffding_margin(n_sample, c.eps_pe))
        rest = np.setdiff1d(np.arange(n_s), sample, assume_unique=True)
        ka, kb = ka[rest], kb[rest]
        if rec is not None:
            k_idx = keep[rest]
            m.eve_known_key_bits = int(np.sum(rec.touched[k_idx] & (rec.bases[k_idx] == states.bases[k_idx])))
        m.key_block_bits = len(ka)
        m.event("estimate", "info", f"QBER {100 * m.qber_estimate:.2f} % from {n_sample} sampled bits")
        # single-photon bound: exact for an ideal source; decoy-state or worst-case (GLLP) for a laser
        if c.source_model == "single_photon":
            bound = SinglePhotonBound(1.0, m.qber_upper_bound)
        elif c.source_model == "weak_coherent":
            bound = gllp_bound(c.mu_signal, m.gain_signal, m.qber_upper_bound)
        else:
            (tot, dets, derr, dsift) = decoy_counts
            bound = decoy_bound(c.mu_signal, c.mu_decoy, tuple(tot), tuple(dets), derr, dsift, c.eps_pe)
            m.y1_lower = bound.y1_lower
        m.single_photon_fraction, m.e1_upper = bound.single_fraction, bound.e1_upper
        if decoy_counts is not None and m.gain_signal > 0:
            # an honest channel fixes the decoy gain once the signal and vacuum gains are known [ma2005]:
            # 1 - Q_k = (1 - Y0) e^(-k T) for every intensity k, so T follows from Q_mu and Y0 (the vacuum gain)
            y0 = min(m.gain_vacuum, 0.5)
            t_eff = -math.log(max(1e-300, (1 - m.gain_signal) / (1 - y0))) / c.mu_signal
            expected = 1 - (1 - y0) * math.exp(-c.mu_decoy * t_eff)
            sd = math.sqrt(max(expected * (1 - expected), 1e-300) / max(decoy_counts[0][1], 1))
            m.decoy_gain_deviation_sd = (m.gain_decoy - expected) / sd
            if m.decoy_gain_deviation_sd < -5:
                m.alert = True
                m.event("estimate", "warning", f"decoy gain {m.decoy_gain_deviation_sd:.1f} standard deviations below what the "
                        "signal gain implies for an honest channel: consistent with photon-number splitting")
            elif m.decoy_gain_deviation_sd > 5:
                m.alert = True
                m.event("estimate", "warning", f"decoy gain {m.decoy_gain_deviation_sd:.1f} standard deviations above what the "
                        "signal gain implies for an honest channel: the channel does not act the same on every intensity")
        if c.source_model != "single_photon":
            # simulation-only: the key an analysis that treated the laser as a single-photon source would have kept
            m.naive_key_bits = max(0, math.floor(len(ka) * (1 - h2(m.qber_upper_bound)) - 1.2 * len(ka) * h2(max(m.qber_estimate, 1e-9))
                                                 - c.verify_tag_bits - 2 * math.log2(1 / c.eps_pa)))
            m.event("estimate", "info" if bound.usable else "alarm",
                    f"at least {100 * max(bound.single_fraction, 0):.1f} % of signal detections are single-photon, "
                    f"their error rate at most {100 * bound.e1_upper:.1f} %")
        if m.qber_estimate > c.qber_alert:
            m.alert = True
            m.event("estimate", "warning", f"QBER above the {100 * c.qber_alert:g} % alert level: possible interception or "
                    "degraded channel; any key will be shortened by privacy amplification")
        if m.qber_estimate > c.qber_threshold:
            m.event("estimate", "alarm", f"QBER above the {100 * c.qber_threshold:g} % threshold")
            return done("qber")
        if not bound.usable:
            return done("single_photon")
        # 7 reconciliation and verification
        rc = reconcile(ka, kb, m.qber_estimate, c.ec_passes, rngs["protocol"], cc)
        m.ec_leaked_bits, m.ec_corrected_bits = rc.leaked_bits, rc.corrected
        m.residual_errors_before_verify = int(np.sum(ka != rc.key_b))
        m.verified = verify(ka, rc.key_b, c.verify_tag_bits, int(rngs["protocol"].integers(2**31)), cc)
        m.event("reconcile", "info" if m.verified else "alarm",
                f"{rc.corrected} bits corrected, {rc.leaked_bits} parities disclosed; keys {'match' if m.verified else 'differ'}")
        if not m.verified:
            return done("verify")
        # 8 privacy amplification
        l = math.floor(len(ka) * bound.single_fraction * (1 - h2(bound.e1_upper)) - rc.leaked_bits - c.verify_tag_bits
                       - 2 * math.log2(1 / c.eps_pa))
        if l <= 0:
            m.event("amplify", "alarm", "no secret key after deductions")
            return done("no_key")
        pa_seed = int(cc.send("A", "privacy_amplification_seed", {"seed": int(rngs["protocol"].integers(2**31))})["seed"])
        final_a, final_b = toeplitz_hash(ka, l, pa_seed), toeplitz_hash(rc.key_b, l, pa_seed)
        m.final_key_bits = l
        m.pa_removed_bits = len(ka) - l
        m.secret_key_rate_bps = l / (m.states_sent / c.pulse_rate_hz) if c.pulse_rate_hz > 0 else 0.0
        m.event("amplify", "info", f"{l:,} final key bits")
        # 9-10 authenticate the transcript, replace the authentication key, deliver the rest (in done)
        return done("", final_a, final_b)
    except AuthenticationFailure as err:
        m.event("classical", "alarm", str(err))
        return done("auth")
