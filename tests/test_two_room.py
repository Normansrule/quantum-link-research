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
from qll.link.hardware_log import read_site_logs, run_from_site_logs, simulate_quantum, write_site_logs
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
    assert len(b.read_text().splitlines()) - 1 == int(rec.det.detected.sum())  # Room B logs only its clicks
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
    lines = b.read_text().splitlines()
    (tmp_path / "bad.csv").write_text("\n".join([lines[0], lines[2], lines[1]] + lines[3:]) + "\n")
    with pytest.raises(ValueError, match="increasing"):
        read_site_logs(a, tmp_path / "bad.csv")
    (tmp_path / "nobob.csv").write_text("pulse,bob_bit\n1,0\n")
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


def test_classical_link_rejects_tampering_replay_and_wrong_keys():
    key = b"k" * 32
    s1, s2 = socket.socketpair()
    with s1, s2:
        a, b = AuthLink(s1, key, "A"), AuthLink(s2, key, "B")
        a.send(b"sifting: bases 0110"); assert b.recv() == b"sifting: bases 0110"
        b.send(b"ok"); assert a.recv() == b"ok"
        a.send(b"x" * 10)                                                   # altered in transit
        raw = bytearray(s2.recv(4 + 8 + 10 + 32)); raw[14] ^= 1
        s1b, s2b = socket.socketpair()
        with s1b, s2b:
            s1b.sendall(bytes(raw))
            with pytest.raises(LinkError, match="authentication"):
                AuthLink(s2b, key, "B").recv()
        frame = AuthLink(socket.socket(), key, "A")                           # a replayed frame: sequence 0 again
        s3, s4 = socket.socketpair()
        with s3, s4:
            sender, receiver = AuthLink(s3, key, "A"), AuthLink(s4, key, "B")
            sender.send(b"one"); receiver.recv()
            sender.sent = 0; sender.send(b"one")
            with pytest.raises(LinkError, match="expected"):
                receiver.recv()
        frame.sock.close()
        s5, s6 = socket.socketpair()
        with s5, s6:
            AuthLink(s5, key, "A").send(b"hello")
            with pytest.raises(LinkError, match="authentication"):
                AuthLink(s6, b"z" * 32, "B").recv()
