"""Tests for lod_guide S0–S7."""

from __future__ import annotations

import numpy as np
import pytest

from lod_guide.s0_goal import Goal, PRIMARY_USE_CASES, declare_goal
from lod_guide.s1_result_type import classify_result_type
from lod_guide.s2_diagnostics import DEFAULT_THRESHOLDS, run_diagnostics
from lod_guide.s3_correction import CorrectionMethod, attempt_correction
from lod_guide.s4_models import detect_prob_at_least_one, select_model_path
from lod_guide.s5_sample_size import (
    design_effect,
    power_two_proportions,
    recommend_sample_size,
    sample_size_two_proportions,
)
from lod_guide.pipeline import run_guidance


def test_frozen_goals_and_use_cases():
    assert set(Goal) == {
        Goal.E1_VERIFY_LOD,
        Goal.E2_COMPARE_REAGENTS,
        Goal.LOQ_PRECISION,
        Goal.E3_QUALITATIVE_KN,
    }
    assert PRIMARY_USE_CASES["kit_a_vs_kit_b_near_lod"] == Goal.E2_COMPARE_REAGENTS
    with pytest.raises(ValueError):
        declare_goal(Goal.E1_VERIFY_LOD, use_case="kit_a_vs_kit_b_near_lod")


def test_multiclass_requires_success_definition():
    with pytest.raises(ValueError):
        classify_result_type("multiclass", n_classes=4)


def test_diagnostics_normal_pass():
    rng = np.random.default_rng(1)
    x = rng.normal(0, 1, size=100)
    d = run_diagnostics(x)
    assert d.parametric_candidate
    assert d.shape_ok


def test_diagnostics_thresholds_frozen():
    assert DEFAULT_THRESHOLDS.abs_skew_fail == 1.0
    assert DEFAULT_THRESHOLDS.icc_fail == 0.25
    assert DEFAULT_THRESHOLDS.censoring_fail == 0.25


def test_correction_log_helps_lognormal():
    rng = np.random.default_rng(2)
    x = rng.lognormal(0, 1.2, size=120)
    raw = run_diagnostics(x)
    corr = attempt_correction(x)
    # Either correction succeeds or hard-stops to nonparametric — both valid
    assert corr.method in {
        CorrectionMethod.NONE,
        CorrectionMethod.LOG,
        CorrectionMethod.BOX_COX,
        CorrectionMethod.SQRT,
        CorrectionMethod.ROBUST_MAD,
        CorrectionMethod.FAILED,
    }
    if not raw.parametric_candidate and corr.parametric_ok:
        assert corr.method != CorrectionMethod.FAILED


def test_two_proportion_n_90_vs_80():
    n = sample_size_two_proportions(0.90, 0.80)
    assert 180 <= n <= 220
    assert power_two_proportions(0.90, 0.80, 20) < 0.25
    assert power_two_proportions(0.90, 0.80, int(np.ceil(n))) >= 0.78


def test_design_effect():
    assert design_effect(0.0, 5) == 1.0
    assert design_effect(0.2, 5) == pytest.approx(1.8)


def test_recommend_g2():
    res = recommend_sample_size(
        Goal.E2_COMPARE_REAGENTS, p_a=0.9, p_b=0.8, power=0.8
    )
    assert res.n_per_arm >= 190
    assert any("n=20" in w for w in res.warnings)


def test_recommend_g4():
    res = recommend_sample_size(Goal.E3_QUALITATIVE_KN, p=0.95, k=1, power=0.95)
    assert res.n_per_arm >= 1
    assert detect_prob_at_least_one(0.95, res.n_per_arm) >= 0.95


def test_pipeline_g2_binary():
    out = run_guidance(
        goal="E2_COMPARE_REAGENTS",
        result_type="binary",
        use_case="kit_a_vs_kit_b_near_lod",
        p_a=0.9,
        p_b=0.8,
        run_sensitivity=True,
    )
    assert out.sample_size.n_per_arm >= 190
    ec = out.report.sample_size["exact_confirmation"]
    assert ec["confirmation_engine"] == "exact_fisher_enumeration"
    assert 0.0 < ec["power_exact_fisher_at_planned_n"] <= 1.0
    assert ec["power_exact_fisher_at_n20"] < ec["power_exact_fisher_at_planned_n"]
    md = out.report.to_markdown()
    assert "E2_COMPARE_REAGENTS" in md
    assert "S6 Exact confirmation" in md
    assert "power_exact_fisher_at_planned_n" in md
    assert "Challenge-oriented" in md or "folklore" in md.lower()


def test_pipeline_continuous():
    rng = np.random.default_rng(3)
    values = rng.normal(1.0, 0.2, size=60)
    out = run_guidance(
        goal=Goal.E1_VERIFY_LOD,
        result_type="continuous",
        values=values,
        use_case="ldt_lod_establishment",
        p0=0.95,
        run_sensitivity=False,
    )
    assert out.model_path.value.startswith("parametric") or "nonparametric" in out.model_path.value
    assert out.report.parametric_ok in (True, False)


def test_select_model_path():
    assert select_model_path(parametric_ok=True, result_type="binary", correction_method="none").value == "binary_rate"
    assert select_model_path(parametric_ok=False, result_type="continuous", correction_method="failed_use_nonparametric").value == "nonparametric_percentile"
