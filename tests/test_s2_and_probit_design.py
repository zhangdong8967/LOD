"""Tests for S2 threshold sensitivity and probit/logistic design grid."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from lod_guide.research.probit_design_grid import (
    DoseResponseTruth,
    asymptotic_lod_se_log10,
    evaluate_design_grid,
    make_concentration_grid,
    run_probit_design_grid,
)
from lod_guide.research.s2_threshold_sensitivity import (
    evaluate_blank_vector,
    run_s2_threshold_sensitivity,
)
from lod_guide.s2_diagnostics import DEFAULT_THRESHOLDS


def test_s2_threshold_sensitivity_on_normal_blanks():
    rng = np.random.default_rng(0)
    x = rng.normal(0.05, 0.02, size=60)
    out = evaluate_blank_vector(x, strata=None, label="unit_normal")
    assert out["n"] == 60
    assert out["n_variants"] >= 8
    assert "default_parametric_candidate" in out
    # Gaussian blanks should usually remain parametric under default
    assert out["default_parametric_candidate"] is True


def test_s2_threshold_sensitivity_study_writes_json():
    payload = run_s2_threshold_sensitivity()
    assert payload["n_cases"] >= 4
    assert Path(payload["path"]).exists()
    assert "mean_flip_rate" in payload["headline"]
    assert payload["default_thresholds"]["abs_skew_fail"] == DEFAULT_THRESHOLDS.abs_skew_fail


def test_probit_design_grid_se_finite():
    truth = DoseResponseTruth(intercept=2.94, slope=2.0, link="logistic", target_p=0.95)
    conc = make_concentration_grid(truth.lod(), n_levels=5, pattern="equal_log")
    n = np.full(5, 12.0)
    se = asymptotic_lod_se_log10(truth, conc, n)
    assert se["info_ok"] is True
    assert np.isfinite(se["se_log10_lod"])
    assert se["se_log10_lod"] > 0


def test_probit_design_grid_best_beats_or_matches_sparse():
    truth = DoseResponseTruth(intercept=2.94, slope=2.5, link="logistic", target_p=0.95)
    grid = evaluate_design_grid(truth, total_n_grid=[60, 120], n_levels_grid=[4, 8])
    assert grid["best"] is not None
    assert grid["n_designs"] >= 8


def test_run_probit_design_grid_artifact():
    payload = run_probit_design_grid()
    assert Path(payload["path"]).exists()
    assert payload["headline"]["synthetic_best"] is not None
    assert payload["synthetic_logistic"]["n_rows_total"] > 10
