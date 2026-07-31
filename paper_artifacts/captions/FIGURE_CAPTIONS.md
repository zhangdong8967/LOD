# Figure captions (manuscript numbering)

## Main text (Fig 1–5)

One narrative arc: **decision map → folklore failures → finite-sample theory → remedies → tier-A anchor**.

### Fig 1. LoD verification planning pipeline

**Developer ID:** `Fig1-decision-map`  
**Source file:** `Fig1_decision_map.png`  

**Caption.** LoD verification planning pipeline (main text). Laboratories lock a detection claim—G1 verify LoD, G2 compare lots/reagents at c*, or G4 qualitative k/n (S0)—classify hit-rate/binary data (S1), plan replicates from operating characteristics (S5), confirm with exact Fisher/Boschloo methods (S6), and emit an auditable report (S7). G3 LoQ and the optional continuous EP17 LoB branch (S2–S4, P17) are out of main-text scope; see Supplement Fig S-LoB and Table 2. Certificates P1, P7, P8, P18.

### Fig 2. Folklore triple failure

**Developer ID:** `Fig2-folklore-triptych`  
**Source file:** `Fig2_folklore_triptych.png`  

**Caption.** Three independent failure modes of folklore small-n practice. Panel A (G1): probability p^n of observing n/n hits; one-sided Clopper–Pearson lower bound after 20/20 remains far below 0.95. Panel B (G2): exact Fisher miss probability β at folklore n=20 for illustrative reagent pairs; required n* annotated. Panel C (P16): SE(log10 LoD95) under interior-level design versus saturation plateau (non-identifiable concentration LoD).

*Panel note:* Composite panels A–C from paper.main_figures.fig2_folklore_triptych

### Fig 3. Finite-sample theory: gap, Berry–Esseen, Pareto

**Developer ID:** `Fig3-finite-sample`  
**Source file:** `Fig3_finite_sample_theory.png`  

**Caption.** Panel A: asymptotic versus exact Fisher power versus n (90% vs 80%) with 80% reference. Panel B: exact Fisher power heatmap over (p_A, p_B) at folklore n=20 (red–green scale); ring marks 90% vs 80% cell. Panel C: Type I versus power Pareto plane (P18); dashed arrow from folklore to powered design.

*Panel note:* Composite panels A–C from paper.main_figures.fig3_finite_sample_theory

### Fig 4. Remedies: powered n*, exact power, design

**Developer ID:** `Fig4-remedy`  
**Source file:** `Fig4_remedy_composite.png`  

**Caption.** Panel A: required n per arm (80% power) versus competitor hit rate with reference p_A=90%; folklore n=20 marked. Panel B: exact Fisher power at folklore n=20 versus powered n* for 90% vs 80% (G2 reference). Panel C: asymptotic SE(log10 LoD95) for folklore equal-log spacing, c-optimal grid, and minimax dense-near-LoD design (P13). LoB sample-split (P17) panel: supplement FigS_lob_p17_split.

*Panel note:* Composite panels A–C from paper.main_figures.fig4_remedy_composite

### Fig 5. Tier-A empirical anchor (LoD replicate planning)

**Developer ID:** `Fig5-tierA-lod`  
**Source file:** `Fig5_tierA_lod_grid.png`  

**Caption.** Four-panel Tier-A LoD anchor (Table 7). A: qPCR hit rate versus standard concentration (detection curve). B: guidance n versus folklore n=20 on LoD-focused tier-A deposits. C: public deposit size versus planned n for LoD claims. D: headline replicate counts for G1, G2, and G4 versus folklore n=20. Radioimmuno LoQ profile moved to supplement (FigL_radioimmuno_loq_profile).

---

## Supplement (Fig S1–S9)

### Fig S-LoB. P17 LoB sample-split (continuous EP17 path)

**Developer ID:** `FigS-lob-p17`  
**Source file:** `FigS_lob_p17_split.png`  

**Caption.** Supplement only — not part of main-text LoD scope. Under skewed blanks, unsplit gated parametric LoB inflates exceedance above nominal α; P17 half-split with Bonferroni α/2 restores nominal Type I. Relevant when laboratories use continuous EP17 LoB paths (S2–S4).

### Fig S1. LoQ precision profile (tier C troponin demo)

**Developer ID:** `FigS1-loq-troponin`  
**Source file:** `FigL1_loq_precision_profile.png`  

**Caption.** CV% versus pool mean for EP17 Example 3 troponin pools (evidence tier C). Engine-consistency demo only; not a primary empirical claim.

### Fig S2. Discrimination power versus n by Δp

**Developer ID:** `FigS2-power-delta`  
**Source file:** `FigM2_power_vs_n_by_delta.png`  

**Caption.** Asymptotic two-proportion power for p_A=0.90 versus p_B=p_A−Δ, α=0.05 (two-sided). Folklore n=20 (vertical reference) is severely underpowered for Δ=0.10.

### Fig S3. Miss probability β at folklore and powered n

**Developer ID:** `FigS3-miss-beta`  
**Source file:** `FigD1_miss_probability_beta.png`  

**Caption.** Type II error for selected reagent pairs including 90% vs 80% and 90% vs 50%. Full curves; main-text summary in Fig 2B.

### Fig S4. All-positive trap (standalone)

**Developer ID:** `FigS4-all-positive`  
**Source file:** `Fig4_all_positive_composite.png`  

**Caption.** Left: P(X=n)=p^n; right: CP lower bounds versus Uniform residual risk after n/n. Expanded version of Fig 2A.

*Panel note:* Composite panels A–B from paper.journal_figures.fig4_all_positive_composite

### Fig S5. Continuous n*(p_A,p_B) surface

**Developer ID:** `FigS5-nstar-continuous`  
**Source file:** `FigD2_nstar_and_relative_lod.png`  

**Caption.** Equal-arm Fleiss–Chow sample size for 80% power over (p_A,p_B). Three-panel continuous discrimination study; main-text slice in Fig 4A.

### Fig S6. Concentration relative to LoD_95

**Developer ID:** `FigS6-concentration`  
**Source file:** `FigR1_concentration_relative_effects.png`  

**Caption.** Operating characteristics as a continuous function of r=c/LoD_95 (below / at / above LoD): verification pass probability and comparative miss β.

### Fig S7. Evidence landscape

**Developer ID:** `FigS7-evidence`  
**Source file:** `FigC2_diverse_data_landscape.png`  

**Caption.** Public multi-assay deposits (tier A–C) and audited simulation stress DGPs (tier S). See Evidence Ladder (Table 5).

### Fig S8. Folklore n=20 versus algorithm-required n

**Developer ID:** `FigS8-challenge`  
**Source file:** `FigC1_challenge_folklore_vs_algorithm.png`  

**Caption.** Bar comparison of powered n* and achieved power at folklore n=20 across illustrative scenarios; complements Fig 2B.

### Fig S9. Multi-level LoD design SE comparison (full)

**Developer ID:** `FigS9-design-se`  
**Source file:** `Fig9_design_se_comparison.png`  

**Caption.** Asymptotic SE(log10 LoD95) for equal log-spacing folklore, c-optimal grid, and minimax dense-near-LoD design at planning slope; worst-case SE over slope ratios β ∈ [0.5, 1.5]β_plan (P13). Main-text summary in Fig 4C.

*Panel note:* Panels A–B from design_se_figures.fig9_design_se_comparison
