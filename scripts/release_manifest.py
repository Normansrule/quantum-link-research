"""Write a source, data, and release manifest for one release (audit deliverable): the base revision it answers, the
files changed since then with their SHA-256 digests, the digests of the generated data the website and documents
quote, the environment, and the totals of the JUnit reports given. The commit that contains this manifest cannot
name its own hash, so the manifest lists file digests instead; `git rev-parse HEAD` names the commit.

    python scripts/release_manifest.py --base 721889d --out docs/audit/2026-10-11_manifest.json reports/*.xml
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from ci_status_from_junit import counts  # noqa: E402

DATA = ["docs/site_data.json", "docs/status.json", "docs/lab/scenes.json", "docs/lab/catalog.json", "docs/link/ops.json",
        "systems/see510/hardware/two_room.json", "systems/traceability_matrix.csv"]
PACKAGES = ["numpy", "scipy", "matplotlib", "qiskit", "qiskit-aer", "stim", "pymatching", "qutip", "pytest", "playwright", "kyber-py", "cryptography"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", cwd=ROOT, check=True).stdout


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reports", nargs="*"); ap.add_argument("--base", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    changed = sorted(set(git("diff", "--name-only", "--no-renames", a.base).split()) | set(git("ls-files", "--others", "--exclude-standard").split()))
    files = {f: sha256(ROOT / f) for f in changed if (ROOT / f).is_file() and (ROOT / f).resolve() != out.resolve()}
    deleted = [f for f in changed if not (ROOT / f).exists()]
    versions = {}
    for p in PACKAGES:
        try:
            versions[p] = metadata.version(p)
        except metadata.PackageNotFoundError:
            versions[p] = None
    reports = {Path(r).name: counts(Path(r)) for r in a.reports}
    version = next(line.split('"')[1] for line in (ROOT / "pyproject.toml").read_text(encoding="utf-8").splitlines() if line.startswith("version ="))
    manifest = {
        "release": version, "base_revision": git("rev-parse", a.base).strip(),
        "note": "file digests of everything changed since the base revision; the containing commit is named by git, not here",
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "packages": versions},
        "changed_files": files, "deleted_files": deleted,
        "data_digests": {d: sha256(ROOT / d) for d in DATA if (ROOT / d).exists()},
        "test_reports": reports,
        "test_totals": {k: sum(r[k] for r in reports.values()) for k in ("tests", "passed", "failed", "skipped")},
    }
    out.write_text(json.dumps(manifest, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {out}: {len(files)} changed files, {manifest['test_totals']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
