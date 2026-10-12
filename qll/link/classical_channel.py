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

State machine (audit S02): OPEN -> VERIFIED or OPEN -> FAILED, and neither can be left. A failed check, an exhausted
pool, or a verifier error leaves the channel FAILED, and every later finalize raises again; nothing can be sent after
the channel closes, so a verified transcript is immutable; and key release must call require_verified with the digest
of the exact transcript that was checked.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field

from qll.link.authentication import TAG_BITS, AuthKeyPool, forgery_bound, tag

OPEN, VERIFIED, FAILED = "OPEN", "VERIFIED", "FAILED"


class AuthenticationFailure(RuntimeError):
    """A classical message failed its authentication check; the session must be aborted."""


class ChannelClosed(RuntimeError):
    """A message was sent, or key release attempted, outside the state that allows it."""


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
    state: str = OPEN
    failure: str = ""
    transcript_digest: str = ""
    forgery_probability: float = 0.0

    @property
    def finalized(self) -> bool:
        return self.state != OPEN

    def _fail(self, why: str) -> AuthenticationFailure:
        self.state, self.failure = FAILED, why
        return AuthenticationFailure(why)

    def _digest(self) -> str:
        return hashlib.sha256(b"\x1e".join(self._views["A"]) + b"\x1d" + b"\x1e".join(m.body() for m in self.transcript)).hexdigest()

    def require_verified(self, digest: str) -> None:
        """Key release gate: the channel is VERIFIED and `digest` names the transcript that was checked."""
        if self.state != VERIFIED or not digest or digest != self.transcript_digest:
            raise ChannelClosed(f"key release refused: channel {self.state}, transcript digest {'matches' if digest == self.transcript_digest else 'does not match'}")

    def _tag(self, sender: str, kind: str, payload: dict) -> str:
        body = json.dumps([sender, kind, payload], sort_keys=True, separators=(",", ":")).encode()
        return hmac.new(self.auth_key, body, hashlib.sha256).hexdigest()

    def send(self, sender: str, kind: str, payload: dict) -> dict:
        """Send, deliver, and verify one message; return the payload the receiver accepts."""
        if self.state != OPEN:
            raise ChannelClosed(f"channel is {self.state}: no message may be added to a closed transcript")
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
        self._views[sender].append(msg.body())
        if not hmac.compare_digest(msg.tag, self._tag(msg.sender, msg.kind, msg.payload)):
            raise self._fail(f"authentication failed on a '{kind}' message from {sender}")
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

    def finalize(self) -> str:
        """Close the transcript and return its digest. Wegman-Carter mode: each site tags its view of the whole transcript
        and the other checks it. hmac mode: every message was checked on arrival, so closing seals the transcript. Raises
        AuthenticationFailure on any failure, now and on every later call (failures are sticky)."""
        if self.state == VERIFIED:
            return self.transcript_digest
        if self.state == FAILED:
            raise AuthenticationFailure(f"channel already FAILED: {self.failure}")
        if self.mode == "wegman_carter":
            if self.pool is None:
                raise self._fail("wegman_carter mode needs an authentication key pool")
            try:
                k, pad_a, pad_b = self.pool.session_keys()
            except Exception as err:                            # exhausted pool or invalid request: fail closed
                raise self._fail(f"authentication key unavailable: {err}") from err
            view_a, view_b = b"\x1e".join(self._views["A"]), b"\x1e".join(self._views["B"])
            self.forgery_probability = forgery_bound(max(len(view_a), len(view_b)))
            tag_a, tag_b = tag(k, pad_a, view_a), tag(k, pad_b, view_b)
            self.transcript += [Message("A", "transcript_tag", {"bits": TAG_BITS}, ""), Message("B", "transcript_tag", {"bits": TAG_BITS}, "")]
            self.bytes_sent += 2 * (TAG_BITS + 1) // 8
            if tag_a != tag(k, pad_a, view_b) or tag_b != tag(k, pad_b, view_a):
                raise self._fail("transcript tags differ: a classical message was altered in transit")
        self.transcript_digest = self._digest()
        self.state = VERIFIED
        return self.transcript_digest

    @property
    def n_messages(self) -> int:
        return len(self.transcript)
