# English literature and standards library

Open-access PDFs, software documentation snapshots, and a **search protocol** for the `lod_guide` manuscript (*Clinical Chemistry* methods / technical brief track).

## Layout

| Path | Contents |
|------|----------|
| [`SEARCH_PROTOCOL.md`](SEARCH_PROTOCOL.md) | Boolean queries, blocks, inclusion rules |
| [`search_log.csv`](search_log.csv) | PubMed hit counts per query (executed 2026-07-30) |
| [`screening.csv`](screening.csv) | Title/DOI screen sheet → sync with EndNote |
| [`endnote/`](endnote/) | **`.nbib` imports** + EndNote + Scholar instructions |
| [`BIBLIOGRAPHY.md`](BIBLIOGRAPHY.md) | Seed references + BibTeX stubs |
| `papers/` | Open-access PDFs |
| `software/` | Analyse-it, MSstatsLOBD vignette snapshots |

**Locked stack:** PubMed + Google Scholar → **EndNote** (no Embase/WoS).

## Empirical data (linked)

Public datasets: `python -m lod_guide.data.download_real` → `data/raw/` (manifest: `data/raw/evidence_manifest.json`).

## Reproducibility

```bash
# Literature: fetch OA PDFs + metadata (PubMed)
python literature/scripts/literature_fetch.py --priority core
python literature/scripts/literature_fetch.py --blocks B2,C --max-records 20

# Generate reading-note scaffolds
python literature/scripts/literature_summarize.py --priority core

# Block B: screen 200 hits → top 15
python literature/scripts/literature_screen_block_b.py --top 15 --fetch

# Empirical datasets
python -m lod_guide.data.download_real
make paper-artifacts
```

See [`PROGRESS.md`](PROGRESS.md) for download status and [`notes/deep/CORE_READING_NOTES.md`](notes/deep/CORE_READING_NOTES.md) for manuscript-ready close reading.

## Scope (locked)

- **English sources only** for the manuscript reference list.
- **Complement** CLSI EP17-class options; do **not** claim to supersede EP17 / FDA-recognized consensus standards / manufacturer IFU.
