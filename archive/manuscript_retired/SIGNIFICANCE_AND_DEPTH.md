# Author argument map — significance without overclaim

**Audience:** Authors only. Not for paste into the manuscript wholesale.  
**Goal:** One clear chain of reasoning a *Clinical Chemistry* reviewer can follow; avoid AI-style stacking of metaphors.

---

## The single thesis (say this once, early)

EP17 defines LoB/LoD/LoQ and lists admissible paths. Laboratories still verify with fixed replicate counts and default formulas that do not match the **claim in the protocol**. We formalize the missing **prospective design step**: estimand → diagnostics → path → \(n\) → exact confirmation, with quantified operating characteristics and explicit scope limits.

If you cannot state the thesis in one sentence, the section is too diffuse.

---

## Argument chain (dependency order matters)

```
Claim in validation protocol
    ↓  (if skipped: everything downstream is ambiguous)
Estimand E1–E3
    ↓
Are parametric LoB assumptions tenable? (S2–S3)
    ↓
EP17-class path (S4)
    ↓
Powered or precision-based n for that estimand (S5)
    ↓
Exact confirmation at small n where normals lie (Methods §2.3)
    ↓
Report with tier discipline (A primary; C/S not “validation”)
```

**Do not** present S0–S7 as a “decision compiler,” “middleware,” or “Layer III.” Those labels sound generated and do not help a laboratorian.

**Do** say: EP17 tells you what procedures are allowed; this pipeline tells you which procedure matches your stated claim and how many replicates that claim requires.

---

## What prior work already covers (be fair or reviewers will kill us)

| Source | They solved | They did not solve |
|--------|-------------|-------------------|
| EP17-A2 | Definitions; path menu | Prospective \(n\) for each claim type |
| Linnet 2004 | LoD estimation with skewed blanks | Comparative verification design; gates |
| Vaks et al. 2016 | Pass P for **single-method** PCR verification | E2 two-arm discrimination; exact Fisher layer |
| Fleiss 2003 | Two-proportion \(n\) | LoD-specific laboratory workflow |
| Analyse-it / MSstatsLOBD | Path calculators post hoc | Estimand lock; design before data |

Our delta is **narrow but real**: bind textbook design logic to LoD verification workflows inside EP17, show folklore failure on LoD-relevant effect sizes, and document it with tiered public data.

---

## Three concrete failures (use numbers once in Intro, not three times)

1. **E2:** 90% vs 80% at \(n=20\)/arm → exact Fisher power ≈ 0.07.  
2. **E1:** 20/20 positives at claimed 95% LoD → CP lower bound still ≪ 0.95.  
3. **Continuous LoB:** skew/censoring → exceedance rate > α under parametric LoB.

Each failure ties to a **specific misuse**, not to EP17 being “wrong.”

---

## Decision risk \(L\) — how to explain without sounding like ML

**Wrong:** “We minimize an explicit loss function to falsify folklore SOPs.”  
**Right:** “Folklore SOPs implicitly accept high Type II error for comparative claims. We write Type I, Type II, distributional mismatch, and cluster inflation on one scale so two designs can be compared before data collection. Default weights are equal and sensitivity analyses are reported; we do not claim clinical utility optimality.”

Reviewers will ask: “Who picks the weights?”  
Answer prepared: transparent defaults + sensitivity; weights are audit parameters, not elicited patient utilities.

---

## P1–P18 — when to mention in Intro vs Methods

- **Intro:** cite P7, P5, P8/P18 only as labels tied to the three failures above.  
- **Methods/Results:** full certificate table.  
- **Never in Intro:** “machine-checkable,” “verify_all_propositions,” SHA-256, JSON—these belong in Methods/Software.

---

## Clinical stakes (one paragraph max, no alarmism)

Underpowered E2 can yield “equivalent” wording when the study could not detect a 10-point hit-rate gap—misleading for lot release and kit selection. Ungated parametric LoB can understate blank risk. Overclaiming from all-positive runs can pass internal checklists while leaving large uncertainty on \(p\). These are **validation governance** failures, not proof that patients were directly harmed in a cited dataset.

---

## Anticipated reviewer objections

| Objection | Response |
|-----------|----------|
| “This is just sample-size software.” | Software implements a **design protocol** with estimand lock and diagnostic gates; calculators do not enforce claim–\(n\) consistency. |
| “EP17 already covers this.” | EP17 lists paths; it does not derive \(n=199\) for a 90% vs 80% comparison or block parametric LoB when S2 fails. |
| “Vaks et al. 2016 did verification power.” | Single-method confirmation; we add E2, gating, exact layer, tiered evidence. |
| “Where is multi-lab prospective data?” | Brief scope: tier-A public deposits + theory; full article needs partner-lab case—state upfront in §4.3. |
| “Decision theory / estimand jargon.” | Estimand = the claim in the protocol written as a estimable quantity; we map E1–E3 to language validators already use. |

---

## Phrases to delete from manuscript drafts

- decision compiler / middleware / Layer I–III  
- falsifiable objects / inferential contracts / defensible inferential contracts  
- not a narrative / not X but Y (more than once per section)  
- systematically under-formalized / paradigm shift  
- machine-checkable (in Introduction)  
- 149/200 (in main text—Supplement only)

---

## Paste-ready blocks (use sparingly)

### Introduction closing (≈90 words)

We describe a prospective design protocol for EP17-class LoD studies: lock the estimand, gate parametric LoB on blank diagnostics, plan replicate number from operating characteristics, and confirm with exact methods at small \(n\). Fixed local SOPs are shown to carry high Type II error for common comparative claims and loose uncertainty for single-method verification. The framework complements EP17; it does not redefine regulatory LoB/LoD/LoQ.

### Discussion closing (≈80 words)

Detection-capability validation has strong conventions for **reporting** limits and weaker conventions for **designing** studies that match the claim. By linking protocol language to estimands, paths, and sample size before data collection, this work addresses a step EP17 leaves to the laboratory but rarely documents. The output is intended for method-validation planning and audit, not as a substitute for standard-mandated reporting cutoffs.

---

## Cross-references

- Manuscript Intro: [`INTRODUCTION_FULL.md`](INTRODUCTION_FULL.md)  
- Discussion: [`DISCUSSION_PRIOR_WORK.md`](DISCUSSION_PRIOR_WORK.md)  
- Chinese author notes: [`docs/methodology/研究深度阐述.md`](../docs/methodology/研究深度阐述.md)
