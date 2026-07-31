# English literature search protocol

**Manuscript:** *Assumption-Gated Decision Theory for Clinical Limit-of-Detection Evaluation*  
**Goal:** Systematically retrieve **English** standards, methods papers, algorithms, and open datasets relevant to EP17-class LoB/LoD/LoQ **design and verification** — not general analytical chemistry unless needed for Discussion boundaries.

**Output artifacts (to create in next step):**

- `literature/search_log.csv` — query ID, database, date, hits, exported count, notes  
- `literature/screening.csv` — title, DOI, tier (include/exclude), theme block, full-text status  
- Updated `BIBLIOGRAPHY.md` after deduplication  

---

## 1. Databases and reference manager (**locked**)

| Role | Tool | Use for | Export / import |
|------|------|---------|-----------------|
| **Primary** | **PubMed** (+ PMC full text) | All Boolean blocks A–I, author seeds | `.nbib` → EndNote (**PubMed NLM** import filter) |
| **Secondary** | **Google Scholar** | Citation chaining, books, software grey lit | Manual `.enw` / DOI → EndNote; see [`endnote/scholar_citation_chase.md`](endnote/scholar_citation_chase.md) |
| **Reference manager** | **EndNote** | Dedup, groups, Cite While You Write | Library `LOD-manuscript-2026.enl` (local) |
| **Standards metadata** | CLSI / FDA / ICH websites | EP17, EP17IG, EP05, E9(R1) | Manual **Standard** records in EndNote |
| **Open PDFs** | Europe PMC, publisher sites | Full text after screening | Attach to EndNote record |
| **Open data** | Zenodo / Bioconductor / Mendeley | Tier-A evidence (already in `data/raw/`) | Cite as **Dataset** in EndNote |

**Out of scope:** Embase, Web of Science, Chinese national standards, non-English publications.

**First PubMed run (2026-07-30):** see [`search_log.csv`](search_log.csv); EndNote imports in [`endnote/`](endnote/).

---

## 2. Search themes → manuscript sections

Each **Block** maps to Introduction/Methods/Discussion needs in `lod_guide`.

| Block | Theme | Manuscript hook |
|-------|-------|-----------------|
| **A** | EP17 / LoB / LoD / LoQ / detection capability | Standards framing, vocabulary |
| **B** | Sample size, power, two proportions, verification n=20 | G2, C1, Table 3, P8 |
| **C** | Parametric vs nonparametric LoB; skew; left censoring | S2–S4, P5, tier S |
| **D** | Probit / logistic hit-rate; dose–response LoD design | EP17 Example 4, c-optimal, minimax |
| **E** | Precision profile, LoQ, CV%, heterogeneity, ICC | G3, EP05, Carobene DE |
| **F** | Exact tests: Fisher, Boschloo, Barnard; Wilson/CP intervals | G1/G2 confirmation |
| **G** | Estimands, pre-specification, decision analysis | G1–G4, risk \(L\), ICH E9(R1) |
| **H** | Molecular / qPCR / digital PCR LoD | Tier-A Zenodo, CS10 |
| **I** | Proteomics / MS LoB–LoD (MSstatsLOBD) | Tier-A CPTAC |
| **J** | Software & SOP audits (Analyse-it, commercial LIMS) | Prior art, not competitors |

---

## 3. Controlled vocabulary (use in all blocks)

### 3.1 Core MeSH (PubMed)

```
"Limit of Detection"[MeSH]
"Reproducibility of Results"[MeSH]
"Clinical Laboratory Techniques"[MeSH]
"Statistics as Topic"[MeSH]
"Sample Size"[MeSH]
"Diagnostic Techniques and Procedures"[MeSH]
"Immunoassay"[MeSH] OR "Polymerase Chain Reaction"[MeSH]
```

### 3.2 Title/abstract keywords (English)

```
(limit of detection OR limit of blank OR limit of quantitation OR LoD OR LoB OR LoQ OR "detection capability")
AND (clinical OR laboratory OR assay OR immunoassay OR "in vitro diagnostic" OR IVD OR qPCR OR proteomics)
```

### 3.3 Standard-specific terms

