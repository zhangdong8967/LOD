# Online Supplement

**Companion to:** [METHODS_BRIEF.md](METHODS_BRIEF.md)  
**Artifact root:** [`../paper_artifacts/`](../paper_artifacts/) (regenerate with `make paper-artifacts`)  
**Caption sources:** [`../paper_artifacts/captions/FIGURE_CAPTIONS.md`](../paper_artifacts/captions/FIGURE_CAPTIONS.md), [`../paper_artifacts/captions/TABLE_CAPTIONS.md`](../paper_artifacts/captions/TABLE_CAPTIONS.md)

**Figure plan:** [`../paper_artifacts/captions/FIGURE_PLAN.md`](../paper_artifacts/captions/FIGURE_PLAN.md) — main text uses **5 composite figures** only; module detail is in Fig S1–S9.

---

## S0. How to rebuild

```bash
cd <repo>
pip install -e ".[dev]"
python -m lod_guide.data.download_real   # optional if raw files already present
make paper-artifacts
python -m pytest -q
```

Build stamp: `paper_artifacts/MANIFEST.json`.

---

## S1. Decision overview and risk function

Main-text Fig 1 and §2.2. Standard scenario losses (equal weights) are in `data/research/decision_risk.json`. Headline comparisons after the last build:

- G2 loss ratio folklore \(n=20\) / powered \(n^\star\) (90 vs 80) ≈ **3.91**
- G1 loss ratio parametric-on-Exp / nonparametric path ≈ **2.58**

---

## Main figures (embedded) — unified narrative (Fig 1–5)

Narrative arc: **decision map → folklore failures → finite-sample theory → remedies → tier-A anchor**.

### Figure 1. S0–S7 decision map with estimand gates

![Fig 1](../paper_artifacts/figures/Fig1_Fig1-decision-map.png)

**Caption.** LoD verification planning pipeline. Lock detection claim G1/G2/G4 (S0), classify hit-rate/binary data (S1), plan replicates (S5), confirm with exact methods (S6), report (S7). Optional continuous EP17 LoB path (S2–S4): Supplement Fig S-LoB.

*Files:* `paper_artifacts/figures/Fig1_Fig1-decision-map.png` (+ `.pdf`; alias `Fig1_FigM1.*`)

---

### Figure 2. Folklore triple failure

![Fig 2](../paper_artifacts/figures/Fig2_Fig2-folklore-triptych.png)

**Caption.** Three independent failure modes of folklore small-n practice. **A (G1):** probability \(p^n\) of observing \(n/n\) hits; CP lower bound after 20/20 remains far below 0.95. **B (G2):** exact Fisher miss probability \(\beta\) at folklore \(n=20\). **C (P16):** SE(\(\log_{10}\) LoD\(_{95}\)) under interior-level design versus saturation plateau.

*Files:* `paper_artifacts/figures/Fig2_Fig2-folklore-triptych.png` (+ `.pdf`)

---

### Figure 3. Finite-sample theory

![Fig 3](../paper_artifacts/figures/Fig3_Fig3-finite-sample.png)

**Caption.** **A:** asymptotic versus exact Fisher power versus \(n\) (90% vs 80%) with 80% reference. **B:** exact Fisher power heatmap over \((p_A, p_B)\) at folklore \(n=20\); ring marks 90% vs 80% cell. **C:** Type I versus power Pareto plane (P18); dashed arrow from folklore to powered design.

*Files:* `paper_artifacts/figures/Fig3_Fig3-finite-sample.png` (+ `.pdf`)

---

### Figure 4. Remedies

![Fig 4](../paper_artifacts/figures/Fig4_Fig4-remedy.png)

**Caption.** **A:** required \(n\) per arm (80% power) versus competitor hit rate. **B:** exact Fisher power at folklore \(n=20\) vs powered \(n^\star\) (90% vs 80%). **C:** probit LoD design SE (folklore / c-optimal / minimax). LoB/P17 panel: Supplement Fig S-LoB.

*Files:* `paper_artifacts/figures/Fig4_Fig4-remedy.png` (+ `.pdf`)

---

### Figure 5. Tier-A empirical anchor (LoD replicate planning)

![Fig 5](../paper_artifacts/figures/Fig5_Fig5-tierA-lod.png)

