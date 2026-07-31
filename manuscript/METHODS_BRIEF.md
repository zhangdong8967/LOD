# Assumption-Gated Decision Theory for Clinical Limit-of-Detection Evaluation

**Manuscript type:** Methods / Technical Brief (draft)  
**Companion:** [SUPPLEMENT.md](SUPPLEMENT.md) embeds numbered figures and tables from `paper_artifacts/`  
**Main figures:** Fig 1–5 only (see [`FIGURE_PLAN.md`](../paper_artifacts/captions/FIGURE_PLAN.md)); module detail in Fig S1–S9  
**Software:** `lod_guide` (Python package in this repository)  
**Stance:** Complements CLSI EP17-class options; does **not** supersede EP17, YY/WS, or IFU as legal standards.

---

## Abstract

**Background.** Many LoD verification protocols fix \(n \approx 20\) and informal pass rules without planning replicates for the **detection claim** (verify 95% hit rate, compare lots at LoD, or qualitative \(k/n\)). LoB and LoQ are outside this brief’s scope ([`LOD_RESEARCH_SCOPE.md`](../docs/methodology/LOD_RESEARCH_SCOPE.md)).

**Methods.** We specify a prospective design protocol for LoD verification: lock one estimand (G1, G2, or G4), plan replicate number from operating characteristics, and confirm at small \(n\) with exact binomial and Fisher/Boschloo methods. Designs are compared on a transparent decision risk
\[
L = w_I\cdot\mathrm{TypeI} + w_{II}\cdot\beta + w_M\cdot\mathbf{1}\{\text{parametric mismatch}\} + w_C\cdot(\mathrm{DE}-1).
\]
Public datasets are stratified by evidence tier A/B/C/S.

**Results.** G2 folklore \(n=20\) yields exact Fisher power ≈0.07 (90% vs 80%); powered planning requires \(n \approx 199\) per arm. G1 all-positive runs leave large uncertainty on 95% claims (P7). Tier-A qPCR/probit/RMN deposits illustrate LoD replicate ratios versus folklore (Fig 5).

**Conclusions.** Path and sample size for LoD verification can be planned before data collection inside EP17-class workflows. The framework complements EP17; it does not replace regulatory definitions. Routine-chemistry blank–LoD raw archives remain limited; tier C/S materials must not be reported as multi-assay clinical validation.

**Keywords:** limit of detection; EP17; sample size; exact tests; LoB; decision theory; laboratory verification

---

## 1. Introduction

### 1.1 Background

Clinical laboratories must verify **LoD**—detection at a stated low concentration—for qualitative and hit-rate assays. This brief plans **replicate number** for claims G1, G2, and G4; LoB and LoQ are not the research focus ([`LOD_RESEARCH_SCOPE.md`](../docs/methodology/LOD_RESEARCH_SCOPE.md)).

Local SOPs often ignore that pluralism: about **20 replicates**, a **normal LoB** by default, and pass rules such as **all positives** or **at least one hit in n tries**. Those habits skip the step EP17 assigns to the laboratory—matching path and replicate number to the **claim in the validation protocol**. A report may read “equivalent,” “verified,” or “passed” while the study was never sized to support that wording.

### 1.2 The design gap

EP17 specifies what may be estimated; estimation papers (Linnet and Kondratovich, 2004; Galitzine et al., 2018) address how to compute LoD given a path. Kondratovich and Linnet (2017) modeled pass probability for **single-method** molecular verification—evidence that fixed \(n=20\) is inadequate for that estimand. Prospective design for **comparative** claims (two kits or lots at a stated concentration) and for **gated** parametric LoB is rarely documented in recent validation literature (Block B screen, Supplement).

We formalize that missing step: lock one estimand (G1–G4), run diagnostic gates, select an EP17-class path, plan \(n\) from operating characteristics, and confirm at small \(n\) with exact methods.

