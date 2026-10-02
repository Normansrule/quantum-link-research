"""The classical channel between the sites: public, but authenticated, with a full transcript.

Model
-----
Every protocol message (bases, sampled bits, parities, hash seeds, verification tags) is public: the adversary may
read all of it. It must not be alterable, or a man in the middle could impersonate either site. Two modes:
  "wegman_carter" (default): each site keeps the transcript as it saw it; at the end of the session each tags its view
      with a Wegman-Carter tag and the other checks the tag against its own view, before any key is accepted
      [wegman1981] [qll/link/authentication.py]. Information-theoretically secure; costs two one-time pads and a hash
      key per session, drawn from a pool refilled from the session's output.
  "hmac": every message carries HMAC-SHA256(k, sender | kind | payload), checked on receipt [nist2008fips198].
      Computationally secure; costs no key.
An altered message is therefore caught at once (hmac) or at the end of the session (wegman_carter); either way the
session is rejected. The laboratory channel has no modelled latency or loss. The transcript counts messages and bytes.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field

from qll.link.authentication import TAG_BITS, AuthKeyPool, forgery_bound, tag


class AuthenticationFailure(RuntimeError):
    """A classical message failed its authentication check; the session must be aborted."""


@dataclass(frozen=True)
class Message:
    sender: str
    kind: str
    payload: dict
    tag: str

    def body(self) -> bytes:
        return json.dumps([self.sender, self.kind, self.payload], sort_keys=True, separators=(",", ":")).encode()


@dataclass
class AuthenticatedChannel:
    auth_key: bytes
    tamper_kind: str | None = None          # if set, an attacker alters the first message of this kind in transit
    mode: str = "hmac"                      # or "wegman_carter"
    pool: AuthKeyPool | None = None         # required for wegman_carter
    transcript: list = field(default_factory=list)
    bytes_sent: int = 0
    _tampered: bool = False
    _views: dict = field(default_factory=lambda: {"A": [], "B": []})
    finalized: bool = False
    forgery_probability: float = 0.0

    def _tag(self, sender: str, kind: str, payload: dict) -> str:
        body = json.dumps([sender, kind, payload], sort_keys=True, separators=(",", ":")).encode()
        return hmac.new(self.auth_key, body, hashlib.sha256).hexdigest()

    def send(self, sender: str, kind: str, payload: dict) -> dict:
        """Send, deliver, and verify one message; return the payload the receiver accepts."""
        if self.mode == "wegman_carter":
            return self._send_wc(sender, kind, payload)
        msg = Message(sender, kind, payload, self._tag(sender, kind, payload))
        if self.tamper_kind == kind and not self._tampered:
            altered = dict(payload)
            altered["_altered_by_attacker"] = True
            msg = Message(sender, kind, altered, msg.tag)
            self._tampered = True
        self.transcript.append(msg)
        self.bytes_sent += len(msg.body()) + len(msg.tag) // 2
        if not hmac.compare_digest(msg.tag, self._tag(msg.sender, msg.kind, msg.payload)):
            raise AuthenticationFailure(f"authentication failed on a '{kind}' message from {sender}")
        return msg.payload

    def _send_wc(self, sender: str, kind: str, payload: dict) -> dict:
        receiver = "B" if sender == "A" else "A"
        delivered = payload
        if self.tamper_kind == kind and not self._tampered:
            delivered = dict(payload)
            delivered["_altered_by_attacker"] = True
            self._tampered = True
        sent_msg, got_msg = Message(sender, kind, payload, ""), Message(sender, kind, delivered, "")
        self._views[sender].append(sent_msg.body())
        self._views[receiver].append(got_msg.body())
        self.transcript.append(got_msg)
        self.bytes_sent += len(got_msg.body())
        return delivered

    def finalize(self) -> None:
        """Wegman-Carter mode: each site tags its view of the whole transcript; the other checks it. Raises
        AuthenticationFailure if the views differ. A no-op in hmac mode (every message was checked on arrival)."""
        if self.mode != "wegman_carter" or self.finalized:
            return
        if self.pool is None:
            raise ValueError("wegman_carter mode needs an AuthKeyPool")
        self.finalized = True
        k, pad_a, pad_b = self.pool.session_keys()
        view_a, view_b = b"\x1e".join(self._views["A"]), b"\x1e".join(self._views["B"])
        self.forgery_probability = forgery_bound(max(len(view_a), len(view_b)))
        tag_a, tag_b = tag(k, pad_a, view_a), tag(k, pad_b, view_b)
        self.transcript += [Message("A", "transcript_tag", {"bits": TAG_BITS}, ""), Message("B", "transcript_tag", {"bits": TAG_BITS}, "")]
        self.bytes_sent += 2 * (TAG_BITS + 1) // 8
        if tag_a != tag(k, pad_a, view_b) or tag_b != tag(k, pad_b, view_a):
            raise AuthenticationFailure("transcript tags differ: a classical message was altered in transit")

    @property
    def n_messages(self) -> int:
        return len(self.transcript)
