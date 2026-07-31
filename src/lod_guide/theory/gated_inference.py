"""
Post-selection inference for assumption-gated LoB paths.

When S2 diagnostics select parametric vs nonparametric LoB, Type I (blank
exceedance) can exceed nominal α even when each path is calibrated in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from lod_guide.s2_diagnostics import DEFAULT_THRESHOLDS, run_diagnostics
from lod_guide.s4_models import lob_nonparametric, lob_parametric_normal


@dataclass(frozen=True)
class GatedLoBResult:
    parametric_candidate: bool
    lob_used: float
    path: str


def gated_lob_from_sample(
    blank: np.ndarray,
    *,
    alpha: float = 0.05,
    censor_threshold: float | None = None,
) -> GatedLoBResult:
    """Apply S2 gate then parametric or nonparametric LoB."""
    flags = run_diagnostics(blank, censor_threshold=censor_threshold, thresholds=DEFAULT_THRESHOLDS)
    if flags.parametric_candidate:
        lob = lob_parametric_normal(blank, alpha=alpha)
        return GatedLoBResult(True, float(lob), "parametric")
    lob = lob_nonparametric(blank, percentile=100 * (1 - alpha))
    return GatedLoBResult(False, float(lob), "nonparametric")


def population_exceedance_rate(lob: float, *, law: str) -> float:
    if law == "normal":
        return float(norm.sf(lob, loc=0.0, scale=1.0))
    if law == "exponential":
        return float(np.exp(-lob)) if lob > 0 else 1.0
    if law == "lognormal":
        if lob <= 0:
            return 1.0
        return float(norm.sf(np.log(lob)))
    raise ValueError(law)


def monte_carlo_gated_type_i(
    *,
    law: str,
    n_blank: int = 60,
    alpha: float = 0.05,
    n_mc: int = 3000,
    seed: int = 0,
    draw_fn,
) -> dict:
    """Empirical exceedance rate of gated LoB vs fresh test draws."""
    rng = np.random.default_rng(seed)
    rates = []
    paths = {"parametric": 0, "nonparametric": 0}
    for _ in range(n_mc):
        blank = draw_fn(n_blank, rng)
        gated = gated_lob_from_sample(blank, alpha=alpha)
        paths[gated.path] += 1
        test = draw_fn(500, rng)
        rates.append(float(np.mean(test > gated.lob_used)))
    mean_rate = float(np.mean(rates))
    return {
        "law": law,
        "alpha_nominal": alpha,
        "n_blank": n_blank,
        "n_mc": n_mc,
        "mean_exceedance": mean_rate,
        "inflation": mean_rate - alpha,
        "path_counts": paths,
        "always_parametric_exceedance": None,  # filled by caller if needed
    }


def inflation_lower_bound_skew_family(
    *,
    alpha: float = 0.05,
    n_blank: int = 60,
    n_mc: int = 1200,
    seed: int = 0,
) -> dict:
    """
    P17 sketch: under non-Gaussian blanks that sometimes pass S2, gated parametric
    LoB can inflate Type I relative to nominal α.
    """
    rng = np.random.default_rng(seed)

    def draw_lognormal_tight(n: int, r: np.random.Generator) -> np.ndarray:
        return r.lognormal(mean=0.0, sigma=0.22, size=n)

    def draw_gamma(n: int, r: np.random.Generator) -> np.ndarray:
        return r.gamma(shape=4.0, scale=0.25, size=n)

    def draw_uniform(n: int, r: np.random.Generator) -> np.ndarray:
        return r.uniform(0.0, 1.0, size=n)

    candidates = []
    for law_name, draw_fn in (
        ("lognormal_tight", draw_lognormal_tight),
        ("gamma_4_025", draw_gamma),
        ("uniform_0_1", draw_uniform),
    ):
        gated = monte_carlo_gated_type_i(
            law=law_name,
            n_blank=n_blank,
            alpha=alpha,
            n_mc=n_mc,
            seed=seed + hash(law_name) % 997,
            draw_fn=draw_fn,
        )
        par_frac = gated["path_counts"]["parametric"] / n_mc
        candidates.append({**gated, "parametric_fraction": par_frac})

    # Prefer laws where the gate actually selects parametric sometimes
    ranked = sorted(
        candidates,
        key=lambda c: (c["parametric_fraction"] >= 0.05, c["inflation"]),
        reverse=True,
    )
    best = ranked[0]
    best["always_parametric_exceedance"] = _always_par_rate(
        draw_lognormal_tight if best["law"] == "lognormal_tight" else draw_gamma if best["law"] == "gamma_4_025" else draw_uniform,
        n_blank,
        alpha,
        min(n_mc, 600),
        seed + 11,
    )
    best["always_nonparametric_exceedance"] = _always_np_rate(
        draw_lognormal_tight if best["law"] == "lognormal_tight" else draw_gamma if best["law"] == "gamma_4_025" else draw_uniform,
        n_blank,
        alpha,
        min(n_mc, 600),
        seed + 12,
    )
    best["candidate_laws"] = [
        {"law": c["law"], "inflation": c["inflation"], "parametric_fraction": c["parametric_fraction"]}
        for c in ranked
    ]
    return best


def _always_par_rate(draw_fn, n_blank: int, alpha: float, n_mc: int, seed: int) -> float:
    from lod_guide.s4_models import lob_parametric_normal

    rng = np.random.default_rng(seed)
    rates = []
    for _ in range(n_mc):
        blank = draw_fn(n_blank, rng)
        lob_p = lob_parametric_normal(blank, alpha=alpha)
        test = draw_fn(500, rng)
        rates.append(float(np.mean(test > lob_p)))
    return float(np.mean(rates))


def _always_np_rate(draw_fn, n_blank: int, alpha: float, n_mc: int, seed: int) -> float:
    rng = np.random.default_rng(seed)
    rates = []
    for _ in range(n_mc):
        blank = draw_fn(n_blank, rng)
        lob = lob_nonparametric(blank, percentile=100 * (1 - alpha))
        test = draw_fn(500, rng)
        rates.append(float(np.mean(test > lob)))
    return float(np.mean(rates))
