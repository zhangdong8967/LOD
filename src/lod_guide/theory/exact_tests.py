"""
Exact / small-sample methods for two-binomial LoD discrimination.

Why this exists (referee defense):
  Asymptotic pooled-z power (Fleiss–Chow) is convenient but can mis-calibrate
  Type I error and power at folklore n≈20. This module provides:

  1. Fisher's exact test (conditional on margins) — conservative, classical.
  2. Boschloo's unconditional exact test — uses Fisher p as test statistic,
     maximizes null rejection over nuisance p under H0: p_A = p_B = p.
     Typically less conservative than Fisher for 2×2 tables.
  3. Exact (enumeration) power under independent Binomial(n, p_A), Binomial(n, p_B).
  4. Side-by-side comparison with asymptotic pooled-z for transparency.

Barnard's original unconditional test maximizes over a broader critical-region
search; Boschloo is a standard practical unconditional exact procedure and is
what we report as 'unconditional_exact' (Boschloo) in this package.

We additionally implement an unconditional exact test using the absolute risk
difference |p̂_A−p̂_B| as the test statistic (often called a Barnard-CS /
difference-unconditional procedure). Full CSM region-construction Barnard is
NP-hard in general; for equal-arm n≤25 we expose this difference-based Barnard.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from scipy.stats import binom, fisher_exact, norm

from lod_guide.s5_sample_size import power_two_proportions, sample_size_two_proportions


@dataclass(frozen=True)
class TwoByTwoResult:
    a_success: int
    a_n: int
    b_success: int
    b_n: int
    fisher_p_two_sided: float
    boschloo_p_two_sided: float
    barnard_diff_p_two_sided: float
    pooled_z_p_two_sided: float
    method_note: str


def pooled_z_pvalue(a: int, n_a: int, b: int, n_b: int) -> float:
    """Two-sided pooled-z (score) test p-value for H0: p_A = p_B."""
    if n_a <= 0 or n_b <= 0:
        return float("nan")
    p_pool = (a + b) / (n_a + n_b)
    se = np.sqrt(p_pool * (1.0 - p_pool) * (1.0 / n_a + 1.0 / n_b))
    if se < 1e-15:
        return 1.0
    z = (a / n_a - b / n_b) / se
    return float(2.0 * norm.sf(abs(z)))


def fisher_pvalue(a: int, n_a: int, b: int, n_b: int) -> float:
    """Two-sided Fisher exact p-value on [[a, n_a-a], [b, n_b-b]]."""
    table = [[a, n_a - a], [b, n_b - b]]
    _, p = fisher_exact(table, alternative="two-sided")
    return float(p)


@lru_cache(maxsize=256)
def _null_p_grid(n_grid: int = 201) -> tuple[float, ...]:
    return tuple(float(x) for x in np.linspace(0.0, 1.0, n_grid))


def boschloo_pvalue(
    a: int,
    n_a: int,
    b: int,
    n_b: int,
    *,
    n_grid: int = 201,
) -> float:
    """
    Boschloo unconditional exact p-value (two-sided).

    Test statistic T = Fisher two-sided p-value. Observed t0 = T(a,b).
    Under H0 with common p, P(T <= t0 | p) is maximized over p ∈ [0,1].
    """
    t0 = fisher_pvalue(a, n_a, b, n_b)
    p_grid = _null_p_grid(n_grid)

    fisher_mat = np.empty((n_a + 1, n_b + 1), dtype=float)
    for i in range(n_a + 1):
        for j in range(n_b + 1):
            fisher_mat[i, j] = fisher_pvalue(i, n_a, j, n_b)

    reject = fisher_mat <= t0 + 1e-15
    max_prob = 0.0
    for p in p_grid:
        px = binom.pmf(np.arange(n_a + 1), n_a, p)
        py = binom.pmf(np.arange(n_b + 1), n_b, p)
        joint = px[:, None] * py[None, :]
        max_prob = max(max_prob, float(np.sum(joint[reject])))
    return float(min(1.0, max_prob))


def barnard_difference_pvalue(
    a: int,
    n_a: int,
    b: int,
    n_b: int,
    *,
    n_grid: int = 201,
) -> float:
    """
    Unconditional exact p-value using T = |a/n_a − b/n_b| (two-sided).

    Rejects tables with T ≥ T_obs; p = max_p P(T ≥ T_obs | p_A=p_B=p).
    This is a Barnard-type difference-unconditional test (not full CSM search).
    """
    if n_a <= 0 or n_b <= 0:
        return float("nan")
    t0 = abs(a / n_a - b / n_b)
    diff = np.abs(
        np.arange(n_a + 1)[:, None] / n_a - np.arange(n_b + 1)[None, :] / n_b
    )
    reject = diff >= t0 - 1e-15
    max_prob = 0.0
    for p in _null_p_grid(n_grid):
        px = binom.pmf(np.arange(n_a + 1), n_a, p)
        py = binom.pmf(np.arange(n_b + 1), n_b, p)
        joint = px[:, None] * py[None, :]
        max_prob = max(max_prob, float(np.sum(joint[reject])))
    return float(min(1.0, max_prob))


def analyze_two_proportions_exact(
    a: int,
    n_a: int,
    b: int,
    n_b: int,
    *,
    n_grid: int = 201,
) -> TwoByTwoResult:
    return TwoByTwoResult(
        a_success=a,
        a_n=n_a,
        b_success=b,
        b_n=n_b,
        fisher_p_two_sided=fisher_pvalue(a, n_a, b, n_b),
        boschloo_p_two_sided=boschloo_pvalue(a, n_a, b, n_b, n_grid=n_grid),
        barnard_diff_p_two_sided=barnard_difference_pvalue(a, n_a, b, n_b, n_grid=n_grid),
        pooled_z_p_two_sided=pooled_z_pvalue(a, n_a, b, n_b),
        method_note=(
            "Primary small-n: Boschloo; report Fisher (conditional) and Barnard-diff "
            "(unconditional on |Δp|) as sensitivity; pooled-z is asymptotic."
        ),
    )


def exact_power_two_proportions(
    p_a: float,
    p_b: float,
    n: int,
    alpha: float = 0.05,
    *,
    test: str = "fisher",
    n_grid: int = 101,
) -> float:
    """
    Exact power = sum_{rejecting tables} Bin(i;n,p_a) Bin(j;n,p_b).

    test:
      'fisher'   — reject if Fisher p < alpha (fast, slightly conservative power)
      'pooled_z' — reject if pooled-z p < alpha
      'boschloo' — reject if Boschloo p < alpha (slower; use moderate n)
      'barnard_diff' — reject if Barnard-diff p < alpha (slower; n<=25 recommended)
    """
    n = int(n)
    if n <= 0:
        return 0.0
    if test in {"boschloo", "barnard_diff"} and n > 25:
        test = "fisher"

    # Precompute rejection region for Fisher / pooled_z once
    reject = np.zeros((n + 1, n + 1), dtype=bool)
    if test == "fisher":
        for i in range(n + 1):
            for j in range(n + 1):
                reject[i, j] = fisher_pvalue(i, n, j, n) < alpha
    elif test == "pooled_z":
        for i in range(n + 1):
            for j in range(n + 1):
                reject[i, j] = pooled_z_pvalue(i, n, j, n) < alpha
    elif test == "boschloo":
        for i in range(n + 1):
            for j in range(n + 1):
                reject[i, j] = boschloo_pvalue(i, n, j, n, n_grid=n_grid) < alpha
    elif test == "barnard_diff":
        for i in range(n + 1):
            for j in range(n + 1):
                reject[i, j] = barnard_difference_pvalue(i, n, j, n, n_grid=n_grid) < alpha
    else:
        raise ValueError(f"Unknown test={test}")

    px = binom.pmf(np.arange(n + 1), n, p_a)
    py = binom.pmf(np.arange(n + 1), n, p_b)
    joint = px[:, None] * py[None, :]
    return float(np.sum(joint[reject]))


def sample_size_exact_search(
    p_a: float,
    p_b: float,
    alpha: float = 0.05,
    power: float = 0.80,
    *,
    test: str = "fisher",
    n_min: int = 2,
    n_max: int = 400,
) -> dict:
    """
    Smallest equal-arm n with exact power >= target (binary search).
    Starts from asymptotic n* as a warm start.
    """
    n_asym = sample_size_two_proportions(p_a, p_b, alpha, power)
    if not np.isfinite(n_asym):
        return {"n_star_exact": None, "n_star_asymptotic": None, "power": None, "test": test}

    lo = max(n_min, int(max(2, 0.5 * n_asym)))
    hi = min(n_max, int(max(n_asym * 1.5, n_asym + 20)))

    while exact_power_two_proportions(p_a, p_b, hi, alpha, test=test) < power and hi < n_max:
        hi = min(n_max, hi + max(10, hi // 5))

    best = None
    left, right = lo, hi
    while left <= right:
        mid = (left + right) // 2
        pw = exact_power_two_proportions(p_a, p_b, mid, alpha, test=test)
        if pw >= power:
            best = mid
            right = mid - 1
        else:
            left = mid + 1

    if best is None:
        best = hi
    pw_best = exact_power_two_proportions(p_a, p_b, best, alpha, test=test)
    return {
        "n_star_exact": int(best),
        "n_star_asymptotic": float(n_asym),
        "power_at_n_exact": float(pw_best),
        "power_target": power,
        "alpha": alpha,
        "test": test,
        "p_a": p_a,
        "p_b": p_b,
    }


def compare_asymptotic_vs_exact(
    scenarios: list[tuple[str, float, float, int]] | None = None,
    alpha: float = 0.05,
) -> dict:
    """
    Transparent audit table: asymptotic power vs exact Fisher power vs MC pooled-z.
    """
    if scenarios is None:
        scenarios = [
            ("90_vs_80_n20", 0.90, 0.80, 20),
            ("90_vs_80_n30", 0.90, 0.80, 30),
            ("90_vs_80_n50", 0.90, 0.80, 50),
            ("90_vs_80_n199", 0.90, 0.80, 199),
            ("90_vs_85_n20", 0.90, 0.85, 20),
            ("90_vs_50_n20", 0.90, 0.50, 20),
            ("80_vs_70_n20", 0.80, 0.70, 20),
            ("95_vs_85_n30", 0.95, 0.85, 30),
            ("95_vs_90_n40", 0.95, 0.90, 40),
        ]

    from lod_guide.s5_sample_size import simulate_power_two_proportions

    rows = []
    for label, pa, pb, n in scenarios:
        # For large n, skip full exact n* search in default study (slow);
        # still compute exact power at the stated n.
        asym = power_two_proportions(pa, pb, n, alpha)
        exact_f = exact_power_two_proportions(pa, pb, n, alpha, test="fisher")
        exact_z = exact_power_two_proportions(pa, pb, n, alpha, test="pooled_z")
        mc = simulate_power_two_proportions(pa, pb, n, alpha, n_sims=8000, seed=11)
        n_asym = sample_size_two_proportions(pa, pb, alpha, 0.80)
        row = {
            "label": label,
            "p_a": pa,
            "p_b": pb,
            "n": n,
            "power_asymptotic_pooled_z": asym,
            "power_exact_fisher": exact_f,
            "power_exact_pooled_z_enum": exact_z,
            "power_mc_pooled_z": mc,
            "miss_beta_exact_fisher": 1.0 - exact_f,
            "n_star_asymptotic": n_asym,
        }
        # Exact n* only for smaller asymptotic sizes (enumeration cost ~ n^2)
        if np.isfinite(n_asym) and n_asym <= 80:
            n_exact = sample_size_exact_search(pa, pb, alpha, 0.80, test="fisher", n_max=120)
            row["n_star_exact_fisher"] = n_exact["n_star_exact"]
            row["delta_n_exact_minus_asym"] = int(
                n_exact["n_star_exact"] - round(n_exact["n_star_asymptotic"])
            )
        else:
            row["n_star_exact_fisher"] = None
            row["delta_n_exact_minus_asym"] = None
            row["note"] = "exact n* search deferred for large asymptotic n (use Fisher power at n)"
        rows.append(row)

    return {
        "study_id": "ASYMP_VS_EXACT-v1",
        "alpha": alpha,
        "interpretation": (
            "If |exact Fisher power − asymptotic| is material at small n, "
            "prefer exact n* / Fisher–Boschloo for primary claims; "
            "asymptotic remains a continuous design surface approximation."
        ),
        "rows": rows,
    }


def beta_binomial_predictive_all_positive(n: int, a: float = 1.0, b: float = 1.0) -> float:
    """P(all n successes) under Beta(a,b) prior. Uniform → 1/(n+1)."""
    if a == 1.0 and b == 1.0:
        return 1.0 / (n + 1)
    from scipy.special import beta as beta_fn

    return float(beta_fn(a + n, b) / beta_fn(a, b))
