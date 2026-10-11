"""The application: a messenger keyed by the links this program builds (the messenger lab, Phase 6 of the library).

Method
------
Each link's twin gives a secret-key rate, and each encryption policy spends key at its own rate, so the question a
user cares about, how many messages a day and how big a key bank, is arithmetic on the two:

Supply (bits per hour over a day):
    two rooms (P10)          expected_session(two_room.config()) per session, around the clock (the rooms are dark);
    two buildings at night   outdoor_link.predict with avalanche-diode modules at 1 km, for 8 night hours;
    one satellite pass       satellite_pass.pass_summary for a Micius-class station, once a night (an asymptotic
                             upper estimate);
    a Mars lander            no link at all: key loaded before launch and carried, which is how a first Earth-Mars
                             messenger would be keyed.
Spending (bits per message of b bytes, a session key renewed every n messages):
    one-time pad             8 b + 127: the pad itself [vernam1926] and one Wegman-Carter tag pad
                             (qll/link/authentication.py) [wegman1981]; information-theoretically secure [shannon1949];
    QKD-keyed AES-256-GCM    256 / n: computationally secure; Grover's search leaves 128-bit security against a quantum
                             computer [grover1996]; the key is never exchanged in public;
    hybrid ML-KEM + QKD      256 / n of QKD key, combined with an ML-KEM secret (qll/app/hybrid_kem.py)
                             [nist2024fips203]: secure if either the quantum key or the lattice problem holds;
    conventional ECDHE       0: what messengers use today; a recorded conversation can be decrypted later by a
                             large quantum computer running Shor's algorithm [shor1997].
Bank: messages are sent across the waking day while key arrives on the link's schedule; the smallest bank that never
refuses is the sequent-peak capacity of the hourly supply against the hourly demand (qll/app/key_bank.py)
[loucks2017]. A demand above the daily supply cannot be met by any bank, and the messenger refuses rather than fall
back to weaker encryption (REQ-APP-001). Latency is the light time whatever the policy (light_time_delay.py): banked
key adds none, and nothing removes it.
"""
from __future__ import annotations

import math
from functools import lru_cache

from qll.app.key_bank import AES_KEY_BITS, sequent_peak
from qll.channels.light_time_delay import one_way_delay_s
from qll.link import outdoor_link as O
from qll.link import satellite_pass as S
from qll.link import two_room
from qll.link.authentication import TAG_BITS
from qll.link.expected_session import expected_session

POLICIES = ("one-time pad", "QKD-keyed AES-256-GCM", "hybrid ML-KEM + QKD", "conventional ECDHE + AES (today)")
SECURITY = {
    "one-time pad": ("information-theoretic: unbreakable with any computer, if the key is truly secret and never reused", "shannon1949"),
    "QKD-keyed AES-256-GCM": ("computational: 128-bit security against a quantum computer; the key is never sent in public", "grover1996"),
    "hybrid ML-KEM + QKD": ("secure if either the quantum key or the lattice problem holds", "nist2024fips203"),
    "conventional ECDHE + AES (today)": ("recorded traffic can be decrypted later by a large quantum computer", "shor1997"),
}
WAKING_HOURS = range(8, 22)          # messages are sent between 08:00 and 22:00
NIGHT_HOURS = (22, 23, 0, 1, 2, 3, 4, 5)
PASS_HOUR = 1


def bits_per_message(policy: str, msg_bytes: int = 200, rekey_every: int = 100) -> float:
    if policy == "one-time pad":
        return 8 * msg_bytes + TAG_BITS
    if policy in ("QKD-keyed AES-256-GCM", "hybrid ML-KEM + QKD"):
        return AES_KEY_BITS / rekey_every
    if policy == "conventional ECDHE + AES (today)":
        return 0.0
    raise ValueError(f"policy in {POLICIES}")


@lru_cache(maxsize=None)
def sources() -> dict[str, dict]:
    """Each link's key as 24 hourly amounts (bits), from its twin."""
    c = two_room.config()
    rooms_bps = expected_session(c)["key_bits"] / (c.n_pulses / c.pulse_rate_hz)
    p = O.OutdoorParts(distance_m=1000.0, receiver=O.RECEIVERS["spad"])
    oc = O.config(p)
    bldg_bps = O.predict(p)["key_bits"] / (oc.n_pulses / oc.pulse_rate_hz)
    pass_bits = S.pass_summary(S.PRESETS["micius"])["key_bits"]
    out = {
        "two rooms (P10)": [rooms_bps * 3600] * 24,
        "two buildings at night, 1 km": [bldg_bps * 3600 if h in NIGHT_HOURS else 0.0 for h in range(24)],
        "one satellite pass a night": [pass_bits if h == PASS_HOUR else 0.0 for h in range(24)],
        "a Mars lander (key loaded before launch)": [0.0] * 24,
    }
    return {k: {"hourly_bits": v, "bits_per_day": sum(v)} for k, v in out.items()}


def demand_hourly(messages_per_day: float, bits_each: float) -> list[float]:
    per = messages_per_day * bits_each / len(WAKING_HOURS)
    return [per if h in WAKING_HOURS else 0.0 for h in range(24)]


def plan(source: str, policy: str, messages_per_day: float = 500, msg_bytes: int = 200, rekey_every: int = 100, distance_m: float = 10.0,
         preloaded_bits: float = 0.0) -> dict:
    """Messages a day the link can key, the bank that never refuses, how long a preloaded bank lasts, and latency."""
    src = sources()[source]
    b = bits_per_message(policy, msg_bytes, rekey_every)
    supply, demand = src["hourly_bits"], demand_hourly(messages_per_day, b)
    daily_need = messages_per_day * b
    sustainable = daily_need <= src["bits_per_day"] + 1e-9
    bank = sequent_peak(supply, demand) if sustainable else math.inf
    net = daily_need - src["bits_per_day"]
    return {"bits_per_message": b, "supply_bits_per_day": src["bits_per_day"], "demand_bits_per_day": daily_need,
            "messages_per_day_max": (src["bits_per_day"] / b) if b > 0 else math.inf,
            "sustainable": sustainable, "bank_bits": bank,
            "preload_days": (math.inf if net <= 0 else preloaded_bits / net),
            "one_way_s": one_way_delay_s(distance_m), "round_trip_s": 2 * one_way_delay_s(distance_m),
            "security": SECURITY[policy][0], "security_ref": SECURITY[policy][1]}


def main(argv=None) -> None:
    """python -m qll.link.keyed_messaging [--messages N] [--bytes B] [--rekey N] [--measured-bits-per-day K]: the plan for
    every link and policy; with a measured daily key (from P10 ingest reports) it replaces the two-room twin's supply."""
    import argparse
    ap = argparse.ArgumentParser(description=main.__doc__)
    ap.add_argument("--messages", type=float, default=500); ap.add_argument("--bytes", type=int, default=200)
    ap.add_argument("--rekey", type=int, default=100); ap.add_argument("--measured-bits-per-day", type=float, default=None)
    a = ap.parse_args(argv)
    if a.measured_bits_per_day is not None:
        sources()["two rooms (P10)"].update(hourly_bits=[a.measured_bits_per_day / 24] * 24, bits_per_day=a.measured_bits_per_day)
    for s in sources():
        for p in POLICIES:
            r = plan(s, p, a.messages, a.bytes, a.rekey)
            print(f"{s:<42} {p:<34} max {r['messages_per_day_max']:>12.4g}/day  bank {r['bank_bits'] / 8:>12.4g} B  {'ok' if r['sustainable'] else 'REFUSES'}")


if __name__ == "__main__":
    main()
