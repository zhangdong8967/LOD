# Evidence stratified by tier (A/B/C/S)

This report is the **claim firewall**: what each tier may support in the manuscript.

## Tier meanings

| Tier | Meaning | Allowed manuscript use |
|------|---------|------------------------|
| **A** | Public raw / replicate-level validation tables | Primary empirical illustrations |
| **B** | Summaries / very small-n deposits | Diversity / external corroboration only |
| **C** | Synthetic EP17 demos (match Mean/SD) | Method walk-through only — **not clinical truth** |
| **S** | Simulation stress DGPs | Mechanism, coverage, power — **not** multi-assay validation |

## Counts

- Tier A: **9** datasets
- Tier B: **3**
- Tier C: **1**
- Tier S: **8** simulations

## Tier A

- `zenodo_mus_wt_qpcr` (qpcr_cq_continuous) — present=True — Zenodo 12609243 — Mus WT qPCR LoD/LoQ (Cq vs copy number).
- `zenodo_mus_multiplex_qpcr` (qpcr_cq_continuous) — present=True — Zenodo 12609243 — multiplex tCRISPR/WT qPCR LoD/LoQ.
- `analyseit_ep17_estradiol` (immunoassay_continuous) — present=True — CLSI EP17-A2 Appendix A estradiol example (Analyse-it workbook): immunoassay continuous blank + low-level replicates.
- `analyseit_ep17_probit` (probit_hit_rate) — present=True — CLSI EP17-A2 Appendix C probit/hit-rate example (Analyse-it): concentration x detect outcomes.
- `mendeley_carobene_lombardy_eqa` (clinical_chemistry_multilab) — present=True — Carobene A. et al. Commutability of Lombardy Region EQA control materials for enzymes, calcium, and creatinine (Clin Chim Acta 2025; Mendeley 10.17632/r4szpw8sn5). Ten labs; ALT/AST/ALP/CK/LDH/creatinine/calcium raw replicates. CC-BY-4.0.
- `bioc_msstats_lobd_cptac` (proteomics_blank_lob) — present=True — CPTAC Assay Portal peptide spike-in (JHU_DChan_HZhang_ZZhang) via Bioconductor MSstatsLOBD::raw_data (Galitzine et al., Mol Cell Proteomics 2018; Artistic-2.0). 43 peptides × blank (Concentration=0) + concentration grid — proteomics blank–LoB.
- `zenodo_radioimmuno_precision` (radioimmuno_precision_profile) — present=True — Malkamäki et al., Anal. Chem. 10.1021/acs.analchem.4c03393; Zenodo 12664367 Precision.txt — per-sample replicate mean/SD/CV (CC-BY-4.0).
- `zenodo_radioimmuno_linearity` (radioimmuno_linearity_continuous) — present=True — Malkamäki et al., Anal. Chem.; Zenodo 12664367 Linearity_1.txt — concentration (ng) × DPM replicates (CC-BY-4.0).
- `zenodo_rmn_qualification` (rmn_microneutralization_continuous) — present=True — Sawant, Harit, Tomaras. RMN assay qualification dataset (Zenodo 10.5281/zenodo.17108929). Replicate ID50 by dilution; CC-BY-4.0.

## Tier B

- `zenodo_cation_ic_lod` (analytical_chemistry_ic) — present=True — Dierendonck C. Cation LOD/LOQ (Zenodo 5909650). CC-BY-4.0.
- `zenodo_anion_ic_lod` (analytical_chemistry_ic) — present=True — Dierendonck C. Anion LOD/LOQ (Zenodo 5901444). CC-BY-4.0.
- `zenodo_radioimmuno_lod_summary` (radioimmuno_summary) — present=True — Malkamäki et al. radioimmuno-dot-blot LOD summaries (Anal. Chem.; Zenodo 12664367). Tier B blank mean/SD summaries.

## Tier C

- `analyseit_ep17_troponin_precision` (cardiac_precision_profile) — present=True — CLSI EP17-A2 Appendix D troponin I precision-profile pools (Analyse-it; generated to match target Mean/SD) — LoQ-style.

## Tier S

- `sim_normal_blanks` (continuous) — present=True — lod_guide.data.simulate stress DGP
- `sim_skewed_hetero_blanks` (continuous) — present=True — lod_guide.data.simulate stress DGP
- `sim_censored_floor` (continuous) — present=True — lod_guide.data.simulate stress DGP
- `sim_binary_reagents_90_vs_80` (binary) — present=True — lod_guide.data.simulate stress DGP
- `sim_binary_low_p_lod` (binary) — present=True — lod_guide.data.simulate stress DGP
- `sim_poisson_count_hetero` (count) — present=True — lod_guide.data.simulate stress DGP
- `sim_multiclass_blood_type` (multiclass) — present=True — lod_guide.data.simulate stress DGP
- `sim_bimodal_weak_positive` (continuous) — present=True — lod_guide.data.simulate stress DGP

## Empirical tier-A extension (new continuous/precision deposits)

- `zenodo_radioimmuno_precision` tier=A
  - LoQ@CV20≈346.2666667 (all_pools_meet_target_use_lowest_mean)
- `zenodo_radioimmuno_linearity` tier=A
  - LoQ@CV20≈631.7333333333333 (all_pools_meet_target_use_lowest_mean)
- `zenodo_rmn_qualification` tier=A
  - LoQ@CV20≈5.495444143579495 (empirical_log_interpolation)
  - continuous gate: parametric_candidate=False, path=nonparametric_percentile
- `mendeley_carobene_lombardy_eqa` tier=A
  - LoQ@CV20≈0.62 (all_pools_meet_target_use_lowest_mean)
- `bioc_msstats_lobd_cptac` tier=A
  - continuous gate: parametric_candidate=False, path=parametric_lognormal

These results illustrate assumption-gated continuous/precision analysis on independent public deposits, including routine clinical chemistry multi-lab replicates (Carobene) and proteomics blank–LoB (CPTAC/MSstatsLOBD). They do not imply blank-LoB validation across all clinical chemistry panels. Tier C (troponin demo) and tier S (simulations) remain non-substitutes for tier A.

## Forbidden overclaims

- Do not cite tier C/S as proof the algorithm is clinically validated for all chemistry panels.
- Do not pool A+C+S into a single “N datasets support the algorithm” sentence without stratification.
