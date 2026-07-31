# Challenging Folklore LoD Evaluation

lod_guide is an assumption-gated, estimand-specific sample-size and path-selection framework for clinical LoD evaluation that bridges EP17-class options and laboratory practice: it complements and operationalizes consensus documents, challenges folklore SOPs (fixed n, always-normal LoB, saturated comparative metrics), and does not claim to supersede EP17 / YY / WS / manufacturer IFU as legal or standards documents.

## Relation to standards (locked)

Align with EP17-A2 LoB/LoD/LoQ vocabulary and dual parametric/nonparametric spirit; strengthen EP17’s statement that one protocol cannot fit all measurands into an executable S0–S7 decision tree with sample-size consequences; challenge practice myths with power tables and diagnostics—not the standards text itself.

## What we may challenge

- Verification n from tradition is often inadequate for comparative LoD claims.
- Distributional diagnostics should precede parametric LoB.
- Saturated hit metrics can erase reagent differences.
- Heterogeneity is a design factor, not only noise to pool away.
- Algorithm output can serve as a statistical appendix for verification narratives.

## What we do not claim

- That EP17 is wrong and must be replaced.
- That one new n replaces all EP17 study designs.
- That clinical reporting cutoffs can be changed by this algorithm alone without method-validation governance.
- That this package is a competing legal standard number.

## Practice-myth claims (C1–C5)

### C1. Folklore fixed n=20 (or 60) for all LoD questions

**Problem.** Sample size is estimand-dependent. Comparing 90% vs 80% detection rates needs ~199 replicates/arm for 80% power; n=20 yields ~14% power.

**Algorithm response.** S0 locks goal G1–G4; S5 returns powered/precision-based n.

### C2. Always-parametric normal LoB (mean + k·SD)

**Problem.** Near-LoD blanks are often skewed, censored, or batch-heterogeneous; parametric LoB then miscalibrates LoD.

**Algorithm response.** S2 diagnostics + S3 correction gate; hard-stop to S4b nonparametric.

### C3. Pooling across days/lots/operators without checking poolability

**Problem.** High ICC makes a single pooled LoD non-transportable.

**Algorithm response.** S2 ICC/Levene/between-stratum CV; S5 design-effect inflation.

### C4. Using 1-(1-p)^n to compare reagents

**Problem.** Metric saturates near 1 for both p=0.9 and p=0.8; differences vanish.

**Algorithm response.** G2 uses observed rates hat{p} and two-proportion power only.

### C5. One protocol for binary, continuous, count, and multiclass assays

**Problem.** Result types imply different single-trial models and success events.

**Algorithm response.** S1 type routing; diverse real + simulated benchmark catalogue.


## Diverse evidence base

See [EVIDENCE_LADDER.md](EVIDENCE_LADDER.md) for tiers A/B/C/S and claim boundaries.

- **Real public data (multi-family):** Zenodo qPCR; Analyse-it CLSI EP17 estradiol / probit / troponin workbooks; Zenodo cation IC + radioimmuno summaries.
- **Simulated stress tests (tier S):** explicit DGPs with Bernoulli draws, seeds, sha256.
- **Exact small-sample layer:** Fisher + Boschloo ([EXACT_SMALL_SAMPLE.md](EXACT_SMALL_SAMPLE.md)).

Run: `python examples/run_diverse_benchmark.py` and `python -m lod_guide.data.download_real`
