# Hospital / clinical-laboratory LoD replicate panels (tier A-hosp)

Per-replicate detect/Cq rows transcribed from **open-access supplementary datasets** (CC BY). Used for Supplement Table 7b protocol audit rows with evidence tier **A-hosp** (replicate-level hospital/clinical-lab data; distinct from tier **A-pub** aggregate $x/n$ tables in `data/published_lod_tables/`). The parent deposit `plos_bzdok2024_trec_lod` also has a tier **A** verbatim protocol quote in `PROTOCOL_LEDGER` (Table 7 row; publication Methods §LoD).

| File | Institution | Panel | Replicates | Detect rate |
|------|-------------|-------|------------|-------------|
| `plos_bzdok2024_trec_cxce_1to100.csv` | LMU Munich newborn screening | TREC CXCE 1:100 | 14 | 8/14 (57%) |
| `plos_bzdok2024_trec_magnapure_1to100.csv` | LMU Munich newborn screening | TREC MagNA Pure 1:100 | 9 | 8/9 (89%) |
| `plos_bzdok2024_trec_cxce_1to1000.csv` | LMU Munich newborn screening | TREC CXCE 1:1000 (sub-LoD) | 12 | 1/12 |

**Source xlsx:** `data/raw/plos_bzdok2024_trec_lod_s3.xlsx` (PLOS ONE S3; doi:10.1371/journal.pone.0306329.s003).

**Detection rule:** numeric Cp/Cq → `detected=1`; undetermined (`/`) → `detected=0`.

Rebuild CSVs: `python scripts/curate_hospital_lod_replicates.py`  
Rebuild audit: `python -m lod_guide.research.tierA_protocol_audit`
