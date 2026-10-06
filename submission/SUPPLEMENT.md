# Online Supplement

**Title:** Claim-specific sample-size planning for binary hit-rate verification of detection capability

**Companion:** Main manuscript (clinical planning in the main text; mapping rules, lattice margins, audit ledger, and operating-characteristic tables here).

**Main manuscript figures/tables:** Fig. 1 (A–D), Fig. 2 (A–C); Tables 1–3.

**Scope.** Binary hit-rate claims only (each replicate scored detected or not). Blank-SD LoB/LoD, probit/logit concentration estimation, and EP26 quantitative lot tests are out of scope.

**Numbering.** Main-text tables are Tables 1–3. Supplement tables keep the labels cited in the main text (3e, 3f, 7b, 8, 9b, 9c) and are independent of that sequence. Supplement Table 7b is not main-text Table 3.

**Rebuild.** `python3 scripts/build_online_supplement.py`

---

## S1. Claim-mapping rules (audit)

Four phrase rules were applied to 16 publicly accessible rows (Supplementary Table 7b).

1. A stated k-of-n or 19-of-20 pass rule → qualitative pass criteria.
2. A two-lot, two-material, or two-target contrast at the LoD, or a multi-lot detect grid → two-arm comparison. “Equivalent” without a numeric margin was treated as discrimination, not TOST.
3. A single-method 95% detection claim, LoD confirmation sentence, or low-level series without a pass rule or two-arm contrast → benchmark confirmation.
4. Hospital and published x/n tables without a two-arm sentence → benchmark confirmation.

Defaults when rates were unwritten: p0 = 0.95 for benchmark confirmation; (pA, pB) = (0.90, 0.80) for two-arm records (the Introduction planning pair, not a measured hit rate in those files). Replicate counts were not imputed. None of the 16 source texts stated an 80% power target.

## S2. Lattice operating characteristics

The two-arm lattice is 1,225 equally spaced pairs with pA > pB on the integer 50–99% grid, scored with exact two-sided Fisher tests at n = 20 per arm (α = 0.05).

- Cells: 1225
- Fraction with exact Fisher β > 0.80: 0.611
- Cells in which asymptotic pooled-z power exceeded exact Fisher by more than 0.05: 778 (this is the 778-cell count cited in the main text).

Fig. 1C displays n* on a 20–435 scale; that range is a plot scale (95%/90% ≈ 435) and does not cap 1-percentage-point cells.

### Supplementary Table 3f. Exact Fisher underpowering and asymptotic n* by Δp band

| delta_pp_band | n_cells | frac_beta_gt_0.8 | median_power_n20 | median_n_star_asymptotic | min_n_star | max_n_star |
| --- | --- | --- | --- | --- | --- | --- |
| 1–5 | 235 | 1.0 | 0.0252 | 2887.2 | 210.9 | 39239.3 |
| 6–10 | 210 | 1.0 | 0.0444 | 424.8 | 87.3 | 1085.0 |
| 11–20 | 345 | 0.8609 | 0.1236 | 116.0 | 37.2 | 319.2 |
| >20 | 435 | 0.0138 | 0.488 | 31.6 | 11.2 | 83.9 |


### Supplementary Table 3e. Asymptotic versus exact Fisher power at n = 20 (first 25 cells)

