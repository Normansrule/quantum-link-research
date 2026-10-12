"""The two-room bench (protocol P10): its twin from parts, the per-site logs that a two-computer run writes, and the
authenticated classical channel between the rooms."""
import json
import math
import socket
import threading

import numpy as np
import pytest

from qll.link import two_room as T
from qll.link.config import LinkConfig
from qll.link.hardware_log import read_log, read_site_logs, run_from_site_logs, simulate_quantum, write_site_logs
from qll.link.net_transport import AuthLink, LinkError, new_key, probe, serve
from qll.link.protocol_bb84 import run_session

pytestmark = pytest.mark.phase3
SMALL = T.TwoRoomParts(n_pulses=2_000_000)


def test_photon_number_and_filter_attenuation_are_inverse():
    e = 1e-12                                                       # a 1 pJ pulse at 405 nm holds about 2.04 million photons
    assert T.mean_photon_number(e, 405e-9, 0.0) == pytest.approx(2.0388e6, rel=1e-3)
    a = T.attenuation_for(0.5, e, 405e-9)
    assert T.mean_photon_number(e, 405e-9, a) == pytest.approx(0.5, rel=1e-12)


def test_sipm_dark_counts_per_gate():
    assert T.dark_prob_per_gate(300e3, 5e-9, detectors=1) == pytest.approx(1 - math.exp(-1.5e-3))
    assert T.dark_prob_per_gate(300e3, 5e-9) == pytest.approx(1 - math.exp(-3e-3), rel=1e-9)   # two detectors per basis


def test_twin_matches_the_closed_form_prediction():
    p = SMALL
    pred = T.predict(p)
    m = run_session(T.config(p)).metrics
    sd = math.sqrt(pred["click_prob_per_pulse"] * (1 - pred["click_prob_per_pulse"]) / p.n_pulses)
    assert abs(m.detection_probability - pred["click_prob_per_pulse"]) < 5 * sd + 0.002 * pred["click_prob_per_pulse"]
    assert m.qber_estimate == pytest.approx(pred["expected_qber"], abs=0.008)


def test_free_space_gives_key_and_the_fiber_variant_does_not_yet():
    free = run_session(T.config(T.TwoRoomParts())).metrics          # ten-second decoy session across the hallway
    assert free.accepted and free.net_key_bits > 5_000 and abs(free.decoy_gain_deviation_sd) < 5
    fiber = run_session(T.config(T.TwoRoomParts(channel="fiber"))).metrics
    assert not fiber.accepted                                       # 6 dB of coupling at 405 nm: dark counts win
    no_decoy = run_session(T.config(SMALL).with_(source_model="weak_coherent")).metrics
    assert not no_decoy.accepted and no_decoy.reject_reason == "single_photon"


def test_committed_preset_is_the_twin_of_its_parts(tmp_path):
    d = json.loads(T.PRESET.read_text(encoding="utf-8"))
    parts = T.TwoRoomParts(**d["_parts"])
    fresh = json.loads(T.write_preset(parts, tmp_path / "p.json").read_text(encoding="utf-8"))
    assert fresh == d
    assert LinkConfig.from_dict(d) == T.config(parts)


def test_two_site_logs_reproduce_the_simulated_session_exactly(tmp_path):
    c = T.config(T.TwoRoomParts(n_pulses=6_000_000))                # six seconds: the shortest session that keeps key
    rec = simulate_quantum(c)
    a, b = write_site_logs(rec, tmp_path / "room_a.csv", tmp_path / "room_b.csv")
    assert len(b.read_text(encoding="utf-8").splitlines()) - 1 == int(rec.det.detected.sum())  # Room B logs only its clicks
    direct, logged = run_session(c), run_from_site_logs(a, b, c)
    assert logged.metrics.final_key_bits == direct.metrics.final_key_bits > 0
    assert np.array_equal(logged.key_a, direct.key_a) and logged.metrics.run_id == direct.metrics.run_id
    report = T.check_against_twin(logged.metrics, T.TwoRoomParts(n_pulses=6_000_000))
    assert report["all_pass"], report                                  # the twin accepts its own data
    worse = T.check_against_twin(logged.metrics, T.TwoRoomParts(n_pulses=6_000_000, sipm_pde=0.6, polarizer_extinction=20))
    assert [r["result"] for r in worse["rows"]][:2] == ["CHECK", "CHECK"]  # and flags parts that do not match the data
    from qll.link.run import main
    main(["ingest", str(a), "--bob", str(b), "--config", str(T.PRESET), "--set", "n_pulses=6000000"])


