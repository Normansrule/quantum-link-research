"""The three honest numbers for a Mars messenger versus distance: key bits per day (throughput, can look
terrestrial), round-trip time (never can), and the key buffer needed to send once a minute without a refusal."""
from __future__ import annotations

import numpy as np

from qll.app.messenger import required_buffer_bytes
from qll.channels.light_time_delay import round_trip_delay_s
from qll.constants.astro import AU_METERS, EARTH_MARS_MAX_M, EARTH_MARS_MIN_M
from qll.viz._common import cli, finish


def main() -> None:
    args = cli(__doc__)
    import matplotlib.pyplot as plt

    d = np.logspace(5, 12, 300)
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.loglog(d / 1e3, [round_trip_delay_s(x) / 60 for x in d], lw=2, label="round trip (min): the part no throughput hides")
    ax.loglog(d / 1e3, [required_buffer_bytes(0.0, x, 32, messages_per_s=1 / 60) / 1e3 for x in d], lw=2,
              label="key buffer to send 1 msg/min through a round trip (kB, zero key rate)")
    for x, n in ((3.844e8, "Moon"), (EARTH_MARS_MIN_M, "Mars min"), (AU_METERS, "1 au"), (EARTH_MARS_MAX_M, "Mars max")):
        ax.axvline(x / 1e3, ls="--", color="0.7"); ax.text(x / 1e3 * 1.1, 3e-3, n, rotation=90, fontsize=8, color="0.4")
    ax.set(xlabel="distance (km)", ylabel="minutes  /  kilobytes", ylim=(1e-3, 1e4),
           title="Messenger over a light-time channel (REQ-APP-001: refuse, never downgrade)")
    ax.legend(fontsize=8, loc="upper left")
    ax.text(0.99, 0.03, "What to look for: 32 B of QKD key per message × 45 messages in flight at Mars max ≈ 1.4 kB;\nthe buffer is tiny, the wait is not.", transform=ax.transAxes, ha="right", fontsize=8, color="0.3")
    finish(fig, args)


if __name__ == "__main__":
    main()