| p_a | p_b | delta_pp | power_exact_fisher_n20 | power_asymptotic_n20 | gap_asymp_minus_exact | n_star_asymptotic | beta_gt_0.8 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.51 | 0.5 | 1 | 0.020702 | 0.050447 | 0.029745 | 39239.2953 | 1 |
| 0.52 | 0.5 | 2 | 0.021471 | 0.051789 | 0.030318 | 9805.9962 | 1 |
| 0.52 | 0.51 | 1 | 0.020794 | 0.050447 | 0.029654 | 39207.8998 | 1 |
| 0.53 | 0.5 | 3 | 0.022765 | 0.054033 | 0.031268 | 4355.3852 | 1 |
| 0.53 | 0.51 | 2 | 0.021612 | 0.051792 | 0.03018 | 9794.2229 | 1 |
| 0.53 | 0.52 | 1 | 0.020973 | 0.050448 | 0.029475 | 39145.1087 | 1 |
| 0.54 | 0.5 | 4 | 0.0246 | 0.057187 | 0.032587 | 2447.6712 | 1 |
| 0.54 | 0.51 | 3 | 0.022959 | 0.05404 | 0.031081 | 4348.4084 | 1 |
| 0.54 | 0.52 | 2 | 0.02184 | 0.051795 | 0.029955 | 9774.6007 | 1 |
| 0.54 | 0.53 | 1 | 0.021235 | 0.050449 | 0.029214 | 39050.9222 | 1 |
| 0.55 | 0.5 | 5 | 0.027002 | 0.061264 | 0.034261 | 1564.6721 | 1 |
| 0.55 | 0.51 | 4 | 0.024855 | 0.057202 | 0.032346 | 2442.7657 | 1 |
| 0.55 | 0.52 | 3 | 0.023241 | 0.054049 | 0.030808 | 4337.9432 | 1 |
| 0.55 | 0.53 | 2 | 0.022148 | 0.0518 | 0.029652 | 9747.1296 | 1 |
| 0.55 | 0.54 | 1 | 0.021569 | 0.050451 | 0.028881 | 38925.3401 | 1 |
| 0.56 | 0.5 | 6 | 0.030001 | 0.066278 | 0.036277 | 1085.0181 | 1 |
| 0.56 | 0.51 | 5 | 0.027327 | 0.061291 | 0.033964 | 1560.9046 | 1 |
| 0.56 | 0.52 | 4 | 0.025199 | 0.057222 | 0.032022 | 2435.8979 | 1 |
| 0.56 | 0.53 | 3 | 0.023603 | 0.054062 | 0.03046 | 4323.9897 | 1 |
| 0.56 | 0.54 | 2 | 0.022525 | 0.051807 | 0.029281 | 9711.8097 | 1 |
| 0.56 | 0.55 | 1 | 0.021964 | 0.050452 | 0.028488 | 38768.3625 | 1 |
| 0.57 | 0.5 | 7 | 0.033634 | 0.07225 | 0.038616 | 795.8017 | 1 |
| 0.57 | 0.51 | 6 | 0.030406 | 0.066325 | 0.035918 | 1081.9657 | 1 |
| 0.57 | 0.52 | 5 | 0.027743 | 0.061328 | 0.033585 | 1555.8813 | 1 |
| 0.57 | 0.53 | 4 | 0.025622 | 0.057248 | 0.031626 | 2427.0679 | 1 |

*1200 additional rows in `Table03e_asymptotic_vs_exact_n20.csv`.*



## S3. Benchmark confirmation (Supplementary Table 8)

The study confirmation rule is that the lower Clopper–Pearson 95% limit for p is at least 0.95. After 20/20 positives that limit remains below 0.95. Table 8 gives the exact probability of meeting the rule when the true detection probability is 0.90, 0.95, or 0.99.

| n | p_true | P_CP_lower_ge_0.95 | CP_lower_after_n_of_n |
| --- | --- | --- | --- |
| 20 | 0.9 | 0.0 | 0.8316 |
| 20 | 0.95 | 0.0 | 0.8316 |
| 20 | 0.99 | 0.0 | 0.8316 |
| 53 | 0.9 | 0.0 | 0.9328 |
| 53 | 0.95 | 0.0 | 0.9328 |
| 53 | 0.99 | 0.0 | 0.9328 |
| 60 | 0.9 | 0.0 | 0.9404 |
| 60 | 0.95 | 0.0 | 0.9404 |
| 60 | 0.99 | 0.0 | 0.9404 |


## S4. Qualitative pass rules (Supplementary Tables 9b and 9c)

Table 9b: smallest n such that P(X ≥ k | p) ≥ 0.95 for k ∈ {19, 18, 17}. Table 9c: pairs in which both arms can pass 19/20 while exact Fisher power remains low.

