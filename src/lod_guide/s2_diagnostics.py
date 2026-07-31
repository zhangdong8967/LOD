"""
S2 — Empirical diagnostics near LoD.

Frozen default thresholds (v0.1) — change only via DiagnosticThresholds override
with documented justification.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class DiagnosticThresholds:
    """Pass/fail cutoffs for the S2 → S3 gate."""

    # Shape
    abs_skew_warn: float = 0.5
    abs_skew_fail: float = 1.0
    abs_excess_kurtosis_warn: float = 1.0
    abs_excess_kurtosis_fail: float = 2.0
    normality_alpha: float = 0.05  # Shapiro–Wilk / AD reject if p < alpha (n>=8)

    # Censoring / floor
    censoring_warn: float = 0.10  # fraction at/below LOD or zero
    censoring_fail: float = 0.25

    # Heterogeneity across strata
    icc_warn: float = 0.10
    icc_fail: float = 0.25
    levene_alpha: float = 0.05
    between_stratum_cv_warn: float = 0.15  # SD of stratum means / grand mean
    between_stratum_cv_fail: float = 0.30

    # Minimum n for formal normality tests
    min_n_normality_test: int = 8


DEFAULT_THRESHOLDS = DiagnosticThresholds()


@dataclass
class DiagnosticFlags:
    skewness: float
    excess_kurtosis: float
    normality_pvalue: float | None
    normality_ok: bool
    censoring_rate: float
    censoring_ok: bool
    icc: float | None
    levene_pvalue: float | None
    between_stratum_cv: float | None
    heterogeneity_ok: bool
    poolable: bool
    shape_ok: bool
    parametric_candidate: bool
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def _safe_skew_kurtosis(x: np.ndarray) -> tuple[float, float]:
    if x.size < 3:
        return float("nan"), float("nan")
    return float(stats.skew(x, bias=False)), float(stats.kurtosis(x, bias=False, fisher=True))


def _normality_pvalue(x: np.ndarray, min_n: int) -> float | None:
    if x.size < min_n:
        return None
    # Shapiro–Wilk for n <= 5000; else Anderson–Darling p approx via normal
    if x.size <= 5000:
        try:
            return float(stats.shapiro(x).pvalue)
        except Exception:
            return None
    ad = stats.anderson(x, dist="norm")
    # Rough conversion: AD statistic; use KS as fallback p
    return float(stats.kstest(x, "norm", args=(np.mean(x), np.std(x, ddof=1))).pvalue)


def one_way_icc(y: np.ndarray, groups: np.ndarray) -> float | None:
    """ICC(1) from one-way random effects ANOVA."""
    y = np.asarray(y, dtype=float)
    groups = np.asarray(groups)
    if y.size < 4:
        return None
    uniq = np.unique(groups)
    if uniq.size < 2:
        return None
    grand = np.mean(y)
    n_i = []
    ms_b_num = 0.0
    ms_w_num = 0.0
    df_w = 0
    for g in uniq:
        yi = y[groups == g]
        n_i.append(yi.size)
        ms_b_num += yi.size * (np.mean(yi) - grand) ** 2
        ms_w_num += np.sum((yi - np.mean(yi)) ** 2)
        df_w += yi.size - 1
    k = len(uniq)
    df_b = k - 1
    if df_b < 1 or df_w < 1:
        return None
    msb = ms_b_num / df_b
    msw = ms_w_num / df_w if df_w else np.nan
    n0 = (np.sum(n_i) - np.sum(np.square(n_i)) / np.sum(n_i)) / (k - 1)
    if n0 <= 0 or np.isnan(msw):
        return None
    icc = (msb - msw) / (msb + (n0 - 1) * msw)
    return float(np.clip(icc, 0.0, 1.0))


def run_diagnostics(
    values: np.ndarray,
    *,
    strata: np.ndarray | None = None,
    censor_threshold: float | None = None,
    thresholds: DiagnosticThresholds = DEFAULT_THRESHOLDS,
) -> DiagnosticFlags:
    """
    S2 entry point.

    Parameters
    ----------
    values : array of blank or near-LoD continuous measurements (or 0/1 for rates later)
    strata : optional batch/day/operator labels aligned with values
    censor_threshold : values <= threshold counted as censored (default: min if many ties at floor)
    """
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    msgs: list[str] = []
    thr = thresholds

    skew, ekurt = _safe_skew_kurtosis(x)
    p_norm = _normality_pvalue(x, thr.min_n_normality_test)

    shape_fail = (abs(skew) >= thr.abs_skew_fail) or (abs(ekurt) >= thr.abs_excess_kurtosis_fail)
    shape_warn = (abs(skew) >= thr.abs_skew_warn) or (abs(ekurt) >= thr.abs_excess_kurtosis_warn)
    if p_norm is not None and p_norm < thr.normality_alpha:
        shape_fail = True
        msgs.append(f"Normality test rejected (p={p_norm:.4g} < {thr.normality_alpha}).")
    elif shape_fail:
        msgs.append(f"Shape fail: |skew|={abs(skew):.3f}, |excess kurtosis|={abs(ekurt):.3f}.")
    elif shape_warn:
        msgs.append(f"Shape warning: |skew|={abs(skew):.3f}, |excess kurtosis|={abs(ekurt):.3f}.")

    if censor_threshold is None:
        # Heuristic: if >=10% at exact minimum, treat min as floor
        xmin = np.min(x) if x.size else 0.0
        censor_threshold = float(xmin)
    cens = float(np.mean(x <= censor_threshold)) if x.size else 0.0
    # Only treat as censoring if mass at floor is meaningful (not unique continuous min)
    if x.size and np.sum(x <= censor_threshold) <= 1:
        cens = 0.0
    censoring_ok = cens < thr.censoring_fail
    if cens >= thr.censoring_fail:
        msgs.append(f"Censoring/floor rate {cens:.1%} >= fail {thr.censoring_fail:.0%}.")
    elif cens >= thr.censoring_warn:
        msgs.append(f"Censoring/floor rate {cens:.1%} >= warn {thr.censoring_warn:.0%}.")

    icc = None
    levene_p = None
    bcv = None
    heterogeneity_ok = True
    poolable = True

    if strata is not None:
        g = np.asarray(strata)[np.isfinite(np.asarray(values, dtype=float))]
        # align lengths carefully
        mask = np.isfinite(np.asarray(values, dtype=float))
        xv = np.asarray(values, dtype=float)[mask]
        gv = np.asarray(strata)[mask]
        icc = one_way_icc(xv, gv)
        uniq = np.unique(gv)
        if uniq.size >= 2:
            groups = [xv[gv == u] for u in uniq if np.sum(gv == u) >= 2]
            if len(groups) >= 2:
                try:
                    levene_p = float(stats.levene(*groups, center="median").pvalue)
                except Exception:
                    levene_p = None
            means = [float(np.mean(xv[gv == u])) for u in uniq]
            grand = float(np.mean(xv))
            if abs(grand) > 1e-12:
                bcv = float(np.std(means, ddof=1) / abs(grand)) if len(means) > 1 else 0.0
            else:
                bcv = float("nan")

        if icc is not None and icc >= thr.icc_fail:
            heterogeneity_ok = False
            poolable = False
            msgs.append(f"ICC={icc:.3f} >= fail {thr.icc_fail} — not poolable.")
        elif icc is not None and icc >= thr.icc_warn:
            msgs.append(f"ICC={icc:.3f} >= warn {thr.icc_warn} — prefer stratum-aware n.")
            poolable = False
        if levene_p is not None and levene_p < thr.levene_alpha:
            heterogeneity_ok = False
            poolable = False
            msgs.append(f"Levene rejected equal variances (p={levene_p:.4g}).")
        if bcv is not None and not np.isnan(bcv):
            if bcv >= thr.between_stratum_cv_fail:
                heterogeneity_ok = False
                poolable = False
                msgs.append(f"Between-stratum CV={bcv:.3f} >= fail {thr.between_stratum_cv_fail}.")
            elif bcv >= thr.between_stratum_cv_warn:
                poolable = False
                msgs.append(f"Between-stratum CV={bcv:.3f} >= warn {thr.between_stratum_cv_warn}.")

    shape_ok = not shape_fail
    parametric_candidate = shape_ok and censoring_ok and heterogeneity_ok

    if not msgs:
        msgs.append("Diagnostics within default pass bounds for parametric candidacy.")

    return DiagnosticFlags(
        skewness=skew,
        excess_kurtosis=ekurt,
        normality_pvalue=p_norm,
        normality_ok=shape_ok and (p_norm is None or p_norm >= thr.normality_alpha),
        censoring_rate=cens,
        censoring_ok=censoring_ok,
        icc=icc,
        levene_pvalue=levene_p,
        between_stratum_cv=bcv,
        heterogeneity_ok=heterogeneity_ok,
        poolable=poolable,
        shape_ok=shape_ok,
        parametric_candidate=parametric_candidate,
        messages=msgs,
    )
