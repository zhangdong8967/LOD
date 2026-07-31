"""Tests for the all-positive trap mathematics."""

from __future__ import annotations

from lod_guide.research.all_positive_trap import (
    exact_lower_bound_after_all_success,
    inference_after_all_positive,
    prob_all_positive,
    probability_true_p_below_claim_given_all_positive_uniform,
    prop_all_positive_closed_forms,
    run_all_positive_trap_study,
)


def test_p_to_the_n():
    assert abs(prob_all_positive(0.8, 5) - 0.8**5) < 1e-15
    assert abs(prob_all_positive(0.7, 10) - 0.7**10) < 1e-15


def test_cp_lower_closed_form():
    cert = prop_all_positive_closed_forms()
    assert cert["passed"]
    # one-sided n=5: 0.05**(1/5) ≈ 0.55; two-sided ≈ 0.48
    assert 0.54 < exact_lower_bound_after_all_success(5, two_sided=False) < 0.56
    assert 0.47 < exact_lower_bound_after_all_success(5, two_sided=True) < 0.49
    assert 0.73 < exact_lower_bound_after_all_success(10, two_sided=False) < 0.75


def test_n5_n10_cannot_support_p95():
    inf5 = inference_after_all_positive(5, claim_p0=0.95)
    inf10 = inference_after_all_positive(10, claim_p0=0.95)
    assert inf5.cp_low < 0.95
    assert inf10.cp_low < 0.95
    # Compatible in the weak sense (claim not below lower bound? wait - claim 0.95 > cp_low
    # so compatible_with_claim True means claim is ABOVE lower bound i.e. not ruled out
    assert inf5.compatible_with_claim is True
    assert inf5.rejects_claim_one_sided is False


def test_bayes_residual_risk_high_for_n5():
    b = probability_true_p_below_claim_given_all_positive_uniform(5, 0.95)
    assert b["P_true_p_below_claim_given_all_positive"] > 0.7


def test_study_writes_highlights():
    out = run_all_positive_trap_study()
    assert out["highlights"]["P_all_pos_given_p080_n5"] > 0.3
    assert out["highlights"]["CP_lower_n5_onesided"] < 0.6
    assert out["highlights"]["CP_lower_n5_twosided"] < out["highlights"]["CP_lower_n5_onesided"]
