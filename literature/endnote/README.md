# EndNote import (PubMed + Google Scholar)

**Locked workflow:** PubMed (E-utilities + manual) → **EndNote**; citation chaining via **Google Scholar** only.

---

## Files in this folder

| File | Contents | EndNote action |
|------|----------|----------------|
| `pubmed_blocks_A-E-H-I.nbib` | **300 records** — deduplicated union of Blocks A, B, C, D, E, H, I (first 200 hits each where >200) | File → Import → File → Import Option: **PubMed (NLM)** |
| `pubmed_seed_BFG_A2.nbib` | **134 records** — author seeds (Linnet/Kondratovich), Blocks F & G, Armbruster | Same import; EndNote will merge duplicates if DOI/PMID match |
| [`manuscript_references/manuscript_refs_pubmed.nbib`](manuscript_references/manuscript_refs_pubmed.nbib) | **10 records** — main-text journal PMIDs (verified 2026-08-02) | PubMed (NLM) |
| [`manuscript_references/manuscript_refs_manual.enw`](manuscript_references/manuscript_refs_manual.enw) | **27 records** — standards, books, CrossRef classics, Zenodo datasets | EndNote Import |
| [`manuscript_references/README.md`](manuscript_references/README.md) | Manuscript Vancouver list + import steps | — |
| `scholar_citation_chase.md` | Manual Scholar steps (not auto-exported) | Add selected hits via Scholar **Cite → EndNote** or DOI lookup |

After import, run **Library → Find Duplicates** (match on DOI, PMID, title).

---

## Step-by-step (EndNote 20/21)

1. Create a new library: `LOD-manuscript-2026.enl` (store outside repo or in `.gitignore` if large).
2. **Import PubMed batch:**
   - `File` → `Import` → `File…`
   - Select `pubmed_blocks_A-E-H-I.nbib`
   - Import Option: **PubMed (NLM)** or **PubMed (NLM)** / **Reference Manager (RIS)** if NLM unavailable — prefer **PubMed (NLM)**.
   - Repeat for `pubmed_seed_BFG_A2.nbib`.
3. **Add standards manually** (not in PubMed):
   - Reference Type: **Standard** or **Report**
   - CLSI EP17-A2 (2012), EP17IG (2021), EP05-A3, ICH E9(R1)
   - Attach PDF when purchased.
4. **Find Duplicates** → keep best record (prefer record with DOI + abstract).
5. Create **Groups** matching search blocks: `Block-A`, `Block-B`, … `Block-core`.
6. Tag `priority=core` using `literature/screening.csv` (filter PMID column).

---

## Screening workflow

1. Open `../screening.csv` in Excel / Numbers.
2. Sort by `blocks`, then `priority`.
3. Set `include` = `yes` | `no` | `pending`.
4. For `yes` + open access: download PDF → `../papers/` → note path in `full_text_path`.
5. Sync decisions back to EndNote with **Research Notes** field = block + priority.

---

## PubMed hit counts (2026-07-30)

See `../search_log.csv`. Summary:

| Block | PubMed hits | Exported |
|-------|-------------|----------|
| A | 4,296 | 200 |
| B | 2,641 | 200 |
| B2 (Linnet/Kondratovich) | 8 | 8 |
| C | 9 | 9 |
| D | 70 | 70 |
| E | 1,461 | 200 |
| F | 483 | 100 |
| G | 17 | 17 |
| H | 578 | 200 |
| I | 114 | 114 |
| A2 (Armbruster) | 9 | 9 |

**Unique PMIDs in main batch:** 946 (300 in primary `.nbib` cap). Narrow in EndNote using groups + screening before full-text pull.

---

## Cite While You Write

Manuscript draft: `manuscript/METHODS_BRIEF.md` → Word with EndNote plugin → Vancouver or *Clinical Chemistry* style (check journal Author Guidelines).