def test_site_logs_are_validated(tmp_path):
    rec = simulate_quantum(T.config(T.TwoRoomParts(n_pulses=20_000)))
    a, b = write_site_logs(rec, tmp_path / "a.csv", tmp_path / "b.csv")
    lines = b.read_text(encoding="utf-8").splitlines()
    (tmp_path / "bad.csv").write_text("\n".join([lines[0], lines[2], lines[1]] + lines[3:]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="increasing"):
        read_site_logs(a, tmp_path / "bad.csv")
    (tmp_path / "nobob.csv").write_text("pulse,bob_bit\n1,0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing"):
        read_site_logs(a, tmp_path / "nobob.csv")


def _server(key):
    ready = threading.Event()
    threading.Thread(target=serve, args=(0, key, "127.0.0.1", True, ready), daemon=True).start()
    assert ready.wait(5)
    return ready.port


def test_classical_link_round_trips_and_authenticates(tmp_path):
    key = new_key(tmp_path / "k").read_bytes()
    r = probe("127.0.0.1", _server(key), key, n=200, size=512, path_m=10.0)
    assert r["frames"] == 200 and r["rtt_median_us"] > 0 and r["light_round_trip_us"] == pytest.approx(2 * 10 / 299_792_458 * 1e6)


def _pair(key=b"k" * 32, key_b=None, id_a="room-a", id_b="room-b", expect_a=None, expect_b=None):
    """A connected pair after the handshake (B runs in a thread)."""
    s1, s2 = socket.socketpair()
    box = {}
    def side_b():
        try:
            box["b"] = AuthLink.connect(s2, key_b or key, "B", id_b, expect_a)
        except Exception as e:                       # noqa: BLE001 - reported to the test
            box["err"] = e
    t = threading.Thread(target=side_b); t.start()
    try:
        a = AuthLink.connect(s1, key, "A", id_a, expect_b)
    except Exception:
        s1.close(); s2.close()                                              # unblock B, then report A's failure
        t.join(5)
        raise
    t.join(5)
    if "err" in box:
        raise box["err"]
    return s1, s2, a, box["b"]


def test_classical_link_rejects_tampering_replay_reflection_and_wrong_keys():
    s1, s2, a, b = _pair()
    with s1, s2:
        a.send(b"sifting: bases 0110"); assert b.recv() == b"sifting: bases 0110"
        b.send(b"ok"); assert a.recv() == b"ok"
    s1, s2, a, b = _pair()
    with s1, s2:
        a.send(b"one"); b.recv()
        a.sent = 0; a.send(b"one")                                          # replay within the session
        with pytest.raises(LinkError, match="expected"):
            b.recv()
    s1, s2, a, b = _pair()
    with s1, s2:
        a.send(b"x" * 10)
        raw = bytearray(s2.recv(4 + 8 + 10 + 32)); raw[14] ^= 1             # altered in transit
        s1.sendall(bytes(raw))
        with pytest.raises(LinkError, match="authentication"):
            b.recv()
    with pytest.raises(LinkError, match="handshake authentication"):
        _pair(key=b"k" * 32, key_b=b"z" * 32)                             # wrong key: the handshake fails


def test_a_frame_from_one_connection_fails_on_the_next():
    s1, s2, a, b = _pair()
    with s1, s2:
        a.send(b"pay 100")
        captured = s2.recv(4 + 8 + 7 + 32)                                  # an eavesdropper records the frame
    s3, s4, a2, b2 = _pair()                                                # same key, new connection, new session key
    with s3, s4:
        s3.sendall(captured)
        with pytest.raises(LinkError, match="authentication"):
            b2.recv()


def test_reflection_and_identity_and_version_are_checked():
    s1, s2, a, b = _pair()
    with s1, s2:
        b.send(b"to A")
        frame = s1.recv(4 + 8 + 4 + 32)
        s1.sendall(frame)                                                   # B's own frame reflected back to B
        with pytest.raises(LinkError, match="authentication"):
            b.recv()
    with pytest.raises(LinkError, match="identity"):
        _pair(expect_b="room-c")                                            # A expects a different peer
    s1, s2 = socket.socketpair()
    with s1, s2:
        from qll.link.net_transport import _pack, _send_raw
        _send_raw(s1, _pack(b"QLL0", b"A", b"room-a", b"n" * 32))           # an old version
        with pytest.raises(LinkError, match="version"):
            AuthLink.connect(s2, b"k" * 32, "B", "room-b")


def test_stalled_handshakes_and_partial_frames_time_out():
    s1, s2 = socket.socketpair()
    with s1, s2:
        with pytest.raises(LinkError, match="timed out"):
            AuthLink.connect(s2, b"k" * 32, "B", "room-b", timeout=0.2)     # A never speaks
    s1, s2, a, b = _pair()
    with s1, s2:
        s1.sendall(b"\x00\x00\x00\x40" + b"x" * 10)                         # half a frame, then silence
        s2.settimeout(0.2)
        with pytest.raises(LinkError, match="timed out"):
            b.recv()


def test_new_key_refuses_to_overwrite(tmp_path):
    p = new_key(tmp_path / "k")
    assert len(p.read_bytes()) == 32
    with pytest.raises(FileExistsError):
        new_key(p)

@pytest.mark.parametrize("bad, why", [("0.9", "exact integer"), ("1e0", "exact integer"), ("", "exact integer"), (" ", "exact integer")])
def test_logs_refuse_fractional_and_ambiguous_fields(tmp_path, bad, why):
    p = tmp_path / "log.csv"
    p.write_text("pulse,alice_bit,alice_basis,bob_basis,bob_click,bob_bit\n0,1,0,0,1,1\n1," + bad + ",0,0,1,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match=why):
        read_log(p)


def test_logs_refuse_duplicates_unknown_columns_short_rows_and_pulse_gaps(tmp_path):
    cases = {"dup": "pulse,alice_bit,alice_bit,alice_basis,bob_basis,bob_click,bob_bit\n0,1,1,0,0,1,1\n",
             "unknown": "pulse,alice_bit,alice_basis,bob_basis,bob_click,bob_bit,extra\n0,1,0,0,1,1,5\n",
             "short": "pulse,alice_bit,alice_basis,bob_basis,bob_click,bob_bit\n0,1,0,0,1\n",
             "gap": "pulse,alice_bit,alice_basis,bob_basis,bob_click,bob_bit\n0,1,0,0,1,1\n2,1,0,0,1,1\n"}
    for name, text in cases.items():
        p = tmp_path / f"{name}.csv"; p.write_text(text, encoding="utf-8")
        with pytest.raises(ValueError):
            read_log(p)


def test_synthetic_logs_stay_labelled_synthetic(tmp_path):
    from qll.link.hardware_log import provenance, simulate_log
    p = simulate_log(T.config().with_(n_pulses=2000), tmp_path / "run.csv")
    assert provenance(p)["origin"] == "synthetic" and len(provenance(p)["sha256"]) == 64
    q = tmp_path / "copy.csv"; q.write_bytes(p.read_bytes())
    assert provenance(q)["origin"] == "unlabelled"                       # renaming a synthetic file never makes it measured
