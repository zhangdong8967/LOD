# Literature pipeline — progress (2026-07-30)

## Stack (locked)

PubMed + Google Scholar → **EndNote** | Scripts in `literature/scripts/`

---

## Phase status

| Phase | Status | Artifacts |
|-------|--------|-----------|
| Search protocol | **Done** | `SEARCH_PROTOCOL.md`, `search_log.csv` (11 PubMed queries) |
| EndNote export | **Done** | `endnote/blocks/block_*.nbib` (A–I, A2, B2) |
| Automated fetch | **Done (core + B2/C)** | `scripts/literature_fetch.py` |
| Close-reading notes | **Done (core)** | `notes/deep/CORE_READING_NOTES.md` |
| Block B auto-screen (200 hits) | **Done** | `screening_block_B.csv`, top 15 in `BLOCK_B_READING_NOTES.md` |
| Introduction Related Work draft | **Done** | `manuscript/INTRO_RELATED_WORK.md` (+ paragraph in `METHODS_BRIEF.md`) |
| Block notes (auto scaffold) | **Partial** | `notes/deep/BLOCK_B2_NOTES.md`, `BLOCK_C_NOTES.md`, `BLOCK_D_NOTES.md` |
| EndNote library (local) | **Pending (you)** | Import `.nbib` → `LOD-manuscript-2026.enl` |
| Scholar citation chase | **Pending (you)** | `endnote/scholar_citation_chase.md` |
| Final Vancouver list | **Pending** | After EndNote screen → update `BIBLIOGRAPHY.md` |

---

## Download summary

| Tier | PMIDs processed | PDF OK | Abstract only |
|------|-----------------|--------|---------------|
| Core (4) | 33626838, 14764644, 29438992, 18852857 | 2 | 2 |
| Block B2+C (9) | see `notes/manifest.json` | 2 | 7 |
| Block D sample (15) | earlier run | 2 | 13 |
| **Total JSON records** | **26** | **~6 unique PDFs** | **~20** |

### Core papers — full-text status

| Paper | PMID | PDF |
|-------|------|-----|
| Armbruster & Pry 2008 LoB/LoD/LoQ | **18852857** | Yes — `papers/pdfs/18852857_*.pdf` |
| Galitzine 2018 MSstatsLOBD | **29438992** | Yes — PMC OA |
| Linnet & Kondratovich 2004 | **14764644** | **No** (Clin Chem paywall) — abstract in `notes/records/` |
| Vaks et al. 2016 JALM | **33626838** | **No** (JALM paywall) — abstract only |

Paywalled core papers: use **institutional PDF** → save to `literature/papers/pdfs/` → re-run fetch or set `full_text_path` in `screening.csv`.

---

## Commands

```bash
# Fetch metadata + OA PDFs (core)
python literature/scripts/literature_fetch.py --priority core

# Fetch B2/C block (Linnet follow-ups)
python literature/scripts/literature_fetch.py --blocks B2,C --max-records 20

# Regenerate reading scaffolds
python literature/scripts/literature_summarize.py --priority core
python literature/scripts/literature_summarize.py --blocks B2,C
```

---

## Known script fixes applied

1. **PubMed batch PMC elink bug** — per-PMID elink (was assigning wrong PMC PDF across batch).
2. **PDF validation** — title/author/DOI check rejects mislinked OA PDFs.
3. **Title parsing** — `itertext()` for PubMed XML (was spacing letters).
4. **Armbruster PMID** — corrected to **18852857** (was 19151158 in early screening).
5. **Europe PMC timeout** — retries + continue on failure.

---

## Next steps (recommended order)

1. Import `endnote/blocks/block_*.nbib` into EndNote; dedupe.
2. Attach institutional PDFs for Linnet 2004 + Vaks et al. 2016 if available.
3. Screen Block **B** hits (sample size) — mark 10–15 `include=yes` in `screening.csv`.
4. Scholar chase from 4 core DOIs (Fleiss, Chow, Agresti books).
5. Pull quotes/page numbers from PDFs into `CORE_READING_NOTES.md` before citing.
