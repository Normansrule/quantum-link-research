"""Shared helpers for simulations: figure path and a tiny report printer."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "figures"


def report(title: str, rows: list[tuple[str, str]]) -> None:
    print(f"\n== {title} ==")
    for k, v in rows:
        print(f"  {k:<44} {v}")


def save(fig, name: str) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    FIG.mkdir(parents=True, exist_ok=True)
    out = FIG / f"sim_{name}.svg"
    fig.tight_layout(); fig.savefig(out, bbox_inches="tight")
    print(f"  figure → {out.relative_to(ROOT)}")
    return out
