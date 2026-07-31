"""
S3 — Correction gate: transform / robustify with hard stop to nonparametric path.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
from scipy import stats
from scipy.stats import boxcox

from lod_guide.s2_diagnostics import (
    DEFAULT_THRESHOLDS,
    DiagnosticFlags,
    DiagnosticThresholds,
    run_diagnostics,
)


class CorrectionMethod(str, Enum):
    NONE = "none"
    LOG = "log"
    BOX_COX = "box_cox"
    SQRT = "sqrt"
    ROBUST_MAD = "robust_mad"
    FAILED = "failed_use_nonparametric"


@dataclass
class CorrectionResult:
    method: CorrectionMethod
    transformed: np.ndarray
    lambda_boxcox: float | None
    offset: float
    diagnostics_after: DiagnosticFlags
    parametric_ok: bool
    messages: list[str]


def _log_transform(x: np.ndarray) -> tuple[np.ndarray, float]:
    offset = 0.0
    if np.any(x <= 0):
        offset = float(abs(np.min(x)) + 1e-6) if np.min(x) <= 0 else 0.0
        # classic log(x+c) with c = max(0, -min + eps)
        c = -np.min(x) + 1e-6 if np.min(x) <= 0 else 0.0
        offset = float(c)
        return np.log(x + c), offset
    return np.log(x), offset


def attempt_correction(
    values: np.ndarray,
    *,
    strata: np.ndarray | None = None,
    prefer: list[CorrectionMethod] | None = None,
    thresholds: DiagnosticThresholds = DEFAULT_THRESHOLDS,
) -> CorrectionResult:
    """
    Ordered correction attempts; stop at first that restores parametric candidacy.
    If all fail → CorrectionMethod.FAILED (route to S4b).
    """
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    order = prefer or [
        CorrectionMethod.LOG,
        CorrectionMethod.BOX_COX,
        CorrectionMethod.SQRT,
        CorrectionMethod.ROBUST_MAD,
    ]
    messages: list[str] = []

    # Baseline
    base = run_diagnostics(x, strata=strata, thresholds=thresholds)
    if base.parametric_candidate:
        return CorrectionResult(
            method=CorrectionMethod.NONE,
            transformed=x.copy(),
            lambda_boxcox=None,
            offset=0.0,
            diagnostics_after=base,
            parametric_ok=True,
            messages=["No correction needed; parametric candidate on raw scale."],
        )

    for method in order:
        try:
            if method == CorrectionMethod.LOG:
                xt, offset = _log_transform(x)
                lam = None
            elif method == CorrectionMethod.SQRT:
                if np.any(x < 0):
                    messages.append("sqrt skipped (negative values).")
                    continue
                xt, offset, lam = np.sqrt(x), 0.0, None
            elif method == CorrectionMethod.BOX_COX:
                # shift to positive
                shift = 0.0
                xp = x.copy()
                if np.any(xp <= 0):
                    shift = float(-np.min(xp) + 1e-6)
                    xp = xp + shift
                xt, lam = boxcox(xp)
                offset = shift
            elif method == CorrectionMethod.ROBUST_MAD:
                # Standardize by median/MAD then check shape of robust residuals
                med = np.median(x)
                mad = stats.median_abs_deviation(x, scale="normal")
                if mad < 1e-12:
                    messages.append("robust_mad skipped (MAD≈0).")
                    continue
                xt = (x - med) / mad
                offset, lam = 0.0, None
            else:
                continue

            diag = run_diagnostics(xt, strata=strata, thresholds=thresholds)
            # For robust_mad, shape on standardized scale; still require shape_ok
            ok = diag.shape_ok and diag.censoring_ok
            # Heterogeneity on transformed scale still counted
            if method != CorrectionMethod.ROBUST_MAD:
                ok = ok and diag.heterogeneity_ok
            else:
                # robust path allows mild hetero but not ICC fail
                ok = ok and (diag.icc is None or diag.icc < thresholds.icc_fail)

            if ok:
                messages.append(f"Correction '{method.value}' restored parametric candidacy.")
                return CorrectionResult(
                    method=method,
                    transformed=np.asarray(xt, dtype=float),
                    lambda_boxcox=float(lam) if lam is not None else None,
                    offset=float(offset),
                    diagnostics_after=diag,
                    parametric_ok=True,
                    messages=messages,
                )
            messages.append(f"Correction '{method.value}' insufficient: {diag.messages}")
        except Exception as exc:  # noqa: BLE001
            messages.append(f"Correction '{method.value}' failed: {exc}")

    fail_diag = run_diagnostics(x, strata=strata, thresholds=thresholds)
    messages.append("Hard stop: route to nonparametric path (S4b).")
    return CorrectionResult(
        method=CorrectionMethod.FAILED,
        transformed=x.copy(),
        lambda_boxcox=None,
        offset=0.0,
        diagnostics_after=fail_diag,
        parametric_ok=False,
        messages=messages,
    )
