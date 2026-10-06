"""
One-click paper artifact builder.

Produces:
  paper_artifacts/
    captions/FIGURE_CAPTIONS.md, TABLE_CAPTIONS.md, id_map.json
    figures/   (copies of numbered manuscript figures; no in-figure titles)
    tables/    Table01…Table08 CSVs + manuscript/ readable copies
    review/    INTERNAL_REVIEW_P1P6_EXACT.md
    MANIFEST.json
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from lod_guide import __version__
from lod_guide.figures import (
    generate_all_methodology_figures,
    generate_challenge_figures,
)
from lod_guide.paper.internal_review import write_internal_review_memo
from lod_guide.paper.main_figures import generate_main_figures, generate_supplement_figures
from lod_guide.paper.loq_precision import build_loq_precision_tables
from lod_guide.paper.manuscript_tables import build_manuscript_tables
from lod_guide.paper.theory_research import ensure_theory_research
from lod_guide.paper.registry import (
    FIGURES,
    FIG_SRC,
    MAIN_FIGURES,
    SUPPLEMENT_FIGURES,
    TABLES,
    PAPER,
    write_caption_files,
)
from lod_guide.research.continuous_figures import generate_continuous_model_figures
from lod_guide.research.concentration_figures import generate_concentration_figures
from lod_guide.research.decision_risk import evaluate_standard_scenarios
from lod_guide.research.discrimination_figures import generate_discrimination_figures
from lod_guide.research.empirical_tierA_extension import run_empirical_tierA_extension
from lod_guide.research.evidence_stratified_report import build_evidence_stratified_report
from lod_guide.research.e3_operating_characteristics import run_e3_operating_characteristics_study
from lod_guide.research.one_proportion_coverage import run_one_proportion_coverage_study
from lod_guide.research.precision_profile import run_precision_profile_study
from lod_guide.research.tierA_meta_analysis import run_tierA_meta_analysis
from lod_guide.research.tierA_protocol_audit import run_tierA_protocol_audit
from lod_guide.paper.word_export import export_cover_letter_docx, export_manuscript_docx


def _copy_figures(fig_dir: Path) -> list[dict]:
    fig_dir.mkdir(parents=True, exist_ok=True)
    expected: set[str] = set()
    copied = []
    for f in FIGURES:
        src = FIG_SRC / f.source_png
        safe = f.manuscript_id.replace(" ", "")
        dst = fig_dir / f"{safe}_{f.developer_id}{src.suffix if src.suffix else '.png'}"
        expected.add(dst.name)
        expected.add(dst.with_suffix(".pdf").name)
        expected.add(dst.with_suffix(".tif").name)
        status = "missing_source"
        if src.exists():
            shutil.copy2(src, dst)
            pdf = src.with_suffix(".pdf")
            if pdf.exists():
                shutil.copy2(pdf, dst.with_suffix(".pdf"))
            tif = src.with_suffix(".tif")
            if tif.exists():
                shutil.copy2(tif, dst.with_suffix(".tif"))
            status = "copied"
        copied.append(
            {
                "manuscript_id": f.manuscript_id,
                "source": str(src),
                "dest": str(dst),
                "status": status,
            }
        )
    # Drop stale v1/v2 copies not in the current registry.
    for path in list(fig_dir.iterdir()):
        if path.suffix not in {".png", ".pdf"}:
            continue
        if path.name not in expected:
            path.unlink(missing_ok=True)
    return copied


def _paper_figure_stems() -> set[str]:
    return {Path(f.source_png).stem for f in MAIN_FIGURES}


def _prune_non_paper_figures() -> list[str]:
    """Remove non-main figures from figures/methodology/ (keep MAIN_FIGURES stems only)."""
    allowed = _paper_figure_stems()
    removed: list[str] = []
    if not FIG_SRC.is_dir():
        return removed
    for path in list(FIG_SRC.iterdir()):
        if path.suffix not in {".png", ".pdf"}:
            continue
        if path.stem not in allowed:
            path.unlink(missing_ok=True)
            removed.append(path.name)
    return removed


def _regen_paper_figures(*, legacy: bool = False) -> None:
    """Default: main-text Fig 1–2. Legacy bundles for internal exploration."""
    generate_main_figures()
    if not legacy:
        return
    generate_supplement_figures()
    generate_all_methodology_figures()
    generate_challenge_figures()
    generate_discrimination_figures()
    generate_concentration_figures()
    try:
        generate_continuous_model_figures(fine_build=False)
    except Exception:  # noqa: BLE001
        pass
    from lod_guide.paper.journal_figures import generate_journal_figures

    generate_journal_figures()


def _regen_all_figures() -> None:
    """Backward-compatible alias — prefer _regen_paper_figures(legacy=True)."""
    _regen_paper_figures(legacy=True)


def build_paper_artifacts(
    *,
    skip_heavy_exact: bool = True,
    skip_heavy_theory: bool = True,
    legacy_figures: bool = False,
    prune_legacy_figures: bool = True,
) -> dict:
    PAPER.mkdir(parents=True, exist_ok=True)

    theory_meta = ensure_theory_research(force=not skip_heavy_theory)
    captions = write_caption_files(PAPER / "captions")

    try:
        _regen_paper_figures(legacy=legacy_figures)
        journal_fig_error = None
    except Exception as exc:  # noqa: BLE001
        journal_fig_error = str(exc)
        try:
            generate_main_figures()
        except Exception as exc2:  # noqa: BLE001
            journal_fig_error = f"{journal_fig_error}; {exc2}"

    pruned_figures: list[str] = []
    if prune_legacy_figures and not legacy_figures:
        pruned_figures = _prune_non_paper_figures()

    try:
        pp = run_precision_profile_study()
    except Exception as exc:  # noqa: BLE001
        pp = {"error": str(exc)}

    figs = _copy_figures(PAPER / "figures")
    missing = [c for c in figs if c["status"] == "missing_source"]
    if missing:
        try:
            generate_main_figures()
            figs = _copy_figures(PAPER / "figures")
            missing_note = None
        except Exception as exc:  # noqa: BLE001
            missing_note = str(exc)
    else:
        missing_note = None

    loq = build_loq_precision_tables(out_dir=PAPER / "tables")

    try:
        emp = run_empirical_tierA_extension()
    except Exception as exc:  # noqa: BLE001
        emp = {"error": str(exc)}
    try:
        meta = run_tierA_meta_analysis()
    except Exception as exc:  # noqa: BLE001
        meta = {"error": str(exc)}
    try:
        protocol_audit = run_tierA_protocol_audit()
    except Exception as exc:  # noqa: BLE001
        protocol_audit = {"error": str(exc)}
    try:
        e1cov = run_one_proportion_coverage_study()
    except Exception as exc:  # noqa: BLE001
        e1cov = {"error": str(exc)}
    try:
        e3oc = run_e3_operating_characteristics_study()
    except Exception as exc:  # noqa: BLE001
        e3oc = {"error": str(exc)}
    try:
        risk = evaluate_standard_scenarios()
    except Exception as exc:  # noqa: BLE001
        risk = {"error": str(exc)}
    try:
        evrep = build_evidence_stratified_report(download=False)
    except Exception as exc:  # noqa: BLE001
        evrep = {"error": str(exc)}

    print("[paper] building internal review memo + Table 1–6...", flush=True)
    review = write_internal_review_memo(
        force_exact=not skip_heavy_exact,
        force_theory_verify=not skip_heavy_theory,
    )
    ms_tables = build_manuscript_tables()

    manifest = {
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "lod_guide_version": __version__,
        "figures": figs,
        "tables": [t.manuscript_id + " -> " + t.artifact_csv for t in TABLES],
        "manuscript_tables": ms_tables,
        "caption_files": {k: str(v) for k, v in captions.items()},
        "loq_tables": {k: str(v) for k, v in loq.items()},
        "review": {k: str(v) for k, v in review.items()},
        "missing_figure_regen_error": missing_note,
        "journal_figure_error": journal_fig_error,
        "precision_profile": {
            "loq20": (pp or {}).get("target_20", {}).get("loq") if isinstance(pp, dict) else None,
            "path": (pp or {}).get("path") if isinstance(pp, dict) else None,
        },
        "empirical_tierA": emp if isinstance(emp, dict) else {},
        "tierA_meta": meta if isinstance(meta, dict) else {},
        "tierA_protocol_audit": protocol_audit if isinstance(protocol_audit, dict) else {},
        "e1_coverage": e1cov if isinstance(e1cov, dict) else {},
        "e3_operating": e3oc if isinstance(e3oc, dict) else {},
        "decision_risk": risk if isinstance(risk, dict) else {},
        "evidence_stratified": evrep if isinstance(evrep, dict) else {},
        "theory_research": theory_meta,
        "figure_policy": (
            "Main text: Fig 1 (E2 OC, A–D) + Fig 2 (tier A calibration, A–C). "
            "Supplement: tables/JSON only (no supplement figures). "
            "make paper-artifacts generates Fig 1–2; use --legacy-figures for developer bundles."
        ),
        "legacy_figures_built": legacy_figures,
        "pruned_figure_files": pruned_figures,
        "main_figure_count": len(MAIN_FIGURES),
        "supplement_figure_count": len(SUPPLEMENT_FIGURES),
        "publication_readiness": (
            "Clinical Chemistry Article package: LoD verification design + public-data calibration "
            "(Fig 1–2; Tables 1, 3, 7). Tier A deposits calibrate the planner; not multi-assay clinical validation."
        ),
    }
    man_path = PAPER / "MANIFEST.json"
    man_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

    readme = PAPER / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Paper artifacts (auto-generated)",
                "",
                "Build with: `make paper-artifacts` or `python examples/run_paper_artifacts.py`",
                "",
                "## Contents",
                "",
                "- `captions/` — unified Fig/Table captions, FIGURE_PLAN.md, and ID map",
                "- `figures/` — registry main figure(s) only (v7: Fig 1)",
                "- `tables/` — Table 1–8 CSVs (estimands, LoQ, exact vs asymp, P1–P18, evidence, Type I, tier-A meta, E1 coverage)",
                "- `tables/manuscript/` — readable column names for drafting",
                "- `audit/` — theory verification JSON + D1–D3 defect bundle",
                "- `review/` — internal statistical review memo + THEORY_RESEARCH_SUMMARY.md",
                "- `MANIFEST.json` — build stamp",
                "- `manuscript/` — Word draft + cover letter (pandoc)",
                "",
                "## Honest scope",
                "",
                "These files support a **methods / supplement** package with assumption-gated "
                "decision-risk framing. They do not by themselves constitute a finished "
                "Clinical Chemistry full research article.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    manifest["manifest_path"] = str(man_path)

    try:
        word_paths = export_manuscript_docx()
        cover_path = export_cover_letter_docx()
        manifest["manuscript_word"] = {k: str(v) for k, v in word_paths.items()}
        manifest["cover_letter_docx"] = str(cover_path)
    except Exception as exc:  # noqa: BLE001
        manifest["manuscript_word_error"] = str(exc)

    return manifest


if __name__ == "__main__":
    print(json.dumps(build_paper_artifacts(), indent=2, default=str))
