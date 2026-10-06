"""Tests for E3 operating characteristics export (Table 9)."""

from __future__ import annotations

from pathlib import Path

from lod_guide.research.e3_operating_characteristics import (
    e3_grid_rows,
    e3_vs_e2_confusion_rows,
    k_values_for_n,
    min_n_for_pass,
    pass_probability,
    run_e3_operating_characteristics_study,
)


def test_pass_probability_bounds():
    assert pass_probability(p=0.95, n=20, k=19) == pass_probability(p=0.95, n=20, k=19)
    p = pass_probability(p=0.80, n=20, k=19)
    assert 0.0 < p < 1.0


def test_min_n_for_pass_at_anchor():
    n = min_n_for_pass(p=0.95, k=19, target=0.95)
    assert n is not None and n >= 19


def test_g4_vs_g2_headline():
    rows = e3_vs_e2_confusion_rows()
    headline = next(r for r in rows if r["pair"] == "90/80")
    assert headline["miss_beta_fisher"] > 0.8
    assert headline["P_both_arms_pass"] > 0.0


def test_g4_grid_row_count():
    rows = e3_grid_rows()
    assert len(rows) == 20 * sum(len(k_values_for_n(n)) for n in (10, 20, 30, 60))


def test_g4_study_writes_tables(tmp_path, monkeypatch):
    import lod_guide.research.e3_operating_characteristics as mod

    monkeypatch.setattr(mod, "PAPER_TABLES", tmp_path)
    out = run_e3_operating_characteristics_study()
    assert Path(out["tables"]["grid"]).exists()
    assert Path(out["tables"]["g4_vs_g2"]).exists()
