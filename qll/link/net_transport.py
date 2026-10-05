"""The classical channel between two rooms, for real: authenticated, numbered frames over TCP, which runs unchanged on
Ethernet, Wi-Fi, or a pair of fiber media converters with a fiber patch cord between the rooms (P10, milestone M1.1).

Each frame is   length (4 bytes) | sequence number (8 bytes) | payload | tag (32 bytes),
with tag = HMAC-SHA256(k, direction | sequence number | payload) [nist2008fips198]. The receiver rejects a frame
whose tag fails (tampering), whose sequence number is not the next one expected (replay, reordering, or loss), or
that is longer than `max_frame`. The key is pre-shared: generate it with `newkey` in one room and carry the file to
the other. HMAC is computationally secure; the protocol's own Wegman-Carter tags (qll/link/authentication.py) remain
the information-theoretic layer on top, so this transport adds integrity on the wire, not the security argument.

    python -m qll.link.net_transport newkey link.key
    python -m qll.link.net_transport serve --port 5510 --key link.key                 # room B
    python -m qll.link.net_transport probe --host 192.168.1.20 --key link.key -n 2000  # room A: round trips, throughput

`probe` reports the round-trip time distribution, which is what the protocol's classical exchange waits on, and the
light's round trip over the path for comparison (qll/channels/light_time_delay.py; tens of nanoseconds between rooms,
negligible next to the computers' own delays).
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
MAX_FRAME = 1 << 22


class LinkError(Exception):
    """A frame failed its authentication, arrived out of sequence, or was malformed."""


class AuthLink:
    """One end of an authenticated, sequenced stream over a connected socket."""

    def __init__(self, sock: socket.socket, key: bytes, role: str, max_frame: int = MAX_FRAME):
        if len(key) < 32:
            raise ValueError("use a key of at least 32 bytes")
        if role not in ("A", "B"):
            raise ValueError("role must be 'A' or 'B'")
        self.sock, self.key, self.role, self.max_frame = sock, key, role, max_frame
        self.sent = 0
        self.received = 0

    def _tag(self, direction: str, seq: int, payload: bytes) -> bytes:
        return hmac.new(self.key, direction.encode() + struct.pack(">Q", seq) + payload, hashlib.sha256).digest()

    def send(self, payload: bytes) -> None:
        direction = self.role + ">" + ("B" if self.role == "A" else "A")
        body = struct.pack(">Q", self.sent) + payload + self._tag(direction, self.sent, payload)
        self.sock.sendall(struct.pack(">I", len(body)) + body)
        self.sent += 1

    def _read(self, n: int) -> bytes:
        buf = bytearray()
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("peer closed the connection")
            buf += chunk
        return bytes(buf)

    def recv(self) -> bytes:
        (length,) = struct.unpack(">I", self._read(4))
        if not 8 + TAG <= length <= self.max_frame:
            raise LinkError(f"frame length {length} out of range")
        body = self._read(length)
        seq, payload, tag = struct.unpack(">Q", body[:8])[0], body[8:-TAG], body[-TAG:]
        direction = ("B" if self.role == "A" else "A") + ">" + self.role
        if not hmac.compare_digest(tag, self._tag(direction, seq, payload)):
            raise LinkError("authentication failed: the frame was altered or the keys differ")
        if seq != self.received:
            raise LinkError(f"frame {seq} arrived when {self.received} was expected (replay, reorder, or loss)")
        self.received += 1
        return payload


def new_key(path: Path) -> Path:
    Path(path).write_bytes(secrets.token_bytes(32))
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return Path(path)


def serve(port: int, key: bytes, host: str = "0.0.0.0", once: bool = False, ready: threading.Event | None = None) -> None:
    """Room B: accept a connection and echo every authenticated frame back."""
    with socket.create_server((host, port)) as srv:
        if ready is not None:
            ready.port = srv.getsockname()[1]            # type: ignore[attr-defined]
            ready.set()
        while True:
            conn, _ = srv.accept()
            with conn:
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                link = AuthLink(conn, key, "B")
                try:
                    while True:
                        link.send(link.recv())
                except (ConnectionError, LinkError):
                    pass
            if once:
                return


def probe(host: str, port: int, key: bytes, n: int = 1000, size: int = 256, path_m: float = 0.0) -> dict:
    """Room A: send n frames of `size` bytes, wait for each echo, and report round-trip statistics."""
    with socket.create_connection((host, port), timeout=10) as s:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        link = AuthLink(s, key, "A")
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
    p = sub.add_parser("probe"); p.add_argument("--host", required=True); p.add_argument("--port", type=int, default=5510)
    p.add_argument("--key", required=True); p.add_argument("-n", type=int, default=1000); p.add_argument("--size", type=int, default=256)
    p.add_argument("--path-m", type=float, default=10.0)
    a = ap.parse_args(argv)
    if a.cmd == "newkey":
        print(f"wrote {new_key(Path(a.path))}; copy it to the other room by hand (USB stick), never over the network")
    elif a.cmd == "serve":
        serve(a.port, Path(a.key).read_bytes())
    else:
        r = probe(a.host, a.port, Path(a.key).read_bytes(), a.n, a.size, a.path_m)
        for key, v in r.items():
            print(f"{key:>22}: {v:,.3f}" if isinstance(v, float) else f"{key:>22}: {v}")


if __name__ == "__main__":
    main()