**Illustrative protocol.** If a protocol requires lot B to be “equivalent” to lot A at LoD concentration \(c^\star\), the estimand is **G2**. At true hit rates 90% vs 80%, \(n=20\) per arm yields exact Fisher power **0.07**; 80% power requires **\(n \approx 199\)** per arm (Box 1; [`WORKED_EXAMPLE.md`](WORKED_EXAMPLE.md)). Full related-work prose: [`INTRODUCTION_FULL.md`](INTRODUCTION_FULL.md).

### 1.3 Where fixed SOPs fail

See §1.2 (G2 lot-comparison example). Additionally: **G1**—20/20 positives do not certify a 95% LoD claim (P7); **saturation**—\(1-(1-p)^n\) must not be used for reagent comparison (P1).

### 1.4 This work

Locked pipeline **S0–S7**; decision risk \(L\) with default equal weights (sensitivity in Supplement); theory certificates P1–P18; tier **A/B/C/S** evidence firewall; open **`lod_guide`**. Folklore \(n=20\) for G2 carries ≈**3.9×** the equal-weight \(L\) of a powered design. We **complement** EP17; we do **not** supersede legal LoB/LoD/LoQ definitions. Figures 1–5 and Supplement: [`SUPPLEMENT.md`](SUPPLEMENT.md).

---

## 2. Methods

### 2.1 Estimands (Table 1)

Before any formula, the laboratory locks one primary estimand:

| ID | Role | Sample-size engine |
|----|------|--------------------|
| **G1** | Single-method LoD / hit-rate claim | One-proportion vs \(p_0\) |
| **G2** | Compare reagents/lots at \(c^\star\) | Two-proportion; exact Fisher/Boschloo at confirmation |
| **G4** | Qualitative \(k/n\) at detection limit | Binomial cumulative search |

G3 (LoQ / precision) is available in `lod_guide` for EP17 completeness; it is documented in the Supplement and excluded from primary claims in this brief.

Mixing goals in one analysis episode is forbidden.

### 2.2 LoD planning pipeline (Fig 1)

We treat design as minimization of
\[
L = w_I\cdot\mathrm{TypeI} + w_{II}\cdot\beta + w_M\cdot\mathbf{1}\{\text{parametric mismatch}\} + w_C\cdot(\mathrm{DE}-1),
\]
with transparent default weights \(w_\cdot=1\) (sensitivity in Supplement). The **main-text LoD path** is:

**S0** lock G1/G2/G4 → **S1** hit-rate/binary type → **S5** plan \(n\) → **S6** exact confirmation → **S7** report.

Optional continuous EP17 LoB branch (S2–S4, P17): Supplement Fig S-LoB. G3 LoQ: Supplement Table 2.

### 2.3 Design surfaces versus exact confirmation

- **Planning:** asymptotic two-proportion power and Fleiss–Chow \(n^\star(p_A,p_B)\) (Fig 2B, Fig 3, Fig 4A); concentration relative to LoD\(_{95}\) via \(r=c/\mathrm{LoD}_{95}\) (Fig S6).
- **Confirmation (small \(n\)):** exact Fisher power enumeration and Boschloo unconditional tests; Wilson / Clopper–Pearson coverage for G1 intervals (Tables 3, 6, 8).
- **Continuous LoB:** parametric mean + \(z_{1-\alpha}\)SD versus nonparametric 95th percentile, gated by S2 shape/censoring/heterogeneity diagnostics.
- **LoQ (G3):** CV% versus mean precision profile; LoQ@CV20% by interpolation when applicable (Fig 5; Table 2).

Machine-checkable results **P1–P18** are organized in three layers (Table 4; §2.3.1): Layer **A** analytic theorems, Layer **B** finite-sample bounds, Layer **C** numerical certificates. Core lemmas P1–P8 cover saturation, binomial identities, design effect, parametric LoB counterexamples, OVL, all-positive trap, and exact–asymptotic gap; **P12–P18** extend identification, c-optimal/minimax design, selective LoB inflation, and folklore inadmissibility (Fig 4C; full panels in Fig S9).

#### 2.3.1 Theory certificates P12–P18 (A / B / C layers)

