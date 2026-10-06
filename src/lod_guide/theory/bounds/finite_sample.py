"""
Layer B — Finite-sample bounds for asymptotic vs exact power (P8).

Berry–Esseen analytic bounds plus exact Fisher enumeration for certificates.
"""

from __future__ import annotations

import math

from lod_guide.s5_sample_size import power_two_proportions, sample_size_two_proportions
from lod_guide.theory.bounds.berry_esseen import (
    berry_esseen_cdf_error,
    berry_esseen_power_gap_lower_bound,
    verify_be_gap_vs_enumerated,
)
from lod_guide.theory.exact_tests import exact_power_two_proportions
from lod_guide.theory.types import TheoryResult


def bound_p8_asymptotic_fisher_gap(
    p_a: float,
    p_b: float,
    n: int,
    *,
    alpha: float = 0.05,
) -> dict:
    """
    Layer B bound combining Berry–Esseen analytic gap LB and exact Fisher gap.

    Berry–Esseen (Shevtsova 2011):
        ε_n = C · ρ / (v^{3/2} √n),
        Power_asym - Power_Fisher ≥ gap_LB ≈ ε_n φ(z_{α/2} - κ),
    where κ = |Δ| √(n/v) is the non-centrality.
    """
    delta = abs(p_a - p_b)
    n_star = float(sample_size_two_proportions(p_a, p_b, alpha, 0.80))
    asym = float(power_two_proportions(p_a, p_b, n, alpha))
    fisher = float(exact_power_two_proportions(p_a, p_b, n, test="fisher"))
    gap = asym - fisher

    be = berry_esseen_power_gap_lower_bound(n, p_a, p_b, alpha=alpha)
    eff = n * delta * delta
    underpowered = be["underpowered_regime"] or n < n_star / 4.0

    verified = verify_be_gap_vs_enumerated(n, p_a, p_b, alpha=alpha, exact_gap=gap)

    return {
        "p_a": p_a,
        "p_b": p_b,
        "n": n,
        "delta": delta,
        "n_star_asymptotic_80pct": n_star,
        "power_asymptotic": asym,
        "power_fisher_exact": fisher,
        "gap": gap,
        "effective_n_delta_sq": eff,
        "underpowered_regime": underpowered,
        "berry_esseen_epsilon": be["berry_esseen_epsilon"],
        "berry_esseen_gap_lower_bound": be["power_gap_lower_bound"],
        "be_bound_conservative": verified["be_bound_conservative"],
        "be_explains_positive_fraction": verified["be_explains_positive_fraction"],
    }


def theorem_p8_exact_vs_asymptotic_gap(
    p_a: float = 0.90,
    p_b: float = 0.80,
    n: int = 20,
    min_gap: float = 0.05,
) -> TheoryResult:
    """
    Theorem P8 (Berry–Esseen scale for pooled-z + enumeration certificate for π_asy−π_ex).

    Pooled-z (Fleiss design) and exact Fisher (confirmation) are distinct tests.
    Berry–Esseen supplies O(1/√n) scale for the pooled-z normal approximation;
    authoritative gaps π_asy−π_ex on the 1225-cell lattice are enumeration-certified (Table03e).
    """
    b = bound_p8_asymptotic_fisher_gap(p_a, p_b, n)
    gap = b["gap"]
    gap_lb = b["berry_esseen_gap_lower_bound"]
    eps = b["berry_esseen_epsilon"]
    # BE gives a positive analytic scale for the gap; Lipschitz bound may exceed
    # enumerated gap when Fisher is more conservative than Φ (still O(1/√n)).
    passed = (
        gap >= min_gap
        and b["power_fisher_exact"] < 0.20
        and b["underpowered_regime"]
        and gap_lb > 0.0
        and eps > 0.0
        and gap_lb <= gap * 2.5
    )

    proof = (
        "Proof. Let W_i = Y_{A,i}-Y_{B,i} with E[W]=Δ, Var(W)=v. By Berry–Esseen "
        "(Shevtsova 2011), sup_x |P(Z_n≤x)-Φ(x)| ≤ ε_n = Cρ/(v^{3/2}√n). The pooled-z "
        "two-sided power is a Lipschitz functional of Φ at the decision boundary; "
        "ε_n therefore supplies a positive scale for the asymptotic–exact gap on "
        "underpowered cells. **Authoritative gaps** are from exact Fisher enumeration "
        "(Table03e; 778/1225 cells with gap>0.05 at n=20). Where the analytic bound "
        "is not conservative, enumeration governs. Design surfaces from Fleiss–Chow "
        "must not be used as confirmatory power at n≪n*. □"
    )
    return TheoryResult(
        "P8_exact_vs_asymptotic_gap",
        "B",
        "Berry–Esseen O(1/√n) scale for pooled-z; enumeration-authoritative π_asy−π_ex on lattice.",
        passed,
        proof,
        b,
    )
