# Scope note: LoQ out of scope; LoB out of scope — see [`LOD_RESEARCH_SCOPE.md`](LOD_RESEARCH_SCOPE.md).

---

## 1. Why the distinction matters

| Term | Question | Typical assay | Our focus? |
|------|----------|---------------|----------|
| **LoB** | Does blank signal exceed noise? | All | **Yes** (path gating) |
| **LoD** | Is analyte **detected** near zero? | Qualitative PCR, POCT, immuno hit-rate, continuous exceedance | **Yes (core)** |
| **LoQ** | Is a **numeric result** trustworthy at low concentration? | Quantitative chemistry, immuno quant, MS quant | **No (this brief)** |

LoD answers **presence / detection** (binary or hit-rate at \(c^\star\)).  
LoQ answers **precision of quantitation** (CV%, precision profile, functional sensitivity).

They share EP17 vocabulary but **different estimands, different pass rules, different sample-size logic**. A laboratory validating a **qualitative** or **detection-limit** claim does not need LoQ planning in the same protocol episode.

---

## 2. Why LoQ / LoQ appeared in the codebase (historical)

1. **EP17 bundles** LoB, LoD, and LoQ under “detection capability evaluation.” Early `lod_guide` was scoped as full EP17 orchestration.  
2. **Tier-A public data:** radioimmuno and troponin deposits include **precision tables**, so LoQ was used as an empirical anchor (Fig 5, Table 2).  
3. **Pipeline symmetry:** S5 already had a CV / CI half-width engine; LoQ was wired in for completeness.

None of these make LoQ the **scientific question** of this project. They are implementation and data-availability artifacts.

---

## 3. Primary estimands for *this* work (manuscript + thesis)

| ID | Role | Include in main narrative |
|----|------|---------------------------|
| **E1** | Single-method LoD / hit-rate verification | **Yes** |
| **E2** | Compare lots/reagents at \(c^\star\) | **Yes** |
| **E3** | Qualitative \(k/n\) at detection limit | **Yes** |
| **LoQ branch** | LoQ / precision (CV%) | **Software only; Supplement or omit from brief** |

**Continuous paths:** LoB gating + LoD-style exceedance / low-level behavior support **LoD establishment**, not LoQ precision profiles, unless the protocol explicitly claims quantitation limit.

---

## 4. Manuscript consequences (applied)

- **Title / abstract / Introduction:** Lead with **LoD verification design** (LoB gating, E1/E2/E3). Mention LoQ only as “EP17 also defines LoQ; out of scope here” or omit.  
- **Main Results:** Folklore failures (E2 Box 1, E1 all-positive, parametric LoB) — all LoD-centric.  
- **Fig 5 (planned change):** Replace LoQ precision profile as **main-text tier-A anchor** with a **LoD-relevant** tier-A panel (blank–LoB gate, qPCR hit-rate, or probit near LoD). Move radioimmuno LoQ to **Supplement Fig S1** (already tier-C troponin LoQ demo exists).  
- **Table 2 (LoQ):** Supplement only for this brief.  
- **Code:** Keep `Goal.LOQ_PRECISION` and `s5` LoQ engine — no breaking change; document as optional EP17 branch.

---

## 5. One-sentence scope for cover letter / rebuttal

> This brief addresses **prospective design for LoB/LoD verification** (detection claims: E1, E2, E3). **LoQ precision planning (LoQ)** is implemented in the software for EP17 completeness but is **not** part of the detection-limit research question or the primary empirical claims.

---

## 6. Chinese summary (组内口径)

**我们关注的是「能不能检出」（检测下限 LoD），不是「低浓度定量准不准」（LoQ）。**  
LoQ/LoQ 留在软件里是因为 EP17 全家桶和公开数据里有精度表，不应写进本文立意。主文算例、失败模式、Fig 2–4 全部围绕 LoD；LoQ 图/表降级到 Supplement 或后续定量专项稿。
