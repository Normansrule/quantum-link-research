"""Messages without the internet: a model of an off-grid LoRa mesh (phones, handheld radios, solar ridge relays) and
the delivery states a messenger must show honestly.

Radio link
----------
A LoRa receiver's sensitivity is the thermal noise in its bandwidth plus its noise figure plus the lowest signal-to-
noise ratio its spreading factor can demodulate:

    S = -174 dBm/Hz + 10 log10(BW) + NF + SNR_min(SF),   SNR_min = -7.5, -10, ..., -20 dB for SF7 ... SF12
    [semtech2015an1200_22]

so each step up in spreading factor buys about 2.5 dB of range and doubles the symbol time T_sym = 2^SF / BW. A link
closes when the transmit power plus antenna gains, minus the free-space path loss 20 log10(d/km) + 20 log10(f/MHz) +
32.44 dB [friis1946] and an excess loss for terrain and foliage (an assumed planning value per link), still clears the
sensitivity with margin, and when the two antennas see each other over the curve of the Earth: with the standard
four-thirds Earth radius for refraction, d <= 4.12 (sqrt(h1) + sqrt(h2)) km, heights in metres [rappaport2002].

Time on air follows the modem's packet formula: (n_preamble + 4.25) T_sym + T_sym * (8 + max(ceil((8 PL - 4 SF + 28
+ 16 CRC - 20 IH) / (4 (SF - 2 DE))) (CR + 4), 0)), with DE = 1 when T_sym exceeds 16 ms [semtech2013sx1276]. A
20-byte message takes about 57 ms at SF7 and 1.3 s at SF12, so a mesh message's latency is set by hops times time on
air, thousands of times longer than its light time.

Routing and delivery
--------------------
Messages flood: every node that hears a message for the first time rebroadcasts it until a hop limit runs out
(Meshtastic's default is 3 [meshtastic2024]). The recipient's acknowledgment floods back the same way. The states are
strictly ordered and only move forward:

    QUEUED (no neighbour heard it) -> RELAYED (a neighbour rebroadcast it) -> DELIVERED (the recipient's
    end-to-end acknowledgment came back) or UNREACHABLE (the acknowledgment did not arrive in time)

A neighbour's rebroadcast proves only that one hop worked; it never counts as delivery.

Law and scope
-------------
In the United States, amateur stations may not transmit messages encoded to obscure their meaning (47 CFR
97.113(a)(4)) [cfr47_97_113], so an encrypted mesh must run on equipment and bands where encryption is lawful, such as
unlicensed 902-928 MHz devices under Part 15, within their own power and dwell-time limits. This module is a model:
coverage, airtime, and delivery are computed, not measured, and real terrain needs a terrain profile per link.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

SNR_MIN_DB = {7: -7.5, 8: -10.0, 9: -12.5, 10: -15.0, 11: -17.5, 12: -20.0}
QUEUED, RELAYED, DELIVERED, UNREACHABLE = "queued", "relayed", "delivered", "unreachable"
_ORDER = {QUEUED: 0, RELAYED: 1, DELIVERED: 2, UNREACHABLE: 2}


def sensitivity_dbm(sf: int, bw_hz: float = 125e3, noise_figure_db: float = 6.0) -> float:
    if sf not in SNR_MIN_DB or bw_hz <= 0:
        raise ValueError("spreading factor must be 7 to 12 and bandwidth positive")
    return -174.0 + 10 * math.log10(bw_hz) + noise_figure_db + SNR_MIN_DB[sf]


def free_space_loss_db(d_km: float, f_mhz: float = 915.0) -> float:
    if d_km <= 0 or f_mhz <= 0:
        raise ValueError("distance and frequency must be positive")
    return 20 * math.log10(d_km) + 20 * math.log10(f_mhz) + 32.44


def radio_horizon_km(h1_m: float, h2_m: float) -> float:
    if h1_m < 0 or h2_m < 0:
        raise ValueError("antenna heights must be non-negative")
    return 4.12 * (math.sqrt(h1_m) + math.sqrt(h2_m))


def time_on_air_s(payload_bytes: int, sf: int = 9, bw_hz: float = 125e3, cr: int = 1, preamble: int = 8,
                  explicit_header: bool = True, crc: bool = True) -> float:
    """LoRa packet duration; cr = 1..4 for coding rates 4/5 .. 4/8."""
    if sf not in SNR_MIN_DB or not 0 <= payload_bytes <= 255 or cr not in (1, 2, 3, 4):
        raise ValueError("invalid LoRa parameters")
    t_sym = 2 ** sf / bw_hz
    de = 1 if t_sym > 0.016 else 0
    ih = 0 if explicit_header else 1
    n = 8 + max(math.ceil((8 * payload_bytes - 4 * sf + 28 + 16 * int(crc) - 20 * ih) / (4 * (sf - 2 * de))) * (cr + 4), 0)
    return (preamble + 4.25) * t_sym + n * t_sym


@dataclass(frozen=True)
class Node:
    name: str
    x_km: float
    y_km: float
    height_m: float = 2.0               # antenna height above the surrounding terrain
    tx_dbm: float = 20.0
    gain_dbi: float = 2.0
    relay: bool = True                  # rebroadcasts messages it hears


@dataclass
class Mesh:
    nodes: dict
    sf: int = 9
    bw_hz: float = 125e3
    f_mhz: float = 915.0
    margin_db: float = 10.0
    excess_loss_db: float = 20.0         # terrain and foliage on an ordinary link (assumed)
    obstructed: dict = field(default_factory=dict)   # frozenset({a, b}) -> extra loss in dB (a ridge between them)
    hop_limit: int = 3

    def link_margin_db(self, a: str, b: str) -> float | None:
        """Margin above sensitivity of the a -> b link, or None when the radio horizon blocks it."""
        na, nb = self.nodes[a], self.nodes[b]
        d = math.hypot(na.x_km - nb.x_km, na.y_km - nb.y_km)
        if d == 0:
            return math.inf
        if d > radio_horizon_km(na.height_m, nb.height_m):
            return None
        rx = na.tx_dbm + na.gain_dbi + nb.gain_dbi - free_space_loss_db(d, self.f_mhz) - self.excess_loss_db \
            - self.obstructed.get(frozenset((a, b)), 0.0)
        return rx - sensitivity_dbm(self.sf, self.bw_hz)

    def neighbours(self, a: str) -> list[str]:
        out = []
        for b in self.nodes:
            if b != a:
                m = self.link_margin_db(a, b)
                if m is not None and m >= self.margin_db:
                    out.append(b)
        return sorted(out)

    def flood_hops(self, src: str) -> dict[str, int]:
        """Hops at which each node first hears a flood from src; only relays rebroadcast, within the hop limit."""
        seen, q = {src: 0}, deque([src])
        while q:
            u = q.popleft()
            if seen[u] >= self.hop_limit or (u != src and not self.nodes[u].relay):
                continue
            for v in self.neighbours(u):
                if v not in seen:
                    seen[v] = seen[u] + 1
                    q.append(v)
        return seen


@dataclass
class Delivery:
    """One message's delivery record; its state only moves forward."""
    src: str
    dst: str
    state: str = QUEUED
    history: list = field(default_factory=list)

    def advance(self, to: str, t_s: float, why: str) -> None:
        if _ORDER[to] < _ORDER[self.state] or self.state in (DELIVERED, UNREACHABLE) or to == self.state:
            raise ValueError(f"a delivery cannot go from {self.state} to {to}")
        self.state = to
        self.history.append((t_s, to, why))

    def relay_heard(self, t_s: float, relay: str) -> None:
        """A neighbour rebroadcast the message: one hop worked. This is never delivery."""
        if self.state == QUEUED:
            self.advance(RELAYED, t_s, f"heard rebroadcast by {relay}")

    def end_to_end_ack(self, t_s: float, from_node: str) -> None:
        if from_node != self.dst:
            raise ValueError("only the recipient's acknowledgment can mark a message delivered")
        if self.state in (QUEUED, RELAYED):
            self.advance(DELIVERED, t_s, f"acknowledged by {from_node}")

    def timeout(self, t_s: float) -> None:
        if self.state in (QUEUED, RELAYED):
            self.advance(UNREACHABLE, t_s, "no end-to-end acknowledgment before the timeout")


