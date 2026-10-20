"""The LoRa range-walk log (qll/link/radio_survey.py): strict ingestion, honest labels, the signal-from-RSSI identity,
a fit that recovers the law a synthetic walk was drawn from, and the logger's packet parsing on recorded packets."""
import json
import math

import numpy as np
import pytest

from qll.link import mesh_messenger as M
from qll.link import radio_survey as R

pytestmark = pytest.mark.phase3


def test_signal_from_rssi_inverts_signal_plus_noise():
    floor = R.noise_floor_dbm(250e3)
    for s in (-60.0, -120.0, -128.0, -135.0):                          # above and below the noise floor
        rssi = 10 * math.log10(10 ** (s / 10) + 10 ** (floor / 10))
        assert R.signal_dbm(rssi, s - floor) == pytest.approx(s, abs=1e-9)
    assert R.signal_dbm(-80.0, 30.0) == pytest.approx(-80.0, abs=0.01)  # strong signal: RSSI is the signal


def test_prediction_is_the_mesh_models_link_budget():
    run = R.default_run()
    d = 1500.0
    want = 20 + 2 + 2 - M.free_space_loss_db(d / 1000, run["f_mhz"]) - 20.0
    assert R.predicted_signal_dbm(run, [d], 20.0)[0] == pytest.approx(want)
    assert R.sensitivity_dbm(run) == pytest.approx(M.sensitivity_dbm(11, 250e3))


def test_clopper_pearson_closed_forms():
    lo, hi = R.clopper_pearson(20, 20)
    assert hi == 1.0 and lo == pytest.approx(0.025 ** (1 / 20))         # all received: lower bound (alpha/2)^(1/n)
    lo, hi = R.clopper_pearson(0, 20)
    assert lo == 0.0 and hi == pytest.approx(1 - 0.025 ** (1 / 20))
    with pytest.raises(ValueError):
        R.clopper_pearson(3, 2)


def test_the_fit_recovers_the_synthetic_law(tmp_path):
    # no shadowing or fading, and every packet received: the fit must return the exponent exactly
    p = R.simulate_survey(tmp_path / "w.csv", distances_m=(50, 100, 300, 900), packets=5, n=3.2, shadow_sigma_db=0.0,
                          fade_sigma_db=0.0, s_d0_dbm=-70.0)
    fit = R.fit_log_distance(R.read_survey(p))
    assert fit["n"] == pytest.approx(3.2, abs=0.01) and fit["s_d0_dbm"] == pytest.approx(-70.0, abs=0.1)
    sens = R.sensitivity_dbm(R.default_run())
    d = R.range_for_margin_m(fit, sens, 10.0)
    assert R.fitted_signal_dbm(fit, d) == pytest.approx(sens + 10.0)
    # with shadowing and fading over 80 stops and no losses, the exponent comes back within its standard error
    # (4 dB / (sqrt(80) x 4.3 dB of spread in 10 log10 d) = 0.1), and sigma near sqrt(4^2 + 2^2)
    p = R.simulate_survey(tmp_path / "f.csv", distances_m=tuple(np.geomspace(50, 1600, 80)), packets=20, n=2.7,
                          s_d0_dbm=-70.0, seed=3)
    s = R.read_survey(p)
    fit = R.fit_log_distance(s)
    assert s.received.all() and fit["n"] == pytest.approx(2.7, abs=0.3) and fit["sigma_db"] == pytest.approx(4.5, abs=0.8)


def test_synthetic_walks_are_labelled_simulated_and_measured_needs_a_declaration(tmp_path):
    p = R.simulate_survey(tmp_path / "w.csv")
    r = R.report(p)
    assert r["label"] == "SIMULATED" and r["inputs"][0]["origin"] == "synthetic" and len(r["inputs"][0]["sha256"]) == 64
    assert 0 <= r["agreement_default_model"] <= 1 and r["fit"]["n"] > 2
    side = p.with_name(p.name + ".run.json")
    run = json.loads(side.read_text(encoding="utf-8"))
    run["origin"] = "measured"
    side.write_text(json.dumps(run), encoding="utf-8")
    assert R.report(p)["label"] == "MEASURED HARDWARE"
    side.unlink()
    with pytest.raises(ValueError, match="radio settings"):
        R.read_survey(p)                                                 # no sidecar: refused, never assumed


@pytest.mark.parametrize("line, why", [
    ("0,100,0,1,,", "RSSI and SNR"),                                     # a reception without a reading
    ("0,100,0,0,-90,5", "lost packet"),                                  # a loss with a reading
    ("0,100,0,2,-90,5", "0 or 1"),
    ("0,1e2,0,1,-90,5", "integers and distance"),                         # exponents are refused
    ("0,0,0,1,-90,5", "positive"),
    ("0,100,0,1,-90", "fields"),
])
def test_ingestion_refuses_rather_than_repairs(tmp_path, line, why):
    p = R.write_survey(tmp_path / "w.csv", [], R.default_run())
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    with pytest.raises(ValueError, match=why):
        R.read_survey(p)