**Caption.** Four-panel Tier-A LoD anchor (Table 7). **A:** qPCR hit rate versus standard concentration (detection curve). **B:** guidance \(n\) versus folklore \(n{=}20\) on LoD-focused tier-A deposits. **C:** public deposit size versus planned \(n\) for LoD claims. **D:** headline replicate counts for G1, G2, and G4 versus folklore \(n{=}20\). Radioimmuno LoQ profile: supplement `FigL_radioimmuno_loq_profile.png`; troponin demo: Fig S1.

*Files:* `paper_artifacts/figures/Fig5_Fig5-tierA-lod.png` (+ `.pdf`)

---

## Supplement figures (Fig S1–S9)

Full module outputs; see [`FIGURE_PLAN.md`](../paper_artifacts/captions/FIGURE_PLAN.md).

| Fig | Topic | File |
|-----|-------|------|
| **S-LoB** | P17 LoB sample-split (continuous path) | `FigS_lob_p17_split.png` |
| **S1** | LoQ troponin demo (tier C) | `FigS1_FigS1-loq-troponin.png` |
| **S2** | Power vs \(n\) by \(\Delta p\) | `FigS2_FigS2-power-delta.png` |
| **S3** | Miss \(\beta\) curves | `FigS3_FigS3-miss-beta.png` |
| **S4** | All-positive trap (expanded) | `FigS4_FigS4-all-positive.png` |
| **S5** | Continuous \(n^\star\) 3-panel | `FigS5_FigS5-nstar-continuous.png` |
| **S6** | Concentration \(r=c/\mathrm{LoD}_{95}\) | `FigS6_FigS6-concentration.png` |
| **S7** | Evidence landscape | `FigS7_FigS7-evidence.png` |
| **S8** | Folklore vs algorithm bars | `FigS8_FigS8-challenge.png` |
| **S9** | Design SE (full 2-panel) | `FigS9_FigS9-design-se.png` |

Captions: [`FIGURE_CAPTIONS.md`](../paper_artifacts/captions/FIGURE_CAPTIONS.md).

---

## Main tables (machine-readable + manuscript copies)

Readable CSVs for drafting: `paper_artifacts/tables/manuscript/`.  
Raw build CSVs: `paper_artifacts/tables/`.

| ID | Title | Manuscript CSV | Build CSV |
|----|-------|----------------|-----------|
| **Table 1** | LoD estimands G1, G2, G4 | [Table01…](../paper_artifacts/tables/manuscript/Table01_estimands_G1_G4.csv) | [Table01…](../paper_artifacts/tables/Table01_estimands_G1_G4.csv) |
| **Table 2** | LoQ / precision (G3, Supplement) | [Table02…](../paper_artifacts/tables/manuscript/Table02_loq_precision_main.csv) | [Table02…](../paper_artifacts/tables/Table02_loq_precision_main.csv) |
| **Table 3** | Asymptotic vs exact power | [Table03…](../paper_artifacts/tables/manuscript/Table03_exact_vs_asymptotic.csv) | [Table03…](../paper_artifacts/tables/Table03_exact_vs_asymptotic.csv) |
| **Table 4** | Certificates P1–P18 | [Table04…](../paper_artifacts/tables/manuscript/Table04_propositions_P1_P8.csv) | [Table04…](../paper_artifacts/tables/Table04_propositions_P1_P6.csv) |
| **Table 5** | Evidence ladder | [Table05…](../paper_artifacts/tables/manuscript/Table05_evidence_ladder.csv) | [Table05…](../paper_artifacts/tables/Table05_evidence_ladder.csv) |
| **Table 6** | Type I calibration | [Table06…](../paper_artifacts/tables/manuscript/Table06_type1_calibration.csv) | [Table06…](../paper_artifacts/tables/Table06_type1_calibration.csv) |
| **Table 7** | Tier-A meta (primary empirical) | [Table07…](../paper_artifacts/tables/manuscript/Table07_tierA_meta.csv) | [Table07…](../paper_artifacts/tables/Table07_tierA_meta.csv) |
| **Table 8** | G1 Wilson vs CP coverage | [Table08…](../paper_artifacts/tables/manuscript/Table08_g1_one_proportion_coverage.csv) | [Table08…](../paper_artifacts/tables/Table08_g1_one_proportion_coverage.csv) |

