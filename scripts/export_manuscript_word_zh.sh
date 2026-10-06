#!/usr/bin/env bash
# Export standalone Chinese manuscript Word (internal draft).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python - <<'PY'
from lod_guide.paper.word_export import export_chinese_manuscript_docx

paths = export_chinese_manuscript_docx()
print("Wrote:")
for k, p in sorted(paths.items()):
    print(f"  {k}: {p}")
PY