def test_ingestion_refuses_bad_headers_settings_and_duplicates(tmp_path):
    p = R.write_survey(tmp_path / "w.csv", [(0, 100.0, 0, 1, -90.0, 5.0), (0, 100.0, 0, 1, -91.0, 5.0)], R.default_run())
    with pytest.raises(ValueError, match="repeats"):
        R.read_survey(p)
    p = R.write_survey(tmp_path / "x.csv", [(0, 100.0, 0, 1, -90.0, 5.0), (0, 200.0, 1, 1, -91.0, 5.0)], R.default_run())
    with pytest.raises(ValueError, match="more than one distance"):
        R.read_survey(p)
    for bad in ({"preset": "LONG_FAST", "sf": 9}, {"origin": "measured?"}, {"tx_dbm": "20"}, {"colour": "red"}):
        R.write_survey(tmp_path / "y.csv", [(0, 100.0, 0, 1, -90.0, 5.0)], R.default_run(**bad))
        with pytest.raises(ValueError):
            R.read_survey(tmp_path / "y.csv")
    (tmp_path / "z.csv").write_text("stop,distance_m,seq,received,rssi,snr\n", encoding="utf-8")
    (tmp_path / "z.csv.run.json").write_text(json.dumps(R.default_run()), encoding="utf-8")
    with pytest.raises(ValueError, match="header"):
        R.read_survey(tmp_path / "z.csv")


def test_rows_from_heard_counts_gaps_and_shortfall_as_losses():
    heard = [(12, -100.0, 2.5), (14, -101.0, 1.0), (14, -99.0, 3.0), (15, -102.0, -4.0)]   # 13 lost; 14 heard twice
    rows = R.rows_from_heard(heard, 2, 800.0, expected=6)
    assert [r[2] for r in rows] == [12, 13, 14, 15, 16, 17]
    assert [r[3] for r in rows] == [1, 0, 1, 1, 0, 0]
    assert rows[2][4] == -101.0                                          # the first copy heard is kept
    assert R.rows_from_heard([], 0, 50.0, 3) == [(0, 50.0, i, 0, None, None) for i in range(3)]
    assert len(R.rows_from_heard(heard, 2, 800.0, expected=2)) == 4      # never drops a heard packet


def test_append_stop_builds_a_survey_and_refuses_mixed_settings(tmp_path):
    run = R.default_run(origin="measured")
    p = tmp_path / "walk.csv"
    R.append_stop(p, R.rows_from_heard([(0, -80.0, 9.0), (1, -81.0, 9.0)], 0, 100.0, 2), run)
    R.append_stop(p, R.rows_from_heard([(5, -110.0, -3.0)], 1, 900.0, 3), run)
    s = R.read_survey(p)
    assert list(np.unique(s.stop)) == [0, 1] and int(s.received.sum()) == 3 and len(s.stop) == 5
    with pytest.raises(ValueError, match="already"):
        R.append_stop(p, R.rows_from_heard([], 1, 900.0, 2), run)
    with pytest.raises(ValueError, match="settings"):
        R.append_stop(p, R.rows_from_heard([], 2, 1200.0, 2), R.default_run(origin="measured", tx_dbm=10.0))


def test_parse_packet_keeps_only_direct_range_test_packets():
    pkt = {"fromId": "!a1b2c3d4", "rxRssi": -97, "rxSnr": 6.25, "hopStart": 3, "hopLimit": 3,
           "decoded": {"portnum": "RANGE_TEST_APP", "payload": b"seq 42"}}
    assert R.parse_packet(pkt) == (42, -97.0, 6.25)
    assert R.parse_packet(pkt, "!a1b2c3d4") == (42, -97.0, 6.25)
    assert R.parse_packet(pkt, "!ffffffff") is None
    assert R.parse_packet(pkt | {"hopLimit": 2}) is None                 # relayed by another node
    assert R.parse_packet(pkt | {"decoded": {"portnum": "TEXT_MESSAGE_APP", "text": "seq 1"}}) is None
    assert R.parse_packet({k: v for k, v in pkt.items() if k != "rxSnr"}) is None
    assert R.parse_packet(pkt | {"decoded": {"portnum": "RANGE_TEST_APP", "text": "hello"}}) is None


def test_cli_report_and_refusal(tmp_path, capsys):
    p = R.simulate_survey(tmp_path / "w.csv")
    assert R.main(["report", str(p)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("SIMULATED") and "path-loss exponent" in out
    p.with_name(p.name + ".run.json").unlink()
    assert R.main(["report", str(p)]) == 2


def test_protocol_p16_quotes_the_twin():
    from pathlib import Path
    doc = (Path(__file__).resolve().parents[1] / "experiments" / "protocols" / "P16_lora_range_walk.md").read_text(encoding="utf-8")
    run = R.default_run()
    margins = {d: R.predicted_signal_dbm(run, [d], 20.0)[0] - R.sensitivity_dbm(run) for d in (100, 1000, 5000, 10000)}
    for d, label in ((100, "100 m"), (1000, "1 km"), (5000, "5 km"), (10000, "10 km")):
        assert f"| {label} | {margins[d]:.0f} dB |" in doc
    assert f"{M.radio_horizon_km(1.5, 1.5):.1f} km radio horizon" in doc
    assert f"takes {M.time_on_air_s(16, 11, 250e3):.2f} s on air" in doc
    assert f"{R.sensitivity_dbm(run):.1f} dBm".replace("-", "−") in doc