Full captions: [`paper_artifacts/captions/TABLE_CAPTIONS.md`](../paper_artifacts/captions/TABLE_CAPTIONS.md).

### Table 1 (inline preview)

| Estimand | Symbol | Definition | Sample-size engine |
|----------|--------|------------|-------------------|
| G1 | \(p(c^\star)\) or LoD claim | Single-method LoD verification | one-proportion vs \(p_0\) |
| G2 | \(p_A-p_B\) at \(c^\star\) | Compare reagents/lots at LoD concentration | two-proportion / exact Fisher–Boschloo |
| G4 | \(P(X\ge k)\) | Qualitative \(k/n\) at detection limit | binomial cumulative search |

*G3 (LoQ / precision, \(\mathrm{CV}(c)=\sigma/\mu\)) is implemented in `lod_guide` for EP17 completeness; see **Supplement Table 2** and Fig S1 — excluded from main-text LoD claims.*

---

## S-Evidence. Claim firewall

- Stratified report: [`../data/research/EVIDENCE_STRATIFIED_REPORT.md`](../data/research/EVIDENCE_STRATIFIED_REPORT.md)
- Journal-facing copy: [`../paper_artifacts/review/EVIDENCE_CLAIMS_BY_TIER.md`](../paper_artifacts/review/EVIDENCE_CLAIMS_BY_TIER.md)

**Forbidden overclaims:** do not cite tier C/S as multi-panel clinical validation; do not pool A+C+S into one “\(N\) datasets support the algorithm” sentence without stratification.

Current counts (last stratified build): **A=9, B=3, C=1, S=8**.

---

## S-Review. Internal statistical memo

[`../paper_artifacts/review/INTERNAL_REVIEW_P1P6_EXACT.md`](../paper_artifacts/review/INTERNAL_REVIEW_P1P6_EXACT.md)

Covers P1–P8 certificates and exact-vs-asymptotic appendix readiness.

---

## S-Repro. Analysis JSONs cited by the brief

| Topic | Path |
|-------|------|
| Decision risk \(L\) | `data/research/decision_risk.json` |
| Reagent discrimination continuous 99→50% | `data/research/reagent_discrimination_continuous.json` |
| FigD2 (methodology) | `figures/methodology/FigD2_nstar_and_relative_lod.png` — A: \(n^\star\) vs competitor %; B: miss@\(n=20\); C: \(c/\mathrm{LoD}_{95}\) continuum |
| S2 threshold sensitivity | `data/research/s2_threshold_sensitivity.json` |
| Probit / logistic design grid | `data/research/probit_design_grid.json` |
| Decision-weight axioms | `data/research/decision_weight_axioms.json` |
| Multiplicity / sequential | `data/research/multiplicity_sequential.json` |
| Censored Tobit LoB | `data/research/censored_lob_tobit.json` |
| Variance-function LoQ | `data/research/variance_function_loq.json` |
| Probit design robustness | `data/research/probit_design_robustness.json` |
| S2 risk-calibrated thresholds | `data/research/s2_risk_calibrated_thresholds.json` |
| Exact vs asymptotic power | `data/research/exact_vs_asymptotic_power.json` |
| Operating characteristics (MC) | `data/research/operating_characteristics.json` |
| LoB coverage under skew | `data/research/lob_coverage.json` |
| All-positive trap | `data/research/all_positive_trap.json` |
| Type I calibration | `data/research/type1_calibration.json` |
| Tier-A meta | `data/research/tierA_meta_analysis.json` |
| Empirical tier-A extension | `data/research/empirical_tierA_extension.json` |
| EP17 estradiol LoB | `data/research/ep17_estradiol_analysis.json` |
| CPTAC / MSstats blank–LoB | `data/research/msstats_cptac_lob_analysis.json` |
| G1 coverage | `data/research/one_proportion_coverage.json` |
| Reproducibility deposit | `data/research/REPRODUCIBILITY.json` |

---

## S-Software note

Package modules: `lod_guide.pipeline` (S0–S7), `lod_guide.theory`, `lod_guide.research.*`, `lod_guide.paper.build_artifacts`.  
License and third-party data licenses are listed per row in Table 5 / `data/raw/evidence_manifest.json`.
