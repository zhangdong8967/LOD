# 1. Introduction (full draft)

**Manuscript:** *Assumption-Gated Decision Theory for Clinical Limit-of-Detection Evaluation*  
**Status:** Draft for *Clinical Chemistry* **Article** (methods)  
**Companion:** [`METHODS_BRIEF.md`](METHODS_BRIEF.md); [`SIGNIFICANCE_AND_DEPTH.md`](SIGNIFICANCE_AND_DEPTH.md) (author argument map)

---

## 1.1 Background

Clinical laboratories must verify **limit of detection (LoD)**—whether an analyte is detected near zero at a stated concentration—for qualitative PCR, POCT, and hit-rate immunoassays. CLSI EP17-A2 also defines limit of blank (LoB) and limit of quantitation (LoQ); **this brief addresses LoD verification design only**—how many replicates support a detection claim under estimands E1, E2, or E3 (see [`docs/methodology/LOD_RESEARCH_SCOPE.md`](../docs/methodology/LOD_RESEARCH_SCOPE.md)). LoB estimation and LoQ precision planning are optional EP17 branches in the software but are not the research focus here.

Most local LoD verification SOPs nevertheless fix about **20 replicates** and informal pass rules such as **all positives** or **non-significant comparison = equivalent**, without deriving \(n\) from the **detection claim** in the protocol.

That omission is consequential. A validation report may conclude that a new lot “matches” a reference kit, that a manufacturer’s 95% LoD claim is verified, or that a POCT device is “equivalent” at low concentration. Each statement corresponds to a different statistical question and therefore to a different sample-size requirement. When the question is unstated and \(n\) is fixed by tradition, the report can look complete while the study cannot support the inference drawn.

---

## 1.2 A design step EP17 does not spell out

EP17 and prior work address **what** LoD means and **how to estimate** it after data are collected (Linnet and Kondratovich, 2004; Vaks et al., 2016 for single-method verification pass probability). What remains informal is **prospective replicate planning**: given the detection claim in the protocol, how many replicates are required, and what operating characteristics apply?

We treat that missing step as the object of study. Before any LoB/LoD calculation, the laboratory must specify one primary **estimand**—what quantity the study is meant to support:

| ID | Typical protocol language | Statistical target |
|----|---------------------------|-------------------|
| E1 | “Verify manufacturer 95% LoD at \(c^\star\)” | Hit rate \(p(c^\star)\) vs claim \(p_0\) |
| E2 | “New lot equivalent to reference at LoD concentration” | Difference \(p_A(c^\star)-p_B(c^\star)\) |
| E3 | “At least 19/20 positives at detection limit” | Binomial \(k/n\) reliability |

*(LoQ branch / precision-at-low-level is implemented in the software for EP17 completeness but is not a focus of this brief; LoQ concerns quantitative reporting, not detection-limit verification.)*

Only after the estimand is fixed does sample-size planning for that **detection claim** become meaningful. Mixing estimands—for example, using a 19/20 qualitative rule to support a two-arm equivalence statement—invalidates the inference even when the bench work is correct.

---

## 1.3 Illustrative protocol (lot comparison at LoD)

Consider a validation protocol that requires a new reagent **lot B** to be “**equivalent**” to **reference lot A** at the manufacturer LoD concentration \(c^\star\) (e.g., 5 pg/mL for a qualitative immunoassay). That sentence is **comparative**: it targets the difference in hit rates \(p_A(c^\star) - p_B(c^\star)\)—estimand **E2**—not whether either lot alone meets a 95% benchmark (**E1**) or a 19/20 qualitative rule (**E3**).

A typical SOP nevertheless fixes **\(n = 20\)** replicates per arm and treats a non-significant two-sided test at α = 0.05 as evidence of equivalence. Suppose the true detection rates at \(c^\star\) are **90%** for lot A and **80%** for lot B—a 10-percentage-point sensitivity gap that is plausible in lot-to-lot work. Exact Fisher power for that contrast at \(n = 20\) per arm is **0.07**; the study has roughly a **93%** chance of **not** detecting the difference it was written to adjudicate. For 80% power at the same α, Fleiss–Chow planning requires **\(n \approx 199\)** per arm (Table 3; `decision_risk.json`). A “no difference” conclusion after 20 replicates therefore usually means **the design was too small**, not that the lots are equivalent.

On a dense \((p_A,p_B)\) grid at \(n=20\), **61%** of valid comparison cells have miss \(\beta>0.8\) under exact Fisher (1225 cells; Table 3). Eight reference pairs show median \(L_\mathrm{folk}/L_\mathrm{pow}\approx3.9\) (Table 3). The failure is not bench technique; it is that **replicate number was never derived from the claim in the protocol**. Full step-by-step narrative: [`WORKED_EXAMPLE.md`](WORKED_EXAMPLE.md) (Box 1).

---

## 1.4 Related work

**Standards and reviews.** EP17-A2 and Armbruster and Pry (2008) remain the definitional references laboratorians use. Armbruster noted the practical gap between manufacturer establishment studies (often on the order of 60 replicates) and laboratory verification (often about 20). That asymmetry is descriptive, not a powered design rule for every claim type.

**Estimation under misspecification.** Linnet and Kondratovich (2004) showed that partly nonparametric LoB combined with a low-level SD term can yield robust LoD estimates when Gaussian blank assumptions fail. Galitzine et al. (2018) demonstrated that nonlinear low-end response in multiplex mass spectrometry can shift LoB/LoD by substantial margins. Commercial EP17 software (e.g., Analyse-it; MSstatsLOBD) implements individual paths well but typically **after** the user has already chosen path and \(n\).

