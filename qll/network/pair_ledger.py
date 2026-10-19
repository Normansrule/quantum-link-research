"""The pair ledger: entanglement as a resource that is created, aged, consumed, and replaced, and never resurrected.

A quantum network does not keep one entangled pair alive forever; it keeps a service alive by generating fresh pairs,
retiring spent and decayed ones, and joining links by swapping (the division of labour in RFC 9340 [rfc9340]). This
module is the bookkeeping that makes such a service honest. Every pair has one record, and its status moves only
forward:

    pending  -> available  -> consumed   (used by an application, a swap, or a purification)
                           -> expired    (decayed below the fidelity floor, or past the memory cutoff)

Nothing moves backwards. A swap consumes both inputs whether the Bell-state measurement succeeds or not, and a failed
purification consumes both inputs too; a new pair, when there is one, gets a new identifier. No operation can make an
identifier available again by editing its metadata.

Physics
-------
- **Causality.** A pair is created when it is heralded, but neither end may use it until the herald, and for a swapped
  or purified pair the measurement outcome, has reached both ends over the classical channel at light speed: until
  `ready_s` it is pending [bennett1993].
- **Storage.** Each half sits in a depolarizing memory with lifetime T, so the Werner parameter w = (4F - 1)/3 decays
  as exp(-(t_A + t_B)/T); both halves are stored from creation, so F(t) = 1/4 + (F0 - 1/4) exp(-2 (t - t0)/T)
  [werner1989].
- **Swapping.** Two Werner pairs of fidelities F1 and F2 (at the moment of the measurement) become one of fidelity
  F1 F2 + (1 - F1)(1 - F2)/3 [zukowski1993] [briegel1998], with probability p_swap (1/2 for linear optics).
- **Purification.** BBPSSW on two Werner pairs of equal fidelity F keeps F' = [F^2 + ((1-F)/3)^2] / p with probability
  p = F^2 + 2F(1-F)/3 + 5((1-F)/3)^2 (qll/network/purification.py) [bennett1996]; for unequal inputs the same map
  is applied to their mean, a stated approximation.

Sustained service
-----------------
`simulate_service` runs a three-node chain Alice - Relay - Charlie: each link heralds fresh pairs at random, the relay
swaps whenever both links hold a usable pair, and requests for Alice - Charlie pairs arrive at random. It reports the
fraction served, the fidelity delivered, what expired, and the conservation law created = in use + consumed +
expired. The long-run service is sustainable only if the rate of usable end-to-end pairs exceeds demand; and no finite
noisy memory preserves one state for ever: a logical qubit that fails with probability p_L per correction cycle
survives N cycles with probability (1 - p_L)^N, which tends to zero for any p_L > 0 (`survival_probability`). The
target is therefore a service that keeps replacing what it loses, not a pair that never dies.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from qll.channels.light_time_delay import one_way_delay_s

PENDING, AVAILABLE, CONSUMED, EXPIRED = "pending", "available", "consumed", "expired"


class PairUnavailable(RuntimeError):
    """The pair is unknown, already consumed or expired, not yet ready, or below the fidelity floor."""


@dataclass(frozen=True)
class Pair:
    pid: int
    ends: tuple[str, str]                 # always stored sorted
    created_s: float                      # heralded (or produced by a swap or purification)
    ready_s: float                        # when the classical messages have reached both ends
    f0: float                             # fidelity at creation
    t_mem_s: float                        # memory lifetime at both ends
    kind: str                             # "elementary", "swapped", or "purified"
    parents: tuple[int, ...] = ()


def werner_fidelity(f0: float, age_s: float, t_mem_s: float) -> float:
    """Fidelity after both halves have been stored for age_s in depolarizing memories of lifetime t_mem_s."""
    return 0.25 + (f0 - 0.25) * math.exp(-2.0 * max(age_s, 0.0) / t_mem_s)


def swapped_fidelity(f1: float, f2: float) -> float:
    return f1 * f2 + (1 - f1) * (1 - f2) / 3


def bbpssw(f: float) -> tuple[float, float]:
    """(output fidelity, success probability) of one BBPSSW round on two Werner pairs of fidelity f."""
    q = (1 - f) / 3
    p = f * f + 2 * f * q + 5 * q * q
    return (f * f + q * q) / p, p


@dataclass
class PairLedger:
    floor: float = 0.5                    # a pair below this fidelity is useless (teleportation no better than 2/3)
    cutoff_s: float = math.inf            # retire pairs older than this regardless of fidelity
    pairs: dict = field(default_factory=dict)
    status: dict = field(default_factory=dict)
    events: list = field(default_factory=list)          # append-only: (time, event, pair id, detail)
    _next: int = 0
    _live: dict = field(default_factory=dict)           # ends -> ids not yet consumed or expired (an index, not state)

    # ------------------------------------------------------------------------------------------ queries
    def fidelity(self, pid: int, now: float) -> float:
        p = self.pairs[pid]
        return werner_fidelity(p.f0, now - p.created_s, p.t_mem_s)

    def state(self, pid: int, now: float) -> str:
        """The status at `now`: terminal states are stored, pending versus available is computed from causality."""
        s = self.status[pid]
        if s in (CONSUMED, EXPIRED):
            return s
        return PENDING if now < self.pairs[pid].ready_s else AVAILABLE

    def usable(self, pid: int, now: float) -> bool:
        if pid not in self.pairs or self.state(pid, now) != AVAILABLE:
            return False
        p = self.pairs[pid]
        return now - p.created_s <= self.cutoff_s and self.fidelity(pid, now) >= self.floor

    def inventory(self, ends: tuple[str, str], now: float) -> list[int]:
        return sorted(pid for pid in self._live.get(tuple(sorted(ends)), ()) if self.usable(pid, now))

    def live(self, ends: tuple[str, str]) -> int:
        """Pairs between these nodes that still occupy memory (pending or available)."""
        return len(self._live.get(tuple(sorted(ends)), ()))

    def counts(self, now: float) -> dict[str, int]:
        c = {PENDING: 0, AVAILABLE: 0, CONSUMED: 0, EXPIRED: 0}
        for pid in self.pairs:
            c[self.state(pid, now)] += 1
        c["created"] = len(self.pairs)
        return c

    # ------------------------------------------------------------------------------------------ transitions
    def _new(self, ends, now, ready, f0, t_mem, kind, parents=()) -> int:
        if not (0.25 <= f0 <= 1.0) or t_mem <= 0 or ready < now or ends[0] == ends[1]:
            raise ValueError("a pair needs two distinct ends, a fidelity in [1/4, 1], a positive memory lifetime, and ready >= now")
        pid = self._next
        self._next += 1
        self.pairs[pid] = Pair(pid, tuple(sorted(ends)), now, ready, f0, t_mem, kind, tuple(parents))
        self.status[pid] = "live"
        self._live.setdefault(self.pairs[pid].ends, set()).add(pid)
        self.events.append((now, kind, pid, {"ends": tuple(sorted(ends)), "f0": f0, "ready_s": ready, "parents": tuple(parents)}))
        return pid

    def _retire(self, pid: int, now: float, to: str, why: str) -> None:
        if self.status[pid] in (CONSUMED, EXPIRED):                          # terminal states are final
            raise PairUnavailable(f"pair {pid} is already {self.status[pid]}")
        self.status[pid] = to
        self._live[self.pairs[pid].ends].discard(pid)
        self.events.append((now, to, pid, {"why": why}))

    def _require(self, pid: int, now: float) -> float:
        if pid not in self.pairs:
            raise PairUnavailable(f"pair {pid} does not exist")
        s = self.state(pid, now)
        if s == PENDING:
            raise PairUnavailable(f"pair {pid} is pending: its herald reaches both ends at {self.pairs[pid].ready_s:.6g} s, not before")
        if s != AVAILABLE:
            raise PairUnavailable(f"pair {pid} is {s}")
        f = self.fidelity(pid, now)
        if f < self.floor or now - self.pairs[pid].created_s > self.cutoff_s:
            raise PairUnavailable(f"pair {pid} has decayed (F = {f:.4f}) or passed its cutoff")
        return f

    def herald(self, ends: tuple[str, str], now: float, f0: float, t_mem_s: float, herald_delay_s: float = 0.0) -> int:
        """A fresh elementary pair, usable once its herald has reached both ends."""
        return self._new(ends, now, now + herald_delay_s, f0, t_mem_s, "elementary")

    def consume(self, pid: int, now: float, purpose: str = "application") -> float:
        """Hand a usable pair to an application; returns its fidelity at that moment."""
        f = self._require(pid, now)
        self._retire(pid, now, CONSUMED, purpose)
        return f

    def swap(self, a: int, b: int, now: float, rng: np.random.Generator, p_swap: float = 0.5,
             distances_m: dict | None = None) -> int | None:
        """Bell-state measurement at the shared node. Both inputs are consumed either way; on success the outer ends get
        a new pair, ready when the outcome has reached the farther end (distances_m: node -> metres from the relay)."""
        fa, fb = self._require(a, now), self._require(b, now)
        if a == b:
            raise PairUnavailable("a pair cannot be swapped with itself")
        ea, eb = set(self.pairs[a].ends), set(self.pairs[b].ends)
        shared = ea & eb
        if len(shared) != 1:
            raise ValueError("a swap joins two pairs that share exactly one node")
        (relay,) = shared
        outer = tuple(sorted((ea | eb) - shared))
        self._retire(a, now, CONSUMED, f"swapped at {relay}")
        self._retire(b, now, CONSUMED, f"swapped at {relay}")
        if rng.random() >= p_swap:
            self.events.append((now, "swap failed", -1, {"inputs": (a, b), "relay": relay}))
            return None
        d = distances_m or {}
        delay = max(one_way_delay_s(d.get(n, 0.0)) for n in outer)
        t_mem = min(self.pairs[a].t_mem_s, self.pairs[b].t_mem_s)
        return self._new(outer, now, now + delay, swapped_fidelity(fa, fb), t_mem, "swapped", (a, b))

    def purify(self, a: int, b: int, now: float, rng: np.random.Generator, link_delay_s: float = 0.0) -> int | None:
        """BBPSSW on two pairs with the same ends: both consumed; on success a better pair, ready after the two ends have
        exchanged their measurement outcomes (one link delay each way, overlapping: one delay)."""
        fa, fb = self._require(a, now), self._require(b, now)
        if a == b or self.pairs[a].ends != self.pairs[b].ends:
            raise ValueError("purification needs two different pairs between the same two nodes")
        f_out, p = bbpssw((fa + fb) / 2)
        self._retire(a, now, CONSUMED, "purification input")
        self._retire(b, now, CONSUMED, "purification input")
        if rng.random() >= p:
            self.events.append((now, "purification failed", -1, {"inputs": (a, b)}))
            return None
        t_mem = min(self.pairs[a].t_mem_s, self.pairs[b].t_mem_s)
        return self._new(self.pairs[a].ends, now, now + link_delay_s, f_out, t_mem, "purified", (a, b))

    def expire(self, now: float) -> list[int]:
        """Retire every live pair that has decayed below the floor or passed the cutoff."""
        gone = []
        for pid in sorted(set().union(*self._live.values())) if self._live else ():
            p = self.pairs[pid]
            if self.fidelity(pid, now) < self.floor or now - p.created_s > self.cutoff_s:
                self._retire(pid, now, EXPIRED, "decayed" if self.fidelity(pid, now) < self.floor else "cutoff")
                gone.append(pid)
        return gone

    def check_invariants(self, now: float) -> None:
        """Conservation and monotonicity, replayed from the append-only event log."""
        c = self.counts(now)
        assert c[PENDING] + c[AVAILABLE] + c[CONSUMED] + c[EXPIRED] == c["created"]
        terminal = {}
        for _, ev, pid, _ in self.events:
            if pid < 0:
                continue
            if ev in (CONSUMED, EXPIRED):
                assert pid not in terminal, f"pair {pid} retired twice"
                terminal[pid] = ev
            elif pid in terminal:
                raise AssertionError(f"pair {pid} reappeared after being {terminal[pid]}")
        for pid, p in self.pairs.items():
            assert p.ready_s >= p.created_s
            for parent in p.parents:
                assert self.status[parent] == CONSUMED and self.pairs[parent].created_s <= p.created_s


# ---------------------------------------------------------------------------------------------- the service
def oldest_first(ledger: PairLedger, candidates: list[int], now: float) -> int:
    """Use the pair created earliest: spends pairs before they expire, at the cost of lower delivered fidelity."""
    return min(candidates, key=lambda pid: (ledger.pairs[pid].created_s, pid))


def freshest_first(ledger: PairLedger, candidates: list[int], now: float) -> int:
    """Use the pair with the highest fidelity now: better pairs delivered, more pairs left to expire unused."""
    return max(candidates, key=lambda pid: (ledger.fidelity(pid, now), -pid))


def deadline_aware(ledger: PairLedger, candidates: list[int], now: float) -> int:
    """TODO (your design): choose which usable pair to spend, for swaps at the relay and for serving requests.

    `candidates` are ids that are usable right now (available, above ledger.floor, within the cutoff). Useful facts:
      ledger.fidelity(pid, now)          fidelity at this moment (it only falls)
      ledger.pairs[pid].created_s        when the pair was made
      ledger.pairs[pid].t_mem_s          its memory lifetime
      ledger.floor                       the fidelity below which it expires
    The trade-off: oldest_first spends pairs before they expire (less waste, lower fidelity delivered); freshest_first
    delivers the best pair (higher fidelity, more pairs expire unused). A better policy might, for example, spend the
    pair closest to expiring only when it still has margin above the floor, or keep the freshest in reserve. The time a
    pair has left is t_left = -(t_mem_s / 2) * ln(w_floor / w_now), with w = (4F - 1)/3.
    Return one id from candidates. tests/test_pair_ledger.py runs it in the three-node service against both references.
    """
    raise NotImplementedError("deadline_aware is yours to write: see its docstring")


@dataclass(frozen=True)
class ChainDesign:
    link_km: float = 25.0                 # Alice-Relay and Relay-Charlie, each
    attempt_rate_hz: float = 1_000.0      # entanglement attempts per link per second
    p_herald: float = 0.01                # success per attempt (loss, detection)
    f0: float = 0.97                      # fidelity of a fresh elementary pair
    t_mem_s: float = 0.5                  # memory lifetime
    capacity: int = 4                     # memory slots per link end
    p_swap: float = 0.5                   # Bell-state measurement success
    floor: float = 0.8                    # requests need at least this end-to-end fidelity
    fiber_index: float = 1.47


def simulate_service(d: ChainDesign = ChainDesign(), demand_hz: float = 1.0, horizon_s: float = 60.0, dt_s: float = 1e-3,
                     seed: int = 0, policy=oldest_first, deadline_s: float = 1.0) -> dict:
    """Run the three-node chain for horizon_s: links herald pairs, the relay swaps when both links hold a usable pair,
    and Alice-Charlie requests (Poisson, demand_hz) are served from the end-to-end inventory before their deadline."""
    if not (d.link_km > 0 and d.attempt_rate_hz > 0 and 0 < d.p_herald <= 1 and 0.5 < d.f0 <= 1 and d.t_mem_s > 0
            and d.capacity >= 1 and 0 < d.p_swap <= 1 and 0.25 <= d.floor < 1 and demand_hz >= 0 and horizon_s > 0 and dt_s > 0):
        raise ValueError("invalid chain design or run parameters")
    rng = np.random.default_rng(seed)
    led = PairLedger(floor=d.floor)
    L_m = d.link_km * 1e3
    herald_delay = one_way_delay_s(d.fiber_index * L_m)          # source at one end; the herald crosses the link
    dist = {"Alice": d.fiber_index * L_m, "Charlie": d.fiber_index * L_m}
    queue, served, missed, fids, waits = [], 0, 0, [], []
    steps = int(round(horizon_s / dt_s))
    p_link = 1 - (1 - d.p_herald) ** (d.attempt_rate_hz * dt_s)  # at least one success per step
    samples = []
    for k in range(steps):
        now = k * dt_s
        led.expire(now)
        for ends in (("Alice", "Relay"), ("Relay", "Charlie")):
            if led.live(ends) < d.capacity and rng.random() < p_link:
                led.herald(ends, now, d.f0, d.t_mem_s, herald_delay)
        left, right = led.inventory(("Alice", "Relay"), now), led.inventory(("Relay", "Charlie"), now)
        while left and right:
            a, b = policy(led, left, now), policy(led, right, now)
            led.swap(a, b, now, rng, d.p_swap, dist)
            left, right = led.inventory(("Alice", "Relay"), now), led.inventory(("Relay", "Charlie"), now)
        for _ in range(rng.poisson(demand_hz * dt_s)):
            queue.append(now)
        while queue and now - queue[0] > deadline_s:
            queue.pop(0)
            missed += 1
        e2e = led.inventory(("Alice", "Charlie"), now)
        while queue and e2e:
            pid = policy(led, e2e, now)
            fids.append(led.consume(pid, now, "request"))
            waits.append(now - queue.pop(0))
            served += 1
            e2e = led.inventory(("Alice", "Charlie"), now)
        if k % max(1, steps // 300) == 0:
            c = led.counts(now)
            samples.append({"t": now, "available": c[AVAILABLE], "pending": c[PENDING], "consumed": c[CONSUMED], "expired": c[EXPIRED],
                            "e2e": len(e2e), "served": served, "missed": missed, "queued": len(queue)})
    end = steps * dt_s
    led.check_invariants(end)
    c = led.counts(end)
    kinds = {k: sum(1 for p in led.pairs.values() if p.kind == k) for k in ("elementary", "swapped", "purified")}
    requests = served + missed + len(queue)
    return {"design": d.__dict__, "demand_hz": demand_hz, "horizon_s": horizon_s, "policy": policy.__name__,
            "requests": requests, "served": served, "missed": missed, "still_queued": len(queue),
            "availability": served / requests if requests else 1.0,
            "mean_fidelity": float(np.mean(fids)) if fids else None, "min_fidelity": float(min(fids)) if fids else None,
            "mean_wait_s": float(np.mean(waits)) if waits else None,
            "counts": c, "kinds": kinds, "swap_failures": sum(1 for e in led.events if e[1] == "swap failed"),
            "end_to_end_rate_hz": kinds["swapped"] / horizon_s, "samples": samples}


def survival_probability(p_logical: float, cycles: float) -> float:
    """Probability that a logical qubit failing independently with p_L per correction cycle survives N cycles."""
    if not (0.0 <= p_logical <= 1.0) or cycles < 0:
        raise ValueError("p_logical must lie in [0, 1] and cycles must be non-negative")
    return math.exp(cycles * math.log1p(-p_logical)) if p_logical < 1 else (1.0 if cycles == 0 else 0.0)


def cycles_to_survival(p_logical: float, target: float) -> float:
    """Largest number of cycles N with (1 - p_L)^N >= target; infinite only when p_L = 0."""
    if not (0.0 <= p_logical < 1.0 and 0.0 < target < 1.0):
        raise ValueError("p_logical must lie in [0, 1) and target in (0, 1)")
    return math.inf if p_logical == 0 else math.floor(math.log(target) / math.log1p(-p_logical))
