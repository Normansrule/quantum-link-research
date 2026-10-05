"""A simulated operations day for the two-site link: the CONOPS's normal, degraded, and adversarial modes over 24 hours.

Method
------
Sessions run every `interval_min` minutes from one configuration, modified while scripted events are active:
polarization drift that grows until the operator realigns, a partial and a full intercept-and-resend attack, a fiber
bend, an altered classical message, and a fiber cut. The authentication pool and both sites' key stores persist all
day. An external application draws 256-bit keys at a steady rate; when the store is empty it is refused (fail
closed). For every session the monitor's indicators are recorded (status, error rate, alert, keys, pool, bank), and
for every adversarial or degrading event the time until the monitor first flagged it. The result feeds the evidence
(scenario 9) and the operations console page (docs/link/), which replays it. It is a replay of a simulation, not live
telemetry.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from qll.link.config import LinkConfig
from qll.link.demo_app import DemoApp
from qll.link.key_store import KeyUnavailable, SiteKeyManager
from qll.link.monitor import REJECT_REASONS
from qll.link.protocol_bb84 import new_auth_pool, run_session


@dataclass(frozen=True)
class OpsEvent:
    start_h: float
    end_h: float
    name: str
    kind: str                    # "degradation", "attack", or "fault"
    change: dict                 # configuration fields while active; (a, b) tuples ramp linearly from a to b
    description: str

    def active(self, t_h: float) -> bool:
        return self.start_h <= t_h < self.end_h

    def values(self, t_h: float) -> dict:
        x = (t_h - self.start_h) / max(self.end_h - self.start_h, 1e-9)
        return {k: (v[0] + (v[1] - v[0]) * x if isinstance(v, tuple) else v) for k, v in self.change.items()}


DEFAULT_PLAN = (
    OpsEvent(3.0, 5.0, "polarization drift", "degradation", {"misalignment_error": (0.015, 0.075)},
             "temperature change twists the fiber's polarization; the operator realigns at 05:00"),
    OpsEvent(8.0, 9.0, "partial interception", "attack", {"eve_fraction": 0.2},
             "intercept-and-resend on 20 % of pulses"),
    OpsEvent(12.0, 12.5, "fiber bend", "fault", {"extra_loss_db": 8.0}, "a cable tray is moved; 8 dB of bend loss"),
    OpsEvent(14.0, 15.0, "full interception", "attack", {"eve_fraction": 1.0}, "intercept-and-resend on every pulse"),
    OpsEvent(17.0, 17.25, "classical tampering", "attack", {"tamper_classical": True},
             "a message on the classical channel is altered in transit"),
    OpsEvent(19.0, 20.0, "fiber cut", "fault", {"extra_loss_db": 60.0}, "the fiber is cut; repaired at 20:00"),
)


@dataclass
class OperationsDay:
    base: LinkConfig = field(default_factory=lambda: LinkConfig(scenario="9_operations_day", distance_km=10.0, seed=900))
    plan: tuple = DEFAULT_PLAN
    hours: float = 24.0
    interval_min: float = 15.0
    demand_keys_per_hour: float = 330.0
    initial_bank_keys: int = 250
    degraded_ratio: float = 0.5          # flag the link when detections fall below this share of their baseline

    def run(self) -> dict:
        mgr = {"A": SiteKeyManager("A"), "B": SiteKeyManager("B")}
        sa, sb = mgr["A"].store_for("B"), mgr["B"].store_for("A")
        sa.authorized.add("ops-app-A"); sb.authorized.add("ops-app-B")
        app_a, app_b = DemoApp("ops-app-A", sa), DemoApp("ops-app-B", sb)
        pool = new_auth_pool(self.base)
        # yesterday's stock in the bank, from one accepted session at the base configuration
        warm = run_session(self.base.with_(seed=self.base.seed - 1, n_pulses=4_000_000), mgr, pool=pool)
        excess = sa.status()["stored_key_count"] - self.initial_bank_keys
        if excess > 0:                                                    # trim to the starting stock at both sites
            sb.get_key_with_ids("ops-app-B", [kid for kid, _ in sa.get_key("ops-app-A", excess)])
        rows, log, owed = [], [], 0.0
        n = int(round(self.hours * 60 / self.interval_min))
        state = {"alert": False, "refusing": False}
        baseline_detection = warm.metrics.detection_probability
        for i in range(n):
            t = i * self.interval_min / 60
            active = [e for e in self.plan if e.active(t)]
            for e in self.plan:
                if abs(e.start_h - t) < 1e-9:
                    log.append({"t_h": t, "level": "event", "message": f"{e.name} begins: {e.description}"})
                if abs(e.end_h - t) < 1e-9:
                    log.append({"t_h": t, "level": "event", "message": f"{e.name} ends"})
            changes = {}
            for e in active:
                changes.update(e.values(t))
            c = self.base.with_(seed=self.base.seed + i, **changes)
            m = run_session(c, mgr, pool=pool).metrics
            degraded = m.detection_probability < self.degraded_ratio * baseline_detection
            status = "rejected" if not m.accepted else "alert" if m.alert else "degraded" if degraded else "accepted"
            if degraded and m.detection_probability > 0 and status != "rejected" and not state["alert"]:
                log.append({"t_h": t, "level": "warning", "message": f"detection rate {100 * m.detection_probability / baseline_detection:.0f} % "
                            "of its baseline: loss has increased (bend, connector, or fiber)"})
            if status == "rejected":
                log.append({"t_h": t, "level": "alarm", "message": f"session rejected: {REJECT_REASONS.get(m.reject_reason, m.reject_reason)}"})
            elif status == "alert" and not state["alert"]:
                log.append({"t_h": t, "level": "warning", "message": f"error rate {100 * m.qber_estimate:.1f} % above the alert level; key shortened"})
            state["alert"] = status != "accepted"
            # the application draws keys over the next interval
            owed += self.demand_keys_per_hour * self.interval_min / 60
            want, served, refused = int(owed), 0, 0
            owed -= want
            for _ in range(want):
                try:
                    env = app_a.send(b"telemetry frame (non-sensitive test data)")
                    app_b.receive(env)
                    served += 1
                except KeyUnavailable:
                    refused += 1
            if refused and not state["refusing"]:
                log.append({"t_h": t, "level": "alarm", "message": "key store empty: the application is refused (fail closed)"})
            if not refused and state["refusing"]:
                log.append({"t_h": t, "level": "info", "message": "key available again: the application resumes"})
            state["refusing"] = refused > 0
            rows.append({"t_h": round(t, 4), "events": [e.name for e in active], "status": status, "reason": m.reject_reason,
                         "qber": round(m.qber_estimate, 5) if m.sample_bits else None, "alert": m.alert,
                         "detection": m.detection_probability, "loss_db": round(m.channel_loss_db, 3),
                         "misalignment": round(c.misalignment_error, 4), "final_key_bits": m.final_key_bits,
                         "net_key_bits": m.net_key_bits, "keys_delivered": m.keys_delivered_256, "auth_spent": m.auth_bits_consumed,
                         "pool_bits": pool.bits, "bank_keys": sa.status()["stored_key_count"], "served": served, "refused": refused,
                         "eve_known_key_bits": m.eve_known_key_bits, "run_id": m.run_id, "seed": c.seed})
        return {"config": {k: v for k, v in self.base.to_dict().items() if k in ("distance_km", "n_pulses", "pulse_rate_hz",
                                                                                  "detector_efficiency", "dark_count_prob",
                                                                                  "misalignment_error", "qber_threshold",
                                                                                  "qber_alert", "auth_mode", "auth_pool_bits")},
                "interval_min": self.interval_min, "demand_keys_per_hour": self.demand_keys_per_hour,
                "initial_bank_keys": self.initial_bank_keys,
                "plan": [{"start_h": e.start_h, "end_h": e.end_h, "name": e.name, "kind": e.kind, "description": e.description} for e in self.plan],
                "reasons": REJECT_REASONS, "sessions": rows, "log": log, "summary": summarize(rows, self.plan), "warmup_run_id": warm.metrics.run_id}


def summarize(rows: list[dict], plan) -> dict:
    n = len(rows)
    detect = {}
    for e in plan:
        hit = next((r["t_h"] for r in rows if e.start_h <= r["t_h"] < e.end_h and r["status"] != "accepted"), None)
        detect[e.name] = None if hit is None else round((hit - e.start_h) * 60, 1)
    return {"sessions": n, "accepted": sum(r["status"] != "rejected" for r in rows),
            "accepted_clean": sum(r["status"] == "accepted" for r in rows), "alerts": sum(r["status"] == "alert" for r in rows),
            "degraded": sum(r["status"] == "degraded" for r in rows),
            "rejected": sum(r["status"] == "rejected" for r in rows), "keys_delivered": sum(r["keys_delivered"] for r in rows),
            "keys_served": sum(r["served"] for r in rows), "keys_refused": sum(r["refused"] for r in rows),
            "minutes_to_flag": detect, "min_pool_bits": min(r["pool_bits"] for r in rows),
            "min_bank_keys": min(r["bank_keys"] for r in rows)}


def write(result: dict, path: Path) -> Path:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(result, indent=0, separators=(",", ":")), encoding="utf-8")
    return Path(path)
