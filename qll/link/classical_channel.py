"""The classical channel between the sites: public, but authenticated, with a full transcript.

Model
-----
Every protocol message (bases, sampled bits, parities, hash seeds, verification tags) is public: the adversary may
read all of it. It must not be alterable, or a man in the middle could impersonate either site, so each message
carries a tag HMAC-SHA256(k_auth, sender | kind | payload) [nist2008fips198], verified on receipt; a failed check
aborts the session. HMAC rests on a computational assumption; information-theoretic authentication, as the security
of BB84 strictly requires, uses Wegman-Carter universal hashing with a pre-shared key that is replenished from the
QKD output [wegman1981]. That substitution is recorded as an open item (systems/see510/09_limitations_and_hardware.md).
The laboratory channel has no modelled latency or loss. The transcript counts messages and bytes for the monitor.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field


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
    transcript: list = field(default_factory=list)
    bytes_sent: int = 0
    _tampered: bool = False

    def _tag(self, sender: str, kind: str, payload: dict) -> str:
        body = json.dumps([sender, kind, payload], sort_keys=True, separators=(",", ":")).encode()
        return hmac.new(self.auth_key, body, hashlib.sha256).hexdigest()

    def send(self, sender: str, kind: str, payload: dict) -> dict:
        """Send, deliver, and verify one message; return the payload the receiver accepts."""
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

    @property
    def n_messages(self) -> int:
        return len(self.transcript)
