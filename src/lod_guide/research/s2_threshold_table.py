"""
Export frozen S2 diagnostic thresholds for the online supplement (Table 2a).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from lod_guide.paper.registry import PAPER
from lod_guide.s2_diagnostics import DEFAULT_THRESHOLDS
from lod_guide.thresholds import THRESHOLD_SPEC

TABLE_NAME = "Table02a_s2_diagnostic_thresholds.csv"


def s2_threshold_rows() -> list[dict[str, str]]:
    t = DEFAULT_THRESHOLDS
    return [
        {
            "Domain": "Shape",
            "Diagnostic": "|skewness|",
            "Warn_threshold": str(t.abs_skew_warn),
            "Fail_threshold": str(t.abs_skew_fail),
            "Test_or_rule": "Sample skewness on blank or near-LoD series",
            "If_fail": "S3 transform attempt; shape fail blocks parametric candidacy",
        },
        {
            "Domain": "Shape",
            "Diagnostic": "|excess kurtosis|",
            "Warn_threshold": str(t.abs_excess_kurtosis_warn),
            "Fail_threshold": str(t.abs_excess_kurtosis_fail),
            "Test_or_rule": "Fisher excess kurtosis",
            "If_fail": "S3 transform attempt; shape fail blocks parametric candidacy",
        },
        {
            "Domain": "Shape",
            "Diagnostic": "Normality",
            "Warn_threshold": "",
            "Fail_threshold": f"p < {t.normality_alpha}",
            "Test_or_rule": f"Shapiro–Wilk if n ≥ {t.min_n_normality_test}",
            "If_fail": "Shape fail; route to S4b if S3 cannot recover",
        },
        {
            "Domain": "Censoring",
            "Diagnostic": "Floor / censoring rate",
            "Warn_threshold": f"{t.censoring_warn:.0%}",
            "Fail_threshold": f"{t.censoring_fail:.0%}",
            "Test_or_rule": "Fraction at or below reporting floor",
            "If_fail": "Censoring fail; nonparametric LoB path (S4b)",
        },
        {
            "Domain": "Heterogeneity",
            "Diagnostic": "ICC(1)",
            "Warn_threshold": str(t.icc_warn),
            "Fail_threshold": str(t.icc_fail),
            "Test_or_rule": "One-way random-effects ICC across strata",
            "If_fail": "Fail: not poolable; warn: prefer stratum-aware n or DE inflation",
        },
        {
            "Domain": "Heterogeneity",
            "Diagnostic": "Levene (median)",
            "Warn_threshold": "",
            "Fail_threshold": f"p < {t.levene_alpha}",
            "Test_or_rule": "Levene test across strata (≥2 groups)",
            "If_fail": "Heterogeneity fail; not poolable",
        },
        {
            "Domain": "Heterogeneity",
            "Diagnostic": "Between-stratum CV",
            "Warn_threshold": str(t.between_stratum_cv_warn),
            "Fail_threshold": str(t.between_stratum_cv_fail),
            "Test_or_rule": "SD(stratum means) / |grand mean|",
            "If_fail": "Fail: not poolable; warn: DE or stratified design",
        },
        {
            "Domain": "Gate",
            "Diagnostic": "parametric_candidate",
            "Warn_threshold": "",
            "Fail_threshold": "Any shape, censoring, or heterogeneity fail",
            "Test_or_rule": "Logical AND of S2 pass flags",
            "If_fail": "S4b nonparametric LoB; sets mismatch flag M in audit ledger L",
        },
    ]


def export_s2_threshold_table(out_dir: Path | None = None) -> dict[str, str]:
    out_dir = out_dir or (PAPER / "tables")
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = s2_threshold_rows()
    fieldnames = list(rows[0].keys())
    csv_path = out_dir / TABLE_NAME
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    json_path = out_dir.parent / "research" / "s2_threshold_spec.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "spec_version": THRESHOLD_SPEC["version"],
        "table_csv": str(csv_path),
        "thresholds": THRESHOLD_SPEC,
        "parametric_candidate_rule": "shape_ok AND censoring_ok AND heterogeneity_ok",
        "s3_methods": ["log", "box_cox", "sqrt", "robust_mad", "failed_use_nonparametric"],
        "s4_paths": [
            "parametric_normal",
            "parametric_lognormal",
            "parametric_gamma",
            "nonparametric_percentile",
            "nonparametric_bootstrap",
        ],
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"csv": str(csv_path), "json": str(json_path)}


if __name__ == "__main__":
    print(json.dumps(export_s2_threshold_table(), indent=2))
