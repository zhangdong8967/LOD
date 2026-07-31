# Clinical Scenarios Covered by lod_guide

This document answers: **what laboratory situations exist, and does our research cover them with scripts?**

---

## 1. Two axes of clinical need

| Axis | Options |
|------|---------|
| **Decision goal** | Single-method LoD verify/establish · Compare reagents/lots · LoQ precision · Qualitative \(k/n\) |
| **Assay family** | Molecular/qPCR · Immunoassay · Clinical chemistry continuous · Hematology counts · Blood-bank multiclass |

Every lab request should map to **one primary goal (G1–G4)** and **one result type** before any formula.

---

## 2. Scenario catalogue (CS01–CS14)

| ID | Lab situation | Goal | Coverage | Script |
|----|---------------|------|----------|--------|
| CS01 | Confirm **one** reagent hit-rate LoD claim | G1 | **covered** | `examples/scenarios/cs01_verify_single_hitrate.py` |
| CS02 | Continuous LoB/LoD (chemistry-style blanks) | G1 | **covered** | `cs02_continuous_lob_lod.py` |
| CS03 | NAT / qualitative \(k/n\) design | G4 | **covered** | `cs03_qualitative_kn.py` |
| CS04 | “5/5 or 10/10 = 100% LoD?” trap | G1 | **covered** | `cs04_all_positive_trap.py` — *illustrative slice* of continuous \(p^n\) field; see [CONTINUOUS_MODELS.md](CONTINUOUS_MODELS.md) |
| CS05 | Compare kits **90% vs 80%** | G2 | **covered** | `cs05_compare_kits_90_vs_80.py` — *one point* on \(n^\star(p_A,p_B)\); full surface in continuous models |
| CS06 | Compare kits **90% vs 50%** | G2 | **covered** | `cs06_compare_kits_90_vs_50.py` — *one point* on same continuous discrimination field |
| CS07 | **Lot-to-lot** LoD check | G2 | **covered** | `cs07_lot_to_lot.py` |
| CS08 | Miss-difference (β) audit | G2 | **covered** | `cs08_miss_probability_audit.py` |
| CS09 | LoQ / functional sensitivity | G3 | **partial** | `cs09_loq_precision.py` |
| CS10 | Molecular qPCR concentration curve | G1 | **covered** | `cs10_molecular_qpcr_curve.py` |
| CS11 | Hematology low-count detection | G1 | **partial** | `cs11_hematology_low_count.py` |
| CS12 | Qualitative immunoassay cutoff | G4 | **covered** | `cs12_immunoassay_qualitative.py` |
| CS13 | Blood-bank multiclass reliability | G4 | **partial** | `cs13_blood_bank_multiclass.py` |
| CS14 | Skew/hetero → nonparametric gate | G1 | **covered** | `cs14_skew_hetero_gate.py` |
| CS15 | Specimens **below / at / above** LoD | G1/G2 | **covered** | `cs15_concentration_relative_lod.py` |

Run all:

```bash
python examples/run_clinical_scenarios.py
```

Catalogue code: `lod_guide.scenarios`.

---

## 3. Coverage verdict (honest)

| Need | Covered? |
|------|----------|
| Lab confirms **single** reagent LoD (hit-rate) | Yes (CS01 + CS04 trap) |
| Lab confirms **single** continuous LoB/LoD | Yes algorithmically (CS02, CS14); real chemistry panels still few |
| Lab compares **two kits / lots** | Yes (CS05–CS08) including miss-β |
| Large vs modest Δp (90–50 vs 90–80) | Yes |
| Qualitative \(k/n\) | Yes (CS03, CS12) |
| LoQ precision profile | **Partial** (CS09) — needs deeper EP17-style engine |
| Hematology counts | **Partial** (CS11) |
| Multiclass blood bank | **Partial** (CS13) — not classic LoD |
| Real multi-analyte clinical chemistry LoD datasets | **Gap** (data access), simulations + qPCR real data available |

**Bottom line:** The **decision scenarios labs care about most** (single verify vs multi-reagent compare, plus the all-positive and miss-β traps) are covered with dedicated scripts. Specialty LoQ/hematology/multiclass are runnable but marked partial until domain engines thicken.

---

## 4. Mapping “your words” → scenarios

| You said | Scenario |
|----------|----------|
| 确认单一试剂检测限 | CS01 / CS02 / CS03 |
| 确认不同检测试剂检测限差异 | CS05 / CS06 / CS07 / CS08 |
| 5次、10次全阳是否可靠 | CS04（举例）→ 连续场 \(p^n\)、\(L(n)\)：`CONTINUOUS_MODELS.md` |
| 80% vs 90%、50% vs 90% | CS05 / CS06（举例）→ 连续面 \(n^\star(p_A,p_B)\)、\(\beta(n;\cdot)\) |
| 找不出差异的错误结论概率 | CS08 |
| 标本低于/等于/高于检测限的影响 | CS15 |

---

## 5. Still to deepen (not missing from catalogue, but thin)

1. Full LoQ precision-profile optimizer (CS09 → covered).  
2. More real clinical chemistry continuous LoD raw data (CS02).  
3. Exact small-sample tests for G2 (Fisher/Barnard) beside pooled \(z\).  
4. Hematology protocol specifics (CS11 → covered).
