"""
Shared dose–response primitives for LoD design and identification theory.

  logit(p) = α + β log10(c)   (logistic; default)
  probit(p) = α + β log10(c)  (optional)

LoD_γ solves p(c) = γ.  Asymptotic SE(log10 LoD) via expected Fisher information
and the delta method.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import expit, logit
from scipy.stats import norm


@dataclass(frozen=True)
class DoseResponseTruth:
    """Working truth on log10-concentration scale."""

    intercept: float  # α
    slope: float  # β (per log10 c)
    link: str = "logistic"  # logistic | probit
    target_p: float = 0.95

    def p_at_log10(self, x: np.ndarray | float) -> np.ndarray:
        eta = self.intercept + self.slope * np.asarray(x, dtype=float)
        if self.link == "probit":
            return norm.cdf(eta)
        return expit(eta)

    def lod_log10(self) -> float:
        if self.link == "probit":
            z = float(norm.ppf(self.target_p))
        else:
            z = float(logit(self.target_p))
        if abs(self.slope) < 1e-12:
            return float("nan")
        return (z - self.intercept) / self.slope

    def lod(self) -> float:
        return float(10 ** self.lod_log10())


def inv_link_grad_weight(p: float, link: str) -> float:
    """
    GLM weight w = (dp/dη)² / (p(1-p)) for η = α + βx.
    Logistic: w = p(1-p).  Probit: φ(η)² / (p(1-p)).
    """
    p = float(np.clip(p, 1e-9, 1 - 1e-9))
    if link == "probit":
        eta = float(norm.ppf(p))
        phi = float(norm.pdf(eta))
        return (phi * phi) / (p * (1 - p))
    return p * (1 - p)


def fisher_info_alpha_beta(
    truth: DoseResponseTruth,
    concentrations: np.ndarray,
    n_per_level: np.ndarray,
) -> np.ndarray:
    """Expected Fisher information matrix for (α, β)."""
    c = np.asarray(concentrations, dtype=float)
    n = np.asarray(n_per_level, dtype=float)
    x = np.log10(c)
    p = truth.p_at_log10(x)
    info = np.zeros((2, 2), dtype=float)
    for xi, pi, ni in zip(x, p, n, strict=True):
        w = inv_link_grad_weight(float(pi), truth.link)
        v = ni * w
        info[0, 0] += v
        info[0, 1] += v * xi
        info[1, 0] += v * xi
        info[1, 1] += v * xi * xi
    return info


def grad_log10_lod(truth: DoseResponseTruth) -> np.ndarray:
    """∇_{(α,β)} log10(LoD_γ); x_L = (z - α)/β."""
    b = truth.slope
    x_l = truth.lod_log10()
    return np.array([-1.0 / b, -x_l / b], dtype=float)


def asymptotic_lod_se_log10(
    truth: DoseResponseTruth,
    concentrations: np.ndarray,
    n_per_level: np.ndarray,
) -> dict:
    """Delta-method asymptotic SE of log10(LoD) from expected binomial information."""
    c = np.asarray(concentrations, dtype=float)
    n = np.asarray(n_per_level, dtype=float)
    info = fisher_info_alpha_beta(truth, c, n)
    try:
        cov = np.linalg.inv(info)
    except np.linalg.LinAlgError:
        return {
            "se_log10_lod": float("inf"),
            "cv_lod_approx": float("inf"),
            "info_ok": False,
            "info_rank": 0,
            "total_n": int(n.sum()),
            "n_levels": int(c.size),
        }

    grad = grad_log10_lod(truth)
    var_x = float(grad @ cov @ grad)
    se_x = float(np.sqrt(max(var_x, 0.0)))
    rank = int(np.linalg.matrix_rank(info))
    return {
        "se_log10_lod": se_x,
        "cv_lod_approx": float(se_x * np.log(10)),
        "info_ok": bool(rank == 2 and np.isfinite(se_x)),
        "info_rank": rank,
        "total_n": int(n.sum()),
        "n_levels": int(c.size),
        "cov_alpha_beta": cov.tolist(),
        "lod_true": truth.lod(),
        "fisher_det": float(np.linalg.det(info)),
    }


def truth_with_slope(
    intercept: float,
    slope: float,
    *,
    link: str = "logistic",
    target_p: float = 0.95,
) -> DoseResponseTruth:
    return DoseResponseTruth(intercept=intercept, slope=slope, link=link, target_p=target_p)


def default_synthetic_truth() -> DoseResponseTruth:
    """LoD95 ≈ 1.0; moderate slope."""
    alpha = float(logit(0.95))
    beta = float(logit(0.95) - logit(0.25))
    return DoseResponseTruth(intercept=alpha, slope=beta, link="logistic", target_p=0.95)
