"""Tests for continuous parameter-space LoD models."""

from __future__ import annotations

import numpy as np

from lod_guide.research.continuous_models import (
    build_all_continuous_models,
    build_all_positive_field,
    build_discrimination_field,
    query_all_positive,
    query_discrimination,
)


def test_all_positive_field_matches_closed_form():
    field = build_all_positive_field(
        p_grid=np.array([0.8, 0.9, 1.0]),
        n_grid=np.array([5, 10]),
    )
    F = np.array(field["F_p_n"])
    # F shape (n, p) from meshgrid indexing xy
    assert abs(F[0, 0] - 0.8**5) < 1e-12
    assert abs(F[1, 1] - 0.9**10) < 1e-12
    assert abs(field["L_one_sided"][0] - 0.05 ** (1 / 5)) < 1e-12
    assert abs(field["B_p_below_claim"][0] - 0.95**6) < 1e-12


def test_query_all_positive_any_p_n():
    q = query_all_positive(0.83, 12)
    assert abs(q["P_all_positive"] - 0.83**12) < 1e-12
    assert q["n"] == 12


def test_discrimination_surface_contains_example_points():
    disc = build_discrimination_field(
        p_a_grid=np.linspace(0.5, 0.95, 10),
        p_b_grid=np.linspace(0.4, 0.9, 10),
        n_grid=np.array([20]),
    )
    # upper triangle finite somewhere
    ns = np.array(disc["n_star_pa_pb"])
    assert np.isfinite(ns).sum() > 0
    q80 = query_discrimination(0.9, 0.8, 20)
    q50 = query_discrimination(0.9, 0.5, 20)
    assert q80["n_star_80"] > q50["n_star_80"]
    assert q80["miss_beta"] > q50["miss_beta"]


def test_build_all_continuous_models_coarse(tmp_path, monkeypatch):
    import lod_guide.research.continuous_models as cm

    monkeypatch.setattr(cm, "OUT_DIR", tmp_path)
    meta = build_all_continuous_models(fine=False)
    assert (tmp_path / "all_positive_field.npz").exists()
    assert (tmp_path / "discrimination_field.npz").exists()
    assert (tmp_path / "concentration_field.npz").exists()
    assert "slices" in meta["philosophy"].lower() or "continuous" in meta["philosophy"].lower()
    # example points recover known ordering
    ex = meta["discrimination_summary"]["example_points"]
    assert ex["0.90_vs_0.80"]["n_star_80"] > ex["0.90_vs_0.50"]["n_star_80"]
