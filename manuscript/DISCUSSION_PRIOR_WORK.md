# 4. Discussion — Relation to prior work (full draft)

**Insert as:** §4.1–§4.3 within [`METHODS_BRIEF.md`](METHODS_BRIEF.md) Discussion, replacing the single “Relation to standards” paragraph.

---

## 4.1 Relation to prior work

### Standards and reviews (EP17, Armbruster)

CLSI EP17-A2 remains the **legal vocabulary** for LoB, LoD, and LoQ. Our framework treats EP17 as an **option set**, not an algorithm: parametric vs nonparametric LoB, hit-rate vs continuous paths, and precision-profile LoQ are admissible branches already enumerated in the standard. Armbruster and Pry (2008) provide the most widely cited laboratorian summary, including the practical asymmetry that manufacturers often use **~60** replicates for establishment while laboratories verify with **~20**. We do not dispute those definitions or recommended verification *forms*; we argue that **replicate number and path** must be justified for the **detection estimand actually claimed** (verify single-method LoD vs discriminate two hit rates vs qualitative \(k/n\)). EP17 tells laboratories what may be estimated; `lod_guide` adds **when** each LoD branch is statistically defensible and **how large** \(n\) must be under an explicit loss. LoQ precision planning (G3) remains in the software but is not part of this brief’s primary claims.

### Estimation methods (Linnet, Galitzine, commercial tools)

Linnet and Kondratovich (2004) solved an **estimation** problem under non-Gaussian blanks—a direct intellectual ancestor of our S4b nonparametric route and S2 skew gate. Their sample-size material targets **establishment** confidence intervals, not powered **comparative** verification. Galitzine et al. (2018) show that low-end intensity plateaus in multiplex MS can materially shift LoB/LoD; our tier-A CPTAC illustration adopts that ecosystem while **not** extrapolating MS nonlinear fits to routine analyzer chemistry. Commercial EP17 modules (e.g., Analyse-it) and Bioconductor MSstatsLOBD implement **single-path calculators** with workbook-friendly output; they do not enforce estimand locking, mismatch penalties in \(L\), or exact small-sample confirmation at the end of the pipeline. Positioning: we are **orchestration + design theory**, not a replacement LoD estimator.

### Verification probability (Kondratovich and Linnet, 2017)

The JALM 2017 paper is the strongest direct precedent for criticizing blind **\(n=20\)** verification: pass probability varies with concentration ratio and replicate count under EP17 rules. We extend that line in three ways: (**i**) **G2** two-proportion discrimination (e.g., 90% vs 80%) with Fleiss–Chow planning and exact Fisher/Boschloo confirmation; (**ii**) quantification of **asymptotic vs exact** power gap (P8); (**iii**) embedding verification into the multi-term loss \(L\) alongside mismatch and design-effect penalties. Their Poisson-binomial PCR structure is complementary; our G2 engine is **estimand-generic** for binomial hit-rate comparisons.

### Contemporary validation literature (Block B screen)

Our July 2026 PubMed screen of 200 “LoD + sample size/verification” hits is consistent with a **reporting** culture: after excluding 149 non-clinical-lab records, remaining validation papers typically publish LoB/LoD/LoQ **point estimates** and CLSI/ISO checklists (immunoassay, molecular POCT, proteomics RMP) without prospective **power** for comparative LoD claims. Recent examples include neurofilament light chain immunoassay verification (J Appl Lab Med, 2026), apolipoprotein reference measurement procedures (*Clin Chem*, 2026), and influenza POCT LOD with parallel clinical specimens (CCLM, 2026). Those papers are valuable **practice snapshots**; they should not be mistaken for evidence that folklore \(n\) is powered for **all** estimands. Our tier-A meta-summary (Table 7) serves a different purpose: illustrating **gate behavior** on public deposits, not benchmarking commercial assays.

### General biostatistics (Fleiss, exact tests)

Two-proportion sample size and exact conditional tests are classical (Fleiss et al., 2003; Boschloo, 1970). Our contribution is **domain operationalization**: binding these methods to G2 inside S0–S7, demonstrating the **folklore failure mode** on LoD-relevant effect sizes, and publishing machine-checkable certificates (P8, P18) tied to laboratory audit JSON—not re-deriving binomial theory.

---

## 4.2 What this brief establishes

For EP17-class workflows, LoD verification can be planned prospectively: diagnostic gates restrict parametric LoB to admissible blank behavior; sample size can be tied to the estimand stated in the protocol; and small-sample confirmation can use exact methods where asymptotic planning overstates power. Numerically, a folklore \(n=20\) design for discriminating 90% vs 80% detection carries about **3.9×** the equal-weight decision risk of a powered plan; all-positive runs leave substantial uncertainty on a 95% LoD claim; and tier-A continuous blanks often fail parametric candidacy under preset S2 thresholds.

