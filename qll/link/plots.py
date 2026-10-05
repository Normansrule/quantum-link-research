"""Evidence plots for the two-site link (systems/see510/evidence/plots/). Simulated sessions are points; the closed-form
expectation of qll/link/models.py is a gray line, so every plot doubles as a validation figure. Colors follow a
validated categorical order (blue, orange, aqua); outcome markers pair a status color with a shape and a legend label,
never color alone. Every plotted value is also in the scenario CSV files.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from qll.link import models
from qll.link.config import LinkConfig
from qll.link.monitor import REJECT_REASONS

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
MODEL, MUTED, GRID = "#55534e", "#8a887f", "#e6e5df"
GOOD, CRITICAL = "#0ca30c", "#d03b3b"


def _style(ax, title, xlabel, ylabel):
    ax.set_title(title, loc="left", fontsize=11)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def _save(fig, out: Path, name: str) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"{name}.svg"
    fig.tight_layout()
    import matplotlib
    with matplotlib.rc_context({"svg.hashsalt": name}):                       # stable element ids and no date: reruns
        fig.savefig(p, metadata={"Date": None})                              # leave an unchanged file unchanged
    import matplotlib.pyplot as plt
    plt.close(fig)
    return p


def _outcome(ax, x, y, ok, **kw):
    x, y, ok = np.asarray(x), np.asarray(y), np.asarray(ok, dtype=bool)
    if ok.any():
        ax.plot(x[ok], y[ok], "o", ms=7, mfc=GOOD, mec="white", mew=1.2, label="key accepted", **kw)
    if (~ok).any():
        ax.plot(x[~ok], y[~ok], "X", ms=8, mfc=CRITICAL, mec="white", mew=1.0, label="key rejected", **kw)


def make_all(dist, eve, loss, pairs, base: LinkConfig, out: Path) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    paths = []
    main = [m for m in dist if m.scenario == "2_distance"]
    long = [m for m in dist if m.scenario == "2_distance_long_block"]
    grid = np.linspace(0, max(m.distance_km for m in main), 200)

    # 1 loss vs distance
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.plot(grid, [models.channel_loss_db(base.with_(distance_km=d)) for d in grid], color=MODEL, lw=2)
    ax.plot([m.distance_km for m in main], [m.channel_loss_db for m in main], "o", ms=7, color=BLUE, mec="white")
    ax.annotate(f"{base.attenuation_db_per_km:g} dB/km", (grid[-1] * 0.6, models.channel_loss_db(base.with_(distance_km=grid[-1] * 0.6))),
                xytext=(10, -18), textcoords="offset points", color=MODEL)
    _style(ax, "Channel loss grows linearly with fiber length", "fiber length (km)", "channel loss (dB)")
    paths.append(_save(fig, out, "loss_vs_distance"))

    # 2 detection probability vs distance
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.semilogy(grid, [models.detection_prob(base.with_(distance_km=d)) for d in grid], color=MODEL, lw=2, label="model")
    ax.semilogy([m.distance_km for m in main], [max(m.detection_probability, 1e-9) for m in main], "o", ms=7, color=BLUE, mec="white", label="simulated sessions")
    ax.axhline(models.background_click_prob(base), color=MUTED, ls="--", lw=1)
    ax.annotate("background (dark counts)", (grid[-1], models.background_click_prob(base)), xytext=(-150, 6), textcoords="offset points", color=MUTED, fontsize=9)
    _style(ax, "Detection probability per pulse", "fiber length (km)", "detections per pulse")
    ax.legend(frameon=False)
    paths.append(_save(fig, out, "detection_vs_distance"))

    # 3 QBER vs distance
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    g2 = np.linspace(0, 250, 300)
    ax.plot(g2, [100 * models.expected_qber(base.with_(distance_km=d)) for d in g2], color=MODEL, lw=2, label="model")
    est = [m for m in main if m.sample_bits]
    ax.plot([m.distance_km for m in est], [100 * m.qber_estimate for m in est], "o", ms=7, color=BLUE, mec="white", label="estimated in session")
    ax.axhline(100 * base.qber_threshold, color=CRITICAL, ls="--", lw=1.2)
    ax.annotate(f"abort threshold {100 * base.qber_threshold:g} %", (5, 100 * base.qber_threshold), xytext=(0, 4), textcoords="offset points", fontsize=9)
    ax.axhline(100 * base.qber_alert, color=MUTED, ls=":", lw=1.2)
    ax.annotate(f"operator alert {100 * base.qber_alert:g} %", (5, 100 * base.qber_alert), xytext=(0, 4), textcoords="offset points", fontsize=9, color=MUTED)
    _style(ax, "Error rate: flat until dark counts take over", "fiber length (km)", "QBER (%)")
    ax.set_ylim(0, 30); ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0, 0.85))
    paths.append(_save(fig, out, "qber_vs_distance"))

    # 4 usable key vs distance
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.semilogy(grid, [max(models.asymptotic_secret_bits(base.with_(distance_km=d)), 1e-1) for d in grid], color=MODEL, lw=2, label="asymptotic reference (10⁶ pulses)")
    acc = [m for m in main if m.final_key_bits > 0]
    ax.semilogy([m.distance_km for m in acc], [m.final_key_bits for m in acc], "o", ms=7, color=BLUE, mec="white", label="final key, 10⁶-pulse sessions")
    accl = [m for m in long if m.final_key_bits > 0]
    if accl:
        ax.semilogy([m.distance_km for m in accl], [m.final_key_bits for m in accl], "s", ms=7, color=ORANGE, mec="white", label="final key, 10⁷-pulse sessions")
    _style(ax, "Usable key per session", "fiber length (km)", "final key bits")
    ax.set_ylim(10, None); ax.legend(frameon=False, fontsize=9)
    paths.append(_save(fig, out, "key_vs_distance"))

    # 5 acceptance vs distance
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    by = defaultdict(list)
    for m in main:
        by[m.distance_km].append(m.accepted)
    xs = sorted(by)
    frac = [np.mean(by[d]) for d in xs]
    ax.bar(range(len(xs)), frac, color=BLUE, width=0.6)
    for i, d in enumerate(xs):
        ax.text(i, frac[i] + 0.03, f"{sum(by[d])}/{len(by[d])}", ha="center", fontsize=9)
    ax.set_xticks(range(len(xs)), [f"{d:g}" for d in xs])
    _style(ax, "Sessions accepted (10⁶ pulses, three seeds)", "fiber length (km)", "fraction accepted")
    ax.set_ylim(0, 1.15)
    paths.append(_save(fig, out, "acceptance_vs_distance"))

    # 6 baseline vs adversary
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    fg = np.linspace(0, 1, 100)
    ax.plot(100 * fg, [100 * models.expected_qber(base.with_(eve_fraction=f)) for f in fg], color=MODEL, lw=2, label="model: e_mis + f/4")
    ev = [m for m in eve if m.scenario == "3_interception"]
    fr = [0.0 if m.adversary == "none" else float(m.adversary.split(" on ")[1].split(" %")[0]) for m in ev]
    _outcome(ax, fr, [100 * m.qber_estimate for m in ev], [m.accepted for m in ev])
    ax.axhline(100 * base.qber_threshold, color=CRITICAL, ls="--", lw=1.2)
    ax.axhline(100 * base.qber_alert, color=MUTED, ls=":", lw=1.2)
    _style(ax, "Interception raises the error rate", "pulses intercepted and resent (%)", "estimated QBER (%)")
    ax.legend(frameon=False, loc="upper left")
    paths.append(_save(fig, out, "baseline_vs_adversary"))

    # 7 privacy amplification against what the adversary knew
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    acc_e = [m for m in ev if m.accepted and m.adversary != "none"]
    if acc_e:
        xs = np.arange(len(acc_e))
        ax.bar(xs - 0.2, [m.eve_known_key_bits for m in acc_e], 0.38, color=ORANGE, label="key bits the adversary knew")
        ax.bar(xs + 0.2, [m.pa_removed_bits for m in acc_e], 0.38, color=BLUE, label="bits removed by privacy amplification")
        ax.set_xticks(xs, [m.adversary.split(" on ")[1].replace(" of pulses", "") + f"\nseed {m.seed}" for m in acc_e], fontsize=8)
        ax.legend(frameon=False, fontsize=9)
    _style(ax, "Amplification removes more than the adversary knew", "interception (accepted sessions)", "bits")
    paths.append(_save(fig, out, "amplification_vs_adversary"))

    # 8 noise vs adversary
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.4))
    for ax, attr, lab, scale, ttl in ((axs[0], "qber_estimate", "estimated QBER (%)", 100, "Error rate"),
                                      (axs[1], "detection_probability", "detections per pulse", 1, "Detection probability")):
        nx = [100 * n.config.misalignment_error for n, a in pairs if a]
        ax.plot(nx, [scale * getattr(n.metrics, attr) for n, a in pairs if a], "o", ms=8, color=BLUE, mec="white", label="ordinary noise")
        ax.plot(nx, [scale * getattr(a.metrics, attr) for n, a in pairs if a], "s", ms=6, color=ORANGE, mec="white", label="adversary, same expected QBER")
        _style(ax, ttl, "expected QBER (%)", lab)
    axs[1].set_ylim(0, 0.3)
    axs[0].legend(frameon=False, fontsize=9)
    fig.suptitle("Noise and interception look the same to these indicators", x=0.02, ha="left", fontsize=12)
    paths.append(_save(fig, out, "noise_vs_adversary"))

    # 9 high loss
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    lg = np.linspace(0, max(m.channel_loss_db for m in loss), 200)
    ax.semilogy(lg, [max(models.asymptotic_secret_bits(base.with_(extra_loss_db=x)), 1e-1) for x in lg], color=MODEL, lw=2, label="asymptotic reference")
    _outcome(ax, [m.channel_loss_db for m in loss], [max(m.final_key_bits, 12) for m in loss], [m.accepted for m in loss])
    _style(ax, "Inserted attenuation: key until about 15 dB per 10⁶-pulse block", "inserted loss (dB)", "final key bits")
    ax.set_ylim(10, None); ax.legend(frameon=False, fontsize=9)
    ax.annotate("rejected sessions are drawn at the axis floor", (0.02, 0.04), xycoords="axes fraction", fontsize=8, color=MUTED)
    paths.append(_save(fig, out, "high_loss"))

    # 10b net key against distance: what authentication costs
    if net_main := [m for m in main if m.final_key_bits > 0]:
        fig, ax = plt.subplots(figsize=(6.4, 3.8))
        ax.semilogy([m.distance_km for m in net_main], [m.final_key_bits for m in net_main], "o", ms=7, color=BLUE, mec="white", label="final key")
        pos = [m for m in net_main if m.net_key_bits > 0]
        ax.semilogy([m.distance_km for m in pos], [m.net_key_bits for m in pos], "s", ms=6, color=ORANGE, mec="white", label="net key, after replacing authentication key")
        ax.axhline(net_main[0].auth_bits_consumed, color=MUTED, ls="--", lw=1.2)
        ax.annotate(f"authentication cost {net_main[0].auth_bits_consumed} bits per session", (1, net_main[0].auth_bits_consumed), xytext=(0, 5), textcoords="offset points", fontsize=9, color=MUTED)
        _style(ax, "Net key: a session must out-earn its authentication", "fiber length (km)", "bits per session")
        ax.legend(frameon=False, fontsize=9)
        paths.append(_save(fig, out, "net_key_vs_distance"))

    # 10 session outcomes
    allm = dist + eve + loss + [n.metrics for n, _ in pairs] + [a.metrics for _, a in pairs if a]
    cnt = Counter("accepted" if m.accepted else m.reject_reason for m in allm)
    order = ["accepted"] + [k for k in REJECT_REASONS if cnt.get(k)]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.barh(range(len(order)), [cnt[k] for k in order], color=[GOOD] + [CRITICAL] * (len(order) - 1), height=0.6)
    ax.set_yticks(range(len(order)), ["accepted"] + [f"rejected: {k}" for k in order[1:]])
    for i, k in enumerate(order):
        ax.text(cnt[k] + 0.3, i, str(cnt[k]), va="center", fontsize=9)
    ax.invert_yaxis()
    _style(ax, f"Outcomes of all {len(allm)} scenario sessions", "sessions", "")
    paths.append(_save(fig, out, "session_outcomes"))
    return paths


def sources_plot(rows, out: Path) -> Path:
    """Scenario 8: the key, the key a naive analysis would have kept, and what the adversary knew, per source case."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labels = [lab.replace(", photon-number splitting", ",\nphoton-number splitting") for lab, _ in rows]
    ms = [r.metrics for _, r in rows]
    x = np.arange(len(ms))
    fig, ax = plt.subplots(figsize=(9.6, 4.4))
    ax.bar(x - 0.27, [m.final_key_bits for m in ms], 0.26, color=BLUE, label="final key (this analysis)")
    ax.bar(x, [m.naive_key_bits for m in ms], 0.26, color=AQUA, label="key a single-photon analysis would keep")
    ax.bar(x + 0.27, [m.eve_known_key_bits for m in ms], 0.26, color=ORANGE, label="key-block bits the adversary knew")
    for i, m in enumerate(ms):
        ax.text(i, max(m.final_key_bits, m.naive_key_bits, m.eve_known_key_bits) * 1.04 + 500,
                "accepted" if m.accepted else "rejected", ha="center", fontsize=8, color=GOOD if m.accepted else CRITICAL)
    ax.set_xticks(x, labels, fontsize=8)
    ax.set_ylim(0, 1.15 * max(max(m.final_key_bits, m.naive_key_bits, m.eve_known_key_bits) for m in ms))
    _style(ax, "Sources at 25 km: decoys expose photon-number splitting", "", "bits per 10\u2077-pulse session")
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    return _save(fig, out, "sources_and_pns")