Theory results are machine-audited via `lod_guide.theory.propositions.verify_all_propositions()` and deposited under `data/research/`. Layers follow the package convention: **A** = closed-form or proof-sketched theorems; **B** = exact finite-sample enumeration/bounds; **C** = Monte Carlo or grid certificates.

| ID | Layer | Statement (abbrev.) | S5 / clinical role |
|----|-------|---------------------|-------------------|
| **P12** | C | Locally **c-optimal** multi-level design beats equal log-spacing + equal \(n\) on asymptotic efficiency for SE(\(\log_{10}\mathrm{LoD}_{95}\)) | Planning surface for EP17 probit-class hit-rate studies |
| **P13** | C | **Minimax** design over \(\beta\in[0.5,1.5]\beta_{\mathrm{plan}}\) lowers worst-case SE vs folklore equal log | Default recommendation when slope is uncertain |
| **P14** | C | c-efficiency \((\mathrm{SE}_{\mathrm{ref}}/\mathrm{SE}_{\mathrm{opt}})^2 > 1\) for reference vs c-optimal | Quantifies gain from design optimization |
| **P15** | A | \(\log_{10}\mathrm{LoD}\) **identifiable** iff Fisher rank\(=2\), \(\|\beta\|>0\), and \(\geq 2\) interior hit-rate levels | **Hard gate** before probit-path planning |
| **P16** | A | Saturation/floor plates → **non-identifiable** \(\log_{10}\mathrm{LoD}\) even at large \(N\) | Blocks folklore grids that sit below the inflection region |
| **P17** | C | Conditional Type I \| S2 selects parametric LoB can exceed nominal α on skew blanks | Motivates nonparametric path after failed S2 |
| **P18** | B | Folklore \(n=20\) is **Pareto-inadmissible** vs powered \(n^\star\approx 199\) on exact Fisher OC plane | G2 discrimination; complements P8 |

Supplementary certificates (same audit run): General Equivalence Theorem check for c-optimal designs (`C_optimal_equivalence`, C); selective LoB error decomposition (`P17_selective_inflation`, C); formal minimax problem statement (`P13_minimax_formal`, C).

**S5 multilevel integration.** When `plan_multilevel_lod=True` on binary hit-rate paths, S5 calls `recommend_multilevel_lod_design`: if P15 fails → **`LoDDesignBlockedError`** (hard stop); if P15 passes → return minimax concentrations, per-level \(n\), and SE(\(\log_{10}\mathrm{LoD}\)) at plan and worst-case slopes (JSON: `minimax_probit_design.json`, `c_optimal_lod_design.json`; Fig 4C; Fig S9).

### 2.4 Evidence ladder (Table 5; Fig S7)

Public materials are stratified:

| Tier | Meaning | Allowed claim use |
|------|---------|-------------------|
| **A** | Raw / replicate-level public deposits | Primary empirical illustrations |
| **B** | Summaries / very small-\(n\) | Corroboration only |
| **C** | Synthetic EP17 demos | Engine walk-through only |
| **S** | Simulation stress DGPs | Mechanism, coverage, power — **not** multi-assay validation |

Primary empirical meta-summary (Table 7) includes **only** tier A. Current counts after download: A=9, B=3, C=1, S=8.

### 2.5 Software and reproducibility

Analyses are implemented in the open Python package `lod_guide`. One-command packaging:

```bash
pip install -e ".[dev]"
python -m lod_guide.data.download_real
python examples/run_theory_depth.py    # P12–P18 JSON + certificates
make paper-artifacts
```

Seeds, JSON audits, and SHA stamps live under `data/research/` and `paper_artifacts/MANIFEST.json` (Supplement §S-Repro).

---

## 3. Results

### 3.1 Folklore \(n=20\) is high-risk for close discrimination (G2)

For \(p_A=0.90\) vs \(p_B=0.80\), α=0.05:

- Monte Carlo power at folklore \(n=20\) ≈ **0.14**; at asymptotic \(n^\star\) ≈ **0.81** (operating-characteristic study).
- Exact Fisher power at \(n=20\) ≈ **0.07**; miss β ≈ **0.93** (Table 3; P8).
- Decision-risk ratio folklore / powered ≈ **3.9** under equal weights (Supplement decision-risk table).

