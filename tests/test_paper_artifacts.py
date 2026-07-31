"""Tests for paper artifact registry and builders."""

from __future__ import annotations

from pathlib import Path

from lod_guide.paper.loq_precision import build_loq_precision_tables, design_rows_cv_and_ci
from lod_guide.paper.registry import FIGURES, MAIN_FIGURES, SUPPLEMENT_FIGURES, TABLES, write_caption_files
from lod_guide.paper.build_artifacts import build_paper_artifacts
from lod_guide.theory.propositions import verify_all_propositions


def _figure_sort_key(manuscript_id: str) -> tuple[int, int | str]:
    parts = manuscript_id.split()
    token = parts[1]
    if token.startswith("S"):
        suffix = token[1:]
        if suffix.startswith("-"):
            return (1, 0)  # Fig S-LoB before numbered supplement figures
        return (1, int(suffix))
    return (0, int(token))


def test_figure_table_ids_unique_and_ordered():
    fig_ids = [f.manuscript_id for f in FIGURES]
    tab_ids = [t.manuscript_id for t in TABLES]
    assert fig_ids == sorted(fig_ids, key=_figure_sort_key)
    assert tab_ids == sorted(tab_ids, key=lambda s: int(s.split()[1]))
    assert len(fig_ids) == len(set(fig_ids))
    assert len(MAIN_FIGURES) == 5
    assert len(SUPPLEMENT_FIGURES) == 10
    assert len(FIGURES) == 15
    assert len(TABLES) >= 5
    assert all(f.caption and len(f.caption) > 40 for f in FIGURES)
    assert all(t.caption and len(t.caption) > 40 for t in TABLES)


def test_loq_design_rows_monotonic():
    rows = design_rows_cv_and_ci(
        sigma_over_mu_grid=(0.25, 0.40),
        target_cv_pct_grid=(20.0, 10.0),
        half_width_frac_grid=(0.10,),
    )
    cv_rows = [r for r in rows if r["block"] == "CV_of_mean"]
    # tighter CV target => larger n at same sigma/mu
    n_20 = next(r["n_required"] for r in cv_rows if r["sigma_over_mu"] == 0.25 and r["target_CV_pct"] == 20.0)
    n_10 = next(r["n_required"] for r in cv_rows if r["sigma_over_mu"] == 0.25 and r["target_CV_pct"] == 10.0)
    assert n_10 > n_20
    # larger imprecision => larger n at same target
    n_hi = next(r["n_required"] for r in cv_rows if r["sigma_over_mu"] == 0.40 and r["target_CV_pct"] == 20.0)
    assert n_hi > n_20


def test_build_loq_writes(tmp_path):
    out = build_loq_precision_tables(out_dir=tmp_path)
    assert out["main"].exists()
    text = out["main"].read_text(encoding="utf-8")
    assert "CV_of_mean" in text
    assert "n_required" in text


def test_captions_write(tmp_path):
    paths = write_caption_files(tmp_path)
    fig_text = paths["figures"].read_text(encoding="utf-8")
    assert "Fig 1" in fig_text
    assert "Fig S1" in fig_text
    assert paths["plan"].exists()
    assert "Table 2" in paths["tables"].read_text(encoding="utf-8")


def test_propositions_all_pass():
    certs = verify_all_propositions()
    assert len(certs) == 22
    assert all(c.passed for c in certs)


def test_build_paper_artifacts_smoke(tmp_path, monkeypatch):
    import lod_guide.paper.build_artifacts as ba
    import lod_guide.paper.registry as reg
    import lod_guide.paper.loq_precision as lp
    import lod_guide.paper.internal_review as ir
    import lod_guide.paper.manuscript_tables as mt

    monkeypatch.setattr(ba, "PAPER", tmp_path)
    monkeypatch.setattr(reg, "PAPER", tmp_path)
    monkeypatch.setattr(mt, "PAPER", tmp_path)
    monkeypatch.setattr(lp, "OUT", tmp_path / "tables")
    monkeypatch.setattr(ir, "PAPER", tmp_path)
    monkeypatch.setattr(ir, "TABLES", tmp_path / "tables")
    monkeypatch.setattr(ir, "REVIEW", tmp_path / "review")

    man = build_paper_artifacts(skip_heavy_exact=False)
    assert (tmp_path / "MANIFEST.json").exists()
    assert (tmp_path / "captions" / "FIGURE_CAPTIONS.md").exists()
    assert (tmp_path / "tables" / "Table02_loq_precision_main.csv").exists()
    assert (tmp_path / "tables" / "Table03_exact_vs_asymptotic.csv").exists()
    assert (tmp_path / "tables" / "Table04_propositions_P1_P6.csv").exists()
    assert (tmp_path / "review" / "INTERNAL_REVIEW_P1P6_EXACT.md").exists()
    assert "publication_readiness" in man
    assert "figure_policy" in man
    assert man.get("main_figure_count") == 5
    assert len(FIGURES) == 15
    assert len(TABLES) >= 8