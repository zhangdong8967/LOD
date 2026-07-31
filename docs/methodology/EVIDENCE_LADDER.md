# Evidence Ladder — Real Data, Simulations, and Exact Statistics

This document states **what evidence exists**, **what it can support**, and **what it cannot**, so statistical referees are not invited to over-claim.

## 1. Evidence tiers

| Tier | Meaning | Role in claims |
|------|---------|----------------|
| **A** | Public raw replicates (blank/low or concentration×detect) | Primary empirical illustrations |
| **B** | Public summaries / small-n analytical deposits | Diversity / external corroboration only |
| **C** | Synthetic EP17 demo workbooks (Match target Mean/SD) | Method walk-through, not empirical truth |
| **S** | Simulation stress DGPs with known truth + seed + sha256 | Mechanism, coverage, power — **not** substitutes for real multi-assay data |

Machine manifest after download: `data/raw/evidence_manifest.json`.  
Simulation DGP catalogue: `data/simulated/dgp_catalogue.json`.

## 2. Real public datasets currently wired

| ID | Family | Tier |
|----|--------|------|
| `zenodo_mus_wt_qpcr` | qPCR Cq / hit-rate | A |
| `zenodo_mus_multiplex_qpcr` | qPCR multiplex | A |
| `analyseit_ep17_estradiol` | Immunoassay continuous (EP17 estradiol) | A |
| `analyseit_ep17_probit` | Concentration × detect (EP17 probit) | A |
| `analyseit_ep17_troponin_precision` | Troponin precision-profile pools | C |
| `zenodo_cation_ic_lod` | Ion chromatography cations | B |
| `zenodo_anion_ic_lod` | Ion chromatography anions | B |
| `mendeley_carobene_lombardy_eqa` | Routine clinical chemistry multi-lab (ALT/AST/ALP/CK/LDH/crea/Ca) | **A** |
| `bioc_msstats_lobd_cptac` | Proteomics blank–LoB (CPTAC / MSstatsLOBD, Concentration=0) | **A** |
| `zenodo_radioimmuno_lod_summary` | Radioimmuno blank mean/SD | B |
| `zenodo_radioimmuno_precision` | Radioimmuno replicate mean/SD/CV table | **A** |
| `zenodo_radioimmuno_linearity` | Radioimmuno ng×DPM linearity replicates | **A** |
| `zenodo_rmn_qualification` | RMN ID50 replicates by dilution | **A** |

**Honest gap:** hematology near-LoD **blank** raw open deposits remain scarce. Routine chemistry **multi-lab precision** is covered by Carobene Lombardy EQA (tier A). **Proteomics blank–LoB** is covered by CPTAC/MSstatsLOBD (tier A; not an analyzer panel). True blank–LoB EP17 designs for electrolytes/ALT on clinical chemistry analyzers still scarce — we do not invent them.

After download, regenerate the stratified claim firewall:

```bash
python -m lod_guide.research.empirical_tierA_extension
python -m lod_guide.research.evidence_stratified_report
```

Artifacts: `data/research/EVIDENCE_STRATIFIED_REPORT.md`, `paper_artifacts/review/EVIDENCE_CLAIMS_BY_TIER.md`.

```bash
python -m lod_guide.data.download_real
```

## 3. Simulations (tier S)

Eight DGPs in `lod_guide.data.simulate`: normal blanks, skewed hetero lognormal, left-censoring, Bernoulli 90 vs 80 (full draws), low-p Bernoulli, Poisson day mixture, multiclass ABO, bimodal mixture.

Each JSON records `dgp`, `seed`, and `sha256_payload`.

## 4. Statistical algorithm policy (small-sample)

| Purpose | Method |
|---------|--------|
| Continuous design surface \(n^\star(p_A,p_B)\) | Asymptotic Fleiss–Chow / pooled-z |
| Primary small-\(n\) test for 2×2 hit tables | **Boschloo** unconditional exact (Fisher as conditional reference) |
| Primary small-\(n\) power / miss \(\beta\) | Exact binomial enumeration |
| Transparent audit | `research/exact_power_study.py` → `data/research/exact_vs_asymptotic_power.json` |

We **do not** claim asymptotic power is exact at folklore \(n=20\).

## 5. What a paper may claim vs must not

**May claim:** assumption-gated guidance; estimand-specific \(n\); exact vs asymptotic discrepancy tables; multi-family public case studies (qPCR + EP17 immunoassay/probit + radioimmuno precision/linearity + RMN + Carobene multilab chemistry + CPTAC proteomics blank–LoB + analytical add-ons), **always stratified by A/B/C/S**; stress DGPs with known truth.

**Must not claim:** that the package has been validated on all clinical assay classes with proprietary manufacturer raw data; that tier C/S evidence equals multi-center clinical chemistry verification archives; that pooling A+C+S into one “N datasets support the algorithm” sentence is valid.
