"""
Unified journal figure / table numbering and captions.

Main text (Fig 1–5): one narrative arc — decision map → folklore failures →
finite-sample theory → remedies → tier-A anchor.

Supplement (Fig S1–S9): full module outputs and sensitivity panels.

Manuscript IDs are stable for the paper draft.
Source filenames under figures/methodology/ remain developer IDs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIG_SRC = ROOT / "figures" / "methodology"
PAPER = ROOT / "paper_artifacts"


@dataclass(frozen=True)
class FigureSpec:
    manuscript_id: str  # e.g. Fig 1 or Fig S1
    developer_id: str  # e.g. Fig1_decision_map
    title: str
    caption: str
    panel_note: str = ""
    source_png: str = ""  # relative to figures/methodology
    tier: str = "main"  # "main" | "supplement"


@dataclass(frozen=True)
class TableSpec:
    manuscript_id: str
    developer_id: str
    title: str
    caption: str
    artifact_csv: str  # relative to paper_artifacts/tables


MAIN_FIGURES: tuple[FigureSpec, ...] = (
    FigureSpec(
        "Fig 1",
        "Fig1-decision-map",
        "LoD verification planning pipeline",
        (
            "LoD verification planning pipeline (main text). Laboratories lock a detection claim—"
            "G1 verify LoD, G2 compare lots/reagents at c*, or G4 qualitative k/n (S0)—classify "
            "hit-rate/binary data (S1), plan replicates from operating characteristics (S5), "
            "confirm with exact Fisher/Boschloo methods (S6), and emit an auditable report (S7). "
            "G3 LoQ and the optional continuous EP17 LoB branch (S2–S4, P17) are out of "
            "main-text scope; see Supplement Fig S-LoB and Table 2. Certificates P1, P7, P8, P18."
        ),
        source_png="Fig1_decision_map.png",
        tier="main",
    ),
    FigureSpec(
        "Fig 2",
        "Fig2-folklore-triptych",
        "Folklore triple failure",
        (
            "Three independent failure modes of folklore small-n practice. "
            "Panel A (G1): probability p^n of observing n/n hits; one-sided Clopper–Pearson "
            "lower bound after 20/20 remains far below 0.95. "
            "Panel B (G2): exact Fisher miss probability β at folklore n=20 for illustrative "
            "reagent pairs; required n* annotated. "
            "Panel C (P16): SE(log10 LoD95) under interior-level design versus saturation "
            "plateau (non-identifiable concentration LoD)."
        ),
        panel_note="Composite panels A–C from paper.main_figures.fig2_folklore_triptych",
        source_png="Fig2_folklore_triptych.png",
        tier="main",
    ),
    FigureSpec(
        "Fig 3",
        "Fig3-finite-sample",
        "Finite-sample theory: gap, Berry–Esseen, Pareto",
        (
            "Panel A: asymptotic versus exact Fisher power versus n (90% vs 80%) with 80% reference. "
            "Panel B: exact Fisher power heatmap over (p_A, p_B) at folklore n=20 (red–green scale); "
            "ring marks 90% vs 80% cell. Panel C: Type I versus power Pareto plane (P18); "
            "dashed arrow from folklore to powered design."
        ),
        panel_note="Composite panels A–C from paper.main_figures.fig3_finite_sample_theory",
        source_png="Fig3_finite_sample_theory.png",
        tier="main",
    ),
    FigureSpec(
        "Fig 4",
        "Fig4-remedy",
        "Remedies: powered n*, exact power, design",
        (
            "Panel A: required n per arm (80% power) versus competitor hit rate with reference "
            "p_A=90%; folklore n=20 marked. Panel B: exact Fisher power at folklore n=20 versus "
            "powered n* for 90% vs 80% (G2 reference). Panel C: asymptotic SE(log10 LoD95) for "
            "folklore equal-log spacing, c-optimal grid, and minimax dense-near-LoD design (P13). "
            "LoB sample-split (P17) panel: supplement FigS_lob_p17_split."
        ),
        panel_note="Composite panels A–C from paper.main_figures.fig4_remedy_composite",
        source_png="Fig4_remedy_composite.png",
        tier="main",
    ),
    FigureSpec(
        "Fig 5",
        "Fig5-tierA-lod",
        "Tier-A empirical anchor (LoD replicate planning)",
        (
            "Four-panel Tier-A LoD anchor (Table 7). "
            "A: qPCR hit rate versus standard concentration (detection curve). "
            "B: guidance n versus folklore n=20 on LoD-focused tier-A deposits. "
            "C: public deposit size versus planned n for LoD claims. "
            "D: headline replicate counts for G1, G2, and G4 versus folklore n=20. "
            "Radioimmuno LoQ profile moved to supplement (FigL_radioimmuno_loq_profile)."
        ),
        source_png="Fig5_tierA_lod_grid.png",
        tier="main",
    ),
)


SUPPLEMENT_FIGURES: tuple[FigureSpec, ...] = (
    FigureSpec(
        "Fig S-LoB",
        "FigS-lob-p17",
        "P17 LoB sample-split (continuous EP17 path)",
        (
            "Supplement only — not part of main-text LoD scope. Under skewed blanks, unsplit "
            "gated parametric LoB inflates exceedance above nominal α; P17 half-split with "
            "Bonferroni α/2 restores nominal Type I. Relevant when laboratories use continuous "
            "EP17 LoB paths (S2–S4)."
        ),
        source_png="FigS_lob_p17_split.png",
        tier="supplement",
    ),
    FigureSpec(
        "Fig S1",
        "FigS1-loq-troponin",
        "LoQ precision profile (tier C troponin demo)",
        (
            "CV% versus pool mean for EP17 Example 3 troponin pools (evidence tier C). "
            "Engine-consistency demo only; not a primary empirical claim."
        ),
        source_png="FigL1_loq_precision_profile.png",
        tier="supplement",
    ),
    FigureSpec(
        "Fig S2",
        "FigS2-power-delta",
        "Discrimination power versus n by Δp",
        (
            "Asymptotic two-proportion power for p_A=0.90 versus p_B=p_A−Δ, α=0.05 (two-sided). "
            "Folklore n=20 (vertical reference) is severely underpowered for Δ=0.10."
        ),
        source_png="FigM2_power_vs_n_by_delta.png",
        tier="supplement",
    ),
    FigureSpec(
        "Fig S3",
        "FigS3-miss-beta",
        "Miss probability β at folklore and powered n",
        (
            "Type II error for selected reagent pairs including 90% vs 80% and 90% vs 50%. "
            "Full curves; main-text summary in Fig 2B."
        ),
        source_png="FigD1_miss_probability_beta.png",
        tier="supplement",
    ),
    FigureSpec(
        "Fig S4",
        "FigS4-all-positive",
        "All-positive trap (standalone)",
        (
            "Left: P(X=n)=p^n; right: CP lower bounds versus Uniform residual risk after n/n. "
            "Expanded version of Fig 2A."
        ),
        panel_note="Composite panels A–B from paper.journal_figures.fig4_all_positive_composite",
        source_png="Fig4_all_positive_composite.png",
        tier="supplement",
    ),
    FigureSpec(
        "Fig S5",
        "FigS5-nstar-continuous",
        "Continuous n*(p_A,p_B) surface",
        (
            "Equal-arm Fleiss–Chow sample size for 80% power over (p_A,p_B). "
            "Three-panel continuous discrimination study; main-text slice in Fig 4A."
        ),
        source_png="FigD2_nstar_and_relative_lod.png",
        tier="supplement",
    ),
    FigureSpec(
        "Fig S6",
        "FigS6-concentration",
        "Concentration relative to LoD_95",
        (
            "Operating characteristics as a continuous function of r=c/LoD_95 "
            "(below / at / above LoD): verification pass probability and comparative miss β."
        ),
        source_png="FigR1_concentration_relative_effects.png",
        tier="supplement",
    ),
    FigureSpec(
        "Fig S7",
        "FigS7-evidence",
        "Evidence landscape",
        (
            "Public multi-assay deposits (tier A–C) and audited simulation stress DGPs (tier S). "
            "See Evidence Ladder (Table 5)."
        ),
        source_png="FigC2_diverse_data_landscape.png",
        tier="supplement",
    ),
    FigureSpec(
        "Fig S8",
        "FigS8-challenge",
        "Folklore n=20 versus algorithm-required n",
        (
            "Bar comparison of powered n* and achieved power at folklore n=20 across "
            "illustrative scenarios; complements Fig 2B."
        ),
        source_png="FigC1_challenge_folklore_vs_algorithm.png",
        tier="supplement",
    ),
    FigureSpec(
        "Fig S9",
        "FigS9-design-se",
        "Multi-level LoD design SE comparison (full)",
        (
            "Asymptotic SE(log10 LoD95) for equal log-spacing folklore, c-optimal grid, and "
            "minimax dense-near-LoD design at planning slope; worst-case SE over slope ratios "
            "β ∈ [0.5, 1.5]β_plan (P13). Main-text summary in Fig 4C."
        ),
        panel_note="Panels A–B from design_se_figures.fig9_design_se_comparison",
        source_png="Fig9_design_se_comparison.png",
        tier="supplement",
    ),
)


FIGURES: tuple[FigureSpec, ...] = MAIN_FIGURES + SUPPLEMENT_FIGURES


TABLES: tuple[TableSpec, ...] = (
    TableSpec(
        "Table 1",
        "T1_estimands",
        "Primary LoD estimands G1, G2, G4",
        (
            "Detection-limit estimands before sample-size planning. Mixing goals in one episode "
            "is forbidden; engines differ by row. G3 (LoQ / precision) is an optional EP17 "
            "branch documented in Supplement Table 2 and excluded from main-text claims."
        ),
        "Table01_estimands_G1_G4.csv",
    ),
    TableSpec(
        "Table 2",
        "T2_loq_precision",
        "LoQ / precision design (G3)",
        (
            "Required n so that CV of the mean (100·(σ/μ)/√n) meets target CV%, "
            "and n for mean CI half-width under Normal sampling. "
            "**Supplement only (G3 LoQ)** — out of main-text LoD scope; "
            "radioimmuno tier-A profile in FigL; troponin EP17 pools tier-C demo (Fig S1)."
        ),
        "Table02_loq_precision_main.csv",
    ),
    TableSpec(
        "Table 3",
        "T3_exact_vs_asymp",
        "Asymptotic versus exact discrimination power",
        (
            "For selected (p_A,p_B,n): asymptotic pooled-z power, exact Fisher power, "
            "exact pooled-z enumeration, Monte Carlo pooled-z, and miss β under Fisher. "
            "Primary small-n confirmatory reporting should prefer exact / Boschloo; "
            "asymptotic surfaces remain design approximations. Supports Fig 3."
        ),
        "Table03_exact_vs_asymptotic.csv",
    ),
    TableSpec(
        "Table 4",
        "T4_propositions",
        "Machine certificates P1–P18",
        (
            "Internal review table: proposition ID, statement, pass/fail, key numeric details "
            "(P1–P8 core lemmas and bounds; P12–P18 identification, c-optimal/minimax design, "
            "selective LoB inflation, folklore inadmissibility). "
            "Re-run produces SHA-auditable certificates in the analysis protocol."
        ),
        "Table04_propositions_P1_P6.csv",
    ),
    TableSpec(
        "Table 5",
        "T5_evidence_ladder",
        "Public evidence ladder",
        (
            "Downloaded real datasets by evidence tier "
            "(A=raw/replicate-level public deposits; B=summary; C=synthetic EP17 demo; S=simulation DGPs) "
            "and assay family. Includes radioimmuno precision/linearity (Zenodo 12664367), "
            "RMN ID50 (Zenodo 17108929), Carobene multi-lab chemistry, and CPTAC/MSstatsLOBD "
            "proteomics blank–LoB as tier-A cases. Hematology analyzer blank–LoD raw deposits remain a gap."
        ),
        "Table05_evidence_ladder.csv",
    ),
    TableSpec(
        "Table 6",
        "T6_type1_calibration",
        "Finite-sample Type I error under H0",
        (
            "Empirical Type I rates for pooled-z and Fisher (and Boschloo at n=20) "
            "under p_A=p_B=p. Documents conservatism of Fisher and calibration of pooled-z."
        ),
        "Table06_type1_calibration.csv",
    ),
    TableSpec(
        "Table 7",
        "T7_tierA_meta",
        "Tier-A meta-summary across public deposits",
        (
            "One row per evidence-tier-A dataset: parametric gate outcome, model path, "
            "guidance n versus folklore n=20, and LoQ@CV20% when a precision profile applies. "
            "Tier C/S deposits are excluded by design. Supports Fig 5."
        ),
        "Table07_tierA_meta.csv",
    ),
    TableSpec(
        "Table 8",
        "T8_g1_coverage",
        "G1 Wilson vs Clopper–Pearson coverage",
        (
            "Monte Carlo coverage and mean width for Wilson and Clopper–Pearson intervals "
            "under binomial LoD hit-rate scenarios. Supports confirmatory G1 interval policy."
        ),
        "Table08_g1_one_proportion_coverage.csv",
    ),
)


def write_caption_files(out_dir: Path | None = None) -> dict[str, Path]:
    out_dir = out_dir or (PAPER / "captions")
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_md = out_dir / "FIGURE_CAPTIONS.md"
    tab_md = out_dir / "TABLE_CAPTIONS.md"
    map_json = out_dir / "id_map.json"
    plan_md = out_dir / "FIGURE_PLAN.md"

    fig_lines = [
        "# Figure captions (manuscript numbering)",
        "",
        "## Main text (Fig 1–5)",
        "",
        "One narrative arc: **decision map → folklore failures → finite-sample theory → remedies → tier-A anchor**.",
        "",
    ]
    for f in MAIN_FIGURES:
        fig_lines += [
            f"### {f.manuscript_id}. {f.title}",
            "",
            f"**Developer ID:** `{f.developer_id}`  ",
            f"**Source file:** `{f.source_png}`  ",
            "",
            f"**Caption.** {f.caption}",
            "",
        ]
        if f.panel_note:
            fig_lines += [f"*Panel note:* {f.panel_note}", ""]

    fig_lines += ["---", "", "## Supplement (Fig S1–S9)", ""]
    for f in SUPPLEMENT_FIGURES:
        fig_lines += [
            f"### {f.manuscript_id}. {f.title}",
            "",
            f"**Developer ID:** `{f.developer_id}`  ",
            f"**Source file:** `{f.source_png}`  ",
            "",
            f"**Caption.** {f.caption}",
            "",
        ]
        if f.panel_note:
            fig_lines += [f"*Panel note:* {f.panel_note}", ""]

    plan_lines = [
        "# Figure plan (unified main vs supplement)",
        "",
        "## Main text — 5 figures only",
        "",
        "| Fig | Role | Panels |",
        "|-----|------|--------|",
        "| **Fig 1** | S0–S7 workflow + P17 branch | single map |",
        "| **Fig 2** | Why folklore fails | A: all-positive; B: G2 miss@20; C: saturation |",
        "| **Fig 3** | Finite-sample theory | A: power gap; B: Fisher heatmap @ n=20; C: Pareto |",
        "| **Fig 4** | Remedies | A: powered n*; B: exact power folklore vs n*; C: design SE |",
        "| **Fig 5** | Tier-A LoD anchor | A: qPCR hit rate; B: n ratio; C: deposit vs n; D: G1/G2/G4 n |",
        "",
        "## Supplement — module detail",
        "",
        "| Fig | Replaces / expands |",
        "|-----|---------------------|",
        "| S-LoB | P17 LoB sample-split (continuous EP17 path) |",
        "| S1 | Troponin LoQ demo (tier C) |",
        "| S2 | Full power-vs-n curves (old Fig 2) |",
        "| S3 | Full miss-β curves (old Fig 3) |",
        "| S4 | All-positive standalone (old Fig 4) |",
        "| S5 | Continuous n* 3-panel (old Fig 5–6) |",
        "| S6 | Concentration r=c/LoD (old Fig 6) |",
        "| S7 | Evidence landscape (old Fig 7) |",
        "| S8 | Challenge bar chart |",
        "| S9 | Full design SE 2-panel (old Fig 9) |",
        "",
        "Build: `make paper-artifacts` → `paper.main_figures.generate_main_figures()` first.",
        "",
    ]

    tab_lines = ["# Table captions (manuscript numbering)", ""]
    for t in TABLES:
        tab_lines += [
            f"## {t.manuscript_id}. {t.title}",
            "",
            f"**Developer ID:** `{t.developer_id}`  ",
            f"**CSV:** `tables/{t.artifact_csv}`  ",
            "",
            f"**Caption.** {t.caption}",
            "",
        ]

    import json

    mapping = {
        "main_figures": [asdict(f) for f in MAIN_FIGURES],
        "supplement_figures": [asdict(f) for f in SUPPLEMENT_FIGURES],
        "figures": [asdict(f) for f in FIGURES],
        "tables": [asdict(t) for t in TABLES],
    }
    fig_md.write_text("\n".join(fig_lines), encoding="utf-8")
    tab_md.write_text("\n".join(tab_lines), encoding="utf-8")
    plan_md.write_text("\n".join(plan_lines), encoding="utf-8")
    map_json.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
    return {"figures": fig_md, "tables": tab_md, "map": map_json, "plan": plan_md}
