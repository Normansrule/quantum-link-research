"""Verification step L2: with key banked in advance, a secure message is readable after one trip, between two ends
that share nothing but their own bank files. The banks are made from an accepted session, refuse tampering and
overwriting, and never let a key be used twice, even across restarts; the measured delivery times match the trip
counts of qll/space/latency_floor.py."""
import json
import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

from qll.link import banked_messenger as BM
from qll.link.key_store import KeyUnavailable
from qll.link.net_transport import AuthLink, new_key
from qll.space.latency_floor import SECURITY_TRIPS

pytestmark = pytest.mark.phase3
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def banks(tmp_path_factory):
    d = tmp_path_factory.mktemp("banks")
    info = BM.banks_from_session(d / "a.json", d / "b.json")
    return d, info


def _copy(banks, tmp_path):
    d, _ = banks
    for n in ("a.json", "b.json"):
        (tmp_path / n).write_bytes((d / n).read_bytes())
    return tmp_path / "a.json", tmp_path / "b.json"


def test_each_site_banks_its_own_key_and_the_identifiers_agree(banks, tmp_path):
    d, info = banks
    a, body_a = BM.load_bank(d / "a.json", "A")
    b, body_b = BM.load_bank(d / "b.json", "B")
    assert info["keys"] >= 10 and body_a["key_ids"] == body_b["key_ids"] and body_a["execution_id"] == body_b["execution_id"]
    assert all(a._keys[k] == b._keys[k] for k in body_a["key_ids"])               # equal because the session was accepted
    assert "not a security-reviewed" in body_a["origin"]
    if os.name == "posix":
        assert (d / "a.json").stat().st_mode & 0o777 == 0o600
    with pytest.raises(BM.BankError):
        BM.banks_from_session(d / "a.json", tmp_path / "other.json")                # never overwrites a bank
    with pytest.raises(BM.BankError):
        BM.load_bank(d / "a.json", "B")                                             # the wrong site's file


def test_an_edited_bank_is_refused(banks, tmp_path):
    a, _ = _copy(banks, tmp_path)
    body = json.loads(a.read_text(encoding="utf-8"))
    h = body["bits_hex"]
    body["bits_hex"] = ("0" if h[10] != "0" else "1").join([h[:10], h[11:]])
    a.write_text(json.dumps(body), encoding="utf-8")
    with pytest.raises(BM.BankError):
        BM.load_bank(a, "A")


def _pair(path_a, path_b, delay=0.0):
    """Two ends on a real loopback connection, each with its own store loaded from its own file."""
    key = os.urandom(32)
    srv = socket.create_server(("127.0.0.1", 0))
    out = {}

    def site_b():
        conn, _ = srv.accept()
        link = AuthLink.connect(conn, key, "B", "site-b", "site-a")
        store, _ = BM.load_bank(path_b, "B")
        out["b"] = BM.Receiver(link, store, delay, path_b)
        out["b_result"] = out["b"].serve()
        conn.close()

    t = threading.Thread(target=site_b, daemon=True)
    t.start()
    s = socket.create_connection(srv.getsockname())
    link = AuthLink.connect(s, key, "A", "site-a", "site-b")
    store, _ = BM.load_bank(path_a, "A")
    return BM.Sender(link, store, delay, path_a), t, out, s, srv


def _finish(snd, t, out, s, srv):
    BM._send(snd.link, {"t": "done"}, 0.0)
    log = BM._recv(snd.link)["log"]
    t.join(5); s.close(); srv.close()
    return log


def test_messages_decrypt_and_keys_are_never_reused(banks, tmp_path):
    a, b = _copy(banks, tmp_path)
    snd, t, out, s, srv = _pair(a, b)
    first = snd.banked(b"meet at the lab at nine")
    snd.on_demand(b"the same, with key made now")
    BM._send(snd.link, {"t": "msg", "kid": first["kid"], "nonce": "00" * 12, "ct": "00" * 32}, 0.0)     # replay of a spent key
    ((kid, key),) = snd.store.get_key(BM.APP, 1)
    BM._send(snd.link, {"t": "msg", "kid": kid, "nonce": "00" * 12, "ct": "ff" * 40}, 0.0)               # altered ciphertext
    log = _finish(snd, t, out, s, srv)
    assert [e["ok"] for e in log] == [True, True, False, False]
    assert "already used" in log[2]["error"] and "altered" in log[3]["error"]
    # restart both ends: the ledgers keep every spent key spent
    sa, body = BM.load_bank(a, "A")
    sb, _ = BM.load_bank(b, "B")
    assert body["spent_before_load"] == 1 and first["kid"] not in sa._keys and first["kid"] not in sb._keys and kid not in sb._keys


def test_an_empty_bank_refuses_to_send(banks, tmp_path):
    a, b = _copy(banks, tmp_path)
    snd, t, out, s, srv = _pair(a, b)
    snd.store.get_key(BM.APP, snd.store.status()["stored_key_count"])          # spend everything
    with pytest.raises(KeyUnavailable, match="refusing to send"):
        snd.banked(b"no key left")
    assert _finish(snd, t, out, s, srv) == []


def test_two_processes_deliver_in_the_trips_the_model_counts(banks, tmp_path):
    """The real thing: two operating-system processes, each loading only its own bank, with a 40 ms emulated path."""
    a, b = _copy(banks, tmp_path)
    key = new_key(tmp_path / "link.key")
    port_file = tmp_path / "port"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    server = subprocess.Popen([sys.executable, "-m", "qll.link.banked_messenger", "serve", "--bank", str(b), "--key", str(key),
                               "--port-file", str(port_file), "--delay-ms", "40"], cwd=ROOT, env=env)
    try:
        for _ in range(200):
            if port_file.exists() and port_file.read_text(encoding="utf-8").strip():
                break
            time.sleep(0.05)
        r = subprocess.run([sys.executable, "-m", "qll.link.banked_messenger", "send", "--bank", str(a), "--key", str(key),
                            "--port", port_file.read_text(encoding="utf-8").strip(), "--delay-ms", "40", "-n", "4"],
                           cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", timeout=60)
    finally:
        server.wait(timeout=10) if server.poll() is None else None
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout)
    banked, demand = res["modes"]["banked"], res["modes"]["on-demand"]
    assert banked["trips"] == SECURITY_TRIPS["banked key"] and demand["trips"] == SECURITY_TRIPS["QKD on demand"]
    assert 0.95 < banked["trips_measured"] < 1.6 and 2.95 < demand["trips_measured"] < 3.8
    assert res["refused"] == 0 and res["bank"]["keys_left"] == banks[1]["keys"] - 4             # one key per banked message
