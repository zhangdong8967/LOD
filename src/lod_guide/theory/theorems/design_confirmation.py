"""
Layer A/B — Design vs confirmation separation (Theorem T2 structure).

Pooled-z (Fleiss design) and exact Fisher (confirmatory) are distinct decision rules;
Berry–Esseen supplies a scale for the pooled-z normal approximation; enumerated
gaps between pooled-z power and Fisher power are authoritative on the lattice.
"""

from __future__ import annotations

from lod_guide.s5_sample_size import power_two_proportions
from lod_guide.theory.bounds.finite_sample import bound_p8_asymptotic_fisher_gap
from lod_guide.theory.exact_tests import exact_power_two_proportions
from lod_guide.theory.types import TheoryResult


def theorem_t2a_pooled_z_fisher_distinct(
    *,
    p_a: float = 0.90,
    p_b: float = 0.80,
    n: int = 20,
) -> TheoryResult:
    """
    Lemma T2a (distinct decision rules).

    Pooled-two-sided-z and exact Fisher are different rejection maps on {0,…,n}²;
    their power functions π_asy and π_ex need not coincide at any (p_A,p_B,n).
    """
    pi_asy = float(power_two_proportions(p_a, p_b, n))
    pi_ex = float(exact_power_two_proportions(p_a, p_b, n, test="fisher"))
    gap = pi_asy - pi_ex
    passed = gap > 0.01

    proof = (
        "Proof. The pooled-z test rejects on a quadratic inequality in (x_A,x_B) "
        "with Gaussian critical values; Fisher's exact test rejects on hypergeometric "
        "tail probabilities conditional on the table margin. These rejection regions "
        "differ on finite {0,…,n}² for generic (p_A,p_B,n), so π_asy≠π_ex in general. "
        "Witness: positive gap at stated (p_A,p_B,n). Design (S5) may reference π_asy; "
        "confirmatory ledgers (S6) must report π_ex at prespecified n. □"
    )
    return TheoryResult(
        "T2a_pooled_z_fisher_distinct",
        "A",
        "Pooled-z and exact Fisher are distinct tests; π_asy≠π_ex in general.",
        passed,
        proof,
        {"p_a": p_a, "p_b": p_b, "n": n, "pi_asy": pi_asy, "pi_ex": pi_ex, "gap": gap},
    )


def theorem_t2b_berry_esseen_design_scale(
    *,
    p_a: float = 0.90,
    p_b: float = 0.80,
    n: int = 20,
) -> TheoryResult:
    """
    Theorem T2b (Berry–Esseen scale for pooled-z normal approximation).

    For W_i=Y_{A,i}−Y_{B,i}, the Berry–Esseen bound ε_n=O(1/√n) controls normal
    approximation error for the pooled-z statistic; combined with Lipschitz transfer,
    |π_asy−Φ| scales as O(ε_n) on underpowered cells. This does NOT bound Fisher
    power directly; lattice enumeration (Table 3e) is authoritative for π_asy−π_ex.
    """
    b = bound_p8_asymptotic_fisher_gap(p_a, p_b, n)
    passed = (
        b["gap"] >= 0.05
        and b["berry_esseen_epsilon"] > 0
        and b["berry_esseen_gap_lower_bound"] > 0
        and b["underpowered_regime"]
    )

    proof = (
        "Proof. Apply Berry–Esseen to Z_n=(W̄−Δ)/√(v/n) for the difference of "
        "Bernoulli samples. The pooled-z two-sided power is a Lipschitz functional "
        "of Φ at the decision boundary, yielding a positive O(ε_n) scale for "
        "normal-approximation error in π_asy. **Corollary (enumeration-authoritative):** "
        "the gap π_asy−π_ex between distinct tests is certified cell-wise on the "
        "1225-cell lattice (Table03e); where the BE scale is not conservative for "
        "that cross-test gap, enumeration governs. □"
    )
    return TheoryResult(
        "T2b_berry_esseen_design_scale",
        "B",
        "BE supplies O(1/√n) scale for pooled-z normal approximation; lattice enum for π_asy−π_ex.",
        passed,
        proof,
        b,
    )