Fig 2B and Fig 3A visualize the same qualitative message across Δp (full curves: Fig S2–S3).

### 3.2 All-positive runs do not certify a 95% LoD claim (G1)

\(P(X=n)=p^n\). At \(p=0.90\), \(n=5\), all-positive probability ≈0.59; even after observing \(n/n\), one-sided Clopper–Pearson lower bounds remain far below 0.95 at small \(n\) (Fig 2A; P7).

### 3.3 Parametric LoB fails under skew (tier S + gate)

Under exponential blanks, population exceedance of the parametric LoB exceeds nominal α (theory + MC; LoB coverage study). Nonparametric paths track α more closely under skew. Decision risk for parametric-on-Exp versus nonparametric path is elevated (~2.6× in the standard scenario set).

### 3.4 Tier-A public deposits: gates often select nonparametric paths (Table 7)

Illustrative continuous blank–LoB: EP17 estradiol worked example (Analyse-it / CLSI Appendix A). Proteomics blank–LoB: CPTAC / MSstatsLOBD calibration (Concentration=0 light areas)—**domain-bounded** to targeted MS, not analyzer chemistry. Multi-lab routine chemistry (Carobene Lombardy EQA) supports **precision / design-effect** illustration, not blank–LoB. Primary LoQ profile: radioimmuno Precision table (Fig 5, tier A); troponin EP17 Example 3 remains tier-C engine demo (Fig S1).

Across tier-A continuous analyses with blank-like vectors, parametric candidacy is frequently rejected by S2; guidance \(n\) for continuous establishment episodes commonly exceeds folklore 20 (Table 7 ratios).

### 3.5 G1 interval policy (Table 8)

Wilson and Clopper–Pearson coverage under binomial hit-rate scenarios are tabulated for confirmatory one-proportion reporting.

### 3.6 Multi-level hit-rate design and theory depth (P12–P18; Fig 4)

On synthetic logistic truth (LoD\(_{95}\)=1, \(N=60\), \(K=5\)):

- **c-optimal** grid design lowers asymptotic SE(\(\log_{10}\mathrm{LoD}\)) vs equal log-spacing folklore (P12; efficiency \(>1\), P14).
- **Minimax** dense-near-LoD + LoD-weighted allocation reduces worst-case SE over \(\beta\in[0.5,1.5]\beta_{\mathrm{plan}}\) vs folklore (P13; Fig 4C; Fig S9B).
- **Saturation plates** (all concentrations far below LoD) fail P16 identifiability; S5 raises `LoDDesignBlockedError` rather than returning a powered plan.
- **Folklore G2** \(n=20\) remains Pareto-dominated by powered \(n^\star\approx 199\) on exact Fisher Type I / power (P18; loss ratio ≈ 3.5×).

S2 threshold perturbations (`s2_threshold_sensitivity.json`) and probit slope-misspecification robustness (`probit_design_robustness.json`) are in the Supplement.

### 3.7 Theory/algorithm completion (v0.4.3)

Supplement JSONs cover: decision-weight axioms (A1–A4); Barnard-difference tests; Holm multiplicity; Tobit LoB; Rocke–Lorenzato LoQ; pre-test LoB inflation (`pre_test_lob_inflation.json`); Pareto exact \(n\) (`pareto_exact_sample_size.json`). Machine certificates: **P1–P18** plus supplementary c-optimal equivalence and selective inflation (22 results; `verify_all_propositions()`).

---

## 4. Discussion

### 4.1 Relation to prior work

**Standards (EP17, Armbruster).** We treat EP17 as an **option set**, not a single SOP. Armbruster and Pry (2008) summarize manufacturer (~60) vs laboratory (~20) replicate asymmetry; we add **estimand-specific** powered \(n\) and auditable path gates without redefining LoB/LoD/LoQ.

