"""Record one stop of a LoRa range walk (experiments/protocols/P16_lora_range_walk.md) from a Meshtastic board
plugged into this computer by USB.

The sending board runs Meshtastic's Range Test module, which transmits a numbered packet every interval. At each stop,
run this script with the stop number and its distance; it listens for the given number of minutes, keeps only direct
Range Test packets from the sender, and appends the stop to the survey CSV with the losses filled in
(qll.link.radio_survey.rows_from_heard). The first stop also writes the sidecar <out>.run.json with the radio settings,
labelled "measured". Then: python -m qll.link.radio_survey report <out>.

Needs the meshtastic package (pip install meshtastic), which the rest of the repository does not. UNTESTED ON
HARDWARE in this repository's CI: the packet parsing is tested with recorded packet dictionaries, the serial link is
not.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from qll.link import radio_survey as R  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--out", type=Path, required=True, help="survey CSV (created on the first stop)")
    p.add_argument("--stop", type=int, required=True)
    p.add_argument("--distance-m", type=float, required=True, help="distance from the sender, from a map or GPS")
    p.add_argument("--minutes", type=float, default=10.0)
    p.add_argument("--interval-s", type=float, default=30.0, help="the sender's Range Test interval")
    p.add_argument("--sender", default=None, help="the sender's node id, such as !a1b2c3d4 (recommended)")
    p.add_argument("--port", default=None, help="serial port; found automatically when omitted")
    p.add_argument("--preset", default="LONG_FAST", choices=sorted(R.PRESETS))
    p.add_argument("--f-mhz", type=float, default=906.875, help="channel centre; the Meshtastic app shows it")
    p.add_argument("--tx-dbm", type=float, required=True, help="the sender's transmit power setting")
    p.add_argument("--tx-gain-dbi", type=float, default=2.0)
    p.add_argument("--rx-gain-dbi", type=float, default=2.0)
    p.add_argument("--tx-height-m", type=float, required=True)
    p.add_argument("--rx-height-m", type=float, required=True)
    p.add_argument("--payload-bytes", type=int, default=16)
    p.add_argument("--site", default="")
    p.add_argument("--notes", default="")
    a = p.parse_args(argv)

    try:
        from meshtastic.serial_interface import SerialInterface
        from pubsub import pub
    except ImportError:
        print("this script needs the meshtastic package: pip install meshtastic", file=sys.stderr)
        return 2

    run = {"origin": "measured", "preset": a.preset, "f_mhz": a.f_mhz, "tx_dbm": a.tx_dbm, "tx_gain_dbi": a.tx_gain_dbi,
           "rx_gain_dbi": a.rx_gain_dbi, "tx_height_m": a.tx_height_m, "rx_height_m": a.rx_height_m,
           "payload_bytes": a.payload_bytes, "sender_interval_s": a.interval_s, "site": a.site,
           "date": time.strftime("%Y-%m-%d"), "notes": a.notes, "writer": "scripts/lora_survey_logger.py"}
    run = R._with_preset(run)
    heard = []

    def on_receive(packet, interface):
        got = R.parse_packet(packet, a.sender)
        if got is not None:
            heard.append(got)
            print(f"  seq {got[0]}  RSSI {got[1]:.0f} dBm  SNR {got[2]:.2f} dB", flush=True)

    pub.subscribe(on_receive, "meshtastic.receive")
    iface = SerialInterface(a.port) if a.port else SerialInterface()
    print(f"stop {a.stop} at {a.distance_m:g} m: listening for {a.minutes:g} minutes", flush=True)
    try:
        time.sleep(a.minutes * 60)
    except KeyboardInterrupt:
        print("stopped early", file=sys.stderr)
    finally:
        iface.close()
    expected = int(a.minutes * 60 // a.interval_s)
    rows = R.rows_from_heard(heard, a.stop, a.distance_m, expected)
    R.append_stop(a.out, rows, run)
    got = sum(r[3] for r in rows)
    print(f"stop {a.stop}: {got} of {len(rows)} packets received; appended to {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
