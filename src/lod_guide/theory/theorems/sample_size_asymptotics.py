"""
Layer A — Fleiss–Chow design-surface asymptotics (Theorem T4).

Leading-term n*(p_A,p_B) ~ C(p̄)/Δ² as contrast Δ → 0.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import norm

from lod_guide.s5_sample_size import sample_size_two_proportions
from lod_guide.theory.types import TheoryResult


def fleiss_leading_coefficient(
    p_bar: float,
    *,
    alpha: float = 0.05,
    power: float = 0.80,
) -> float:
    """C(p̄) such that n*(p̄+Δ/2, p̄−Δ/2) ≈ C/Δ² for small Δ (symmetric about p̄)."""
    za = float(norm.ppf(1 - alpha / 2))
    zb = float(norm.ppf(power))
    var_sym = 2.0 * p_bar * (1.0 - p_bar)
    return float((za * np.sqrt(var_sym) + zb * np.sqrt(var_sym)) ** 2)


def theorem_t4_fleiss_nstar_delta_scaling(
    *,
    p_bar: float = 0.85,
    alpha: float = 0.05,
    power: float = 0.80,
    delta_pp: int = 2,
    rel_tol: float = 0.08,
) -> TheoryResult:
    """
    Theorem T4 (design-surface leading term).

    For fixed p̄ ∈ (0,1), α, and target power 1−β, define symmetric pairs
    p_A = p̄ + Δ/2, p_B = p̄ − Δ/2. Then the Fleiss–Chow design surface satisfies
        n*(p_A,p_B) = C(p̄,α,β)/Δ² + O(1)
    as Δ → 0, with C = (z_{α/2}√(2p̄(1−p̄)) + z_{1−β}√(2p̄(1−p̄)))².
    """
    c_lead = fleiss_leading_coefficient(p_bar, alpha=alpha, power=power)
    delta = delta_pp / 100.0
    p_a = round(p_bar + delta / 2, 4)
    p_b = round(p_bar - delta / 2, 4)
    if p_b <= 0 or p_a >= 1 or p_a <= p_b:
        return TheoryResult(
            "T4_fleiss_nstar_delta_scaling",
            "A",
            "n*(symmetric about p̄) ~ C(p̄)/Δ² + O(1).",
            False,
            "Invalid p̄ for symmetric pair.",
            {},
        )

    n_star = float(sample_size_two_proportions(p_a, p_b, alpha, power))
    predicted = c_lead / (delta ** 2)
    rel_err = abs(n_star - predicted) / max(predicted, 1.0)

    # Also check Δ=1 pp if feasible
    checks: list[dict] = []
    for dpp in (1, 2, 3, 5):
        d = dpp / 100.0
        pa = round(p_bar + d / 2, 4)
        pb = round(p_bar - d / 2, 4)
        if pb <= 0 or pa >= 1:
            continue
        ns = float(sample_size_two_proportions(pa, pb, alpha, power))
        pred = c_lead / (d ** 2)
        checks.append(
            {
                "delta_pp": dpp,
                "n_star": ns,
                "c_over_delta_sq": pred,
                "rel_err": abs(ns - pred) / max(pred, 1.0),
            }
        )

    passed = rel_err <= rel_tol and all(c["rel_err"] <= rel_tol for c in checks)

    proof = (
        "Proof. Expand p_A=p̄+Δ/2, p_B=p̄−Δ/2 in Eq. (2). The denominator is Δ². "
        "For small Δ, p_A(1−p_A)+p_B(1−p_B)=2p̄(1−p̄)+O(Δ²) and "
        "2p̄(1−p̄) appears in both numerator terms, yielding "
        "n* = ((z_{α/2}+z_{1−β})²·2p̄(1−p̄))/Δ² + O(1). "
        "Finite Δ checks on the integer lattice match within O(1) relative error "
        "for small Δ (numerical certificate). □"
    )
    return TheoryResult(
        "T4_fleiss_nstar_delta_scaling",
        "A",
        "Symmetric Fleiss n*(p̄±Δ/2) = C(p̄)/Δ² + O(1) with explicit leading coefficient.",
        passed,
        proof,
        {
            "p_bar": p_bar,
            "C_leading": c_lead,
            "delta_pp_witness": delta_pp,
            "n_star": n_star,
            "predicted_leading": predicted,
            "rel_err_witness": rel_err,
            "small_delta_checks": checks,
        },
    )
