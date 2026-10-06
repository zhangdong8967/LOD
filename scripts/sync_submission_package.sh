#!/usr/bin/env bash
# Copy ScholarOne-ready files into submission/ (single upload folder).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/submission"
SRC_FIG="$ROOT/figures/methodology"
SRC_MS="$ROOT/paper_artifacts/manuscript"

mkdir -p "$DEST"

copy_if() {
  local src="$1" name="$2"
  if [[ -f "$src" ]]; then
    cp -f "$src" "$DEST/$name"
    echo "  copied $name"
  else
    echo "  MISSING: $src" >&2
    return 1
  fi
}

echo ">>> Syncing submission/ from latest build..."
copy_if "$SRC_MS/Clinical_Chemistry_submission.docx" "Clinical_Chemistry_submission.docx"
copy_if "$SRC_MS/Tables_main.docx" "Tables_main.docx"
copy_if "$SRC_MS/Figure_legends.docx" "Figure_legends.docx"
copy_if "$SRC_MS/Cover_letter.docx" "Cover_letter.docx"
copy_if "$SRC_MS/Online_Supplement.pdf" "Online_Supplement.pdf"
copy_if "$SRC_MS/Clinical_Chemistry_author_bundle.docx" "Clinical_Chemistry_author_bundle.docx"
copy_if "$SRC_MS/LOD_manuscript_zh.docx" "LOD_manuscript_zh.docx"
copy_if "$SRC_FIG/Fig1_lod_replicate_planning.png" "Fig1_lod_replicate_planning.png"
copy_if "$SRC_FIG/Fig2_tierA_calibration.png" "Fig2_tierA_calibration.png"
if [[ -f "$SRC_FIG/Fig1_lod_replicate_planning.tif" ]]; then
  cp -f "$SRC_FIG/Fig1_lod_replicate_planning.tif" "$DEST/Fig1_lod_replicate_planning.tif"
  echo "  copied Fig1_lod_replicate_planning.tif"
fi
if [[ -f "$SRC_FIG/Fig2_tierA_calibration.tif" ]]; then
  cp -f "$SRC_FIG/Fig2_tierA_calibration.tif" "$DEST/Fig2_tierA_calibration.tif"
  echo "  copied Fig2_tierA_calibration.tif"
fi
echo ">>> Done: $DEST"
