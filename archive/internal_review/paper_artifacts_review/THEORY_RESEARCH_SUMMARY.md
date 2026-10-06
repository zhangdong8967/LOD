# Theory research summary

**Generated:** 2026-08-10T07:14:46.568851+00:00
**Certificate source:** `/Users/zhangdong/PycharmProjects/PythonProject/LOD/data/audit/theory_verification_latest.json`

## Layer counts

- **Layer A:** 7/7 passed
- **Layer B:** 3/3 passed
- **Layer C:** 12/12 passed

## Verification defects (main text D1–D3)

### D1 — Estimand conflation (E3 vs E1 vs E2)

E3 pass, E1 confirmation, and E2 discrimination are distinct acceptance events; filing one as evidence for another mixes estimands.

Certificates: P7_all_positive_trap

### D2 — Small-n operating-characteristic gap (design vs confirmation)

Asymptotic pooled-z power can exceed exact Fisher power at folklore n; S5 design must be followed by S6 exact confirmation.

Certificates: P8_exact_vs_asymptotic_gap

### D3 — Pareto-inadmissible folklore designs (E2)

Folklore n=20 can be strictly Pareto-dominated on the exact Fisher (Type I, power) plane by powered n* for prespecified (p_A, p_B).

Certificates: P18_folklore_pareto_dominated

## All certificates

- `[PASS]` **P1_saturation** (layer A): lim (φ_n(p_A)-φ_n(p_B))=0; comparative use of φ_n is information-destroying.
- `[PASS]` **P2_binomial_reliability** (layer A): P(S_n>=1)=1-(1-p)^n.
- `[PASS]` **P5_parametric_lob_inconsistency** (layer A): For Exp(1), mean+z·sd ≠ F^{-1}(1-α); parametric LoB miscalibrated.
- `[PASS]` **P6_ovl_separation** (layer A): Overlap coefficient of Binomial sampling laws decreases as n increases (separation).
- `[PASS]` **P7_all_positive_trap** (layer A): n/n successes do not certify a high LoD claim: CP lower = α^(1/n) << claim while p^n can be large.
- `[PASS]` **P15_lod_identifiability** (layer A): LoD concentration is identifiable when Fisher rank=2 and ≥2 interior hit-rate levels exist.
- `[PASS]` **P16_saturation_trap** (layer A): Saturation/floor plates yield non-identifiable log10(LoD) despite large total n.
- `[PASS]` **P8_exact_vs_asymptotic_gap** (layer B): Berry–Esseen scale + enumerated certificate for asymptotic-over-Fisher gap at folklore n.
- `[PASS]` **P18_folklore_pareto_dominated** (layer B): Folklore n=20 is locally Pareto-dominated by n' in {21,…,35} (headline) and by powered n* under exact Fisher OC.
- `[PASS]` **P17_sample_split_remedy** (layer B): Sample splitting restores marginal Type I ≤ α + ε under skew gated LoB.
- `[PASS]` **P3_two_proportion_power** (layer C): Fleiss–Chow n yields asymptotic and MC power near target.
- `[PASS]` **P4_design_effect** (layer C): DE=1+(m-1)ρ under compound symmetry.
- `[PASS]` **P9_holm_fwer** (layer C): Holm–Bonferroni keeps FWER near/below α under a global null (MC sketch).
- `[PASS]` **P10_weight_scale_invariance** (layer C): Decision loss L is homogeneous of degree 1 in the weight vector.
- `[PASS]` **P11_tobit_uncensored_agreement** (layer C): Tobit Normal LoB agrees with mean+z·SD when nothing is left-censored.
- `[PASS]` **P12_c_optimal_efficiency** (layer C): Locally c-optimal multi-level design has higher asymptotic efficiency than equal log/equal n.
- `[PASS]` **P13_minimax_robust_design** (layer C): Minimax slope-robust design has lower worst-case SE(log10 LoD) than equal log/equal n.
- `[PASS]` **P14_efficiency_ratio** (layer C): Asymptotic c-efficiency (variance ratio) exceeds 1 for reference vs c-optimal design.
- `[PASS]` **P17_gated_lob_inflation** (layer C): When S2 selects parametric LoB on Gamma blanks, exceedance can exceed nominal α (MC).
- `[PASS]` **C_optimal_equivalence** (layer C): Locally c-optimal LoD design satisfies the General Equivalence Theorem (numerical check).
- `[PASS]` **P17_selective_inflation** (layer C): Conditional Type I | G=1 can exceed nominal α under skew when S2 selects parametric LoB.
- `[PASS]` **P13_minimax_formal** (layer C): Minimax over B=[0.5,1.5]·β_plan beats folklore equal-log design.