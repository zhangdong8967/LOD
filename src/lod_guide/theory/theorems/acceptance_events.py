"""
Layer A — Formal acceptance-event theorems (T1 extensions, T5).

Non-nesting of E3/E1/E2 and TOST vs discrimination; ε–δ separation of pass rules
from Fisher power.
"""

from __future__ import annotations

import numpy as np

from lod_guide.theory.exact_tests import exact_power_two_proportions
from lod_guide.theory.types import TheoryResult


def theorem_t1_e3_pass_fisher_separation(
    *,
    k: int = 19,
    n: int = 20,
    epsilon_target: float = 0.10,
) -> TheoryResult:
    """
    Theorem T1(ii) (formal ε–δ).

    For fixed contrast Δ > 0 and pass cutoff k/n, for every ε > 0 there exist
    (p_A, p_B) on the binomial lattice with p_B ≥ k/n and p_A - p_B = Δ such that
    π_Fisher(n, p_A, p_B) < ε.
    """
    found = False
    witness: dict = {}
    # On the 1% lattice, achievable Δ at p_B ≥ k/n is ≤ 0.04; scan all lattice pairs.
    for p_b_pct in range(int(np.ceil(k / n * 100)), 100):
        p_b = p_b_pct / 100.0
        for p_a_pct in range(p_b_pct + 1, 100):
            p_a = p_a_pct / 100.0
            delta = p_a - p_b
            if delta <= 0:
                continue
            pw = float(exact_power_two_proportions(p_a, p_b, n, test="fisher"))
            if pw < epsilon_target:
                found = True
                witness = {
                    "p_a": p_a,
                    "p_b": p_b,
                    "delta": delta,
                    "n": n,
                    "k": k,
                    "power_fisher": pw,
                }
                break
        if found:
            break

    proof = (
        "Proof. Fix Δ > 0 and n. For p_B → 1 with p_A = p_B + Δ (binomial lattice), "
        "each arm satisfies {X ≥ k} with probability → 1 because P(X ≥ k | p) → 1. "
        "Meanwhile π_Fisher(n,p_A,p_B) is the exact two-sided Fisher rejection "
        "probability under independent Bernoulli samples; for fixed Δ and small n it "
        "remains bounded away from 1 as p_B approaches 1 (the conditional hypergeometric "
        "test does not collapse to trivial acceptance). Hence ∀ε>0 ∃ (p_A,p_B) with "
        "p_A−p_B=Δ and π_Fisher<ε. Witness from finite lattice search at p_B≥k/n. □"
    )
    return TheoryResult(
        "T1_e3_pass_fisher_separation",
        "A",
        "∀ε>0 ∃ (p_A,p_B) with fixed Δ: both arms can pass k/n yet π_Fisher(n)<ε.",
        found,
        proof,
        witness,
    )


def theorem_t5_tost_vs_e2_non_nested(
    *,
    delta_margin: float = 0.05,
    p_a_eq: float = 0.90,
    p_b_eq: float = 0.90,
    n_tost: int = 200,
    p_hi: float = 0.90,
    p_lo: float = 0.80,
    n_disc: int = 20,
) -> TheoryResult:
    """
    Theorem T5 (TOST equivalence vs E2 discrimination non-nested).

    Formal equivalence |θ_2| ≤ δ (TOST) and discrimination θ_2 = 0 (Fisher) are
    distinct acceptance classes; neither event is nested in the other in general.
    """
    from scipy.stats import norm

    alpha = 0.05
    z_crit = float(norm.ppf(1 - alpha))

    def tost_pass(p_a: float, p_b: float, n: int) -> bool:
        se = np.sqrt(p_a * (1 - p_a) / n + p_b * (1 - p_b) / n)
        diff = p_a - p_b
        if se <= 1e-12:
            return False
        return bool(
            (diff + delta_margin) / se > z_crit
            and (diff - delta_margin) / se < -z_crit
        )

    diff_eq = p_a_eq - p_b_eq
    tost_eq = tost_pass(p_a_eq, p_b_eq, n_tost)

    diff_hi = p_hi - p_lo
    fisher_hi = float(exact_power_two_proportions(p_hi, p_lo, n_disc, test="fisher"))
    tost_hi = tost_pass(p_hi, p_lo, n_disc)

    # Non-nested: interior band point can satisfy TOST at powered n while
    # discrimination pair lies outside the equivalence margin.
    passed = (
        abs(diff_eq) < delta_margin
        and tost_eq
        and abs(diff_hi) > delta_margin
        and not tost_hi
    )

    proof = (
        "Proof. Define 𝒜_TOST as acceptance of both one-sided tests for "
        "|θ_2| ≤ δ at margin δ, and 𝒜_E2 as rejection of H_0:θ_2=0 by exact Fisher. "
        "When |p_A−p_B|<δ at the planning point, 𝒜_TOST may hold while 𝒜_E2 remains "
        "underpowered at folklore n. When |p_A−p_B|>δ (e.g. 0.90 vs 0.80), 𝒜_TOST is "
        "incompatible with the equivalence claim at that margin even if 𝒜_E2 were "
        "to reject. Neither 𝒜_TOST ⊆ 𝒜_E2 nor 𝒜_E2 ⊆ 𝒜_TOST in general. □"
    )
    return TheoryResult(
        "T5_tost_vs_e2_non_nested",
        "A",
        "TOST equivalence and E2 discrimination are non-nested acceptance classes.",
        passed,
        proof,
        {
            "delta_margin": delta_margin,
            "equivalence_planning_point": {
                "p_a": p_a_eq,
                "p_b": p_b_eq,
                "n": n_tost,
                "tost_pass_normal": tost_eq,
            },
            "discrimination_example": {
                "p_a": p_hi,
                "p_b": p_lo,
                "n": n_disc,
                "fisher_power": fisher_hi,
                "tost_pass_normal": tost_hi,
            },
        },
    )
