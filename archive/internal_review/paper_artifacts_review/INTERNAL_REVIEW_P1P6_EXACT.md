# Internal statistical review memo

**Scope.** Machine certificates **P1–P18** (plus supplementary results), verification defects **D1–D3** (Supplement §S2b), and exact vs asymptotic discrimination power (Table 3–4).

## Verification defects (D1–D3)

### D1 — Estimand conflation (E3 vs E1 vs E2)

E3 pass, E1 confirmation, and E2 discrimination are distinct acceptance events; filing one as evidence for another mixes estimands.

Certificates: P7_all_positive_trap

### D2 — Small-n operating-characteristic gap (design vs confirmation)

Asymptotic pooled-z power can exceed exact Fisher power at folklore n; S5 design must be followed by S6 exact confirmation.

Certificates: P8_exact_vs_asymptotic_gap

### D3 — Pareto-inadmissible folklore designs (E2)

Folklore n=20 can be strictly Pareto-dominated on the exact Fisher (Type I, power) plane by powered n* for prespecified (p_A, p_B).

Certificates: P18_folklore_pareto_dominated

## Verdict on propositions

- Certificates run: **22**; failures: **0**.
- `P1_saturation` — **PASS**: lim (φ_n(p_A)-φ_n(p_B))=0; comparative use of φ_n is information-destroying.
- `P2_binomial_reliability` — **PASS**: P(S_n>=1)=1-(1-p)^n.
- `P5_parametric_lob_inconsistency` — **PASS**: For Exp(1), mean+z·sd ≠ F^{-1}(1-α); parametric LoB miscalibrated.
- `P6_ovl_separation` — **PASS**: Overlap coefficient of Binomial sampling laws decreases as n increases (separation).
- `P7_all_positive_trap` — **PASS**: n/n successes do not certify a high LoD claim: CP lower = α^(1/n) << claim while p^n can be large.
- `P15_lod_identifiability` — **PASS**: LoD concentration is identifiable when Fisher rank=2 and ≥2 interior hit-rate levels exist.
- `P16_saturation_trap` — **PASS**: Saturation/floor plates yield non-identifiable log10(LoD) despite large total n.
- `P8_exact_vs_asymptotic_gap` — **PASS**: Berry–Esseen scale + enumerated certificate for asymptotic-over-Fisher gap at folklore n.
- `P18_folklore_pareto_dominated` — **PASS**: Folklore n=20 is locally Pareto-dominated by n' in {21,…,35} (headline) and by powered n* under exact Fisher OC.
- `P17_sample_split_remedy` — **PASS**: Sample splitting restores marginal Type I ≤ α + ε under skew gated LoB.
- `P3_two_proportion_power` — **PASS**: Fleiss–Chow n yields asymptotic and MC power near target.
- `P4_design_effect` — **PASS**: DE=1+(m-1)ρ under compound symmetry.
- `P9_holm_fwer` — **PASS**: Holm–Bonferroni keeps FWER near/below α under a global null (MC sketch).
- `P10_weight_scale_invariance` — **PASS**: Decision loss L is homogeneous of degree 1 in the weight vector.
- `P11_tobit_uncensored_agreement` — **PASS**: Tobit Normal LoB agrees with mean+z·SD when nothing is left-censored.
- `P12_c_optimal_efficiency` — **PASS**: Locally c-optimal multi-level design has higher asymptotic efficiency than equal log/equal n.
- `P13_minimax_robust_design` — **PASS**: Minimax slope-robust design has lower worst-case SE(log10 LoD) than equal log/equal n.
- `P14_efficiency_ratio` — **PASS**: Asymptotic c-efficiency (variance ratio) exceeds 1 for reference vs c-optimal design.
- `P17_gated_lob_inflation` — **PASS**: When S2 selects parametric LoB on Gamma blanks, exceedance can exceed nominal α (MC).
- `C_optimal_equivalence` — **PASS**: Locally c-optimal LoD design satisfies the General Equivalence Theorem (numerical check).
- `P17_selective_inflation` — **PASS**: Conditional Type I | G=1 can exceed nominal α under skew when S2 selects parametric LoB.
- `P13_minimax_formal` — **PASS**: Minimax over B=[0.5,1.5]·β_plan beats folklore equal-log design.

