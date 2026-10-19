"""Secure messages in one trip: a messenger whose key was banked before the message existed, run between two
independent processes (verification step L2 of systems/program/10_anywhere_at_light_speed.md).

What it does
------------
Each site holds its own bank file and nothing else in common. A bank comes from an accepted session of the protocol
(qll/link/protocol_bb84.py, simulated by default): Site A's key goes into A's file and Site B's key into B's, and each
site cuts it into 256-bit keys with the same identifiers (qll/link/key_store.py), so the two files never have to be
compared or copied. Files are created exclusively with owner-only permissions, and loading one refuses a file whose
identifiers or digests do not match its own content. The bank file itself is never rewritten: each site appends the
identifier of every key it is about to use to a spent ledger (<bank>.spent), flushed to disk before the key is used,
and loading a bank tombstones every identifier in its ledger, so a key is never used twice even across restarts.

A message travels over the session-bound authenticated transport (qll/link/net_transport.py) as

    {"t": "msg", "kid": <key identifier>, "nonce": <96 bits>, "ct": AES-256-GCM(key, nonce, plaintext, aad = kid)}

so the receiver can decrypt it the moment it arrives: one one-way trip [nist2007sp800-38d]. Every key is used for one
message and then tombstoned at both ends, whether the message decrypts or not; a replayed, reordered, or altered
message is refused, and a sender with an empty bank refuses to send rather than fall back to an unkeyed message.

For comparison, "on demand" runs the message pattern of a key made at the moment of sending: photons out, bases back,
reconciliation out with the ciphertext, so the receiver decrypts after three trips. Its key is a timing stand-in (HKDF
of the transport's session key and fresh nonces [rfc5869]); it reproduces QKD's message pattern, not QKD's security.

Path delay
----------
Two processes on one machine are microseconds apart, so each frame can be held for an emulated one-way delay before
it is sent: set it to a route's delay from qll/space/latency_floor.py (35.4 ms for Los Angeles to London by a
low-orbit laser mesh, for example) and the measured delivery times can be compared with the model's trip counts.
Delivery is timed on one wall clock, so the two processes must share a machine; across machines, use the round
trip that "send" also reports.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import statistics
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from qll.link.key_store import KeyStore, KeyUnavailable
from qll.link.net_transport import AuthLink, LinkError, _hkdf

APP = "banked-messenger"
KEY_BITS = 256
TRIPS = {"banked": 1, "on-demand": 3}


class BankError(RuntimeError):
    """A bank file is missing, malformed, inconsistent, or would overwrite another."""


# --------------------------------------------------------------------------------------------- bank files
def write_bank(path: Path, site: str, peer: str, key_bits: np.ndarray, run_id: str, execution_id: str, origin: str) -> Path:
    """Write one site's bank: its own accepted key bits and the identifiers that name them. Never overwrites."""
    bits = np.asarray(key_bits, dtype=np.uint8)
    if bits.ndim != 1 or bits.size < KEY_BITS or not np.isin(bits, (0, 1)).all():
        raise BankError(f"a bank needs at least {KEY_BITS} key bits")
    store = KeyStore(site, peer, KEY_BITS)
    ids = store.deposit(run_id, bits, execution_id)
    body = {"site": site, "peer": peer, "key_size_bits": KEY_BITS, "run_id": run_id, "execution_id": execution_id, "origin": origin,
            "n_bits": int(bits.size), "bits_hex": np.packbits(bits).tobytes().hex(), "key_ids": ids,
            "key_sha256": [hashlib.sha256(store._keys[k]).hexdigest() for k in ids]}
    path = Path(path)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as err:
        raise BankError(f"{path} exists: a bank is never overwritten (its keys may already be spent)") from err
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(body, f, indent=1)
    return path


def spent_path(bank: Path) -> Path:
    return Path(str(bank) + ".spent")


def record_spent(bank: Path, kid: str) -> None:
    """Write-ahead record that a key is used: on disk before the key encrypts or decrypts anything."""
    with open(spent_path(bank), "a", encoding="utf-8") as f:
        f.write(kid + "\n")
        f.flush()
        os.fsync(f.fileno())


def load_bank(path: Path, site: str) -> tuple[KeyStore, dict]:
    """Load one site's bank into a fresh key store, checking that identifiers and digests match the file's own bits,
    and tombstone every key its spent ledger names."""
    try:
        body = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise BankError(f"cannot read bank {path}: {err}") from err
    if body.get("site") != site:
        raise BankError(f"{path} belongs to site {body.get('site')!r}, not {site!r}")
    bits = np.unpackbits(np.frombuffer(bytes.fromhex(body["bits_hex"]), dtype=np.uint8))[: int(body["n_bits"])]
    store = KeyStore(site, body["peer"], int(body["key_size_bits"]), authorized={APP})
    ids = store.deposit(body["run_id"], bits, body["execution_id"])
    digests = [hashlib.sha256(store._keys[k]).hexdigest() for k in ids]
    if ids != body["key_ids"] or digests != body["key_sha256"]:
        raise BankError(f"{path}: key identifiers or digests do not match its bits (corrupted or edited)")
    sp = spent_path(Path(path))
    spent = [k for k in dict.fromkeys(sp.read_text(encoding="utf-8").split()) if k in store._keys] if sp.exists() else []
    if spent:
        store.get_key_with_ids(APP, spent, purpose="spent in an earlier run")
    body["spent_before_load"] = len(spent)
    return store, body


