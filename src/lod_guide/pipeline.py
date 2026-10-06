"""
End-to-end S0→S7 guidance pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from lod_guide.s0_goal import Goal, GoalSpec, declare_goal
from lod_guide.s1_result_type import ResultType, ResultTypeSpec, classify_result_type
from lod_guide.s2_diagnostics import (
    DEFAULT_THRESHOLDS,
    DiagnosticFlags,
    DiagnosticThresholds,
    run_diagnostics,
)
from lod_guide.s3_correction import CorrectionResult, attempt_correction
from lod_guide.s4_gated_lob import LoBEstimationMode
from lod_guide.s4_models import (
    ModelPath,
    estimate_lob_lod,
    select_model_path,
)
from lod_guide.s5_sample_size import SampleSizeResult, exact_confirmation_ledger, recommend_sample_size
from lod_guide.s6_report import GuidanceReport
from lod_guide.s7_sensitivity import sensitivity_compare_reagents
from lod_guide.theory.detection_limit_semantics import dual_five_percent_frame


@dataclass
class GuidanceResult:
    goal: GoalSpec
    result_type: ResultTypeSpec
    diagnostics: DiagnosticFlags | None
    correction: CorrectionResult | None
    model_path: ModelPath
    sample_size: SampleSizeResult
    report: GuidanceReport
    lob_lod: dict[str, Any] | None = None
    multilevel_lod_design: Any | None = None


def run_guidance(
    *,
    goal: Goal | str,
    result_type: ResultType | str,
    values: np.ndarray | None = None,
    strata: np.ndarray | None = None,
    low_level: np.ndarray | None = None,
    use_case: str | None = None,
    # sample size inputs
    p: float | None = None,
    p_a: float | None = None,
    p_b: float | None = None,
    p0: float | None = None,
    k: int = 1,
    alpha: float = 0.05,
    power: float = 0.80,
    target_cv_pct: float | None = None,
    sigma_over_mu: float | None = None,
    sd: float | None = None,
    ci_half_width: float | None = None,
    cluster_size: int = 1,
    thresholds: DiagnosticThresholds = DEFAULT_THRESHOLDS,
    n_classes: int | None = None,
    success_definition: str | None = None,
    run_sensitivity: bool = True,
    plan_multilevel_lod: bool = False,
    hit_concentrations: np.ndarray | None = None,
    hit_n_per_level: np.ndarray | None = None,
    multilevel_total_n: int = 60,
    multilevel_n_levels: int = 5,
    lob_estimation_mode: LoBEstimationMode | str = LoBEstimationMode.STANDARD,
) -> GuidanceResult:
    """
    Execute S0→S7 and return a structured GuidanceResult + markdown-ready report.
    """
    goal_spec = declare_goal(goal, use_case=use_case)
    rt_spec = classify_result_type(
        result_type, n_classes=n_classes, success_definition=success_definition
    )

    diagnostics = None
    correction = None
    parametric_ok = True
    correction_method = "none"
    icc = 0.0

    if values is not None and rt_spec.result_type in {
        ResultType.CONTINUOUS,
        ResultType.COUNT,
    }:
        diagnostics = run_diagnostics(values, strata=strata, thresholds=thresholds)
        correction = attempt_correction(values, strata=strata, thresholds=thresholds)
        parametric_ok = correction.parametric_ok
        correction_method = correction.method.value
        if diagnostics.icc is not None and np.isfinite(diagnostics.icc):
            icc = float(diagnostics.icc)
    elif rt_spec.result_type == ResultType.BINARY:
        parametric_ok = True
        correction_method = "none"

    model_path = select_model_path(
        parametric_ok=parametric_ok,
        result_type=rt_spec.result_type.value,
        correction_method=correction_method,
    )

    ss = recommend_sample_size(
        goal_spec.goal,
        p=p,
        p_a=p_a,
        p_b=p_b,
        p0=p0,
        k=k,
        alpha=alpha,
        power=power,
        target_cv_pct=target_cv_pct,
        sigma_over_mu=sigma_over_mu,
        sd=sd,
        ci_half_width=ci_half_width,
        icc=icc,
        cluster_size=cluster_size,
        parametric_ok=parametric_ok,
        use_simulation=not parametric_ok and goal_spec.goal == Goal.E2_COMPARE_REAGENTS,
    )

    multilevel: Any | None = None
    if plan_multilevel_lod and rt_spec.result_type == ResultType.BINARY:
        from lod_guide.s5_lod_design import LoDDesignBlockedError, recommend_multilevel_lod_design

        try:
            multilevel = recommend_multilevel_lod_design(
                concentrations=hit_concentrations,
                n_per_level=hit_n_per_level,
                total_n=multilevel_total_n,
                n_levels=multilevel_n_levels,
                block_on_non_identifiable=True,
            )
        except LoDDesignBlockedError as exc:
            raise LoDDesignBlockedError(str(exc), exc.certificate) from exc

    lob_lod = None
    if values is not None and (
        model_path
        in {
            ModelPath.PARAMETRIC_NORMAL,
            ModelPath.PARAMETRIC_LOGNORMAL,
            ModelPath.NONPARAMETRIC_PERCENTILE,
        }
        or lob_estimation_mode != LoBEstimationMode.STANDARD
    ):
        data_for_est = correction.transformed if correction is not None else values
        lob_mode = LoBEstimationMode(lob_estimation_mode)
        if lob_mode != LoBEstimationMode.STANDARD:
            from lod_guide.s4_gated_lob import estimate_gated_lob

            est = estimate_gated_lob(
                data_for_est,
                low_level=low_level,
                model_path=model_path,
                alpha=alpha,
                mode=lob_mode,
            )
        else:
            est = estimate_lob_lod(data_for_est, low_level, path=model_path, alpha=alpha)
        lob_lod = {"lob": est.lob, "lod": est.lod, "details": est.details}

    passed = []
    failed = []
    if diagnostics is not None:
        if diagnostics.shape_ok:
            passed.append("shape_ok")
        else:
            failed.append("shape_ok")
        if diagnostics.censoring_ok:
            passed.append("censoring_ok")
        else:
            failed.append("censoring_ok")
        if diagnostics.heterogeneity_ok:
            passed.append("heterogeneity_ok")
        else:
            failed.append("heterogeneity_ok")
        if diagnostics.poolable:
            passed.append("poolable")
        else:
            failed.append("poolable")
    else:
        passed.append("diagnostics_skipped_for_result_type")

    sens = None
    if run_sensitivity and goal_spec.goal == Goal.E2_COMPARE_REAGENTS and p_a and p_b:
        sens = sensitivity_compare_reagents(p_a=p_a, deltas=[abs(p_a - p_b), 0.05, 0.15])

    diag_summary: dict[str, Any] = {}
    if diagnostics is not None:
        diag_summary = {
            "skewness": diagnostics.skewness,
            "excess_kurtosis": diagnostics.excess_kurtosis,
            "normality_pvalue": diagnostics.normality_pvalue,
            "censoring_rate": diagnostics.censoring_rate,
            "icc": diagnostics.icc,
            "parametric_candidate": diagnostics.parametric_candidate,
            "messages": diagnostics.messages,
        }

    warnings = list(ss.warnings)
    if lob_lod and lob_lod.get("details", {}).get("lob_mode"):
        warnings.append(f"LoB estimation mode: {lob_lod['details']['lob_mode']}")
    if correction is not None:
        warnings.extend(correction.messages)
    if multilevel is not None:
        warnings.extend(multilevel.warnings)
        if multilevel.recommended_design:
            warnings.append(
                "S5 multilevel LoD: use minimax recommended concentrations/allocation "
                f"(pattern={multilevel.recommended_design['pattern']}, "
                f"allocation={multilevel.recommended_design['allocation']})."
            )

    p_alt = ss.details.get("p_alt") if ss.details else None
    try:
        exact_confirm = exact_confirmation_ledger(
            goal_spec.goal,
            n_per_arm=ss.n_per_arm,
            alpha=alpha,
            p_a=p_a,
            p_b=p_b,
            p0=p0,
            p=p,
            p_alt=p_alt,
            k=k,
        )
    except ValueError:
        exact_confirm = {
            "confirmation_engine": "unavailable",
            "note": "Exact confirmation ledger could not be built (missing inputs).",
        }

    details_with_exact = dict(ss.details)
    details_with_exact["s6_exact_confirmation"] = exact_confirm
    claim_p0 = p0 if p0 is not None else ss.details.get("claim_p0", 0.95)
    details_with_exact["lod95_semantics"] = dual_five_percent_frame(
        p0=float(claim_p0), alpha=alpha
    ).to_dict()

    sample_size_report = {
        "n_per_arm": ss.n_per_arm,
        "n_total": ss.n_total,
        "method": ss.method.value,
        "expected_power_or_precision": ss.expected_power_or_precision,
        "design_effect": ss.design_effect,
        "details": details_with_exact,
        "exact_confirmation": exact_confirm,
    }
    if multilevel is not None:
        sample_size_report["multilevel_lod_design"] = multilevel.to_dict()
    report = GuidanceReport(
        goal=goal_spec.goal.value,
        use_case=use_case,
        result_type=rt_spec.result_type.value,
        diagnostics_summary=diag_summary,
        correction_method=correction_method,
        model_path=model_path.value,
        parametric_ok=parametric_ok,
        sample_size=sample_size_report,
        assumptions_passed=passed,
        assumptions_failed=failed,
        warnings=warnings,
        lob=lob_lod["lob"] if lob_lod else None,
        lod=lob_lod["lod"] if lob_lod else None,
        sensitivity=sens,
    )

    return GuidanceResult(
        goal=goal_spec,
        result_type=rt_spec,
        diagnostics=diagnostics,
        correction=correction,
        model_path=model_path,
        sample_size=ss,
        report=report,
        lob_lod=lob_lod,
        multilevel_lod_design=multilevel,
    )
