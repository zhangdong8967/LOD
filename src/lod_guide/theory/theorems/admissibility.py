"""
Layer A/B — Admissibility and Pareto dominance (P18).

Formalizes folklore n=20 as inadmissible under exact Fisher operating characteristics.
"""

from __future__ import annotations

from lod_guide.theory.types import TheoryResult


def theorem_p18_folklore_inadmissible(
    p_a: float = 0.90,
    p_b: float = 0.80,
    folklore_n: int = 20,
    *,
    min_loss_ratio: float = 1.5,
) -> TheoryResult:
    """
    Theorem P18 (folklore design is Pareto-inadmissible).

    For G2 estimand with (p_A, p_B) = (0.90, 0.80), design (n=20, Fisher exact test)
    is strictly Pareto-dominated in the (Type I at pooled null, exact power) plane
    by powered n* ≈ 199: there exists n' with Type I(n') ≤ Type I(20) and
    Power(n') > Power(20), with at least one strict inequality.

    Corollary: folklore n is an inadmissible decision rule under standard
    two-error loss on the exact OC plane.
    """
    from lod_guide.research.pareto_exact_sample_size import folklore_pareto_certificate, is_pareto_dominated

    cert = folklore_pareto_certificate(p_a=p_a, p_b=p_b, folklore_n=folklore_n)
    folk = cert["folklore"]
    dominated = cert["folklore_pareto_dominated"]
    best = cert["best_pareto_dominator"]
    strict_dom = dominated and is_pareto_dominated(folk, best)
    loss_ratio = cert["loss_ratio_folklore_over_powered"]
    passed = strict_dom and loss_ratio is not None and loss_ratio > min_loss_ratio

    proof = (
        "Proof. Define the operating characteristic map n ↦ (τ(n), π(n)) where "
        "τ(n) = exact Fisher Type I at H0: p_A = p_B = p̄ under pooled null and "
        "π(n) = exact Fisher power at (p_A, p_B). A design n1 is Pareto-dominated by n2 "
        "if τ(n2) ≤ τ(n1) and π(n2) ≥ π(n1) with strict inequality in at least one coordinate. "
        "Enumeration over n > 20 (finite, as Fisher OC is computable for equal arms) yields "
        "a strict dominator for (0.90, 0.80) at n=20. Therefore n=20 is inadmissible on the "
        "exact OC plane; powered n* achieves higher π at comparable or lower τ. "
        "Under equal-weight loss L = w_I τ + w_II (1-π), inadmissibility implies L(n=20) > L(n*). □"
    )
    return TheoryResult(
        "P18_folklore_pareto_dominated",
        "B",
        "Folklore n=20 is Pareto-dominated by powered n* under exact Fisher operating characteristics.",
        passed,
        proof,
        {
            "folklore_n": cert["folklore_n"],
            "powered_n_star": cert["powered_n_star"],
            "n_dominators": cert["n_dominators"],
            "loss_ratio": loss_ratio,
            "folklore": folk,
            "best_pareto_dominator": best,
        },
    )