def banks_from_session(path_a: Path, path_b: Path, config=None) -> dict:
    """Run one session of the protocol and bank each site's own accepted key in its own file."""
    from qll.link.config import LinkConfig
    from qll.link.protocol_bb84 import run_session

    c = config or LinkConfig(n_pulses=400_000)
    r = run_session(c)
    if not r.metrics.accepted or len(r.key_a) < KEY_BITS:
        raise BankError(f"the session was not accepted ({r.metrics.reject_reason or 'too little key'}); nothing is banked")
    execution_id = uuid.uuid4().hex
    origin = "simulated BB84 session (qll.link.protocol_bb84): a demonstration key, not a security-reviewed one"
    write_bank(path_a, "A", "B", r.key_a, r.metrics.run_id, execution_id, origin)
    write_bank(path_b, "B", "A", r.key_b, r.metrics.run_id, execution_id, origin)
    return {"run_id": r.metrics.run_id, "execution_id": execution_id, "keys": len(r.key_a) // KEY_BITS, "bits": int(len(r.key_a))}


# --------------------------------------------------------------------------------------------- the two ends
def _send(link: AuthLink, obj: dict, delay_s: float) -> None:
    if delay_s > 0:
        time.sleep(delay_s)                              # the frame is in flight for the emulated path delay
    link.send(json.dumps(obj, separators=(",", ":")).encode())


def _recv(link: AuthLink) -> dict:
    return json.loads(link.recv().decode())


@dataclass
class Sender:
    link: AuthLink
    store: KeyStore
    delay_s: float = 0.0
    bank: Path | None = None                              # where the spent ledger lives (None: in memory only)

    def banked(self, plaintext: bytes) -> dict:
        try:
            ((kid, key),) = self.store.get_key(APP, 1, purpose="message")
        except KeyUnavailable as err:
            raise KeyUnavailable("bank empty: refusing to send rather than send unkeyed") from err
        if self.bank is not None:
            record_spent(self.bank, kid)
        nonce = os.urandom(12)
        ct = AESGCM(key).encrypt(nonce, plaintext, kid.encode())
        t0 = time.time_ns()
        _send(self.link, {"t": "msg", "kid": kid, "nonce": nonce.hex(), "ct": ct.hex()}, self.delay_s)
        return {"mode": "banked", "kid": kid, "sent_ns": t0}

    def on_demand(self, plaintext: bytes) -> dict:
        t0 = time.time_ns()
        n_a = os.urandom(16)
        _send(self.link, {"t": "photons", "n": n_a.hex()}, self.delay_s)                        # trip 1
        n_b = bytes.fromhex(_recv(self.link)["bases"])                                          # trip 2
        key = _hkdf(self.link.key, n_a + n_b, b"timing stand-in for a QKD session")
        nonce = os.urandom(12)
        ct = AESGCM(key).encrypt(nonce, plaintext, b"on-demand")
        _send(self.link, {"t": "recon", "nonce": nonce.hex(), "ct": ct.hex()}, self.delay_s)     # trip 3
        return {"mode": "on-demand", "sent_ns": t0}


@dataclass
class Receiver:
    link: AuthLink
    store: KeyStore
    delay_s: float = 0.0
    bank: Path | None = None

    def serve(self) -> dict:
        """Handle messages until the sender says it is done; reply with when each one could be read."""
        log, pending = [], None
        while True:
            m = _recv(self.link)
            t = m["t"]
            if t == "done":
                _send(self.link, {"t": "log", "log": log}, 0.0)
                return {"messages": log}
            if t == "msg":
                entry = {"mode": "banked", "kid": m["kid"]}
                try:
                    ((kid, key),) = self.store.get_key_with_ids(APP, [m["kid"]], purpose="message")   # consumed either way
                    if self.bank is not None:
                        record_spent(self.bank, kid)
                    pt = AESGCM(key).decrypt(bytes.fromhex(m["nonce"]), bytes.fromhex(m["ct"]), kid.encode())
                    entry.update(ok=True, read_ns=time.time_ns(), sha256=hashlib.sha256(pt).hexdigest())
                except KeyUnavailable:
                    entry.update(ok=False, error="unknown or already used key identifier")
                except InvalidTag:
                    entry.update(ok=False, error="authentication failed: altered ciphertext")
                log.append(entry)
            elif t == "photons":
                pending = bytes.fromhex(m["n"]), os.urandom(16)
                _send(self.link, {"t": "bases", "bases": pending[1].hex()}, self.delay_s)
            elif t == "recon":
                if pending is None:
                    log.append({"mode": "on-demand", "ok": False, "error": "reconciliation without a session"})
                    continue
                key = _hkdf(self.link.key, pending[0] + pending[1], b"timing stand-in for a QKD session")
                pending = None
                try:
                    pt = AESGCM(key).decrypt(bytes.fromhex(m["nonce"]), bytes.fromhex(m["ct"]), b"on-demand")
                    log.append({"mode": "on-demand", "ok": True, "read_ns": time.time_ns(), "sha256": hashlib.sha256(pt).hexdigest()})
                except InvalidTag:
                    log.append({"mode": "on-demand", "ok": False, "error": "authentication failed: altered ciphertext"})
            else:
                log.append({"ok": False, "error": f"unknown message type {t!r}"})


def summarize(sent: list[dict], log: list[dict], delay_s: float) -> dict:
    """Pair each sent message with the receiver's log and compare delivery with the model's trip counts."""
    out = {"delay_ms": delay_s * 1e3, "modes": {}}
    for mode, trips in TRIPS.items():
        lat = [(r["read_ns"] - s["sent_ns"]) / 1e6 for s, r in zip(sent, log) if s["mode"] == mode and r.get("ok")]
        if not lat:
            continue
        pred = trips * delay_s * 1e3
        med = statistics.median(lat)
        out["modes"][mode] = {"messages": len(lat), "trips": trips, "predicted_ms": pred, "median_ms": med, "max_ms": max(lat),
                              "overhead_ms": med - pred, "trips_measured": med / (delay_s * 1e3) if delay_s > 0 else None}
    out["refused"] = sum(1 for r in log if not r.get("ok"))
    return out


# --------------------------------------------------------------------------------------------- command line
def _serve_cli(a) -> int:
    store, body = load_bank(Path(a.bank), "B")
    key = Path(a.key).read_bytes()
    with socket.create_server((a.host, a.port)) as srv:
        if a.port_file:
            Path(a.port_file).write_text(str(srv.getsockname()[1]), encoding="utf-8")
        conn, _ = srv.accept()
        with conn:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            link = AuthLink.connect(conn, key, "B", "site-b", "site-a")
            conn.settimeout(60)
            Receiver(link, store, a.delay_ms / 1e3, Path(a.bank)).serve()
    return 0


def _send_cli(a) -> int:
    store, body = load_bank(Path(a.bank), "A")
    key = Path(a.key).read_bytes()
    with socket.create_connection((a.host, a.port), timeout=10) as s:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        link = AuthLink.connect(s, key, "A", "site-a", "site-b")
        s.settimeout(60)
        snd = Sender(link, store, a.delay_ms / 1e3, Path(a.bank))
        sent = []
        for i in range(a.n):
            msg = f"message {i}: hello from site A".encode()
            for mode in a.modes:
                sent.append(snd.banked(msg) if mode == "banked" else snd.on_demand(msg))
        _send(link, {"t": "done"}, 0.0)
        log = _recv(link)["log"]
    result = summarize(sent, log, a.delay_ms / 1e3)
    result["bank"] = {"run_id": body["run_id"], "origin": body["origin"], "keys_left": store.status()["stored_key_count"]}
    print(json.dumps(result, indent=1))
    return 0 if result["refused"] == 0 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Secure messages in one trip, with key banked in advance (step L2).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bank", help="run one session and bank each site's key in its own file")
    b.add_argument("--out-a", required=True); b.add_argument("--out-b", required=True); b.add_argument("--pulses", type=int, default=400_000)
    s = sub.add_parser("serve", help="site B: receive and decrypt")
    s.add_argument("--bank", required=True); s.add_argument("--key", required=True); s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=0); s.add_argument("--port-file"); s.add_argument("--delay-ms", type=float, default=0.0)
    c = sub.add_parser("send", help="site A: send n messages per mode and compare delivery with the model")
    c.add_argument("--bank", required=True); c.add_argument("--key", required=True); c.add_argument("--host", default="127.0.0.1")
    c.add_argument("--port", type=int, required=True); c.add_argument("--delay-ms", type=float, default=0.0); c.add_argument("-n", type=int, default=10)
    c.add_argument("--modes", nargs="+", choices=list(TRIPS), default=list(TRIPS))
    a = ap.parse_args(argv)
    if a.cmd == "bank":
        from qll.link.config import LinkConfig
        print(json.dumps(banks_from_session(Path(a.out_a), Path(a.out_b), LinkConfig(n_pulses=a.pulses)), indent=1))
        return 0
    try:
        return _serve_cli(a) if a.cmd == "serve" else _send_cli(a)
    except (BankError, LinkError, KeyUnavailable, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
