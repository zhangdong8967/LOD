# Research Status — Honest Inventory (not a paper)

**Date focus:** deepen science before manuscript writing.  
**Package:** `lod_guide` v0.4.x — assumption-gated decision theory + multi-assay evidence ladder + exact small-sample methods.

See also: [ELEVATED_FRAMING.md](ELEVATED_FRAMING.md), [PUBLICATION_READINESS.md](PUBLICATION_READINESS.md).

---

## 1. Are the scripts “all written”?

| Layer | Status | Notes |
|-------|--------|-------|
| S0–S7 guidance pipeline | **Done** | Usable end-to-end |
| Theory P1–P11 + audit hash | **Done** | P7 all-positive; P8 exact vs asymptotic; P9 Holm FWER; P10 weight scale; P11 Tobit agreement |
| **Three-layer theory (P1–P18+)** | **Done (v0.5)** | `theory/theorems/` (A), `theory/bounds/` (B), `theory/certificates/` (C); see `archive/manuscript_retired/THEORY_MONOGRAPH.md` |
| Challenge positioning | **Done** | Manifesto + Clinical Chemistry theory draft |
| Real data download (multi-assay ladder) | **Done (v0.4.1)** | Tier A=10 (qPCR×2, estradiol, probit, radioimmuno precision+linearity, RMN, Carobene, **CPTAC/MSstatsLOBD**, **TREC newborn screening**); B=3; C=1 troponin demo; see EVIDENCE_LADDER.md + EVIDENCE_STRATIFIED_REPORT.md |
| Simulated stress catalogue | **Done (v0.4)** | 8 DGPs with draws, seed, sha256, dgp_catalogue.json |
| **Deep qPCR hit-rate / logistic LoD** | **Done (v0.3 depth)** | `research/deep_qpcr.py` |
| **MC operating characteristics** | **Done (v0.3 depth)** | folklore vs \(n^\star\) |
| **LoB coverage under skew** | **Done (v0.3 depth)** | parametric vs nonparametric |
| Exact two-proportion power (Fisher/Boschloo) | **Done (v0.4)** | `theory/exact_tests.py` + exact_power_study |
| Continuous clinical chemistry panels (real) | **Improved** | Estradiol (A) blank–LoB + radioimmuno (A) + RMN (A) + Carobene 10-lab routine chemistry (A, precision/DE) + **CPTAC proteomics blank–LoB (A)**; anion/cation IC (B); troponin LoQ remains C; hematology + analyzer electrolyte blank-LoD still scarce |
| Probit EP17-style multi-concentration design optimizer | **Done (v0.4.2)** | `research/probit_design_grid.py` — logistic/probit info-matrix SE(log10 LoD) design grid + EP17 workbook fit |
| **Precision-profile LoQ engine** | **Done (v0.4.1)** | CV vs mean, LoQ@CV%, n design; troponin EP17 Ex.3 |
| **EP17 estradiol continuous LoB/LoD** | **Done (v0.4.1)** | Diagnostics + para/nonpar LoB + bootstrap CI |
| **Type I calibration (Fisher/z)** | **Done (v0.4.1)** | Finite-sample H0 rejection rates; Boschloo optional demo |
| **Decision-risk loss \(L\)** | **Done** | `research/decision_risk.py` — TypeI/β/mismatch/DE |
| **Tier-A meta (Table 7)** | **Done** | `research/tierA_meta_analysis.py` |
| **E1 Wilson/CP coverage (Table 8)** | **Done** | `research/one_proportion_coverage.py` |
| **S2 threshold sensitivity** | **Done (v0.4.2)** | `research/s2_threshold_sensitivity.py` — flip rates under tightened/loosened DiagnosticThresholds |
| **Journal figures (no in-PNG titles)** | **Done** | panel letters only; captions in paper_artifacts |
| Bootstrap CI for nonparametric LoB | **Done (basic)** | `research/bootstrap_ci.py` — extend next |
| Multiplicity / sequential LoD verification | **Done (v0.4.2)** | Holm–Bonferroni + OBF/Pocock α-spending (`multiplicity_sequential.py`) |
| Decision-weight axioms / Pareto sensitivity | **Done (v0.4.2)** | A1–A4 + preference library (`decision_weight_axioms.py`) |
| Censored / Tobit LoB | **Done (v0.4.2)** | Left-censored Normal MLE + hot-deck percentile (`censored_lob.py`) |
| Variance-function LoQ (Rocke–Lorenzato) | **Done (v0.4.2)** | `variance_function_loq.py` |
| Probit design misspecification robustness | **Done (v0.4.2)** | `probit_design_robustness.py` |
| S2 risk-calibrated thresholds | **Done (v0.4.2)** | Proposal only; defaults stay frozen (`s2_risk_calibrated_thresholds.py`) |
| Clinical scenario catalogue CS01–CS15 | **Done** | `scenarios.py` + `examples/scenarios/` |
| **Continuous parameter-space models** | **Done (v0.3)** | \(p^n\), \(n^\star(p_A,p_B)\), \(r\in(0,\infty)\); CS04–CS06 are slices only |
| Manuscript | **Draft brief done** | `manuscript/METHODS_BRIEF.md` + `SUPPLEMENT.md` (embeds `paper_artifacts/`); full journal research article still deferred |