def operations_plot(result: dict, out: Path) -> Path:
    """Scenario 9: the operations day as four stacked panels on one time axis (no dual axes), events shaded."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows, cfg = result["sessions"], result["config"]
    t = np.array([r["t_h"] for r in rows])
    status = np.array([r["status"] for r in rows])
    fig, axes = plt.subplots(4, 1, figsize=(10.4, 9.2), sharex=True, gridspec_kw={"height_ratios": [1.25, 1, 1, 0.8]})
    shade = {"degradation": AQUA, "attack": ORANGE, "fault": MUTED}
    for ax in axes:
        for e in result["plan"]:
            ax.axvspan(e["start_h"], e["end_h"], color=shade[e["kind"]], alpha=0.14, lw=0)
    for e in result["plan"]:
        axes[0].text((e["start_h"] + e["end_h"]) / 2, 1.01, e["name"].replace(" ", "\n", 1), ha="center", va="bottom", fontsize=7,
                     color=MODEL, transform=axes[0].get_xaxis_transform())
    ax = axes[0]
    q = np.array([np.nan if r["qber"] is None else 100 * r["qber"] for r in rows])
    ax.plot(t, q, color=BLUE, lw=1.2)
    marks = {"accepted": ("o", GOOD, "accepted"), "degraded": ("s", AQUA, "accepted, loss flagged"),
             "alert": ("^", ORANGE, "accepted with alert"), "rejected": ("X", CRITICAL, "rejected")}
    for s, (mk, col, lab) in marks.items():
        k = status == s
        if k.any():
            ax.plot(t[k], np.where(np.isnan(q[k]), 0.0, q[k]), mk, ms=6, mfc=col, mec="white", mew=0.8, label=lab, ls="none")
    ax.axhline(100 * cfg["qber_threshold"], color=CRITICAL, lw=1, ls="--")
    ax.axhline(100 * cfg["qber_alert"], color=ORANGE, lw=1, ls=":")
    ax.text(24, 100 * cfg["qber_threshold"], " abort", va="center", fontsize=7, color=CRITICAL)
    ax.text(24, 100 * cfg["qber_alert"], " alert", va="center", fontsize=7, color=ORANGE)
    ax.set_ylim(0, 27)
    _style(ax, "A simulated operations day on the 10 km link (sessions every "
               f"{result['interval_min']:g} min)", "", "error rate (%)")
    ax.title.set_y(1.16)
    ax.legend(frameon=False, fontsize=7, ncol=4, loc="upper left", bbox_to_anchor=(0, 0.83))
    ax = axes[1]
    ax.bar(t, [r["net_key_bits"] for r in rows], width=0.2, align="edge", color=BLUE)
    _style(ax, "Key per session after the authentication key is replaced", "", "bits")
    ax = axes[2]
    ax.step(t + result["interval_min"] / 60, [r["bank_keys"] for r in rows], where="pre", color=BLUE, lw=1.5)
    rk = [r["t_h"] for r in rows if r["refused"]]
    if rk:
        ax.plot(rk, [0] * len(rk), "X", ms=7, mfc=CRITICAL, mec="white", label="application refused (fail closed)", ls="none")
        ax.legend(frameon=False, fontsize=7, loc="upper right")
    _style(ax, f"Keys in the store at Site A (application draws {result['demand_keys_per_hour']:g} per hour)", "", "256-bit keys")
    ax = axes[3]
    ax.step(t + result["interval_min"] / 60, [r["pool_bits"] for r in rows], where="pre", color=BLUE, lw=1.5)
    ax.set_ylim(0, 1.15 * max(cfg["auth_pool_bits"], max(r["pool_bits"] for r in rows)))
    _style(ax, "Authentication key pool", "time of day (h)", "bits")
    axes[-1].set_xlim(0, 24); axes[-1].set_xticks(range(0, 25, 3))
    return _save(fig, out, "operations_day")
