"""Tests for E2 comparison grid export (Table 3 extensions)."""

from __future__ import annotations

from lod_guide.research.comparison_grid_export import (
    REF_PAIRS,
    build_comparison_grid,
    compare_asymptotic_scenarios,
    export_comparison_grid_tables,
    grid_csv_rows,
    reference_pair_rows,
)


def test_ref_pairs_count():
    assert len(REF_PAIRS) == 8


def test_comparison_grid_valid_cells():
    grid = build_comparison_grid()
    assert grid["summary"]["n_valid_cells"] >= 1200
    rows = grid_csv_rows(grid)
    assert len(rows) == grid["summary"]["n_valid_cells"]


def test_reference_pair_rows_complete():
    rows = reference_pair_rows()
    assert len(rows) == 8
    for r in rows:
        assert 0 <= r["power_exact_fisher"] <= 1
        assert r["miss_beta_exact_fisher"] == 1 - r["power_exact_fisher"]
        assert r["n_star_ceiling"] >= r["n"]
        if r["power_exact_fisher_at_n_star"] is not None:
            assert 0 <= r["power_exact_fisher_at_n_star"] <= 1
    headline = next(r for r in rows if r["pair"] == "90/80")
    assert headline["n_star_ceiling"] == 199
    assert headline["power_exact_fisher_at_n_star"] is not None
    assert headline["power_exact_fisher_at_n_star"] >= 0.75


def test_compare_asymptotic_scenarios_includes_all_ref_at_n20():
    scenarios = compare_asymptotic_scenarios()
    n20 = [s for s in scenarios if s[3] == 20]
    assert len(n20) == 8


def test_export_comparison_grid_tables(tmp_path):
    paths = export_comparison_grid_tables(tmp_path)
    assert (tmp_path / "Table03_reference_pairs_n20.csv").exists()
    assert (tmp_path / "Table03_comparison_grid_n20.csv").exists()
    assert paths["reference_pairs"].endswith("Table03_reference_pairs_n20.csv")
