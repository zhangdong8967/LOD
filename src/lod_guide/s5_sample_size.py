"""
S5 — Sample-size engine: analytic formulae + simulation fallback.

Design-effect inflation for clustered / heterogeneous replicates:
    n_total ≈ n_indep * [1 + (m - 1) * ρ]
where m = cluster size, ρ = ICC.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
from scipy import stats
from scipy.stats import norm

from lod_guide.s0_goal import Goal
from lod_guide.s4_models import detect_prob_at_least_k, detect_prob_at_least_one


class SampleSizeMethod(str, Enum):
    ANALYTIC_TWO_PROPORTION = "analytic_two_proportion"
    ANALYTIC_ONE_PROPORTION = "analytic_one_proportion"
    ANALYTIC_CV_PRECISION = "analytic_cv_precision"
    ANALYTIC_NORMAL_MEAN = "analytic_normal_mean_ci"
    SIMULATION_BOOTSTRAP = "simulation_bootstrap"
    EP17_RULE_OF_THUMB = "ep17_rule_of_thumb"
    EXACT_FISHER_POWER = "exact_fisher_enumeration"
    EXACT_BOSCHLOO = "exact_boschloo_unconditional"


@dataclass
class SampleSizeResult:
    n_per_arm: int
    n_total: int
    method: SampleSizeMethod
    expected_power_or_precision: float
    design_effect: float
    details: dict
    warnings: list[str]


def design_effect(icc: float, cluster_size: int) -> float:
    """DE = 1 + (m-1)ρ."""
    m = max(int(cluster_size), 1)
    if icc is None or not np.isfinite(icc):
        rho = 0.0
    else:
        rho = float(np.clip(icc, 0.0, 1.0))
    return float(1.0 + (m - 1) * rho)


def inflate_n(n: float, deff: float) -> int:
    if not np.isfinite(n) or n <= 0:
        n = 1.0
    if not np.isfinite(deff) or deff < 1.0:
        deff = 1.0
    return int(np.ceil(n * deff))


def sample_size_two_proportions(
    p_a: float,
    p_b: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    if abs(p_a - p_b) < 1e-12:
        return float("inf")
    za = float(norm.ppf(1 - alpha / 2))
    zb = float(norm.ppf(power))
    p_bar = 0.5 * (p_a + p_b)
    num = za * np.sqrt(2 * p_bar * (1 - p_bar)) + zb * np.sqrt(
        p_a * (1 - p_a) + p_b * (1 - p_b)
    )
    return float((num / (p_a - p_b)) ** 2)


def power_two_proportions(p_a: float, p_b: float, n: int, alpha: float = 0.05) -> float:
    p_bar = 0.5 * (p_a + p_b)
    se0 = np.sqrt(p_bar * (1 - p_bar) * (2 / n))
    se1 = np.sqrt(p_a * (1 - p_a) / n + p_b * (1 - p_b) / n)
    delta = abs(p_a - p_b)
    za = float(norm.ppf(1 - alpha / 2))
    crit = za * se0
    power = float(norm.sf(crit, loc=delta, scale=se1) + norm.cdf(-crit, loc=delta, scale=se1))
    return float(np.clip(power, 0.0, 1.0))


def sample_size_one_proportion(
    p: float,
    p0: float,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """One-sample proportion vs reference p0 (e.g. claim verification)."""
    za = float(norm.ppf(1 - alpha / 2))
    zb = float(norm.ppf(power))
    if abs(p - p0) < 1e-12:
        return float("inf")
    num = za * np.sqrt(p0 * (1 - p0)) + zb * np.sqrt(p * (1 - p))
    return float((num / (p - p0)) ** 2)


def sample_size_cv_precision(target_cv_pct: float, sigma_over_mu: float) -> int:
    """
    Rough LoQ: if observed CV ≈ 100*σ/μ, need enough n so SE of mean gives
    effective CV of mean = CV/sqrt(n) below target — here we return n such that
    expected CV of single measurement context is documented; for precision profile
    labs often fix concentration and want CI half-width.
    For v0.1: n so that CV of mean = sigma_over_mu/sqrt(n)*100 <= target_cv_pct.
    """
    if target_cv_pct <= 0 or sigma_over_mu <= 0:
        raise ValueError("target_cv_pct and sigma_over_mu must be positive")
    n = (100.0 * sigma_over_mu / target_cv_pct) ** 2
    return int(np.ceil(n))


def sample_size_mean_ci(sd: float, half_width: float, alpha: float = 0.05) -> int:
    z = float(norm.ppf(1 - alpha / 2))
    return int(np.ceil((z * sd / half_width) ** 2))


def simulate_power_two_proportions(
    p_a: float,
    p_b: float,
    n: int,
    alpha: float = 0.05,
    n_sims: int = 5000,
    seed: int = 0,
) -> float:
    rng = np.random.default_rng(seed)
    xa = rng.binomial(n, p_a, size=n_sims)
    xb = rng.binomial(n, p_b, size=n_sims)
    p_pool = (xa + xb) / (2 * n)
    se = np.sqrt(np.maximum(p_pool * (1 - p_pool) * (2 / n), 1e-16))
    z = np.where(se > 1e-12, (xa / n - xb / n) / se, 0.0)
    pvals = 2 * norm.sf(np.abs(z))
    return float(np.mean((pvals < alpha) & (se > 1e-12)))


def recommend_sample_size(
    goal: Goal,
    *,
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
    icc: float = 0.0,
    cluster_size: int = 1,
    parametric_ok: bool = True,
    use_simulation: bool = False,
) -> SampleSizeResult:
    """
    S5 entry: goal-specific n with optional design-effect inflation.
    """
    warnings: list[str] = []
    deff = design_effect(icc, cluster_size)
    if deff > 1.05:
        warnings.append(
            f"Design effect DE={deff:.2f} from ICC={icc:.3f}, cluster_size={cluster_size}."
        )

    if goal == Goal.G2_COMPARE_REAGENTS:
        if p_a is None or p_b is None:
            raise ValueError("G2 requires p_a and p_b")
        n_cont = sample_size_two_proportions(p_a, p_b, alpha, power)
        n = inflate_n(n_cont, deff)
        method = SampleSizeMethod.ANALYTIC_TWO_PROPORTION
        exp = power_two_proportions(p_a, p_b, max(n, 2), alpha)
        if use_simulation or not parametric_ok:
            exp = simulate_power_two_proportions(p_a, p_b, n, alpha)
            method = SampleSizeMethod.SIMULATION_BOOTSTRAP
        if n <= 20:
            warnings.append(
                f"Recommended n={n} but folklore n=20 is often underpowered for "
                f"Δ={abs(p_a-p_b):.2f}; check power curve."
            )
        # Explicit folklore warning when people might use 20
        n20_power = power_two_proportions(p_a, p_b, 20, alpha)
        if n20_power < power:
            warnings.append(
                f"With n=20 per arm, approx power≈{n20_power:.0%} < target {power:.0%}."
            )
        return SampleSizeResult(
            n_per_arm=n,
            n_total=2 * n,
            method=method,
            expected_power_or_precision=exp,
            design_effect=deff,
            details={"n_continuous": n_cont, "p_a": p_a, "p_b": p_b, "power_target": power},
            warnings=warnings,
        )

    if goal == Goal.G1_VERIFY_LOD:
        # Prefer one-proportion vs claim p0 if provided; else precision of p
        if p is None:
            p = 0.95
        if p0 is None:
            p0 = 0.95
        # For verification of hit rate near claim, use one-sample size for detectable deviation
        # Default: detect drop of 0.10 below claim unless p provided differently
        p_alt = p if p != p0 else max(p0 - 0.10, 0.01)
        n_cont = sample_size_one_proportion(p_alt, p0, alpha, power)
        n = inflate_n(n_cont, deff)
        # EP17-style floor for continuous establishment often larger; keep analytic + note
        warnings.append(
            "G1 uses one-proportion power vs claim; align concentrations with EP17 materials."
        )
        return SampleSizeResult(
            n_per_arm=n,
            n_total=n,
            method=SampleSizeMethod.ANALYTIC_ONE_PROPORTION,
            expected_power_or_precision=power,
            design_effect=deff,
            details={"p0": p0, "p_alt": p_alt, "n_continuous": n_cont},
            warnings=warnings,
        )

    if goal == Goal.G3_LOQ_PRECISION:
        if target_cv_pct is None or sigma_over_mu is None:
            if sd is not None and ci_half_width is not None:
                n = inflate_n(sample_size_mean_ci(sd, ci_half_width, alpha), deff)
                return SampleSizeResult(
                    n_per_arm=n,
                    n_total=n,
                    method=SampleSizeMethod.ANALYTIC_NORMAL_MEAN,
                    expected_power_or_precision=ci_half_width,
                    design_effect=deff,
                    details={"sd": sd, "half_width": ci_half_width},
                    warnings=warnings,
                )
            raise ValueError("G3 requires (target_cv_pct & sigma_over_mu) or (sd & ci_half_width)")
        n = inflate_n(sample_size_cv_precision(target_cv_pct, sigma_over_mu), deff)
        return SampleSizeResult(
            n_per_arm=n,
            n_total=n,
            method=SampleSizeMethod.ANALYTIC_CV_PRECISION,
            expected_power_or_precision=target_cv_pct,
            design_effect=deff,
            details={"sigma_over_mu": sigma_over_mu, "target_cv_pct": target_cv_pct},
            warnings=warnings,
        )

    if goal == Goal.G4_QUALITATIVE_KN:
        if p is None:
            p = 0.95
        # Find minimal n such that P(X>=k) >= power (here power re-used as target probability)
        target = power if power > 0.5 else 0.95
        n_found = None
        for n_try in range(max(k, 1), 10_000):
            if detect_prob_at_least_k(p, n_try, k) >= target:
                n_found = n_try
                break
        if n_found is None:
            n_found = 10_000
            warnings.append("G4 search hit n=10000 cap.")
        n = inflate_n(n_found, deff)
        return SampleSizeResult(
            n_per_arm=n,
            n_total=n,
            method=SampleSizeMethod.ANALYTIC_ONE_PROPORTION,
            expected_power_or_precision=detect_prob_at_least_k(p, n, k),
            design_effect=deff,
            details={"p": p, "k": k, "target_prob": target, "P_at_least_one": detect_prob_at_least_one(p, n)},
            warnings=warnings,
        )

    raise ValueError(f"Unsupported goal: {goal}")


def power_two_proportions_exact(
    p_a: float,
    p_b: float,
    n: int,
    alpha: float = 0.05,
    *,
    test: str = "fisher",
) -> float:
    """Exact enumeration power; see theory.exact_tests for methods."""
    from lod_guide.theory.exact_tests import exact_power_two_proportions

    return exact_power_two_proportions(p_a, p_b, n, alpha, test=test)


def sample_size_two_proportions_exact(
    p_a: float,
    p_b: float,
    alpha: float = 0.05,
    power: float = 0.80,
    *,
    test: str = "fisher",
    n_max: int = 400,
) -> dict:
    """Exact equal-arm n* search (Fisher or pooled-z enumeration)."""
    from lod_guide.theory.exact_tests import sample_size_exact_search

    return sample_size_exact_search(p_a, p_b, alpha, power, test=test, n_max=n_max)
