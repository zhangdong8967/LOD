#!/usr/bin/env bash
# Build online supplement PDF/DOCX from manuscript/SUPPLEMENT.md (+ embedded CSV tables).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# macOS BasicTeX/MacTeX and Homebrew pandoc are often outside minimal IDE PATHs.
export PATH="/Library/TeX/texbin:/usr/local/texlive/2024/bin/universal-darwin:/usr/local/texlive/2023/bin/universal-darwin:/opt/homebrew/bin:/usr/local/bin:${PATH}"

OUT_DIR="$ROOT/paper_artifacts/manuscript"
TABLE_DIR="$ROOT/paper_artifacts/tables/manuscript"
BUILD="$OUT_DIR/supplement_build.md"

mkdir -p "$OUT_DIR"

python3 - <<'PY'
import csv
from pathlib import Path
from typing import Optional

root = Path(".")
out = Path("paper_artifacts/manuscript/supplement_build.md")
table_dir = Path("paper_artifacts/tables/manuscript")


def csv_to_md_table(path: Path, max_rows: Optional[int] = None) -> str:
    if not path.exists():
        return f"*[{path.name} not found]*\n"
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        return ""
    header, *body = rows
    if max_rows is not None:
        body = body[:max_rows]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    if max_rows is not None and len(rows) - 1 > max_rows:
        lines.append(f"\n*… {len(rows) - 1 - max_rows} additional rows in `{path.name}`.*\n")
    return "\n".join(lines) + "\n"


base = (root / "manuscript/SUPPLEMENT.md").read_text(encoding="utf-8")
parts = [base, "\n\n---\n\n# Embedded supplement tables\n\n"]

embed_specs = [
    ("Table 2 (LoQ precision)", "Table02_loq_precision_main.csv", 15),
    ("Table 2a (S2 diagnostic thresholds)", "Table02a_s2_diagnostic_thresholds.csv", None),
    ("Table 4 (Propositions)", "Table04_propositions_P1_P18.csv", None),
    ("Table 5 (Evidence ladder)", "Table05_evidence_ladder.csv", None),
    ("Table 6 (Type I calibration)", "Table06_type1_calibration.csv", None),
    ("Table 7b-S (Protocol audit summary)", "Table07b_protocol_audit_summary.csv", None),
    ("Table 7b (Protocol audit quotes)", "Table07b_protocol_audit.csv", 16),
    ("Table 8 (E1 coverage)", "Table08_e1_one_proportion_coverage.csv", None),
    ("Table 9c (E3 vs E2 confusion @ n=20)", "../Table09c_e3_vs_e2_confusion_n20.csv", None),
]

for title, fname, cap in embed_specs:
    path = table_dir / fname if not fname.startswith("..") else table_dir.parent / fname.replace("../", "")
    parts.append(f"## {title}\n\n")
    parts.append(csv_to_md_table(path, cap))

out.write_text("".join(parts), encoding="utf-8")
print(f"Wrote {out}")
PY

pandoc "$BUILD" -o "$OUT_DIR/Online_Supplement.docx"

pdf_ok=false
pdf_err=""
for engine in xelatex pdflatex lualatex; do
  if ! command -v "$engine" >/dev/null 2>&1; then
    continue
  fi
  if pandoc "$BUILD" \
    -o "$OUT_DIR/Online_Supplement.pdf" \
    --pdf-engine="$engine" \
    -V geometry:margin=1in \
    -V fontsize=11pt \
    2>"$OUT_DIR/.supplement_pdf_${engine}.log"; then
    pdf_ok=true
    echo "PDF engine: $engine"
    rm -f "$OUT_DIR"/.supplement_pdf_*.log
    break
  fi
  pdf_err="$(tail -n 5 "$OUT_DIR/.supplement_pdf_${engine}.log" 2>/dev/null || true)"
done

if [ "$pdf_ok" = false ]; then
  echo "ERROR: could not build Online_Supplement.pdf (DOCX was written)." >&2
  echo "Install a LaTeX distribution, e.g.:" >&2
  echo "  brew install --cask basictex" >&2
  echo "  sudo tlmgr update --self && sudo tlmgr install collection-latexrecommended" >&2
  if [ -n "$pdf_err" ]; then
    echo "Last engine log:" >&2
    echo "$pdf_err" >&2
  fi
  exit 1
fi

echo "Wrote:"
echo "  $OUT_DIR/Online_Supplement.pdf"
echo "  $OUT_DIR/Online_Supplement.docx"
echo "  $BUILD"