def send(mesh: Mesh, src: str, dst: str, payload_bytes: int = 64, ack_bytes: int = 16, rebroadcast_delay_s: float = 0.05,
         timeout_s: float = 30.0) -> Delivery:
    """Deliver one message by flooding and wait for the recipient's acknowledgment, which floods back."""
    msg = Delivery(src, dst)
    hops = mesh.flood_hops(src)
    t_msg = time_on_air_s(payload_bytes, mesh.sf, mesh.bw_hz) + rebroadcast_delay_s
    t_ack = time_on_air_s(ack_bytes, mesh.sf, mesh.bw_hz) + rebroadcast_delay_s
    relays = [n for n, h in hops.items() if h == 1 and mesh.nodes[n].relay and n != dst]
    if relays:
        msg.relay_heard(2 * t_msg, relays[0])                    # the source hears its neighbour's rebroadcast
    if dst in hops:
        back = mesh.flood_hops(dst)
        if src in back:
            t = hops[dst] * t_msg + back[src] * t_ack
            if t <= timeout_s:
                msg.end_to_end_ack(t, dst)
                return msg
    msg.timeout(timeout_s)
    return msg


def mountain_scenario(with_ridge_relay: bool = True) -> Mesh:
    """Two hikers in neighbouring valleys 18 km apart, with a ridge between them, a base camp, and a solar relay on the
    ridge 300 m above both valleys (heights are above the local terrain; the ridge blocks the valley-to-valley paths)."""
    nodes = {n.name: n for n in [
        Node("hiker A", 0.0, 0.0, 2.0, relay=False), Node("hiker B", 18.0, 0.0, 2.0, relay=False),
        Node("base camp", 4.0, 1.0, 6.0), Node("valley relay", 13.0, -1.0, 6.0),
    ]}
    if with_ridge_relay:
        nodes["ridge relay"] = Node("ridge relay", 9.0, 0.5, 300.0, tx_dbm=22.0, gain_dbi=5.0)
    ridge = {frozenset(p): 45.0 for p in [("hiker A", "hiker B"), ("hiker A", "valley relay"), ("base camp", "hiker B"),
                                          ("base camp", "valley relay")]}
    return Mesh(nodes, obstructed=ridge)
