# Research scope (locked): LoD replicate planning

**Core question:** Under stated conditions (estimand, effect size, α, β), **how many replicates** are required to support a **LoD verification claim**?

**Not the research question:**

| Topic | EP17 role | This project |
|-------|-----------|--------------|
| **LoB** (limit of blank) | Defines blank noise; enters some **continuous** LoD formulas | **Out of scope** as an object of study. Blank handling in code exists only where EP17 continuous workflows require it; we do not claim new LoB methodology. |
| **LoQ** (limit of quantitation) | Quantitative reporting limit (CV%, precision profile) | **Out of scope.** LoQ remains optional software; not in manuscript claims. |
| **LoD** (limit of detection) | Detection / hit-rate at low concentration | **Primary focus.** |

---

## 1. What “LoD” means here

We mean **detection-limit verification**, not quantitation-limit verification:

- **E1:** Does this method detect at rate ≥ \(p_0\) at concentration \(c^\star\)? (e.g., verify 95% LoD claim)  
- **E2:** Do two lots/reagents differ in detection rate at \(c^\star\)? (e.g., “equivalent at LoD”)  
- **E3:** Does a qualitative \(k/n\) rule hold at the detection limit?

Result types: **binary / hit-rate** (PCR, POCT, qualitative immuno) are the **primary** use cases. Continuous blank–signal LoD paths (EP17 Appendix A style) are **EP17 context**, not the thesis contribution.

---

## 2. Why LoB and LoQ appeared in the repo

- **EP17** groups LoB, LoD, LoQ in one document; early `lod_guide` mirrored the full menu.  
- **Public data:** some tier-A deposits are precision/blank-heavy (radioimmuno, estradiol, CPTAC); they were used for gate demos, not because LoB/LoQ is the research target.  
- **Software completeness:** S2–S4 LoB gates and LoQ branch engine remain for users running full EP17 workflows.

**Manuscript rule:** Main text, abstract, cover letter, and Box 1 discuss **LoD sample size and operating characteristics only.**

---

## 3. Primary vs supplementary content

| Content | Status |
|---------|--------|
| E1 all-positive trap (P7) | **Main** |
| E2 folklore n=20 vs powered n* (Box 1, Fig 2–3) | **Main** |
| E3 k/n vs E1 mix-up | **Main** (text) |
| Exact Fisher / Boschloo for hit-rate LoD | **Main** |
| Probit / multilevel hit-rate design (P12–P16) | **Main** (LoD concentration planning) |
| Parametric LoB mismatch (P5), P17 sample-split | **Supplement** or one sentence (“continuous EP17 path only”) |
| Tier-A blank–LoB gate tables | **Supplement**; not headline Results |
| LoQ profiles (radioimmuno, troponin) | **Supplement only** |
| Fig 5 | **LoD-focused:** qPCR hit-rate + E1/E2/E3 planned \(n\) | **Main** |
| Fig 1 | LoD pipeline S0→S1→S5→S6→S7; E1/E2/E3 only | **Main** |
| Fig 4B | Exact Fisher power folklore vs powered | **Main** |
| Fig S-LoB | P17 LoB sample-split (was Fig 4B) | **Supplement** |

---

## 7. Figure LoD 化（2026-07-30）

- **Fig 1** (`flowchart_fig1.py`, `Fig1_pipeline.tex`): estimand 仅 E1/E2/E3；主路径 S0→S1→S5→S6→S7；S2–S4 LoB 标注为 Optional Supplement。  
- **Fig 4B**: 精确 Fisher 功效（\(n=20\) vs \(n^\star\)，90% vs 80%）；原 P17 LoB 柱图 → `FigS_lob_p17_split`。  
- **Fig 5**: tier-A qPCR 检出率 + planned \(n\)（前一轮已完成）。

---

## 4. One-sentence thesis (Chinese)

**在明确验证目标（E1/E2/E3）和效应量的条件下，LoD 验证需要多少次重复、用什么精确检验——而不是重新定义 LoB 或 LoQ。**

## 5. One-sentence thesis (English)

**We specify prospective replicate number and confirmation tests for LoD verification claims (E1, E2, E3); LoB and LoQ are outside the research scope though optional EP17 branches remain in software.**

---

## 6. Cross-references

- Supersedes emphasis in [`LOD_SCOPE_VS_LOQ.md`](LOD_SCOPE_VS_LOQ.md) (LoQ section still valid; LoB now explicitly out).  
- Manuscript: [`METHODS_BRIEF.md`](../../manuscript/METHODS_BRIEF.md), [`COVER_LETTER.md`](../../manuscript/COVER_LETTER.md).
