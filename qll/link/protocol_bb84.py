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

from qll.link.adversary import AdversaryRecord, InterceptResend
from qll.link.classical_channel import AuthenticatedChannel, AuthenticationFailure
from qll.link.codec import pack, pack_indices, unpack, unpack_indices
from qll.link.config import LinkConfig
from qll.link.key_store import SiteKeyManager
from qll.link.models import channel_loss_db, channel_transmittance, hoeffding_margin
from qll.link.monitor import SessionMetrics
from qll.link.quantum_channel import FiberChannel
from qll.link.reconciliation import reconcile, verify
from qll.link.site_a import SiteA
from qll.link.site_b import SiteB
from qll.qkd.binary_entropy import h2
from qll.qkd.privacy_amplification import toeplitz_hash

PROTOCOL = "BB84 (ideal single-photon source, prepare and measure)"
STREAMS = ("site_a", "adversary", "channel", "site_b", "protocol")


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


def run_session(c: LinkConfig, managers: dict[str, SiteKeyManager] | None = None, site_a: str = "A",
                site_b: str = "B") -> SessionResult:
    t0 = time.perf_counter()
    rngs = dict(zip(STREAMS, (np.random.default_rng(s) for s in np.random.SeedSequence(c.seed).spawn(len(STREAMS)))))
    adversary = InterceptResend(c.eve_fraction, rngs["adversary"]) if c.eve_fraction > 0 else None
    m = SessionMetrics(c.run_id(), c.scenario, PROTOCOL, c.seed, c.distance_km, channel_loss_db(c), channel_transmittance(c),
                       f"intercept-resend on {100 * c.eve_fraction:g} % of pulses" if adversary else "none", c.n_pulses,
                       timestamp_utc=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"))
    cc = AuthenticatedChannel(auth_key_for(c), tamper_kind="sifting_bases_b" if c.tamper_classical else None)
    empty = np.zeros(0, dtype=np.int8)
    rec: AdversaryRecord | None = None
    ids: list = []

    def done(reason: str = "", key_a=empty, key_b=empty) -> SessionResult:
        m.reject_reason = reason
        m.accepted = reason == ""
        m.event("decide", "info" if m.accepted else "alarm", m.status)
        m.classical_messages, m.classical_bytes = cc.n_messages, cc.bytes_sent
        m.execution_time_s = time.perf_counter() - t0
        return SessionResult(c, m, key_a, key_b, cc, rec, ids)

    try:
        # 1-2 configure and verify readiness
        cc.send("A", "session_start", {"run_id": m.run_id, "n_pulses": c.n_pulses, "protocol": "BB84"})
        cc.send("B", "session_ready", {"run_id": m.run_id})
        m.event("ready", "info", f"session {m.run_id} established; channel loss {m.channel_loss_db:.2f} dB")
        # 3-4 quantum transmission
        states = SiteA(rngs["site_a"]).prepare(c.n_pulses)
        out = FiberChannel(c, rngs["channel"], adversary).transmit(states)
        rec = out.adversary
        det = SiteB(c, rngs["site_b"]).measure(out)
        m.states_detected = int(det.detected.sum())
        m.detection_probability = m.states_detected / c.n_pulses
        m.eve_touched = rec.n_touched if rec else 0
        m.event("transmit", "info", f"{c.n_pulses:,} states sent, {m.states_detected:,} detected")
        # 5 sifting over the authenticated public channel
        idx = np.nonzero(det.detected)[0]
        payload = cc.send("B", "sifting_bases_b", {"idx": pack_indices(idx), "bases": pack(det.bases[idx])})
        idx_rx, bases_b = unpack_indices(payload["idx"]), unpack(payload["bases"])
        bases_a = unpack(cc.send("A", "sifting_bases_a", pack(states.bases[idx_rx])))
        match = bases_a == bases_b
        keep = idx_rx[match]
        ka, kb = states.bits[keep].astype(np.int8), det.bits[keep].astype(np.int8)
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
        if m.qber_estimate > c.qber_alert:
            m.alert = True
            m.event("estimate", "warning", f"QBER above the {100 * c.qber_alert:g} % alert level: possible interception or "
                    "degraded channel; any key will be shortened by privacy amplification")
        if m.qber_estimate > c.qber_threshold:
            m.event("estimate", "alarm", f"QBER above the {100 * c.qber_threshold:g} % threshold")
            return done("qber")
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
        l = math.floor(len(ka) * (1 - h2(m.qber_upper_bound)) - rc.leaked_bits - c.verify_tag_bits - 2 * math.log2(1 / c.eps_pa))
        if l <= 0:
            m.event("amplify", "alarm", "no secret key after deductions")
            return done("no_key")
        pa_seed = int(cc.send("A", "privacy_amplification_seed", {"seed": int(rngs["protocol"].integers(2**31))})["seed"])
        final_a, final_b = toeplitz_hash(ka, l, pa_seed), toeplitz_hash(rc.key_b, l, pa_seed)
        m.final_key_bits = l
        m.pa_removed_bits = len(ka) - l
        m.secret_key_rate_bps = l / (c.n_pulses / c.pulse_rate_hz)
        m.event("amplify", "info", f"{l:,} final key bits")
        # 9 deliver accepted key to both sites' stores
        if managers is not None:
            ids = managers[site_a].store_for(site_b, c.key_size_bits).deposit(m.run_id, final_a)
            ids_b = managers[site_b].store_for(site_a, c.key_size_bits).deposit(m.run_id, final_b)
            assert ids == ids_b
            m.keys_delivered_256 = len(ids)
            m.event("deliver", "info", f"{len(ids)} keys of {c.key_size_bits} bits deposited at both sites")
        return done("", final_a, final_b)
    except AuthenticationFailure as err:
        m.event("classical", "alarm", str(err))
        return done("auth")
