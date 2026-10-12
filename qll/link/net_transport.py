"""The classical channel between two rooms, for real: authenticated, numbered frames over TCP, which runs unchanged on
Ethernet, Wi-Fi, or a pair of fiber media converters with a fiber patch cord between the rooms (P10, milestone M1.1).

Session binding (audit S04). Each connection starts with a handshake under the pre-shared key k:
    A -> B   HELLO   version | "A" | identity_A | nonce_A (32 random bytes)
    B -> A   HELLO   version | "B" | identity_B | nonce_B | HMAC(k, "confirm B" | transcript)
    A -> B   CONFIRM HMAC(k, "confirm A" | transcript)
where the transcript is both HELLO messages. Each side checks the other's confirmation, the protocol version, and,
when configured, the peer's expected identity. The session key is HKDF-SHA256(k, salt = nonce_A | nonce_B,
info = version | identity_A | identity_B) [rfc5869] and the session identifier is SHA-256 of the transcript. Each frame
is   length (4 bytes) | sequence number (8 bytes) | payload | tag (32 bytes),
with tag = HMAC-SHA256(session key, session id | direction | sequence number | payload) [nist2008fips198]. Fresh nonces
from both ends give every connection a new key, so a frame recorded on one connection fails on any other; the direction
in the tag stops reflection; the sequence number stops replay and reordering within a connection; the version in the
transcript stops a downgrade. Handshakes and reads have deadlines, and frames have a maximum length.

What this is not. It is a small lab construction from standard primitives, not a reviewed transport protocol; for
anything beyond a controlled lab network use mutually authenticated TLS with pinned certificates. HMAC is
computationally secure; the protocol's own Wegman-Carter tags (qll/link/authentication.py) remain the
information-theoretic layer on top, so this transport adds integrity on the wire, not the security argument. The key is
pre-shared: generate it with `newkey` (it refuses to overwrite an existing file) and carry it to the other room.

    python -m qll.link.net_transport newkey link.key
    python -m qll.link.net_transport serve --port 5510 --key link.key --id room-b               # room B
    python -m qll.link.net_transport probe --host 192.168.1.20 --key link.key --id room-a -n 2000 # room A

`probe` reports the round-trip time distribution, which is what the protocol's classical exchange waits on, and the
light's round trip over the path for comparison (qll/channels/light_time_delay.py; tens of nanoseconds between rooms,
negligible next to the computers' own delays). Note: the full BB84 session (qll/link/protocol_bb84.py) still runs
both sites in one process; this transport and the two-site logs are the pieces for separate endpoints (audit S05).
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import os
import secrets
import socket
import struct
import threading
import time
from pathlib import Path

import numpy as np

from qll.channels.light_time_delay import round_trip_delay_s

TAG = 32
NONCE = 32
MAX_FRAME = 1 << 22
VERSION = b"QLL1"
MAX_ID = 64
HANDSHAKE_TIMEOUT_S = 5.0


class LinkError(Exception):
    """A frame or handshake failed authentication, arrived out of sequence, timed out, or was malformed."""


def _hkdf(key: bytes, salt: bytes, info: bytes) -> bytes:
    prk = hmac.new(salt, key, hashlib.sha256).digest()                       # RFC 5869 extract
    return hmac.new(prk, info + b"\x01", hashlib.sha256).digest()             # expand, one block (32 bytes)


def _pack(*fields: bytes) -> bytes:
    return b"".join(struct.pack(">H", len(f)) + f for f in fields)


def _unpack(data: bytes, n: int) -> list[bytes]:
    out, i = [], 0
    for _ in range(n):
        if i + 2 > len(data):
            raise LinkError("malformed handshake")
        (ln,) = struct.unpack(">H", data[i:i + 2]); i += 2
        if i + ln > len(data):
            raise LinkError("malformed handshake")
        out.append(data[i:i + ln]); i += ln
    if i != len(data):
        raise LinkError("malformed handshake")
    return out


class AuthLink:
    """One end of an authenticated, sequenced stream bound to one fresh session. Create it with AuthLink.connect, which
    runs the handshake; frames from any other session, direction, or position are rejected."""

    def __init__(self, sock: socket.socket, session_key: bytes, session_id: bytes, role: str, peer_identity: str,
                 max_frame: int = MAX_FRAME):
        self.sock, self.key, self.session_id, self.role, self.peer_identity = sock, session_key, session_id, role, peer_identity
        self.max_frame = max_frame
        self.sent = 0
        self.received = 0

    # ------------------------------------------------------------------------------------------- handshake
    @classmethod
    def connect(cls, sock: socket.socket, psk: bytes, role: str, identity: str, expect_peer: str | None = None,
                timeout: float = HANDSHAKE_TIMEOUT_S, max_frame: int = MAX_FRAME) -> "AuthLink":
        if len(psk) < 32:
            raise ValueError("use a key of at least 32 bytes")
        if role not in ("A", "B"):
            raise ValueError("role must be 'A' or 'B'")
        ident = identity.encode()
        if not 0 < len(ident) <= MAX_ID:
            raise ValueError(f"identity must be 1 to {MAX_ID} bytes")
        old = sock.gettimeout()
        sock.settimeout(timeout)
        try:
            nonce = secrets.token_bytes(NONCE)
            if role == "A":
                hello_a = _pack(VERSION, b"A", ident, nonce)
                _send_raw(sock, hello_a)
                reply = _recv_raw(sock, 4 * (2 + MAX_ID + NONCE + TAG))
                ver, r, id_b, nonce_b, confirm_b = _unpack(reply, 5)
                hello_b = _pack(ver, r, id_b, nonce_b)
                _check_hello(ver, r, b"B", id_b, nonce_b, expect_peer)
                transcript = hello_a + hello_b
                if not hmac.compare_digest(confirm_b, hmac.new(psk, b"confirm B" + transcript, hashlib.sha256).digest()):
                    raise LinkError("handshake authentication failed: the peer does not hold the key")
                _send_raw(sock, hmac.new(psk, b"confirm A" + transcript, hashlib.sha256).digest())
                id_a, nonce_a, peer = ident, nonce, id_b
            else:
                hello_a = _recv_raw(sock, 4 * (2 + MAX_ID + NONCE))
                ver, r, id_a, nonce_a = _unpack(hello_a, 4)
                _check_hello(ver, r, b"A", id_a, nonce_a, expect_peer)
                hello_b = _pack(VERSION, b"B", ident, nonce)
                transcript = hello_a + hello_b
                confirm_b = hmac.new(psk, b"confirm B" + transcript, hashlib.sha256).digest()
                _send_raw(sock, _pack(VERSION, b"B", ident, nonce, confirm_b))
                confirm_a = _recv_raw(sock, TAG)
                if not hmac.compare_digest(confirm_a, hmac.new(psk, b"confirm A" + transcript, hashlib.sha256).digest()):
                    raise LinkError("handshake authentication failed: the peer does not hold the key")
                nonce_b, peer = nonce, id_a
                id_b = ident
            key = _hkdf(psk, nonce_a + nonce_b, VERSION + b"|" + id_a + b"|" + id_b)
            sid = hashlib.sha256(transcript).digest()[:16]
        except socket.timeout as err:
            raise LinkError("handshake timed out") from err
        finally:
            sock.settimeout(old)
        return cls(sock, key, sid, role, peer.decode(), max_frame)

    # ------------------------------------------------------------------------------------------- frames
    def _tag(self, direction: str, seq: int, payload: bytes) -> bytes:
        return hmac.new(self.key, self.session_id + direction.encode() + struct.pack(">Q", seq) + payload, hashlib.sha256).digest()

    def send(self, payload: bytes) -> None:
        direction = self.role + ">" + ("B" if self.role == "A" else "A")
        body = struct.pack(">Q", self.sent) + payload + self._tag(direction, self.sent, payload)
        if len(body) > self.max_frame:
            raise LinkError("frame too long")
        self.sock.sendall(struct.pack(">I", len(body)) + body)
        self.sent += 1

    def recv(self) -> bytes:
        try:
            (length,) = struct.unpack(">I", _read(self.sock, 4))
            if not 8 + TAG <= length <= self.max_frame:
                raise LinkError(f"frame length {length} out of range")
            body = _read(self.sock, length)
        except socket.timeout as err:
            raise LinkError("read timed out (partial or missing frame)") from err
        seq, payload, tag = struct.unpack(">Q", body[:8])[0], body[8:-TAG], body[-TAG:]
        direction = ("B" if self.role == "A" else "A") + ">" + self.role
        if not hmac.compare_digest(tag, self._tag(direction, seq, payload)):
            raise LinkError("authentication failed: the frame was altered, reflected, from another session, or the keys differ")
        if seq != self.received:
            raise LinkError(f"frame {seq} arrived when {self.received} was expected (replay, reorder, or loss)")
        self.received += 1
        return payload


def _check_hello(ver: bytes, role: bytes, want: bytes, ident: bytes, nonce: bytes, expect_peer: str | None) -> None:
    if ver != VERSION:
        raise LinkError(f"protocol version {ver!r} is not {VERSION!r}")
    if role != want:
        raise LinkError(f"peer claims role {role!r}, expected {want!r}")
    if len(nonce) != NONCE or not 0 < len(ident) <= MAX_ID:
        raise LinkError("malformed handshake")
    if expect_peer is not None and ident.decode(errors="replace") != expect_peer:
        raise LinkError(f"peer identity {ident.decode(errors='replace')!r} is not the expected {expect_peer!r}")


def _read(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise LinkError("peer closed the connection mid-frame" if buf else "peer closed the connection")
        buf += chunk
    return bytes(buf)


def _send_raw(sock: socket.socket, data: bytes) -> None:
    sock.sendall(struct.pack(">I", len(data)) + data)


def _recv_raw(sock: socket.socket, limit: int) -> bytes:
    (n,) = struct.unpack(">I", _read(sock, 4))
    if not 0 < n <= limit:
        raise LinkError("handshake message length out of range")
    return _read(sock, n)


def new_key(path: Path) -> Path:
    """Write 32 random bytes to a new file readable only by its owner; refuse to overwrite an existing key."""
    path = Path(path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError as err:
        raise FileExistsError(f"{path} exists; refusing to overwrite a key (delete it deliberately first)") from err
    with os.fdopen(fd, "wb") as fh:
        fh.write(secrets.token_bytes(32))
    return path


def serve(port: int, key: bytes, host: str = "0.0.0.0", once: bool = False, ready: threading.Event | None = None,
          identity: str = "room-b", expect_peer: str | None = None, idle_timeout: float = 30.0) -> None:
    """Room B: accept a connection, run the handshake, and echo every authenticated frame back. A connection that
    stalls in its handshake or goes idle is dropped, so it cannot hold the listener."""
    with socket.create_server((host, port)) as srv:
        if ready is not None:
            ready.port = srv.getsockname()[1]            # type: ignore[attr-defined]
            ready.set()
        while True:
            conn, _ = srv.accept()
            with conn:
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                try:
                    link = AuthLink.connect(conn, key, "B", identity, expect_peer)
                    conn.settimeout(idle_timeout)
                    while True:
                        link.send(link.recv())
                except (ConnectionError, LinkError, OSError):
                    pass
            if once:
                return


def probe(host: str, port: int, key: bytes, n: int = 1000, size: int = 256, path_m: float = 0.0, identity: str = "room-a",
          expect_peer: str | None = None) -> dict:
    """Room A: handshake, send n frames of `size` bytes, wait for each echo, and report round-trip statistics."""
    with socket.create_connection((host, port), timeout=10) as s:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        link = AuthLink.connect(s, key, "A", identity, expect_peer)
        rtt = np.empty(n)
        payload = secrets.token_bytes(size)
        t_start = time.perf_counter()
        for i in range(n):
            t0 = time.perf_counter()
            link.send(payload)
            if link.recv() != payload:
                raise LinkError("echo differs from what was sent")
            rtt[i] = time.perf_counter() - t0
        total = time.perf_counter() - t_start
    return {"frames": n, "bytes_per_frame": size, "rtt_median_us": float(np.median(rtt) * 1e6),
            "rtt_p99_us": float(np.percentile(rtt, 99) * 1e6), "rtt_max_us": float(rtt.max() * 1e6),
            "goodput_kbit_s": 2 * n * size * 8 / total / 1e3,
            "light_round_trip_us": round_trip_delay_s(path_m) * 1e6}       # the physical floor (in vacuum; fiber is slower)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    k = sub.add_parser("newkey"); k.add_argument("path")
    s = sub.add_parser("serve"); s.add_argument("--port", type=int, default=5510); s.add_argument("--key", required=True)
    s.add_argument("--id", default="room-b"); s.add_argument("--expect-peer", default=None)
    p = sub.add_parser("probe"); p.add_argument("--host", required=True); p.add_argument("--port", type=int, default=5510)
    p.add_argument("--key", required=True); p.add_argument("-n", type=int, default=1000); p.add_argument("--size", type=int, default=256)
    p.add_argument("--path-m", type=float, default=10.0); p.add_argument("--id", default="room-a"); p.add_argument("--expect-peer", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "newkey":
        print(f"wrote {new_key(Path(a.path))}; copy it to the other room by hand (USB stick), never over the network")
    elif a.cmd == "serve":
        serve(a.port, Path(a.key).read_bytes(), identity=a.id, expect_peer=a.expect_peer)
    else:
        r = probe(a.host, a.port, Path(a.key).read_bytes(), a.n, a.size, a.path_m, a.id, a.expect_peer)
        for key, v in r.items():
            print(f"{key:>22}: {v:,.3f}" if isinstance(v, float) else f"{key:>22}: {v}")


if __name__ == "__main__":
    main()