| k | p_pct | target_P_pass | min_n | pass_rule_at_min_n | P_pass_at_min_n |
| --- | --- | --- | --- | --- | --- |
| 19 | 90 | 0.95 | 24 | 19/24 | 0.972342 |
| 18 | 90 | 0.95 | 23 | 18/23 | 0.977392 |
| 17 | 90 | 0.95 | 22 | 17/22 | 0.981784 |
| 19 | 95 | 0.95 | 22 | 19/22 | 0.977818 |
| 18 | 95 | 0.95 | 21 | 18/21 | 0.981119 |
| 17 | 95 | 0.95 | 20 | 17/20 | 0.984098 |
| 19 | 99 | 0.95 | 20 | 19/20 | 0.983141 |
| 18 | 99 | 0.95 | 19 | 18/19 | 0.984726 |
| 17 | 99 | 0.95 | 18 | 17/18 | 0.986244 |


| pair | n_per_arm | pass_rule | P_pass_arm_a | P_pass_arm_b | P_both_arms_pass | exact_fisher_power | miss_beta_fisher |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 90/80 | 20 | 19/20 | 0.391747 | 0.069175 | 0.027099 | 0.072484 | 0.927516 |
| 95/85 | 20 | 19/20 | 0.73584 | 0.175558 | 0.129182 | 0.069645 | 0.930355 |
| 90/70 | 20 | 19/20 | 0.391747 | 0.007637 | 0.002992 | 0.241679 | 0.758321 |
| 95/90 | 20 | 19/20 | 0.73584 | 0.391747 | 0.288263 | 0.016712 | 0.983288 |


At p = 0.95, P(X ≥ 19 | n = 20) = 0.7358.

## S5. Protocol audit ledger (Supplementary Table 7b)

Convenience sample, not a prevalence survey. Mapped claims in the ledger still use internal labels E1/E2/E3 (benchmark confirmation / two-arm / qualitative pass). Main text uses the descriptive names.

### Compact summary

| no | audit_id | evidence_tier | mapped_claim | archived_n | guidance_n_star | n_ratio_vs_20 | oc_metric | oc_value_at_archived_n |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | analyseit_ep17_estradiol | A | qualitative pass | 20 | 21 | 1.05 | E3_pass_probability | 0.7358 |
| 2 | analyseit_ep17_probit | A | two-arm | 20 | 199 | 9.95 | Fisher_power | 0.0725 |
| 3 | zenodo_mus_multiplex_qpcr | A | two-arm | 20 | 199 | 9.95 | Fisher_power | 0.0725 |
| 4 | zenodo_mus_wt_qpcr | A | two-arm | 20 | 199 | 9.95 | Fisher_power | 0.0725 |
| 5 | mendeley_carobene_lombardy_eqa | A | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 |
| 6 | bioc_msstats_lobd_cptac | A | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 |
| 7 | zenodo_radioimmuno_precision | A | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 |
| 8 | zenodo_radioimmuno_linearity | A | benchmark confirmation | 20 |  |  | E1_CP_confirm_probability | 0.0 |
| 9 | zenodo_rmn_qualification | A | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 |
| 10 | plos_bzdok2024_trec_lod | A | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 |
| 11 | plos_bzdok2024_trec_cxce_1to100 | A-hosp | benchmark confirmation | 14 | 53 | 3.79 | E1_CP_confirm_probability | 0.0 |
| 12 | plos_bzdok2024_trec_cxce_1to1000 | A-hosp | benchmark confirmation | 12 | 53 | 4.42 | E1_CP_confirm_probability | 0.0 |
| 13 | plos_bzdok2024_trec_magnapure_1to100 | A-hosp | benchmark confirmation | 9 | 53 | 5.89 | E1_CP_confirm_probability | 0.0 |
| 14 | jcm_hansen2020_abbott | A-pub | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 |
| 15 | plos_lim2021_mcatarrhalis | A-pub | benchmark confirmation | 50 | 53 | 1.06 | E1_CP_confirm_probability | 0.0 |
| 16 | scirep_jiang2025_mp | A-pub | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 |


