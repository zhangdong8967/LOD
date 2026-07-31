"""
S4 — Parametric (S4a) and nonparametric (S4b) LoD-related models.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
from scipy import stats
from scipy.special import comb


class ModelPath(str, Enum):
    PARAMETRIC_NORMAL = "parametric_normal"
    PARAMETRIC_LOGNORMAL = "parametric_lognormal"
    PARAMETRIC_GAMMA = "parametric_gamma"
    PARAMETRIC_POISSON = "parametric_poisson"
    PARAMETRIC_PROBIT = "parametric_probit_hitrate"
    PARAMETRIC_TOBIT_NORMAL = "parametric_tobit_normal_censored"
    NONPARAMETRIC_PERCENTILE = "nonparametric_percentile"
    NONPARAMETRIC_BOOTSTRAP = "nonparametric_bootstrap"
    BINARY_RATE = "binary_rate"


@dataclass
class LoBLoDEstimate:
    path: ModelPath
    lob: float | None
    lod: float | None
    details: dict


def lob_parametric_normal(blank: np.ndarray, alpha: float = 0.05) -> float:
    """Classical LoB ≈ mean + z_{1-α} * SD (EP17 parametric spirit)."""
    x = np.asarray(blank, dtype=float)
    z = float(stats.norm.ppf(1 - alpha))
    return float(np.mean(x) + z * np.std(x, ddof=1))


def lod_from_lob_sd(lob: float, sd_low: float, beta: float = 0.05) -> float:
    """LoD ≈ LoB + z_{1-β} * SD_low."""
    z = float(stats.norm.ppf(1 - beta))
    return float(lob + z * sd_low)


def lob_nonparametric(blank: np.ndarray, percentile: float = 95.0) -> float:
    return float(np.percentile(np.asarray(blank, dtype=float), percentile))


def detect_prob_at_least_one(p: float, n: int) -> float:
    return float(1.0 - (1.0 - p) ** n)


def detect_prob_at_least_k(p: float, n: int, k: int) -> float:
    # P(X >= k) for X~Bin(n,p)
    return float(sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1)))


def poisson_detection_prob(lam: float, threshold: int = 1) -> float:
    if threshold <= 0:
        return 1.0
    return float(1.0 - stats.poisson.cdf(threshold - 1, lam))


def select_model_path(
    *,
    parametric_ok: bool,
    result_type: str,
    correction_method: str,
) -> ModelPath:
    if result_type == "binary":
        return ModelPath.BINARY_RATE
    if result_type == "multiclass":
        return ModelPath.BINARY_RATE  # success event reduced to Bernoulli after S1 definition
    if result_type == "count":
        return ModelPath.PARAMETRIC_POISSON if parametric_ok else ModelPath.NONPARAMETRIC_BOOTSTRAP
    if not parametric_ok:
        return ModelPath.NONPARAMETRIC_PERCENTILE
    if correction_method in {"log", "box_cox"}:
        return ModelPath.PARAMETRIC_LOGNORMAL
    return ModelPath.PARAMETRIC_NORMAL


def estimate_lob_lod(
    blank: np.ndarray,
    low_level: np.ndarray | None = None,
    *,
    path: ModelPath,
    alpha: float = 0.05,
    beta: float = 0.05,
) -> LoBLoDEstimate:
    blank = np.asarray(blank, dtype=float)
    if path == ModelPath.NONPARAMETRIC_PERCENTILE:
        lob = lob_nonparametric(blank, 100 * (1 - alpha))
        lod = None
        if low_level is not None:
            # nonparametric LoD proxy: percentile of low-level above LoB rate — simplified
            lod = float(np.percentile(low_level, 100 * (1 - beta)))
        return LoBLoDEstimate(path, lob, lod, {"note": "percentile LoB/LoD proxy"})

    if path in {
        ModelPath.PARAMETRIC_NORMAL,
        ModelPath.PARAMETRIC_LOGNORMAL,
        ModelPath.PARAMETRIC_GAMMA,
    }:
        lob = lob_parametric_normal(blank, alpha=alpha)
        sd_low = float(np.std(low_level, ddof=1)) if low_level is not None else float(np.std(blank, ddof=1))
        lod = lod_from_lob_sd(lob, sd_low, beta=beta)
        return LoBLoDEstimate(path, lob, lod, {"sd_low": sd_low})

    if path == ModelPath.PARAMETRIC_TOBIT_NORMAL:
        from lod_guide.research.censored_lob import lob_tobit_normal

        c_at = float(np.min(blank))
        fit = lob_tobit_normal(blank, censor_at=c_at, alpha=alpha)
        lob = fit.get("lob")
        lod = None
        if low_level is not None and lob is not None:
            sd_low = float(np.std(low_level, ddof=1))
            lod = lod_from_lob_sd(float(lob), sd_low, beta=beta)
        return LoBLoDEstimate(path, lob, lod, {"tobit": fit})

    return LoBLoDEstimate(path, None, None, {"note": "estimate not applicable for this path"})
