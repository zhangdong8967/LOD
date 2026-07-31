# Cover letter (draft)

**Journal:** *Clinical Chemistry* — Methods / Technical Brief  
**Title:** Assumption-Gated Decision Theory for Clinical Limit-of-Detection Evaluation  
**Authors:** [Insert]  
**Corresponding author:** [Insert]

---

Dear Editor,

We submit a methods brief on **prospective replicate planning for LoD verification** (detection claims G1, G2, G4). We do **not** propose new regulatory definitions of LoB, LoD, or LoQ, and we do **not** replace CLSI EP17-A2. **LoB and LoQ are outside the research scope** of this manuscript; the question we address is how many replicates support a stated **detection** claim—for example, equivalence of two lots at the LoD concentration versus confirmation of a 95% hit-rate benchmark.

**Why this belongs in *Clinical Chemistry*.** Detection capability sits at the boundary between analytical validation and reported patient results near zero. The journal’s readership already uses EP17; the practical failure mode we document is familiar—underpowered “no difference” conclusions when two reagents or lots are compared at low concentration, and over-interpretation of all-positive runs for single-method LoD claims. We quantify one comparative scenario that laboratorians will recognize: if true hit rates at the LoD concentration are 90% versus 80%, a folklore design with \(n = 20\) per arm has exact Fisher power **0.07**, whereas 80% power requires **\(n \approx 199\)** per arm (Introduction Box 1; Results Table 3). That gap is not a criticism of EP17; it arises when comparative claims are stated in prose but not in sample-size planning.

**Relation to prior work.** Linnet and Kondratovich (2004) address LoD **estimation** under non-Gaussian blanks; Kondratovich and Linnet (2017) model **single-method** verification pass probability for molecular assays—the closest precedent to our critique of fixed \(n\). We extend that line to **two-proportion (G2)** discrimination, diagnostic gating of parametric LoB, exact Fisher/Boschloo confirmation, and a transparent multi-component decision risk for comparing folklore versus powered designs. Commercial EP17 tools compute LoB/LoD/LoQ on a chosen path; they do not enforce estimand-specific planning before data collection.

**Evidence and scope (stated upfront).** Primary illustrations use **nine tier-A public deposits** (qPCR, immunoassay blank–LoB, probit, multi-lab chemistry precision, proteomics blank–LoB, radioimmuno, RMN, etc.) to show gate behavior—not to benchmark commercial assays. Synthetic EP17 demos and simulation stress tests are tiered separately and are **not** presented as multi-assay clinical validation. Raw blank–LoD archives for routine electrolyte/enzyme analyzers remain limited; we say so explicitly in the Discussion. A full research article with a prospective partner-laboratory case is a logical next step; this submission is intentionally sized as a **methods brief** with an online Supplement (`paper_artifacts/`) and reproducible code (`lod_guide`).

**Availability.** All figures, tables, seeds, and audit JSON are rebuildable via `make paper-artifacts`. Theory certificates P1–P18 are checked by `verify_all_propositions()`.

We believe the brief will interest clinical chemists who write or review method-validation protocols, and biostatisticians who advise laboratories on EP17 workflows. Thank you for your consideration.

Sincerely,

[Name]  
[Affiliation]  
[Email]

---

## Editor checklist (internal)

| Item | Where addressed |
|------|-----------------|
| Narrow claim, no EP17 overreach | Paragraph 1 |
| Concrete motivating example | Paragraph 2 (90% vs 80%, n=20 vs 199) |
| Fair citation of Linnet / Kondratovich | Paragraph 3 |
| Limitations before reviewer asks | Paragraph 4 |
| Reproducibility | Paragraph 5 |
| Brief vs full paper scope | Paragraph 4 |

## Optional reviewer preemption (one sentence each)

- **“Just sample-size software.”** → Estimand lock and diagnostic gates are part of the protocol, not a calculator after the fact.  
- **“Fleiss already covers two proportions.”** → True; we bind it to LoD verification claims inside S0–S7 and show folklore failure at LoD-relevant effect sizes.  
- **“No prospective lab data.”** → Acknowledged; tier-A public deposits illustrate gates; prospective case deferred to full article.
