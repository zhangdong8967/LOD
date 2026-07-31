#!/usr/bin/env bash
# LOD — one-click full analysis + manuscript artifacts
#
# Usage:
#   ./run.sh                 # full pipeline (default)
#   ./run.sh --quick         # skip download, heavy benchmark, paper build
#   ./run.sh --skip-pdf      # skip THEORY_MONOGRAPH.pdf
#   ./run.sh --only theory,paper
#
# Outputs:
#   data/audit/run_all_analyses_latest.json   master log
#   data/research/*.json                      study results
#   figures/methodology/                      canonical figures
#   paper_artifacts/                          manuscript bundle
#   manuscript/THEORY_MONOGRAPH.pdf           (optional)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# BasicTeX / MacTeX CLI (often missing from IDE shells)
if [[ -x /Library/TeX/texbin/pdflatex ]]; then
  export PATH="/Library/TeX/texbin:$PATH"
fi

QUICK=0
SKIP_TESTS=0
SKIP_PDF=0
ONLY=""
EXTRA=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quick) QUICK=1; shift ;;
    --skip-tests) SKIP_TESTS=1; shift ;;
    --skip-pdf) SKIP_PDF=1; shift ;;
    --only)
      ONLY="${2:-}"
      shift 2
      ;;
    -h|--help)
      sed -n '2,16p' "$0"
      exit 0
      ;;
    *)
      EXTRA+=("$1")
      shift
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
RUN_ARGS=()
[[ "$QUICK" -eq 1 ]] && RUN_ARGS+=(--quick)
[[ "$SKIP_TESTS" -eq 1 ]] && RUN_ARGS+=(--skip-tests)
[[ -n "$ONLY" ]] && RUN_ARGS+=(--only "$ONLY")
if [[ ${#RUN_ARGS[@]} -gt 0 || ${#EXTRA[@]} -gt 0 ]]; then
  python examples/run_all_analyses.py "${RUN_ARGS[@]}" "${EXTRA[@]}"
else
  python examples/run_all_analyses.py
fi

if [[ "$QUICK" -eq 0 ]] && { [[ -z "$ONLY" ]] || [[ "$ONLY" == *"paper"* ]]; }; then
  echo ">>> [4/4] Fig 1 TikZ vector + sync + theory PDF"
  if [[ -x scripts/fig1_tikz.sh ]]; then
    ./scripts/fig1_tikz.sh || echo "warn: fig1-tikz skipped (no LaTeX engine)"
  fi
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
echo "  Log:        data/audit/run_all_analyses_latest.json"
echo "  Figures:    figures/methodology/"
echo "  Manuscript: paper_artifacts/"
echo "  Layout:     docs/PROJECT_LAYOUT.md"
echo "======================================================================"
