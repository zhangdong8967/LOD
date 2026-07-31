#!/usr/bin/env bash
# Compile Fig 1 TikZ vector (Fig1_pipeline.tex → figures/methodology/Fig1_decision_map.*)
#
# Usage: ./scripts/fig1_tikz.sh   OR   make fig1-tikz
#
# Requires local pdflatex (BasicTeX), bundled/project tectonic (.tools/tectonic), or Docker.
#
# First-time BasicTeX (no sudo):
#   export PATH="/Library/TeX/texbin:$PATH"
#   tlmgr init-usertree
#   tlmgr --usermode install standalone pgf helvetic
#
# Run from repo root:  cd .../LOD && make fig1-tikz

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEX_DIR="$ROOT/manuscript/figures_tex"
JOB="Fig1_pipeline"
FIG_DIR="$ROOT/figures/methodology"
PAPER_FIG="$ROOT/paper_artifacts/figures"
BUNDLED_TECTONIC="$ROOT/.tools/tectonic"

run_pdflatex() {
  local -a cmd=("$@")
  (cd "$TEX_DIR" && "${cmd[@]}" -interaction=nonstopmode -halt-on-error "${JOB}.tex")
}

run_tectonic() {
  local tectonic_bin="$BUNDLED_TECTONIC"
  if [[ ! -x "$tectonic_bin" ]]; then
    tectonic_bin="$(command -v tectonic)"
  fi
  (cd "$TEX_DIR" && "$tectonic_bin" -X compile "${JOB}.tex")
}

# BasicTeX on macOS installs to /Library/TeX/texbin (often not on non-login PATH).
if ! command -v pdflatex >/dev/null 2>&1 && [[ -x /Library/TeX/texbin/pdflatex ]]; then
  export PATH="/Library/TeX/texbin:$PATH"
fi

if command -v pdflatex >/dev/null 2>&1; then
  echo "Fig 1 TikZ: local pdflatex ..."
  run_pdflatex pdflatex
elif [[ -x "$BUNDLED_TECTONIC" ]] || command -v tectonic >/dev/null 2>&1; then
  echo "Fig 1 TikZ: tectonic ..."
  run_tectonic
elif command -v docker >/dev/null 2>&1; then
  echo "Fig 1 TikZ: Docker texlive/texlive ..."
  docker run --rm \
    -v "$ROOT:/work" \
    -w /work/manuscript/figures_tex \
    texlive/texlive:latest \
    pdflatex -interaction=nonstopmode -halt-on-error "${JOB}.tex"
else
  echo "error: need pdflatex, tectonic (.tools/tectonic), or Docker." >&2
  exit 127
fi

PDF="$TEX_DIR/${JOB}.pdf"
PNG_TMP="$(mktemp "${TMPDIR:-/tmp}/fig1.XXXXXX.png")"
PNG="$FIG_DIR/Fig1_decision_map.png"
mkdir -p "$FIG_DIR" "$PAPER_FIG"

if command -v sips >/dev/null 2>&1; then
  sips -s format png "$PDF" --out "$PNG_TMP" >/dev/null
elif command -v pdftoppm >/dev/null 2>&1; then
  pdftoppm -png -singlefile "$PDF" "${PNG_TMP%.png}"
  PNG_TMP="${PNG_TMP%.png}.png"
else
  echo "error: need sips (macOS) or pdftoppm to rasterize PDF" >&2
  exit 1
fi

for stem in Fig1_Fig1-decision-map; do
  cp -f "$PDF" "$FIG_DIR/Fig1_decision_map.pdf"
  cp -f "$PNG_TMP" "$FIG_DIR/Fig1_decision_map.png"
  cp -f "$PDF" "$PAPER_FIG/${stem}.pdf"
  cp -f "$PNG_TMP" "$PAPER_FIG/${stem}.png"
done
rm -f "$PNG_TMP"

echo "Wrote $FIG_DIR/Fig1_decision_map.png and PDF copies under $FIG_DIR and $PAPER_FIG"