```
(CLSI OR EP17 OR "EP17-A2" OR "evaluation of detection capability")
(FDA AND "consensus standard" AND EP17)
(ICH AND estimand)
(ISO 11843 OR "capability of detection")
```

### 3.4 Statistical method terms

```
(two proportion* OR binomial OR Fisher exact OR Boschloo OR Barnard OR Clopper Pearson OR Wilson score)
(sample size OR power OR "operating characteristic" OR "type II error" OR beta)
(probit OR logistic AND (hit rate OR detection probability OR dose response))
(precision profile OR "limit of quantitation" OR CV% OR heteroscedastic*)
(nonparametric AND (blank OR LoB OR percentile OR order statistic))
```

---

## 4. Boolean search strings (copy-paste)

Date window default: **1990–2026** (extend to 1980 for Fisher/Boschloo classics if needed).  
Language filter: **English** only.

### Block A — EP17 / detection capability (standards + applications)

**PubMed:**

```
(
  ("limit of detection"[Title/Abstract] OR "limit of blank"[Title/Abstract] OR "limit of quantitation"[Title/Abstract]
   OR "detection capability"[Title/Abstract] OR LoD[Title/Abstract] OR LoB[Title/Abstract] OR LoQ[Title/Abstract])
  AND
  ("clinical laboratory"[Title/Abstract] OR "clinical chemistry"[Title/Abstract] OR immunoassay[Title/Abstract]
   OR "in vitro diagnostic"[Title/Abstract] OR IVD[Title/Abstract] OR "measurement procedure"[Title/Abstract])
)
OR
(EP17[Title/Abstract] OR "CLSI EP17"[Title/Abstract] OR "evaluation of detection capability"[Title/Abstract])
```

**Embase (Emtree + text):**

```
('limit of detection'/exp OR 'detection limit'/exp OR 'limit of quantitation'/exp)
AND ('clinical chemistry'/exp OR 'in vitro diagnostic device'/exp OR 'laboratory test'/exp)
AND (EP17 OR CLSI OR 'detection capability').af.
```

**Web of Science:**

```
TS=((("limit of detection" OR "limit of blank" OR "limit of quantitation" OR "detection capability") AND ("clinical laboratory" OR "clinical chemistry" OR immunoassay OR IVD)))
OR TS=(EP17 OR "CLSI EP17")
```

---

### Block B — Sample size & verification (C1, G2, n=20 folklore)

**PubMed:**

```
(
  ("limit of detection"[Title/Abstract] OR LoD[Title/Abstract] OR "detection capability"[Title/Abstract])
  AND
  ("sample size"[Title/Abstract] OR "power"[Title/Abstract] OR "sample sizes"[Title/Abstract]
   OR "operating characteristic*"[Title/Abstract] OR "verification"[Title/Abstract] OR "replicate"[Title/Abstract])
)
AND (English[Language])
```

**High-precision subquery (molecular verification — seed paper):**

```
(Kondratovich[Author] OR Linnet[Author]) AND ("limit of detection"[Title/Abstract] OR verification[Title/Abstract])
```

**Web of Science (cited reference search):**

- Forward citations of: Linnet & Kondratovich 2004 (*Clin Chem* DOI 10.1373/clinchem.2003.029983)  
- Forward citations of: Kondratovich & Linnet 2017 JALM (DOI 10.1373/jalm.2016.020735)

---

### Block C — Nonparametric LoB / distributional diagnostics (S2, P5)

**PubMed:**

```
(
  ("limit of blank"[Title/Abstract] OR LoB[Title/Abstract] OR blank[Title/Abstract])
  AND
  (nonparametric[Title/Abstract] OR "order statistic*"[Title/Abstract] OR skew*[Title/Abstract]
   OR censored[Title/Abstract] OR tobit[Title/Abstract] OR "left censored"[Title/Abstract])
  AND
  (assay[Title/Abstract] OR laboratory[Title/Abstract] OR immunoassay[Title/Abstract])
)
```

---

### Block D — Probit / logistic LoD & concentration design

**PubMed:**

