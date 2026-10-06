"""Tests for E2 lattice surface model (marginal by Δ)."""

from lod_guide.research.comparison_grid_export import build_comparison_grid
from lod_guide.research.lattice_surface_model import (
    build_lattice_surface_model,
    export_lattice_surface_tables,
    marginal_by_delta,
    summarize_delta_bands,
)
from lod_guide.research.comparison_grid_export import grid_arrays


def test_lattice_surface_model_valid_cells():
    model = build_lattice_surface_model(force=True)
    assert model["lattice"]["n_valid_cells"] == 1225
    assert len(model["marginal_by_delta"]) == 49
    assert model["summary"]["asymptotic_surface_check"]["max_abs_error"] < 1e-9


def test_marginal_by_delta_monotone_nstar():
    grid = build_comparison_grid()
    pa, pb, _, _, nstar = grid_arrays(grid)
    rows = marginal_by_delta(pa, pb, nstar, stat="median")
    # smaller delta -> larger n* (median)
    n_at_5 = next(r["median_value"] for r in rows if r["delta_pp"] == 5)
    n_at_40 = next(r["median_value"] for r in rows if r["delta_pp"] == 40)
    assert n_at_5 > n_at_40


def test_delta_bands_are_the_display_object():
    grid = build_comparison_grid()
    pa, pb, _, miss, nstar = grid_arrays(grid)
    bands = {r["band"]: r for r in summarize_delta_bands(pa, pb, miss, nstar)}
    assert set(bands) == {"1-5", "6-10", "11-20", ">20"}
    assert bands["1-5"]["n_cells"] == 235
    assert bands["6-10"]["n_cells"] == 210
    assert bands["1-5"]["frac_beta_gt_0.8"] == 1.0
    assert bands["6-10"]["frac_beta_gt_0.8"] == 1.0
    assert bands[">20"]["median_n_star_ceiling"] < bands["1-5"]["median_n_star_ceiling"]
    model = build_lattice_surface_model(force=True)
    assert "delta_bands" in model
    assert model["illustrative_pair"]["p_a"] == 0.90


def test_export_lattice_surface_tables(tmp_path):
    paths = export_lattice_surface_tables(tmp_path)
    assert (tmp_path / "Table03f_marginal_by_delta.csv").exists()
    assert paths["marginal_by_delta"].endswith("Table03f_marginal_by_delta.csv")
