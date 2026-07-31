"""Frozen S2 diagnostic threshold specification (v0.1)."""

from lod_guide.s2_diagnostics import DEFAULT_THRESHOLDS, DiagnosticThresholds

__all__ = ["DEFAULT_THRESHOLDS", "DiagnosticThresholds", "THRESHOLD_SPEC"]

THRESHOLD_SPEC = {
    "version": "0.1.0",
    "shape": {
        "abs_skew_warn": DEFAULT_THRESHOLDS.abs_skew_warn,
        "abs_skew_fail": DEFAULT_THRESHOLDS.abs_skew_fail,
        "abs_excess_kurtosis_warn": DEFAULT_THRESHOLDS.abs_excess_kurtosis_warn,
        "abs_excess_kurtosis_fail": DEFAULT_THRESHOLDS.abs_excess_kurtosis_fail,
        "normality_alpha": DEFAULT_THRESHOLDS.normality_alpha,
    },
    "censoring": {
        "warn": DEFAULT_THRESHOLDS.censoring_warn,
        "fail": DEFAULT_THRESHOLDS.censoring_fail,
    },
    "heterogeneity": {
        "icc_warn": DEFAULT_THRESHOLDS.icc_warn,
        "icc_fail": DEFAULT_THRESHOLDS.icc_fail,
        "levene_alpha": DEFAULT_THRESHOLDS.levene_alpha,
        "between_stratum_cv_warn": DEFAULT_THRESHOLDS.between_stratum_cv_warn,
        "between_stratum_cv_fail": DEFAULT_THRESHOLDS.between_stratum_cv_fail,
    },
}
