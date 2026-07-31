"""Bootstrap confidence intervals for nonparametric LoB and binomial rates."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from lod_guide.s4_models import lob_nonparametric, lob_parametric_normal


@dataclass
class BootstrapCI:
    estimate: float
    low: float
    high: float
    n_boot: int
    level: float


def bootstrap_quantile_lob(
    blank: np.ndarray,
    *,
    percentile: float = 95.0,
    n_boot: int = 2000,
    level: float = 0.95,
    seed: int = 0,
) -> BootstrapCI:
    x = np.asarray(blank, dtype=float)
    x = x[np.isfinite(x)]
    rng = np.random.default_rng(seed)
    est = lob_nonparametric(x, percentile=percentile)
    n = x.size
    stats = np.empty(n_boot)
    for b in range(n_boot):
        sample = x[rng.integers(0, n, size=n)]
        stats[b] = lob_nonparametric(sample, percentile=percentile)
    alpha = 1 - level
    low, high = np.quantile(stats, [alpha / 2, 1 - alpha / 2])
    return BootstrapCI(float(est), float(low), float(high), n_boot, level)


def bootstrap_parametric_lob(
    blank: np.ndarray,
    *,
    alpha_lob: float = 0.05,
    n_boot: int = 2000,
    level: float = 0.95,
    seed: int = 0,
) -> BootstrapCI:
    x = np.asarray(blank, dtype=float)
    x = x[np.isfinite(x)]
    rng = np.random.default_rng(seed)
    est = lob_parametric_normal(x, alpha=alpha_lob)
    n = x.size
    stats = np.empty(n_boot)
    for b in range(n_boot):
        sample = x[rng.integers(0, n, size=n)]
        stats[b] = lob_parametric_normal(sample, alpha=alpha_lob)
    alpha = 1 - level
    low, high = np.quantile(stats, [alpha / 2, 1 - alpha / 2])
    return BootstrapCI(float(est), float(low), float(high), n_boot, level)
