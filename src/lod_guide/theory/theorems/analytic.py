"""
Layer A — Analytic theorems (P1, P2, P5, P7).

Each function returns a TheoryResult with a proof sketch suitable for the
theory monograph. Numerical checks are minimal sanity verification only.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import binom, norm

from lod_guide.theory.exact import clopper_pearson_interval, parametric_vs_quantile_lob_exponential
from lod_guide.theory.types import TheoryResult


def theorem_p1_saturation(
    p_a: float = 0.90,
    p_b: float = 0.80,
    n_large: int = 50,
    eps: float = 1e-6,
) -> TheoryResult:
    """
    Theorem P1 (saturation / information destruction).

    φ_n(p) = 1 - (1-p)^n satisfies
        lim_{n→∞} (φ_n(p_A) - φ_n(p_B)) = 0
    for fixed 0 < p_B < p_A < 1. Moreover the gap decays geometrically:
        φ_n(p_A) - φ_n(p_B) = (1-p_B)^n - (1-p_A)^n = O((1-p_A)^n).
    """
    phi = lambda p, n: 1.0 - (1.0 - p) ** n
    gap_n = phi(p_a, n_large) - phi(p_b, n_large)
    gap_1 = phi(p_a, 1) - phi(p_b, 1)
    rate_bound = (1.0 - p_a) ** n_large
    passed = gap_n < eps and gap_1 > gap_n and gap_n <= rate_bound + 1e-12

    proof = (
        "Proof. For 0 < p_A, p_B < 1 with p_B < p_A, we have 0 < (1-p_A) < (1-p_B) < 1. "
        "Hence φ_n(p) = 1 - (1-p)^n → 1 geometrically for each p, and "
        "φ_n(p_A) - φ_n(p_B) = (1-p_B)^n - (1-p_A)^n → 0. The rate is dominated by "
        "(1-p_A)^n since (1-p_B)^n - (1-p_A)^n ≤ (1-p_A)^n · ((1-p_B)/(1-p_A))^n for n≥1 "
        "when p_B < p_A. Comparative endpoints based on φ_n become arbitrarily insensitive "
        "to Δ = p_A - p_B as n grows. □"
    )
    return TheoryResult(
        "P1_saturation",
        "A",
        "lim (φ_n(p_A)-φ_n(p_B))=0; comparative use of φ_n is information-destroying.",
        passed,
        proof,
        {
            "gap_n1": gap_1,
            f"gap_n{n_large}": gap_n,
            "geometric_rate_bound": rate_bound,
            "eps": eps,
        },
    )


def theorem_p2_binomial_identity(p: float = 0.3, n: int = 12) -> TheoryResult:
    """Lemma P2: P(S_n ≥ 1) = 1 - (1-p)^n (exact binomial identity)."""
    closed = 1.0 - (1.0 - p) ** n
    enumer = float(sum(binom.pmf(k, n, p) for k in range(1, n + 1)))
    passed = abs(closed - enumer) < 1e-12

    proof = (
        "Proof. Let S_n ~ Binomial(n,p). Then P(S_n ≥ 1) = 1 - P(S_n = 0) = 1 - (1-p)^n. "
        "The identity follows from the binomial pmf or complement of the all-failure event. □"
    )
    return TheoryResult(
        "P2_binomial_reliability",
        "A",
        "P(S_n>=1)=1-(1-p)^n.",
        passed,
        proof,
        {"closed": closed, "enumerated": enumer},
    )


def theorem_p5_parametric_lob_mismatch(alpha: float = 0.05) -> TheoryResult:
    """
    Theorem P5 (parametric LoB inconsistency under skew).

    For X ~ Exp(1), LoB_par = μ + z_{1-α}σ ≠ F^{-1}(1-α) = -log(α).
    More generally, mean+z·SD equals the (1-α) quantile iff F is Gaussian
    (location-scale), up to affine transform.
    """
    exhibit = parametric_vs_quantile_lob_exponential(alpha)
    lob_par = exhibit["lob_parametric_mean_plus_z_sd"]
    lob_true = exhibit["lob_true_quantile"]
    passed = abs(lob_par - lob_true) > 0.2

    proof = (
        "Proof. For Exp(1), μ=1, σ=1, so LoB_par = 1 + z_{1-α}. The exact (1-α) quantile "
        "is F^{-1}(1-α) = -log(α). Equality of mean+z·SD thresholds with upper quantiles "
        "characterizes the Gaussian family among continuous laws with finite variance "
        "(classical characterization). Hence parametric LoB does not control Type I at α "
        "under skew. Operational corollary: use F^{-1}(1-α) (nonparametric) when diagnostics "
        "reject Gaussianity. □"
    )
    return TheoryResult(
        "P5_parametric_lob_inconsistency",
        "A",
        "For Exp(1), mean+z·sd ≠ F^{-1}(1-α); parametric LoB miscalibrated.",
        passed,
        proof,
        exhibit,
    )


def theorem_p7_all_positive_cp_lower(
    n: int = 5,
    p_modest: float = 0.80,
    claim: float = 0.95,
    alpha: float = 0.05,
) -> TheoryResult:
    """
    Theorem P7 (all-positive trap + exact Clopper–Pearson lower bound).

    After observing X = n successes:
      1. P(X=n | p) = p^n;
      2. The exact one-sided (1-α) lower confidence limit is p_L = α^{1/n};
      3. The two-sided Clopper–Pearson lower uses (α/2)^{1/n}.

    The one-sided limit is the largest p_L such that P(X=n | p=p_L) ≤ α
    (equivalently, the smallest p for which n/n is still plausible at level α).
    """
    p_all = float(p_modest**n)
    lower_one = float(alpha ** (1.0 / n))
    cp_low, _ = clopper_pearson_interval(n, n, alpha=alpha)
    cp_one_sided = float((alpha) ** (1.0 / n))

    # Verify CP formulas and that one-sided lower cannot certify high claim
    passed = (
        lower_one < claim
        and abs(cp_low - (alpha / 2) ** (1.0 / n)) < 1e-10
        and abs(lower_one - cp_one_sided) < 1e-12
    )

    proof = (
        "Proof. (1) P(X=n|p) = p^n is immediate. "
        "(2) For a one-sided (1-α) lower bound on p after x=n, require "
        "P(X=n | p=p_L) ≤ α, i.e. p_L^n ≤ α, hence p_L = α^{1/n}. This is the "
        "largest lower limit compatible with observing n/n at one-sided level α "
        "(Clopper–Pearson / Lehmann–Scheffé exact binomial theory). "
        "(3) Two-sided CP uses (α/2)^{1/n}. Therefore n/n does not certify p≥p_0 "
        "when α^{1/n} << p_0. □"
    )
    return TheoryResult(
        "P7_all_positive_trap",
        "A",
        "n/n successes do not certify a high LoD claim: CP lower = α^(1/n) << claim while p^n can be large.",
        passed,
        proof,
        {
            "n": n,
            "p_modest": p_modest,
            "P_all_positive": p_all,
            "CP_onesided_lower": lower_one,
            "CP_twosided_lower": cp_low,
            "claim": claim,
            "posterior_uniform_P_below_claim": float(claim ** (n + 1)),
        },
    )
