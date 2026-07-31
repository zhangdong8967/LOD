"""Tests for reagent discrimination evaluation."""

from __future__ import annotations

from lod_guide.research.reagent_discrimination import (
    LogisticLoDCurve,
    continuous_p_grid,
    evaluate_pair,
    evaluation_algorithm_spec,
    miss_probability,
    run_continuous_discrimination_study,
    run_reagent_discrimination_study,
)


def test_algorithm_declares_mandatory():
    spec = evaluation_algorithm_spec()
    assert spec["must_evaluate_in_this_research"] is True
    assert spec["false_conclusion"]["must_evaluate"] is True


def test_90_vs_80_needs_large_n():
    sc = evaluate_pair(0.90, 0.80, label="t")
    assert 180 <= sc.n_star_80 <= 220
    assert sc.miss_prob_at_n[20] > 0.75


def test_90_vs_50_much_easier():
    sc = evaluate_pair(0.90, 0.50, label="t")
    assert sc.n_star_80 < 40
    assert sc.miss_prob_at_n[20] < 0.25


def test_miss_is_one_minus_power():
    assert abs(miss_probability(0.9, 0.8, 199) - (1 - 0.8)) < 0.05


def test_relative_lod_monotonic():
    c = LogisticLoDCurve(slope=2.0)
    assert abs(c.lod_multiplier_for_p(0.95) - 1.0) < 1e-9
    assert c.lod_multiplier_for_p(0.50) < c.lod_multiplier_for_p(0.80) < c.lod_multiplier_for_p(0.90) < 1.0


def test_continuous_percent_grid_99_to_50():
    g = continuous_p_grid(99, 50, 1)
    assert g[0] == 0.99
    assert g[-1] == 0.50
    assert len(g) == 50  # 99..50 inclusive


def test_continuous_discrimination_study():
    out = run_continuous_discrimination_study()
    assert out["headline"]["n_competitor_points_per_99pct_curve"] == 49  # 98..50
    assert out["headline"]["n_star_99_vs_98"] > out["headline"]["n_star_99_vs_50"]
    assert out["headline"]["n_star_90_vs_80"] >= 180
    assert abs(out["headline"]["miss20_90_vs_80"] - evaluate_pair(0.9, 0.8).miss_prob_at_n[20]) < 1e-9
    # relative LoD continuum covers every integer percent
    pcts = {r["p_pct"] for r in out["relative_lod_continuum"]}
    assert pcts == set(range(50, 100))


def test_study_headline_keys():
    # smaller MC for test speed
    out = run_reagent_discrimination_study(n_sims_check=800, seed=1)
    assert out["headline"]["90_vs_80_n_star_80power"] >= 190
    assert out["headline"]["90_vs_80_miss_at_n20"] > 0.7
    assert out["headline"]["90_vs_50_n_star_80power"] < 40
    assert out.get("continuous_headline", {}).get("n_star_90_vs_80") is not None
