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
    Theorem P18 (local Pareto inadmissibility on exact Fisher OC plane).

    For E2 at (p_A,p_B), folklore design n=20 is **locally** Pareto-dominated within
    n'∈{21,…,35} on (τ,π) for the illustrative pair and for 91% of lattice cells;
    this is NOT a global inadmissibility theorem over all n'.
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
        "π(n) = exact Fisher power at (p_A, p_B). A design n1 is locally Pareto-dominated by n2 "
        "if τ(n2) ≤ τ(n1) and π(n2) ≥ π(n1) with strict inequality in at least one coordinate. "
        "Enumeration over n in a stated local window (e.g. n' ∈ {21,…,35} at folklore n=20) "
        "yields a strict dominator for (0.90, 0.80). Therefore n=20 is inadmissible on the "
        "exact OC plane for that alternative; powered n* achieves higher π at comparable or lower τ. "
        "Lattice scans in data/research/ quantify the fraction of cells with a local dominator; "
        "undominated cells are not powered exemptions (see pareto_lattice_undominated.json). □"
    )
    return TheoryResult(
        "P18_folklore_pareto_dominated",
        "B",
        "Folklore n=20 is locally Pareto-dominated within n'∈{21,…,35} on exact Fisher OC (lattice scan); not global.",
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
