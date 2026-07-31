#!/usr/bin/env bash
# Build manuscript/THEORY_MONOGRAPH.pdf from THEORY_MONOGRAPH.tex
#
# Usage (from repo root):
#   ./scripts/build_theory_monograph.sh
#   make theory-pdf
#
# Requires either:
#   - local pdflatex (brew install --cask basictex && eval "$(/usr/libexec/path_helper)")
#   - Docker (uses texlive/texlive image)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANUSCRIPT="$ROOT/manuscript"
TEX="$MANUSCRIPT/THEORY_MONOGRAPH.tex"
OUT="$MANUSCRIPT/THEORY_MONOGRAPH.pdf"
FIG="$ROOT/paper_artifacts/figures/Fig1_Fig1-decision-map.pdf"

if [[ ! -f "$TEX" ]]; then
  echo "error: missing $TEX" >&2
  exit 1
fi

if [[ ! -f "$FIG" ]]; then
  echo "Main-text figure PDFs missing. Run first:" >&2
  echo "  make fig1-tikz && make paper-artifacts" >&2
  exit 1
fi

# BasicTeX on macOS installs to /Library/TeX/texbin (often not on non-login PATH).
if ! command -v pdflatex >/dev/null 2>&1 && [[ -x /Library/TeX/texbin/pdflatex ]]; then
  export PATH="/Library/TeX/texbin:$PATH"
fi

run_pdflatex() {
  local cmd=("$@")
  (
    cd "$MANUSCRIPT"
    for _ in 1 2; do
      "${cmd[@]}" -interaction=nonstopmode -halt-on-error THEORY_MONOGRAPH.tex
    done
  )
}

if command -v pdflatex >/dev/null 2>&1; then
  echo "Building with local pdflatex ..."
  run_pdflatex pdflatex
elif command -v docker >/dev/null 2>&1; then
  echo "pdflatex not found — building with Docker (texlive/texlive) ..."
  docker run --rm \
    -v "$ROOT:/work" \
    -w /work/manuscript \
    texlive/texlive:latest \
    bash -lc 'for i in 1 2; do pdflatex -interaction=nonstopmode -halt-on-error THEORY_MONOGRAPH.tex; done'
else
  cat >&2 <<'EOF'
error: no LaTeX engine available.

Option A — Homebrew BasicTeX (~100 MB, recommended on macOS):
  brew install --cask basictex
  eval "$(/usr/libexec/path_helper)"
  sudo tlmgr update --self
  sudo tlmgr install collection-latexrecommended amsmath booktabs hyperref microtype geometry

Option B — install Docker Desktop, then re-run:
  ./scripts/build_theory_monograph.sh

After install, from repo root:
  make theory-pdf
EOF
  exit 127
fi

if [[ -f "$OUT" ]]; then
  echo "Wrote $OUT"
else
  echo "error: build finished but $OUT not found" >&2
  exit 1
fi
