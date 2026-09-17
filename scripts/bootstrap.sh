#!/usr/bin/env bash
# Create or update the qll conda environment and run the Phase 1 gate.
set -euo pipefail
cd "$(dirname "$0")/.."
if conda env list | grep -qE '^qll\s'; then
  conda env update -n qll -f environment.yml --prune
else
  conda env create -f environment.yml
fi
eval "$(conda shell.bash hook)"
conda activate qll
python scripts/check_env.py
pytest -m phase1 -q
python -m qll.systems.traceability