```
(
  (probit[Title/Abstract] OR logistic[Title/Abstract] OR "hit rate"[Title/Abstract] OR "detection probability"[Title/Abstract])
  AND
  ("limit of detection"[Title/Abstract] OR LoD[Title/Abstract] OR "detection capability"[Title/Abstract])
  AND
  (concentration[Title/Abstract] OR dose[Title/Abstract] OR "dose-response"[Title/Abstract])
)
```

**Web of Science + design terms:**

```
TS=((probit OR logistic) AND ("limit of detection" OR LoD) AND (design OR "optimal design" OR "Fisher information" OR D-optimal OR c-optimal))
```

---

### Block E — LoQ / precision profile / multilab heterogeneity

**PubMed:**

```
(
  ("limit of quantitation"[Title/Abstract] OR LoQ[Title/Abstract] OR "precision profile"[Title/Abstract])
  AND
  (CV[Title/Abstract] OR "coefficient of variation"[Title/Abstract] OR imprecision[Title/Abstract] OR EP05[Title/Abstract])
)
OR
("limit of detection"[Title/Abstract] AND (ICC[Title/Abstract] OR "intraclass correlation"[Title/Abstract] OR heterogeneity[Title/Abstract] OR "design effect"[Title/Abstract]))
```

---

### Block F — Exact binomial methods (G1/G2 confirmation)

**PubMed:**

```
(
  (Fisher[Title/Abstract] OR Boschloo[Title/Abstract] OR Barnard[Title/Abstract] OR "exact test"[Title/Abstract])
  AND
  (proportion[Title/Abstract] OR binomial[Title/Abstract] OR "2x2"[Title/Abstract] OR "two by two"[Title/Abstract])
  AND
  (detection[Title/Abstract] OR diagnostic[Title/Abstract] OR sensitivity[Title/Abstract] OR laboratory[Title/Abstract])
)
```

**Note:** Many hits are generic biostatistics; **screen** for laboratory / detection context or cite Agresti + Boschloo 1970 as methods anchors.

---

### Block G — Estimands & decision-theoretic framing

**PubMed:**

```
(estimand[Title/Abstract] OR "target of estimation"[Title/Abstract] OR ICH[Title/Abstract])
AND (diagnostic[Title/Abstract] OR laboratory[Title/Abstract] OR assay[Title/Abstract])
```

**Web of Science:**

```
TS=(estimand AND (assay OR "laboratory test" OR "in vitro diagnostic"))
```

**Include:** ICH E9(R1) addendum (S7) even if not assay-specific.

---

### Block H — Molecular / qPCR LoD

**PubMed:**

```
("limit of detection"[Title/Abstract] OR LoD[Title/Abstract])
AND (qPCR[Title/Abstract] OR "real-time PCR"[Title/Abstract] OR "digital PCR"[Title/Abstract] OR "molecular diagnos*"[Title/Abstract])
AND (verification[Title/Abstract] OR validation[Title/Abstract] OR replicate[Title/Abstract])
```

**Data portal (manual):** Zenodo search `LOD LoQ qPCR`, `limit of detection PCR`.

---

### Block I — Proteomics MS LoB/LoD

**PubMed:**

```
("limit of detection"[Title/Abstract] OR "limit of blank"[Title/Abstract])
AND (proteomics[Title/Abstract] OR "mass spectromet*"[Title/Abstract] OR peptid*[Title/Abstract])
```

**Seed:** Galitzine 2018 MCP (DOI 10.1074/mcp.RA117.000322); package MSstatsLOBD.

---

### Block J — Commercial / software prior art

**Google Scholar:**

```
"detection capability" EP17 (software OR Excel OR "Analyse-it" OR SAS OR R package)
```

**Purpose:** Position `lod_guide` vs calculators; **do not** treat marketing pages as peer-reviewed evidence.

---

## 5. Screening rules

### 5.1 Include (English)

- CLSI/FDA/ICH/ISO **English** guidance documents (metadata + purchased full text).
- Peer-reviewed **methods** papers on LoB/LoD/LoQ estimation, verification, or sample size in **clinical / IVD / molecular** contexts.
- Exact binomial / proportion methods **when applied** to detection or verification (or foundational refs: Fleiss, Agresti, Boschloo).
- Open **datasets** with replicate-level blank, low-level, hit-rate, or precision-profile data (tier A/B in `EVIDENCE_LADDER`).
- Software papers with **documented algorithms** (MSstatsLOBD, EP17 workbook examples).

