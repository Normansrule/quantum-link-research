"""Phase 6: hybrid keys agree, AES-GCM authenticates and refuses replay, the messenger fails closed and respects light time."""
import pytest
from cryptography.exceptions import InvalidTag

from qll.app.aes_gcm_layer import MESSAGE_BUDGET_PER_KEY, KeyedChannel
from qll.app.benchmark import run_conversation
from qll.app.hybrid_kem import combine, establish, keygen
from qll.app.messenger import KeyBuffer, KeyExhausted, Messenger, required_buffer_bytes
from qll.channels.light_time_delay import NotYetArrived, one_way_delay_s, round_trip_delay_s
from qll.constants.astro import EARTH_MARS_MIN_M

pytestmark = pytest.mark.phase6


def test_hybrid_kem_both_sides_agree_and_depend_on_both_inputs():
    ek, dk = keygen()
    a, b = establish(ek, dk, b"q" * 32, distance_m=EARTH_MARS_MIN_M)
    assert a.session_key == b.session_key and len(a.session_key) == 32
    assert a.classical_time_s == pytest.approx(round_trip_delay_s(EARTH_MARS_MIN_M))
    assert combine(b"a" * 32, b"q" * 32) != combine(b"a" * 32, b"r" * 32)     # QKD share matters
    assert combine(b"a" * 32, b"q" * 32) != combine(b"b" * 32, b"q" * 32)     # KEM share matters


def test_aes_gcm_roundtrip_tamper_and_replay():
    ch = KeyedChannel(b"k" * 32, key_id=1)
    seq, nonce, ct = ch.encrypt(b"secret", aad=b"0")
    assert ch.decrypt(nonce, ct, aad=b"0") == b"secret"
    with pytest.raises(RuntimeError):
        ch.decrypt(nonce, ct, aad=b"0")                                       # replay refused
    seq2, nonce2, ct2 = ch.encrypt(b"second", aad=b"1")
    with pytest.raises(InvalidTag):
        ch.decrypt(nonce2, ct2[:-1] + bytes([ct2[-1] ^ 1]), aad=b"1")         # tamper detected
    ch.counter = MESSAGE_BUDGET_PER_KEY
    with pytest.raises(RuntimeError):
        ch.encrypt(b"x")                                                       # budget enforced


def test_messenger_fails_closed_and_respects_light_time():                   # REQ-APP-001, INV-1
    kb = KeyBuffer(key_rate_bps=0.0, capacity_bytes=64, level_bytes=64)
    m = Messenger(EARTH_MARS_MIN_M, kb)
    ch = m.new_session(0.0); env = m.send(b"first", 0.0, ch)
    ch2 = m.new_session(1.0); m.send(b"second", 1.0, ch2)
    with pytest.raises(KeyExhausted):
        m.new_session(2.0)                                                     # buffer empty: refuse, do not downgrade
    with pytest.raises(NotYetArrived):
        m.receive(env, now_s=10.0)
    assert m.receive(env, now_s=env.message.earliest_arrival_s) == b"first"
    assert m.ack_arrival_s(env) == pytest.approx(2 * one_way_delay_s(EARTH_MARS_MIN_M))


def test_buffer_sizing_rule_prevents_refusals():
    rt = round_trip_delay_s(EARTH_MARS_MIN_M)
    interval = 30.0
    need = required_buffer_bytes(0.0, EARTH_MARS_MIN_M, 32, messages_per_s=1 / interval)
    ok = run_conversation(EARTH_MARS_MIN_M, 0.0, int(need) + 32, int(rt / interval) + 1, interval)
    assert ok.refusals == 0
    short = run_conversation(EARTH_MARS_MIN_M, 0.0, 64, int(rt / interval) + 1, interval)
    assert short.refusals > 0 and short.messages_sent == 2
    fed = run_conversation(EARTH_MARS_MIN_M, key_rate_bps=32 * 8 / interval, buffer_bytes=64, messages=20, interval_s=interval)
    assert fed.refusals == 0                                                   # key rate matches consumption
