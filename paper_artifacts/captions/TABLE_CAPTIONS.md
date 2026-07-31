# Table captions (manuscript numbering)

## Table 1. Primary LoD estimands G1, G2, G4

**Developer ID:** `T1_estimands`  
**CSV:** `tables/Table01_estimands_G1_G4.csv`  

**Caption.** Detection-limit estimands before sample-size planning. Mixing goals in one episode is forbidden; engines differ by row. G3 (LoQ / precision) is an optional EP17 branch documented in Supplement Table 2 and excluded from main-text claims.

## Table 2. LoQ / precision design (G3)

**Developer ID:** `T2_loq_precision`  
**CSV:** `tables/Table02_loq_precision_main.csv`  

**Caption.** Required n so that CV of the mean (100·(σ/μ)/√n) meets target CV%, and n for mean CI half-width under Normal sampling. **Supplement only (G3 LoQ)** — out of main-text LoD scope; radioimmuno tier-A profile in FigL; troponin EP17 pools tier-C demo (Fig S1).

## Table 3. Asymptotic versus exact discrimination power

**Developer ID:** `T3_exact_vs_asymp`  
**CSV:** `tables/Table03_exact_vs_asymptotic.csv`  

**Caption.** For selected (p_A,p_B,n): asymptotic pooled-z power, exact Fisher power, exact pooled-z enumeration, Monte Carlo pooled-z, and miss β under Fisher. Primary small-n confirmatory reporting should prefer exact / Boschloo; asymptotic surfaces remain design approximations. Supports Fig 3.

## Table 4. Machine certificates P1–P18

**Developer ID:** `T4_propositions`  
**CSV:** `tables/Table04_propositions_P1_P6.csv`  

**Caption.** Internal review table: proposition ID, statement, pass/fail, key numeric details (P1–P8 core lemmas and bounds; P12–P18 identification, c-optimal/minimax design, selective LoB inflation, folklore inadmissibility). Re-run produces SHA-auditable certificates in the analysis protocol.

## Table 5. Public evidence ladder

**Developer ID:** `T5_evidence_ladder`  
**CSV:** `tables/Table05_evidence_ladder.csv`  

**Caption.** Downloaded real datasets by evidence tier (A=raw/replicate-level public deposits; B=summary; C=synthetic EP17 demo; S=simulation DGPs) and assay family. Includes radioimmuno precision/linearity (Zenodo 12664367), RMN ID50 (Zenodo 17108929), Carobene multi-lab chemistry, and CPTAC/MSstatsLOBD proteomics blank–LoB as tier-A cases. Hematology analyzer blank–LoD raw deposits remain a gap.

## Table 6. Finite-sample Type I error under H0

**Developer ID:** `T6_type1_calibration`  
**CSV:** `tables/Table06_type1_calibration.csv`  

**Caption.** Empirical Type I rates for pooled-z and Fisher (and Boschloo at n=20) under p_A=p_B=p. Documents conservatism of Fisher and calibration of pooled-z.

## Table 7. Tier-A meta-summary across public deposits

**Developer ID:** `T7_tierA_meta`  
**CSV:** `tables/Table07_tierA_meta.csv`  

**Caption.** One row per evidence-tier-A dataset: parametric gate outcome, model path, guidance n versus folklore n=20, and LoQ@CV20% when a precision profile applies. Tier C/S deposits are excluded by design. Supports Fig 5.

## Table 8. G1 Wilson vs Clopper–Pearson coverage

**Developer ID:** `T8_g1_coverage`  
**CSV:** `tables/Table08_g1_one_proportion_coverage.csv`  

**Caption.** Monte Carlo coverage and mean width for Wilson and Clopper–Pearson intervals under binomial LoD hit-rate scenarios. Supports confirmatory G1 interval policy.