**Estimation (Linnet, Galitzine, commercial tools).** Linnet and Kondratovich (2004) motivate our nonparametric branch under skew; Galitzine et al. (2018) bound proteomics tier-A illustrations. Analyse-it and MSstatsLOBD implement **single-path** calculators; `lod_guide` **orchestrates** G1–G4 with mismatch-aware \(L\) and exact confirmation.

**Verification probability (Kondratovich and Linnet, 2017).** Closest precedent for criticizing blind \(n=20\) verification pass rates. We extend to **G2** two-proportion discrimination, exact Fisher/Boschloo (P8), and Pareto inadmissibility of folklore \(n=20\) (P18).

**Block B validation literature (2026 screen).** Of 200 PubMed hits, 149 were non-clinical; remaining papers typically **report** CLSI-aligned LoB/LoD/LoQ (e.g., J Appl Lab Med 2026 NfL; *Clin Chem* 2026 apo RMP) without comparative power planning—consistent with the design gap we fill. Full discussion: [`DISCUSSION_PRIOR_WORK.md`](DISCUSSION_PRIOR_WORK.md).

### 4.2 What this brief establishes

Inside EP17-class option sets, LoD work can be written as **auditable risk minimization**: diagnostic gates control mismatch; exact methods control small-sample Type I / miss-β; evidence tiers prevent overclaiming. Folklore \(n=20\) for G2 carries ~**3.9×** equal-weight loss versus powered design; all-positive runs leave large residual LoD uncertainty; tier-A gates often reject parametric LoB on public blanks.

### 4.3 Limitations

This brief does **not** include a prospective partner-laboratory case in which a protocol was redesigned with S0–S7 and then executed. Tier-A public deposits illustrate gate behavior on archived data; they do not validate all panels or IFU wordings. Raw blank–LoD series for routine analyzer chemistry remain scarce (Carobene supports precision/design effect; CPTAC supports MS blank–LoB—complementary domains). Default equal weights in \(L\) are audit parameters, not elicited clinical utilities. Tier C/S materials are firewalled from tier-A validation claims. We do not replace EP17 or manufacturer IFU. Full limitation prose: [`DISCUSSION_PRIOR_WORK.md`](DISCUSSION_PRIOR_WORK.md) §4.3–§4.4.

### 4.4 Standards stance and publication scope

The algorithm **complements** EP17; legal LoB/LoD/LoQ definitions and reporting cutoffs remain with standards, manufacturers, and local validation governance. This draft targets a **methods / technical brief** with online Supplement (`paper_artifacts/`). A full research article would add a prospective partner-laboratory case or expanded routine-chemistry blank–LoD raw. Cover letter: [`COVER_LETTER.md`](COVER_LETTER.md).

---

## 5. Data and code availability

- Package and scripts: this repository (`lod_guide`).
- Packaged figures/tables/captions: `paper_artifacts/` (see [SUPPLEMENT.md](SUPPLEMENT.md)).
- Public deposits: citations in Table 5 / evidence manifest (`data/raw/evidence_manifest.json` after download).
- Simulation DGPs: `data/simulated/dgp_catalogue.json` (seed + sha256).

---

## 6. Acknowledgments / Conflicts

Draft generated as part of the `lod_guide` methods package. Insert author affiliations, funding, and COI statements before journal submission.

---

## References (minimal set for drafting)

1. CLSI. *Evaluation of Detection Capability for Clinical Laboratory Measurement Procedures*; EP17-A2. Clinical and Laboratory Standards Institute.
2. Galitzine C, et al. Nonlinear curve fitting for targeted MS LoB/LoD (MSstatsLOBD). *Mol Cell Proteomics*. 2018. (CPTAC vignette data.)
3. Carobene A, et al. Lombardy Region EQA commutability / multi-lab chemistry replicates. *Clin Chim Acta*. 2025; Mendeley `10.17632/r4szpw8sn5`.
4. Malkamäki et al. Radioimmuno-dot-blot precision/linearity deposits. Zenodo 12664367.
5. Boschloo RD. Raised conditional level of significance for the 2×2 table when testing independence. *Stat Neerl*. 1970.

*(Expand to full Vancouver/AMA style in the submission build.)*
