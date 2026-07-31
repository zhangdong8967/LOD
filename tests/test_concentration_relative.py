"""Tests for concentration-relative LoD evaluation."""

from __future__ import annotations

from lod_guide.research.concentration_relative import (
    KitCurve,
    evaluate_concentration_grid,
    run_concentration_relative_study,
    verify_claim_pass_prob,
)


def test_verify_all_positive_equals_p_n():
    assert abs(verify_claim_pass_prob(0.8, 5, rule="all_positive") - 0.8**5) < 1e-12


def test_at_lod_ref_near_gamma():
    grid = evaluate_concentration_grid(relative_levels=(1.0,))
    row = grid["rows"][0]
    assert abs(row["p_A"] - 0.95) < 1e-6
    assert abs(row["p_B"] - 0.80) < 1e-3


def test_above_lod_shrinks_delta_and_raises_miss():
    grid = evaluate_concentration_grid(relative_levels=(1.0, 2.0), n_compare=20)
    at_, above = grid["rows"][0], grid["rows"][1]
    assert above["delta_p"] < at_["delta_p"]
    assert above["compare_miss_beta"] > at_["compare_miss_beta"]


def test_below_lod_lower_pass_for_ref():
    grid = evaluate_concentration_grid(relative_levels=(0.5, 1.0), n_verify=20)
    below, at_ = grid["rows"][0], grid["rows"][1]
    assert below["P_pass_A_rate_ge_claim"] < at_["P_pass_A_rate_ge_claim"]


def test_study_writes_headlines():
    out = run_concentration_relative_study()
    assert out["must_evaluate"] is True
    assert out["headlines"]["at_r1.0_lod"]["zone"] == "at_LoD"
