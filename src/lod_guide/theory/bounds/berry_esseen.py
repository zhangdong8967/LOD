"""
Berry–Esseen uniform bounds for two-proportion LoD discrimination (P8).

For independent Bernoulli pairs defining W_i = Y_{A,i} - Y_{B,i} with
E[W]=Δ, Var(W)=v, the standardized sum satisfies
    sup_x |P(Z_n ≤ x) - Φ(x)| ≤ C · ρ / (v^{3/2} √n),
where ρ = E|W-Δ|^3 and C = 0.4748 (Shevtsova 2011 constant).
"""

from __future__ import annotations

import math

import numpy as np
from scipy.stats import norm

# Best known universal Berry–Esseen constant (Shevtsova, 2011).
BERRY_ESSEEN_CONSTANT: float = 0.4748


def _w_distribution(p_a: float, p_b: float) -> tuple[float, float, float, float]:
    """
    Exact pmf of W = Y_A - Y_B on {-1, 0, 1} for independent Bernoulli draws.

    Returns (p_w_minus1, p_w0, p_w1, delta).
    """
    delta = p_a - p_b
    p1 = p_a * (1.0 - p_b)  # W=+1: A=1,B=0
    pm1 = (1.0 - p_a) * p_b  # W=-1: A=0,B=1
    p0 = 1.0 - p1 - pm1
    return pm1, p0, p1, delta


def third_central_moment_w(p_a: float, p_b: float) -> float:
    """ρ = E|W - Δ|^3 for one Bernoulli pair (exact closed form)."""
    pm1, p0, p1, delta = _w_distribution(p_a, p_b)
    return (
        pm1 * abs(-1.0 - delta) ** 3
        + p0 * abs(0.0 - delta) ** 3
        + p1 * abs(1.0 - delta) ** 3
    )


def variance_w(p_a: float, p_b: float) -> float:
    """v = Var(W) for one pair."""
    return p_a * (1.0 - p_a) + p_b * (1.0 - p_b)


def berry_esseen_cdf_error(n: int, p_a: float, p_b: float) -> float:
    """
    Uniform CDF error bound ε_n for Z_n = (S_n - nΔ) / (σ √n).

        ε_n = C · ρ / (v^{3/2} √n).
    """
    if n <= 0:
        return float("inf")
    v = variance_w(p_a, p_b)
    if v <= 0:
        return float("inf")
    rho = third_central_moment_w(p_a, p_b)
    return BERRY_ESSEEN_CONSTANT * rho / (v ** 1.5 * math.sqrt(n))


def berry_esseen_power_gap_lower_bound(
    n: int,
    p_a: float,
    p_b: float,
    *,
    alpha: float = 0.05,
) -> dict:
    """
    Analytic lower bound on Power_asym - Power_Fisher via Berry–Esseen.

    If the pooled-z test uses Φ critical values, perturbing the CDF by at most
    ε_n at the decision boundary changes two-sided power by at most ε_n φ(z*),
    where z* is the effective standardised boundary under H1 (one-sided
    Lipschitz sensitivity; the factor 2 is not applied because the asym–Fisher
    gap is a signed discrepancy, not a symmetric worst case).

    Under H1, non-centrality κ = |Δ| √(n/v). The boundary in standardised units
    is approximately z_{1-α/2} - κ (one-sided contribution to two-sided gap).
    """
    v = variance_w(p_a, p_b)
    delta = abs(p_a - p_b)
    eps = berry_esseen_cdf_error(n, p_a, p_b)
    z_crit = float(norm.ppf(1.0 - alpha / 2.0))
    kappa = delta * math.sqrt(n / v) if v > 0 else 0.0

    # One-sided Lipschitz sensitivity at the effective boundary.
    phi_at_boundary = float(norm.pdf(z_crit - kappa))
    gap_lb = eps * phi_at_boundary

    # Underpowered scale: when κ < z_crit, normal approximation error dominates.
    underpowered = kappa < z_crit and n * delta * delta / max(v, 1e-12) < 8.0

    return {
        "n": n,
        "p_a": p_a,
        "p_b": p_b,
        "delta": delta,
        "variance_w": v,
        "third_moment_rho": third_central_moment_w(p_a, p_b),
        "berry_esseen_epsilon": eps,
        "noncentrality_kappa": kappa,
        "z_crit": z_crit,
        "phi_at_boundary": phi_at_boundary,
        "power_gap_lower_bound": gap_lb,
        "underpowered_regime": underpowered,
        "berry_esseen_formula": "C * rho / (v^(3/2) * sqrt(n))",
    }


def verify_be_gap_vs_enumerated(
    n: int,
    p_a: float,
    p_b: float,
    *,
    alpha: float = 0.05,
    exact_gap: float,
) -> dict:
    """Check analytic BE lower bound is conservative vs enumerated gap."""
    be = berry_esseen_power_gap_lower_bound(n, p_a, p_b, alpha=alpha)
    gap_lb = be["power_gap_lower_bound"]
    return {
        **be,
        "exact_gap_enumerated": exact_gap,
        "be_bound_conservative": gap_lb <= exact_gap + 1e-9,
        "be_explains_positive_fraction": gap_lb / exact_gap if exact_gap > 1e-12 else None,
    }