### Verbatim quotes (truncated display; full CSV in the table folder)

| audit_id | evidence_tier | mapped_claim | archived_n | guidance_n_star | n_ratio_vs_20 | oc_metric | oc_value_at_archived_n | target_rates | quote_source | protocol_quote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analyseit_ep17_estradiol | A | qualitative pass | 20 | 21 | 1.05 | E3_pass_probability | 0.7358 | p=0.95; k/n=19/20 | CLSI EP17-A2 (2012) Sec 7.3; mapped to Analyse-it Appendix A estradiol workbook context | CLSI EP17-A2 Section 7.3: a minimum of 20 replicates at the LoD concentration; for a 95% detection claim, at least 19 of 20 replicates should be detected. |
| analyseit_ep17_probit | A | two-arm | 20 | 199 | 9.95 | Fisher_power | 0.0725 | p_A=0.90, p_B=0.80 (reference lot contrast near LoD) | Analyse-it EP17-A2-Example-4.xlsx, Data sheet header | CLSI EP17-A2 - Appendix C: concentration × replicate detect outcomes for Lot 1, Lot 2, and Lot 3 (hit-rate probit example workbook). |
| zenodo_mus_multiplex_qpcr | A | two-arm | 20 | 199 | 9.95 | Fisher_power | 0.0725 | p_A=0.90, p_B=0.80 (manuscript reference pair at folklore n) | Piaggio A. Zenodo 12609243; multiplex LOD-LOQ CSV | Dataset: Mus WT and tCRISPR multiplex LOD-LOQ (Cq vs standard quantity); steep hit-rate curve near LoD used for lot/target contrast planning. |
| zenodo_mus_wt_qpcr | A | two-arm | 20 | 199 | 9.95 | Fisher_power | 0.0725 | assigned 90%/80% illustrative pair (not lattice-wide median n*) | Piaggio A. Zenodo 12609243; WT LOD-LOQ CSV | Dataset: Mus WT assay LOD-LOQ (Cq vs copy number); hit-rate series by standard quantity near LoD. |
| mendeley_carobene_lombardy_eqa | A | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 | p0=0.95 benchmark confirmation | Carobene A. et al. Clin Chim Acta 2026; Mendeley 10.17632/r4szpw8sn5 | Ten laboratories measured ALT, AST, ALP, CK, LDH, creatinine, and calcium in EQA materials with raw replicate-level results (commutability study). |
| bioc_msstats_lobd_cptac | A | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 | p0=0.95 benchmark confirmation | Galitzine et al. MCP 2018; Bioconductor MSstatsLOBD::raw_data | CPTAC peptide spike-in calibration: blank (Concentration=0) and concentration grid for MSstatsLOBD limit-of-blank estimation. |
| zenodo_radioimmuno_precision | A | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 | p0=0.95 benchmark confirmation | Malkamäki et al. Anal Chem 2025; Zenodo 12664367 Precision.txt | Precision.txt: per-sample replicate mean/SD/CV across radioimmuno-dot-blot pools (LoQ-style precision profile). |
| zenodo_radioimmuno_linearity | A | benchmark confirmation | 20 |  |  | E1_CP_confirm_probability | 0.0 | p0=0.95 (continuous proxy; no hit-rate plan in file) | Malkamäki et al.; Zenodo 12664367 Linearity_1.txt | Linearity_1.txt: concentration (ng) × DPM replicate measurements across the linear range. |
| zenodo_rmn_qualification | A | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 | p0=0.95 benchmark confirmation | Sawant et al. Zenodo 10.5281/zenodo.17108929 | RMN assay qualification dataset: replicate ID50 by dilution for microneutralization LoD-adjacent series. |
| plos_bzdok2024_trec_lod | A | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 | p0=0.95 benchmark confirmation | Bzdok J et al. PLOS ONE 2024; Methods §TREC limit of detection (doi:10.1371/journal.pone.0306329) | To determine the limit of detection, we analysed a serial dilution of plasmid DNA containing the TREC locus; we were able to reliably detect 5 TREC copies per PCR reaction. |
| plos_bzdok2024_trec_cxce_1to100 | A-hosp | benchmark confirmation | 14 | 53 | 3.79 | E1_CP_confirm_probability | 0.0 | p0=0.95; empirical 8/14 (57%) from replicate CSV | Bzdok J et al. PLOS ONE 2024; S3 Dataset (10.1371/journal.pone.0306329.s003); CC BY 4.0 | Limit of detection raw data for TREC compared for CXCE-buffer extractions (S3 Dataset sheet 3; per-replicate Cp). |
| plos_bzdok2024_trec_cxce_1to1000 | A-hosp | benchmark confirmation | 12 | 53 | 4.42 | E1_CP_confirm_probability | 0.0 | p0=0.95; empirical 1/12 (8%) from replicate CSV | Bzdok J et al. PLOS ONE 2024; S3 Dataset (10.1371/journal.pone.0306329.s003); CC BY 4.0 | Sub-LoD dilution panel at 1:1000 with undetermined Cp recorded as non-detect (S3 Dataset sheet 3). |
| plos_bzdok2024_trec_magnapure_1to100 | A-hosp | benchmark confirmation | 9 | 53 | 5.89 | E1_CP_confirm_probability | 0.0 | p0=0.95; empirical 8/9 (89%) from replicate CSV | Bzdok J et al. PLOS ONE 2024; S3 Dataset (10.1371/journal.pone.0306329.s003); CC BY 4.0 | Limit of detection raw data for TREC compared for MagNA Pure 96 extractions (S3 Dataset sheet 3; per-replicate Cp). |
| jcm_hansen2020_abbott | A-pub | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 | p0=0.95; published 16/20 (80%) | Hansen G et al. J Clin Microbiol 2020; CDC/clinical laboratory comparison | Direct comparison of SARS-CoV-2 analytical limits of detection across seven molecular assays (Table 1: detected/tested at stated concentration). |
| plos_lim2021_mcatarrhalis | A-pub | benchmark confirmation | 50 | 53 | 1.06 | E1_CP_confirm_probability | 0.0 | p0=0.95; published 11/50 (22%) | Lim HJ et al. PLOS ONE 2021; Soonchunhyang University hospital-affiliated clinical validation | Analytical sensitivity and LOD were estimated with 50 replicates of positive control bacteria at six different concentrations (Table 3). |
| scirep_jiang2025_mp | A-pub | benchmark confirmation | 20 | 53 | 2.65 | E1_CP_confirm_probability | 0.0 | p0=0.95; published 19/20 (95%) | Jiang Y et al. Sci Rep 2025; Shaanxi Provincial Hospital clinical validation | Each dilution was assessed using the established assay in 20 replicates. The limit of detection (LoD) was determined by probit analysis, defined as the concentration detectable with ≥95% probability (Table 1). |


## S6. Worked example

Archived EP17 Section 7.3 language (Analyse-it estradiol workbook annotation): a minimum of 20 replicates at the LoD concentration, and for a 95% detection claim at least 19 of 20 should be detected.

| Locked claim | n at conventional 20 | n* under Table 1 targets |
| --- | --- | --- |
| Qualitative pass, k held at 19, p = 0.95 | P(pass) = 0.736 | 21 |
| Benchmark confirmation, p = 0.95 | CP lower limit after 20/20 < 0.95; P(confirm) = 0 | 53 |
| Two-arm 90%/80% | exact Fisher power ≈ 0.07 | 199 |

The audit used the qualitative-pass mapping for that sentence.

## S7. Reproducibility

Python 3.10; lod_guide v0.5.0. Tables in this file were regenerated by `scripts/build_online_supplement.py`. Main-text figures remain those in `manuscript/figures/`.
