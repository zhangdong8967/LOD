"""
Unified journal figure / table numbering and captions.

Main text (Fig 1): integrated protocol + E2 planning — single figure (panels A–D).
Supplement: tables and JSON only (v7); optional grid heatmaps in Table 3 CSV.
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
        "Fig1-lod-replicate-planning",
        "Prospective LoD protocol and E2 replicate planning (panels A–D)",
        (
            "**A:** Lock the two-arm claim, score $n=20$ on the equally spaced lattice (not a field prevalence), "
            "then plan $n^*(\\Delta p)$; $n^*$ is not a single default. "
            "**B:** Exact Fisher miss $\\beta$ at $n=20$ over all valid integer pairs ($1225$ cells); "
            "90/80 marked as one worked example (Table 2). "
            "**C:** Design surface $n^*(p_A,p_B)$ (log display scale); $n^*$ is monotone in $\\Delta p$ "
            "(Supplementary Table 3f). "
            "**D:** Logistic $c/\\mathrm{LoD}_{95}$ vs $p$ with slope sensitivity band. "
            "Full lattice: `Table03_comparison_grid_n20.csv`."
        ),
        panel_note="Panels A–D from paper.main_figures.fig1_lod_replicate_planning (single merged figure)",
        source_png="Fig1_lod_replicate_planning.png",
        tier="main",
    ),
    FigureSpec(
        "Fig 2",
        "Fig2-tierA-calibration",
        "Tier A public-deposit calibration (panels A–C)",
        (
            "**A:** Example qPCR / hit-rate deposit near LoD illustrating a steep detection curve. "
            "**B:** Ratios of guidance $n$ to conventional $n=20$ across tier A deposits with applicable "
            "guidance $n$ (often 2.6×–10×). "
            "**C:** Equal-weight decision risk ledger comparing conventional $n=20$ versus powered designs "
            "for reference E2 pairs (and related E1 context). "
            "Numeric meta-summary: Table 7. Calibration on archived public deposits — not multi-assay "
            "clinical validation."
        ),
        panel_note="Panels A–C from paper.main_figures.fig2_empirical_calibration",
        source_png="Fig2_tierA_calibration.png",
        tier="main",
    ),
)


SUPPLEMENT_FIGURES: tuple[FigureSpec, ...] = ()


FIGURES: tuple[FigureSpec, ...] = MAIN_FIGURES + SUPPLEMENT_FIGURES


TABLES: tuple[TableSpec, ...] = (
    TableSpec(
        "Table 1",
        "T1_estimands",
        "Primary LoD estimands E1, E2, E3",
        (
            "Detection-limit estimands before sample-size planning. E1–E3 are Article labels "
            "(not CLSI nomenclature). Mixing goals in one episode is forbidden; engines differ by row. "
            "The LoQ branch (EP17 Section 7.4) is documented in Supplement Table 2 and excluded "
            "from main-text LoD verification claims."
        ),
        "Table01_estimands_E1_E3.csv",
    ),
    TableSpec(
        "Table 2",
        "T2_loq_precision",
        "LoQ / precision design (LoQ branch)",
        (
            "Required n so that CV of the mean (100·(σ/μ)/√n) meets target CV%, "
            "and n for mean CI half-width under Normal sampling. "
            "**Supplement only (LoQ branch)** — out of main-text LoD scope."
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
            "Primary rows: all eight reference pairs at folklore n=20; full 1225-cell lattice in "
            "`Table03_comparison_grid_n20.csv`; marginal by Δ in Table 3f. "
            "Extensions: `Table03_reference_pairs_n20.csv`. "
            "Primary small-n confirmatory reporting should prefer exact / Boschloo; "
            "asymptotic surfaces remain design approximations. Supports Fig 1 and Table 3 extensions."
        ),
        "Table03_exact_vs_asymptotic.csv",
    ),
    TableSpec(
        "Table 4",
        "T4_propositions",
        "Machine certificates P1–P18",
        (
            "Internal review table: proposition ID, **Role** (headline / core / extension), statement, "
            "pass/fail, key numeric details (headline P7, P8, P18 for D1–D3; P12–P17 extension). "
            "Re-run produces SHA-auditable certificates in the analysis protocol."
        ),
        "Table04_propositions_P1_P18.csv",
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
            "One row per evidence-tier-A dataset ($n=10$): parametric gate outcome, model path, "
            "guidance n versus folklore n=20, and LoQ@CV20% when a precision profile applies. "
            "Tier C/S deposits are excluded by design. Supports Fig 2."
        ),
        "Table07_tierA_meta.csv",
    ),
    TableSpec(
        "Table 7b",
        "T7b_protocol_audit",
        "Retrospective protocol-file audit matrix (Supplement)",
        (
            "Prespecified audit rows ($n=16$): verbatim LoD-related protocol language, mapped "
            "detection claim (E1–E3), archived replicate plan $n$, guidance $n^{\\ast}$, and exact "
            "operating characteristic at archived $n$. Ten verbatim protocol quotes from tier-A "
            "public files (Table 7 lists ten tier-A deposits), three tier A-hosp hospital replicate "
            "CSVs (data/hospital_lod_replicates/), and three tier A-pub main-text $x/n$ tables "
            "(data/published_lod_tables/)."
        ),
        "Table07b_protocol_audit.csv",
    ),
    TableSpec(
        "Table 7b-S",
        "T7b_protocol_audit_summary",
        "Retrospective protocol-file audit — compact summary (Supplement)",
        (
            "One row per Table 7b audit row ($n=16$) without verbatim quotes: evidence tier, "
            "mapped claim (E1–E3), archived $n$, guidance $n^{\\ast}$, exact OC at archived $n$, "
            "empirical rate when available, and OC-below-target flag. Supports Results audit summary."
        ),
        "Table07b_protocol_audit_summary.csv",
    ),
    TableSpec(
        "Table 8",
        "T8_e1_coverage",
        "E1 Wilson vs Clopper–Pearson coverage",
        (
            "Monte Carlo coverage and mean width for Wilson and Clopper–Pearson intervals "
            "under binomial LoD hit-rate scenarios. Supports confirmatory E1 interval policy."
        ),
        "Table08_e1_one_proportion_coverage.csv",
    ),
    TableSpec(
        "Table 9",
        "T9_e3_operating",
        "E3 pass-rule operating characteristics",
        (
            "Exact P(X≥k | p, n) for qualitative k/n pass rules with k∈{n−1, n−2, n−3}, "
            "n∈{10,20,30,60}, p=80–99%). Extensions: Table09b minimal n for 95% pass reliability; "
            "Table09c E3-vs-E2 confusion at n=20 (19/20 pass vs Fisher β)."
        ),
        "Table09_e3_operating_characteristics.csv",
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
        "## Main text (Fig 1–2)",
        "",
        "Two main figures: **Fig 1** E2 OC design (A–D) + **Fig 2** tier A calibration (A–C).",
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

    if SUPPLEMENT_FIGURES:
        fig_lines += ["---", "", "## Supplement", ""]
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
        "## Main text — 2 figures (≤6 figures+tables with Tables 1, 3, 7)",
        "",
        "| Fig | Role | Panels |",
        "|-----|------|--------|",
        "| **Fig 1** | E2 OC design | A: estimand/OC/calibration; B: $\\beta$ @ $n=20$; C: $n^*$; D: $c/\\mathrm{LoD}_{95}$ |",
        "| **Fig 2** | Tier A calibration | A: qPCR hit-rate example; B: guidance $n$/20 ratios; C: decision-risk ledger |",
        "",
        "No supplement figures in the v8 main package (grid CSVs and tables only).",
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
