#!/usr/bin/env bash
# Export Clinical Chemistry manuscript + figure legends (+ cover letter) to Word.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python - <<'PY'
from lod_guide.paper.word_export import export_cover_letter_docx, export_manuscript_docx

paths = export_manuscript_docx(include_cover_letter=False)
cover = export_cover_letter_docx()
print("Wrote:")
for k, p in sorted(paths.items()):
    print(f"  {k}: {p}")
print(f"  cover_letter: {cover}")
PY