**Verdict:** Core algorithm + theory/algorithm completion modules (v0.4.2) are written and tested. Remaining gaps are mainly **journal packaging** and **scarce public analyzer blank–LoD raw**, not missing core math/stat/algorithm pieces for a methods brief.

---

## 2. How to run deep research

```bash
pip install -e ".[dev]"
python examples/run_deep_research.py      # includes continuous fields + qPCR + OC + LoB
python -m lod_guide.research.continuous_models
python -m lod_guide.research.continuous_figures
python examples/run_transparent_analysis.py
python -m pytest -q
```

Artifacts: `data/research/*.json`, `data/research/continuous_models/*.npz`, `data/audit/*.json`.  
Method note: [CONTINUOUS_MODELS.md](CONTINUOUS_MODELS.md).

---

## 3. Priority queue (do deep, do fine — before writing)

2. **All-positive trap** (\(n/n\) hits) — **Done.**  
3. **Reagent discrimination + miss β** (90 vs 80, 90 vs 50, relative LoD) — **Done:** `REAGENT_DISCRIMINATION.md`.  
3b. **Continuous fields** over \((p,n)\), \((p_A,p_B)\), \(r\in(0,\infty)\) — **Done:** `CONTINUOUS_MODELS.md` (example percentages are slices only).  
4. **Exact / Boschloo / Fisher / Barnard-diff** — **Done (v0.4.2)**.  
5. **More real datasets** — **Improved (v0.4.1):** +2–3 non-demo tier-A continuous/precision deposits (radioimmuno Precision/Linearity, RMN); still seek hematology raw + electrolytes.  
5b. **Strict A/B/C/S reporting** — **Done:** `evidence_stratified_report` → `EVIDENCE_STRATIFIED_REPORT.md` / `EVIDENCE_CLAIMS_BY_TIER.md`.  
6. **Variance-function / LoQ precision profiles** — **Done (v0.4.2)** (empirical profile + Rocke–Lorenzato).  
7. **Finite-sample coverage tables** for Wilson vs Clopper–Pearson in LoD hit rates. — **Done**  
8. **Sensitivity of diagnostic thresholds** (S2). — **Done (v0.4.2)** (+ risk-calibrated proposal)  
9. **Legacy root scripts** (`lod_*.py`) — migrate or deprecate.  
10. **Probit multi-concentration design grid** — **Done (v0.4.2)** (+ misspecification robustness).  
11. **Multiplicity / sequential / weight axioms / Tobit** — **Done (v0.4.2)**.

---

## 4. What “done enough for a paper” would require

- All priority-queue items 1–5 with deposited tables.  
- Independent re-run producing matching SHA-256 audits.  
- At least one continuous clinical chemistry–like real dataset (or documented impossibility + stronger simulations).  
- Referee-style internal review of P1–P6 and OC tables.

Until then: **keep deepening code and evidence; do not draft the article.**


---

## 5. Paper artifacts (v0.4.1 packaging)

```bash
make paper-artifacts
# or: python examples/run_paper_artifacts.py
```

Outputs under `paper_artifacts/`: unified Fig 1–7 / Table 1–5 captions, CSVs, figure copies, and `review/INTERNAL_REVIEW_P1P6_EXACT.md`.

---

## 6. Expert verdict — can we submit now? (**No**)

As a statistical / mathematical assessment of the *current* package:

**What is already strong (publishable as methods/supplement material):**
- Estimand locking (E1–E3) and S0–S7 gate logic.
- Clear identification theorems / certificates **P1–P11** (incl. Holm FWER, weight scale invariance, Tobit agreement).
- Exact vs asymptotic power discrepancy quantified (Fisher miss β ≈ 93% for 90 vs 80 at n=20).
- Honest evidence ladder (tiers A/B/C/S) instead of overclaiming multi-assay validation.

**What still blocks a top-tier Clinical Chemistry full article:**
1. **Journal packaging** (Word/LaTeX, affiliations, full reference list) — methods brief draft exists under `manuscript/`.
2. **LoQ / precision-profile engine** now also run on tier-A radioimmuno + RMN deposits (not only tier-C troponin); still need more routine chemistry multi-pool panels.
3. **Real continuous clinical chemistry** improved (estradiol blank–LoB + radioimmuno + RMN + Carobene multilab + CPTAC proteomics blank–LoB) but electrolytes/hematology analyzer blank–LoD deposits remain absent.
4. **Figure suite** improved (composite Fig 4 + LoQ profile Fig S1); still needs Word/LaTeX embedding and colorblind check in the draft.
5. **Small-sample primary analysis policy** now includes Boschloo + Barnard-diff + denser exact-power scenarios; full CSM Barnard region search remains optional.
6. Independent re-run / deposited archive with locked seeds for every main table should accompany submission.

**Recommended publication path:**
- **Near-term:** submit/polish `manuscript/METHODS_BRIEF.md` + Supplement from `paper_artifacts/` as methods / technical brief.
- **Full research article:** only after additional routine-chemistry blank–LoD raw or prospective partner-lab case, and internal review memo issues closed.

**Bottom line:** Do **not** claim “ready to submit a complete Clinical Chemistry research paper today.” Do claim: **methods brief draft + reproducible Supplement package are ready for polish and journal formatting.**
