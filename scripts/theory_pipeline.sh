#!/usr/bin/env bash
# Full theory research pipeline: P1–P18 verify → depth studies → Table 4 → audit bundle.
set -euo pipefail
cd "$(dirname "$0")/.."
python -m lod_guide.cli_theory all --force "$@"