### 5.2 Exclude

- Non-English publications (unless official English translation of a standard).
- Pure environmental / geochemical LoD without transferable statistics (unless Discussion boundary cite).
- Machine-learning “detection” unrelated to analytical LoD.
- Narrative reviews without methods contribution (may cite 1–2 for Intro only: e.g. Armbruster 2008).
- Manufacturer IFU / marketing PDFs as primary evidence (cite only as SOP folklore examples).

### 5.3 Priority tags (for `screening.csv`)

| Tag | Meaning |
|-----|---------|
| `core` | Directly citable in Methods/Results |
| `support` | Introduction/Discussion only |
| `standard` | Must purchase or cite as guideline |
| `data` | Candidate for `download_real` extension |
| `exclude` | Logged with reason |

---

## 6. Execution workflow (PubMed + Scholar → EndNote)

**Done (2026-07-30):**

1. PubMed Blocks A, B, C, D, E, H, I + seeds B2, F1, G1, A2 via E-utilities  
2. Exported → `endnote/pubmed_blocks_A-E-H-I.nbib` (300 records), `endnote/pubmed_seed_BFG_A2.nbib` (134 records), `endnote/pubmed_core_seed.nbib` (5 core PMIDs)  
3. Logged hits → `search_log.csv`; initial screen → `screening.csv` (301 rows)

**Your steps in EndNote:**

```text
1. Import the three .nbib files (Import Option: PubMed NLM)
2. Library → Find Duplicates (match DOI, PMID, title)
3. Create groups Block-A … Block-I + Block-core
4. Screen using screening.csv → set include yes/no/pending
5. Scholar citation chase (scholar_citation_chase.md) → import .enw / DOI lookup
6. Add Standard records: CLSI EP17-A2, EP17IG, EP05-A3, ICH E9(R1)
7. Attach open PDFs from PMC / literature/papers/
8. Export final 25–40 refs → update BIBLIOGRAPHY.md
```

See [`endnote/README.md`](endnote/README.md) for click-by-click EndNote instructions.

---

## 7. Seed hits already in repository (skip re-download)

| Block | Item | Location |
|-------|------|----------|
| A, P | Armbruster & Pry 2008 | `papers/armbruster2008_lob_lod_loq_clinlab.pdf` |
| B, T | OpenEpi two-proportion SS | `papers/openepi_two_proportion_sample_size.pdf` |
| A, D | Analyse-it EP17 docs | `software/analyseit_ep17_examples.html` |
| I | MSstatsLOBD vignette | `software/bioconductor_msstatslobd_vignette.html` |
| A | CLSI EP17 shop snapshot | `standards/clsi_ep17_shop.html` |
| H–I | Tier-A datasets | `data/raw/*`, `evidence_manifest.json` |

---

## 8. Expected yield (realistic)

| Block | Expected useful refs | Notes |
|-------|---------------------|-------|
| A | 15–40 | Many EP17 application notes |
| B | 5–15 | Sparse beyond Linnet/Kondratovich — **gap we fill** |
| C | 8–20 | Skew/censoring methods |
| D | 10–25 | Probit LoD + optimal design (stats journals) |
| E | 10–20 | LoQ / EP05 crossover |
| F | 5–10 | Mostly generic; cite classics |
| G | 3–8 | Estimand in IVD is thin — ICH E9(R1) + our framing |
| H | 15–30 | qPCR verification literature |
| I | 5–10 | Proteomics LoB/LoD |
| J | 5–15 | Software docs, not peer review |

**Total after screening:** ~25–40 references for the technical brief; ~60–80 if expanded to full research article.

---

## 9. Decision: databases to use for this project

**Minimum viable (free):**

1. PubMed / PMC  
2. Google Scholar (citation chaining)  
3. Europe PMC (PDF retrieval)  
4. Zenodo / Bioconductor / Mendeley (data + software)  
5. FDA + CLSI + ICH websites (standards metadata)

**Recommended if institutional access available:**

6. Embase  
7. Web of Science  

Proceed with **Blocks A → B → C → D** first (highest manuscript leverage), then E–I, then J.