**Verification probability.** Vaks et al. (2016) modeled the probability of passing EP17-style LoD verification as a function of replicate number and concentration relative to true LoD—direct evidence that pass probability is not well served by a fixed \(n=20\) for **single-method** confirmation (extending Linnet and Kondratovich, 2004). Their framework does not cover **two-arm discrimination** between reagents or lots, diagnostic gating of parametric LoB, or exact small-sample confirmation at the end of planning.

**Recent validation literature.** A structured PubMed screen (Block B, July 2026; details in Supplement) found that most clinical-laboratory LoD papers report validated limits after CLSI workflows; few derive prospective sample size for comparative sensitivity claims. The gap is routine in publication, not an indictment of any single study.

---

## 1.5 Two further failures of fixed \(n=20\) (E1, E3)

Section 1.3 shows the E2 failure. Two related patterns affect **single-method** LoD verification:

**All-positive pass rules (E1).** For a 95% LoD claim, observing 20/20 positives is consistent with \(p=0.90\): \(0.90^{20} \approx 0.12\). One-sided Clopper–Pearson lower bounds at \(n=20\) remain far below 0.95 (Proposition P7; Fig S2A).

**Saturated reliability metrics (E2/E3 confusion).** Using \(1-(1-p)^n\) (“at least one hit”) to compare reagents saturates as \(n\) grows and must not substitute for comparing hit rates \(\hat p\) (Proposition P1; Fig 1B–C).

---

## 1.6 Present work

We provide a locked **S0–S7 pipeline** for **LoD verification design**: lock estimand E1, E2, or E3; plan \(n\) from operating characteristics (S5); confirm at small \(n\) with exact binomial, Fisher, or Boschloo methods (Methods §2.3); emit a structured planning report (S6–S7). Continuous EP17 paths and LoB diagnostics remain in the software for users who need them but are not central to this brief.

The logic is: **(i)** lock estimand; **(ii)** plan \(n\) for Type I / Type II at the stated detection contrast; **(iii)** confirm with exact methods where normal approximations fail; **(iv)** document assumptions and tier of evidence.

Planning uses a multi-component **decision risk**
\[
L = w_I\cdot\mathrm{TypeI} + w_{II}\cdot\beta + w_M\cdot\mathbf{1}\{\text{parametric mismatch}\} + w_C\cdot(\mathrm{DE}-1),
\]
with default equal weights and published sensitivity analyses. The purpose of \(L\) is not to assert a clinically optimal utility function—it is to make the error-rate trade-offs implicit in folklore SOPs **explicit and comparable** across designs.

Analytic results (P1, P7, P8, P18, and probit design P12–P16) formalize LoD-specific failure modes and planning surfaces. Empirical illustrations use **nine tier-A** hit-rate / LoD-relevant deposits (qPCR, probit, RMN, etc.); LoB-only and LoQ-only demos are supplementary (Methods §2.4; **Table 7**). Full E2 grids at \(n=20\) are in **Table 3** CSV extensions.

**Scope.** We **complement** EP17-class options and challenge underpowered local SOPs; we **do not** supersede EP17, manufacturer IFU, or regulatory reporting cutoffs.

---

## 1.7 Organization

Section 2 defines estimands, the S0–S7 gate, decision risk, design surfaces, exact confirmation, evidence tiers, and software. Section 3 reports folklore risk quantification, tier-A LoD deposit summaries, and theory certificates. Main-text **Fig 1** (panels A–D) presents the prospective protocol and answers why folklore \(n=20\) fails, how many replicates are required, and how hit rates map to \(c/\mathrm{LoD}_{95}\). Supplement tables and grid CSVs; LoB/LoQ and sensitivity JSON remain in the Supplement.

---

## Introduction references (Vancouver draft)

1. Clinical and Laboratory Standards Institute. Evaluation of Detection Capability for Clinical Laboratory Measurement Procedures; EP17-A2. Wayne, PA: CLSI; 2012.  
2. Armbruster DA, Pry T. Limit of blank, limit of detection and limit of quantitation. *Clin Biochem Rev*. 2008;29 Suppl 1:S49-S52.  
3. Linnet K, Kondratovich M. Partly nonparametric approach for determining the limit of detection. *Clin Chem*. 2004;50(4):732-740.  
4. Vaks JE, et al. Verification of claimed limit of detection in molecular diagnostics. *J Appl Lab Med*. 2016;1(3):260-270. doi:10.1373/jalm.2016.020735.  
5. Galitzine C, et al. Nonlinear regression improves accuracy of characterization of multiplexed mass spectrometric assays. *Mol Cell Proteomics*. 2018;17(5):913-924.  
6. Fleiss JL, Levin B, Paik MC. *Statistical Methods for Rates and Proportions*. 3rd ed. Hoboken, NJ: Wiley; 2003.  
7. Ray S, et al. Performance evaluation of an automated neurofilament light chain immunoassay. *J Appl Lab Med*. 2026. doi:10.1093/jalm/jfag041.  
8. Diederiks NM, et al. Development and analytical validation of a multiplex LC-MRM-MS-based RMP for apolipoprotein A-I and B. *Clin Chem*. 2026. doi:10.1093/clinchem/hvag041.