---

## 4.3 Limitations (read before interpreting Results)

We state limitations explicitly because several Results figures are easy to over-read.

**No prospective multi-lab case study.** This brief does not report a new partner-laboratory validation in which a protocol was rewritten using S0–S7 and then executed. Tier-A public deposits illustrate **diagnostic gate behavior** on LoD-relevant archived data; they do **not** certify the algorithm across all panels or IFU wordings. LoQ precision profiles in tier-A deposits are supplementary only (see scope note in [`LOD_SCOPE_VS_LOQ.md`](../docs/methodology/LOD_SCOPE_VS_LOQ.md)).

**Scarce routine blank–LoD raw data.** Public replicate-level blank and low-concentration series for mainstream electrolyte/enzyme analyzers remain limited. Carobene multi-lab EQA material supports **precision and design-effect** arguments; CPTAC proteomics supports **blank–LoB under targeted MS**—neither substitutes for routine analyzer blank–LoD archives. Claims in this brief are bounded accordingly.

**Decision risk weights are not clinical utilities.** Default equal weights in \(L\) make folklore and powered designs **comparable on a stated scale**; they do not represent elicited patient-harm utilities. Sensitivity analyses are provided; laboratories should treat \(w\) as audit parameters tied to local tolerance for false alarm versus missed difference.

**Exact versus asymptotic planning at large \(n\).** For G2 at \(n^\star \approx 199\), confirmation uses asymptotic power at the design point; exact enumeration at that \(n\) is documented in planning JSON but is not the primary confirmation workflow for every scenario. Small-\(n\) folklore designs are where exact Fisher/Boschloo gaps matter most (P8, P18).

**Tier firewall.** Tier C (synthetic EP17 demos) and tier S (simulation stress DGPs) demonstrate mechanisms and engine consistency; they must **not** be pooled with tier A as “multi-assay clinical validation.”

**Regulatory scope.** We do **not** replace EP17, YY/T, WS/T, or manufacturer IFU. Legal LoB/LoD/LoQ definitions and reporting cutoffs remain with standards, manufacturers, and local validation governance.

---

## 4.4 What this brief does not claim (summary)

- Prospective multi-lab LoD claim verification on all measurands.  
- Optimality of default weights in \(L\).  
- That tier C/S constitute clinical validation.  
- That equal-weight \(L\) replaces laboratory risk management or accreditation checklists.

---

## 4.5 Relation to standards and publication scope

The `lod_guide` package **complements** EP17: legal LoB/LoD/LoQ numbers and reporting cutoffs remain governed by standards, manufacturers, and local validation governance. This draft is sized as a **methods / technical brief** with online Supplement (`paper_artifacts/`). A full research article would add a prospective partner-laboratory case or expanded routine-chemistry blank–LoD raw and journal-specific figure accessibility review.

---

## 4.6 Broader significance

Validation reports usually document LoB and LoD well; they less often document whether **replicate number and statistical path** matched the **detection claim** in the protocol—equivalence of two kits at the LoD concentration, confirmation of a 95% hit rate, or a qualitative \(k/n\) rule are different requirements (LoQ precision targets, when claimed, are a separate estimand and are out of scope for this brief). EP17’s pluralism is appropriate for diverse measurands, but pluralism without a documented design step collapses in practice to a single habit (\(n \approx 20\), default parametric LoB). This brief argues that step should appear explicitly in method-validation planning: state the estimand, justify the path after blank diagnostics, and plan \(n\) from operating characteristics before interpreting pass/fail. The accompanying software is a planning and audit aid inside EP17; it does not replace standard-mandated definitions or reporting cutoffs.

---

## Discussion cross-reference table

| Prior work | Overlap | Our delta |
|------------|---------|-----------|
| EP17-A2 | Definitions, paths | S0–S7 + estimand + \(L\) |
| Armbruster 2008 | Educator summary | Powered design for non-verification estimands |
| Linnet 2004 | Nonparametric LoD | S2 gate + G2/G1 engines + audit |
| Kondratovich 2017 | Verification pass P | G2 discrimination + exact Fisher + P8/P18 |
| Galitzine 2018 | MS LoB/LoD | Tier-A only; chemistry routed separately |
| Block B validation papers | CLSI reporting | Prospective \(n\) for comparators (gap filled) |
| Analyse-it / MSstatsLOBD | Single-path software | Cross-estimand orchestration |