### Referee notes (P1–P8 core)

- **P1 (saturation):** Correct and central; φ_n must not be used for E2.
- **P2 (binomial identity):** Algebraic; keep as sanity certificate.
- **P3 (Fleiss–Chow):** Asymptotic n* calibrates pooled-z MC power near target; at folklore n=20, **exact Fisher power is materially lower** than asymptotic (see Table 3: 90 vs 80 → ~7% Fisher vs ~14% asymptotic). Do not oversell P3 as exact small-sample calibration.
- **P4 (design effect):** Standard compound-symmetry DE; state ICC estimation uncertainty.
- **P5 (parametric LoB mismatch):** Strong counterexample (Exp); supports S2/S3 gate.
- **P6 (OVL):** Separation on a denser n-grid; not a substitute for power calculations.
- **P7 (all-positive trap):** n/n does not certify high LoD claims (α^(1/n) << claim). **Headline D1.**
- **P8 (exact vs asymptotic gap):** At folklore n for close alternatives, asymptotic power overstates exact Fisher power — design surface ≠ confirmation. **Headline D2.**

### Referee notes (P9–P18 extensions)

- **P9 (Holm FWER):** MC sketch for multi-arm gates; corroborates S4 multiplicity policy.
- **P10 (weight scale):** L is homogeneous in weights — audit ledger, not utility optimum.
- **P11 (Tobit):** Agreement with naive mean+z·SD when uncensored; supports parametric LoB path.
- **P12–P14 (c-optimal / minimax / efficiency):** Multilevel **estimation** branch; not required for E1–E3 verification at c* but documents design dominance over equal-log folklore.
- **P15–P16 (identification):** LoD identifiable on interior hit-rate grid; saturation plates break identifiability.
- **P17 (gated LoB inflation):** Pre-test model selection can inflate Type I; sample-split remedy in supplementary certificate.
- **P18 (folklore inadmissible):** n=20 Pareto-dominated on exact Fisher OC plane. **Headline D3.**

## Exact vs asymptotic (Table 3)

If |exact Fisher power − asymptotic| is material at small n, prefer exact n* / Fisher–Boschloo for primary claims; asymptotic remains a continuous design surface approximation.

### Highlights

- **fisher_power_90vs80_n20:** `0.07248402262703549`
- **fisher_power_90vs80_n199:** `0.765606557054304`
- **exact_n_star_90vs50_fisher:** `{"n_star_exact": 23, "n_star_asymptotic": 19.380842441647857, "power_at_n_exact": 0.811422294681146, "power_target": 0.8, "alpha": 0.05, "test": "fisher", "p_a": 0.9, "p_b": 0.5}`
- **boschloo_demo_18of20_vs_14of20:** `{"fisher_p": 0.2351162351162351, "boschloo_p": 0.15388788553173088, "pooled_z_p": 0.11384629800665785}`

### Table 3 extensions (full E2 grid @ n=20)

- **reference pairs:** `/Users/zhangdong/PycharmProjects/PythonProject/LOD/paper_artifacts/tables/Table03_reference_pairs_n20.csv`
- **full grid (1225 cells):** `/Users/zhangdong/PycharmProjects/PythonProject/LOD/paper_artifacts/tables/Table03_comparison_grid_n20.csv`

### Reporting policy (locked)

- **design_surface:** asymptotic Fleiss-Chow / pooled-z (continuous models)
- **primary_small_n_test:** Boschloo unconditional exact (Fisher as conditional reference)
- **primary_small_n_power:** exact enumeration under independent binomials
- **do_not_claim:** asymptotic power alone is exact at n=20

## Publication readiness (this memo)

These tables are **submission-ready as supplementary statistical appendices** once captions are frozen. They do **not** by themselves make a full Clinical Chemistry paper complete (need narrative manuscript; LoQ engine + estradiol analysis now present as supplements).


## Type I calibration (Table 6)

See `tables/Table06_type1_calibration.csv` and data/research/type1_calibration.json.
