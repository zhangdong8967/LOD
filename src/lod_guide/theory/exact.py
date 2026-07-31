"""Exact / high-integrity interval and test utilities for transparent reporting."""

from __future__ import annotations

import numpy as np
from scipy.stats import beta, norm


def wilson_interval(successes: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if n <= 0:
        return (float("nan"), float("nan"))
    z = float(norm.ppf(1 - alpha / 2))
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = (z / denom) * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return float(max(0.0, center - half)), float(min(1.0, center + half))


def clopper_pearson_interval(successes: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact Clopper–Pearson interval via Beta quantiles."""
    if n <= 0:
        return (float("nan"), float("nan"))
    if successes == 0:
        low = 0.0
    else:
        low = float(beta.ppf(alpha / 2, successes, n - successes + 1))
    if successes == n:
        high = 1.0
    else:
        high = float(beta.ppf(1 - alpha / 2, successes + 1, n - successes))
    return low, high


def parametric_vs_quantile_lob_exponential(alpha: float = 0.05) -> dict:
    """Numeric exhibit for Proposition 5."""
    z = float(norm.ppf(1 - alpha))
    return {
        "distribution": "Exp(1)",
        "lob_parametric_mean_plus_z_sd": 1.0 + z,
        "lob_true_quantile": float(-np.log(alpha)),
        "alpha": alpha,
    }
