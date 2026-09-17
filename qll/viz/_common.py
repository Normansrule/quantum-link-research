"""Shared plotting helpers: headless switch, CLI, and a consistent look."""
from __future__ import annotations

import argparse

import matplotlib


def cli(description: str) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--save", metavar="PATH", help="write an SVG/PNG instead of opening a window")
    args = p.parse_args()
    if args.save:
        matplotlib.use("Agg")
    return args


def finish(fig, args) -> None:
    import matplotlib.pyplot as plt

    fig.tight_layout()
    if args.save:
        fig.savefig(args.save, bbox_inches="tight")
        print(f"wrote {args.save}")
    else:
        plt.show()
