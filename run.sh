#!/usr/bin/env bash
# LOD — one-click full analysis + manuscript artifacts
#
# Usage:
#   ./run.sh                 # full pipeline (default): theory + research + paper
#   ./run.sh --quick         # skip download, heavy benchmark, paper build
#   ./run.sh --skip-pdf      # skip THEORY_MONOGRAPH.pdf
#   ./run.sh --full-tests     # also run full pytest theory suite (~30s)
#   ./run.sh --skip-tests     # skip theory bundle check entirely
#   ./run.sh --only theory    # theory research only (P1–P18 + depth + Table 4)
#
# Outputs:
#   data/audit/theory_verification_latest.json  P1–P18 certificates
#   data/audit/run_all_analyses_latest.json     master log
#   data/research/*.json                        study results
#   figures/methodology/                        canonical figures
#   paper_artifacts/                            manuscript bundle (+ audit/, Table 4)
#   manuscript/THEORY_MONOGRAPH.pdf             (optional)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# BasicTeX / MacTeX CLI (often missing from IDE shells)
if [[ -x /Library/TeX/texbin/pdflatex ]]; then
  export PATH="/Library/TeX/texbin:$PATH"
fi

QUICK=0
SKIP_TESTS=0
FULL_TESTS=0
SKIP_PDF=0
ONLY=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quick) QUICK=1; shift ;;
    --skip-tests) SKIP_TESTS=1; shift ;;
    --full-tests) FULL_TESTS=1; shift ;;
    --skip-pdf) SKIP_PDF=1; shift ;;
    --only)
      ONLY="${2:-}"
      if [[ -z "$ONLY" ]]; then
        echo "run.sh: --only requires a value (e.g. theory,paper)" >&2
        exit 2
      fi
      shift 2
      ;;
    -h|--help)
      sed -n '2,19p' "$0"
      exit 0
      ;;
    *)
      echo "run.sh: unknown option: $1" >&2
      echo "Tip: run one command per line; do not paste shell comments (# ...) into the command." >&2
      echo "Try: ./run.sh --help" >&2
      exit 2
      ;;
  esac
done

echo "======================================================================"
echo "LOD run.sh — $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Root: $ROOT"
echo "======================================================================"

echo ">>> [1/4] Install package (editable + dev)"
python -m pip install -e ".[dev]" -q

echo ">>> [2/4] Remove stale figure aliases (if any)"
python scripts/clean_outputs.py --apply 2>/dev/null || true

echo ">>> [3/4] Analyses + paper artifacts"
# Single args array — macOS /bin/bash 3.2 + set -u rejects "${EMPTY[@]}" expansion.
ALL_ARGS=()
[[ "$QUICK" -eq 1 ]] && ALL_ARGS+=(--quick)
[[ "$SKIP_TESTS" -eq 1 ]] && ALL_ARGS+=(--skip-tests)
[[ "$FULL_TESTS" -eq 1 ]] && ALL_ARGS+=(--full-tests)
[[ -n "$ONLY" ]] && ALL_ARGS+=(--only "$ONLY")
if ((${#ALL_ARGS[@]} > 0)); then
  python examples/run_all_analyses.py "${ALL_ARGS[@]}"
else
  python examples/run_all_analyses.py
fi

if [[ "$QUICK" -eq 0 ]] && { [[ -z "$ONLY" ]] || [[ "$ONLY" == *"paper"* ]]; }; then
  echo ">>> [4/4] Sync paper figures + theory PDF (Fig 1 = merged matplotlib; TikZ skipped)"
  python - <<'PY'
from lod_guide.paper.build_artifacts import _copy_figures
from lod_guide.paper.registry import PAPER
_copy_figures(PAPER / "figures")
print("Synced registry figure copies to paper_artifacts/figures/")
PY
  if [[ "$SKIP_PDF" -eq 0 ]] && command -v pdflatex >/dev/null 2>&1; then
    ./scripts/build_theory_monograph.sh || echo "warn: theory-pdf skipped"
  fi
else
  echo ">>> [4/4] Skipped (quick mode or paper not in --only)"
fi

echo "======================================================================"
echo "Done."
echo "  Theory:     data/audit/theory_verification_latest.json"
echo "  Theory pkg: paper_artifacts/audit/ + Table04_propositions_P1_P18.csv"
echo "  Log:        data/audit/run_all_analyses_latest.json"
echo "  Figures:    figures/methodology/"
echo "  Manuscript: paper_artifacts/"
echo "  Layout:     docs/PROJECT_LAYOUT.md"
echo "======================================================================"
