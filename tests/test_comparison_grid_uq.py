"""Tests for Tier-2 E2 grid UQ (sensitivity bands)."""

from __future__ import annotations

from lod_guide.research.comparison_grid_uq import (
    asymptotic_miss_beta_surface,
    build_grid_uq_summary,
    export_grid_uq_tables,
    nstar_surface,
    p8_gap_mask,
    sensitivity_contour_levels,
)


def test_asymptotic_miss_beta_monotone_in_alpha():
    miss_strict = asymptotic_miss_beta_surface(alpha=0.01)
    miss_lenient = asymptotic_miss_beta_surface(alpha=0.10)
    valid = miss_strict == miss_strict  # finite mask
    # Higher α → higher power → lower miss β.
    assert (miss_strict[valid] >= miss_lenient[valid] - 1e-9).all()


def test_nstar_increases_with_target_power():
    n70 = nstar_surface(target_power=0.70)
    n90 = nstar_surface(target_power=0.90)
    valid = n70 == n70
    assert (n90[valid] >= n70[valid] - 1e-9).all()


def test_build_grid_uq_summary():
    uq = build_grid_uq_summary(force=True)
    assert uq["spec_version"] == "tier2_v1"
    assert uq["summary"]["frac_miss_gt_0.8_exact_fisher"] > 0.5
    assert uq["summary"]["frac_p8_gap_cells"] > 0.0


def test_p8_gap_mask_shape():
    mask = p8_gap_mask()
    miss = asymptotic_miss_beta_surface()
    assert mask.shape == miss.shape


def test_sensitivity_contour_levels():
    miss_spec = sensitivity_contour_levels("miss_beta")
    n_spec = sensitivity_contour_levels("n_star")
    assert miss_spec["level"] == 0.8
    assert miss_spec["surfaces"]["lo"].shape == n_spec["surfaces"]["lo"].shape


def test_export_grid_uq_tables(tmp_path):
    paths = export_grid_uq_tables(tmp_path)
    assert paths["summary"].endswith("Table03d_grid_uq_sensitivity.csv")
    assert paths["p8_gap"].endswith("Table03e_p8_gap_cells.csv")
