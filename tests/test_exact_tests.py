"""Tests for exact / Boschloo small-sample methods."""

from __future__ import annotations

from lod_guide.s5_sample_size import power_two_proportions, power_two_proportions_exact
from lod_guide.theory.exact_tests import (
    boschloo_pvalue,
    exact_power_two_proportions,
    fisher_pvalue,
    sample_size_exact_search,
    analyze_two_proportions_exact,
)


def test_fisher_all_equal_is_one():
    assert fisher_pvalue(10, 20, 10, 20) == 1.0


def test_boschloo_leq_fisher_typically():
    # Boschloo p should be <= Fisher p (less or equally conservative)
    r = analyze_two_proportions_exact(18, 20, 12, 20)
    assert r.boschloo_p_two_sided <= r.fisher_p_two_sided + 1e-12


def test_exact_power_hard_case_low_at_n20():
    pw = exact_power_two_proportions(0.9, 0.8, 20, test="fisher")
    assert pw < 0.35  # folklore n severely underpowered


def test_exact_power_easy_case_ok_at_n20():
    pw = exact_power_two_proportions(0.9, 0.5, 20, test="fisher")
    assert pw > 0.70


def test_exact_n_star_90_vs_50_near_asymp():
    out = sample_size_exact_search(0.9, 0.5, test="fisher", n_max=60)
    assert out["n_star_exact"] is not None
    assert 10 <= out["n_star_exact"] <= 40


def test_s5_exact_wrapper_matches():
    a = power_two_proportions_exact(0.9, 0.5, 20, test="fisher")
    b = exact_power_two_proportions(0.9, 0.5, 20, test="fisher")
    assert abs(a - b) < 1e-15


def test_asymp_and_exact_same_order():
    # Both should say n=20 is weak for 90 vs 80
    assert power_two_proportions(0.9, 0.8, 20) < 0.25
    assert exact_power_two_proportions(0.9, 0.8, 20, test="fisher") < 0.35
