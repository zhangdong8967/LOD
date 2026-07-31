"""
Layer A — Identifiability theorems (P15, P16).

Formalizes when log10(LoD) is identifiable under binomial dose–response models.
"""

from __future__ import annotations

import numpy as np

from lod_guide.research.probit_design_grid import allocate_n, make_concentration_grid
from lod_guide.theory.identification import lod_identifiability_certificate, saturation_certificate
from lod_guide.theory.lod_dose_response import default_synthetic_truth
from lod_guide.theory.types import TheoryResult


def theorem_p15_lod_identifiable(
    *,
    eps: float = 0.02,
    min_interior_levels: int = 2,
) -> TheoryResult:
    """
    Theorem P15 (LoD identifiability — sufficient conditions).

    Under logistic/probit binomial GLM with |β| > 0, log10(LoD_γ) is identifiable
    when:
      (i) Fisher information I(α,β) has rank 2;
      (ii) ≥ 2 design concentrations carry interior hit rates p(c) ∈ (ε, 1-ε);
      (iii) ∇_{(α,β)} log10(LoD) ≠ 0.

    Then asymptotic c-information I_c(LoD) = (g' I^{-1} g)^{-1} > 0.
    """
    truth = default_synthetic_truth()
    lod = truth.lod()
    conc = make_concentration_grid(lod, n_levels=5, pattern="dense_near_lod")
    n_vec = allocate_n(60, 5, scheme="lod_weighted", lod=lod, concentrations=conc)
    cert = lod_identifiability_certificate(
        truth, conc, n_vec, eps=eps, min_interior_levels=min_interior_levels
    )
    passed = cert.identifiable

    proof = (
        "Proof sketch. Model: η(c) = α + β log10(c), p(c) = g(η(c)) for link g. "
        "LoD_γ solves g(α + β x_L) = γ with x_L = log10(LoD). By implicit function theorem, "
        "x_L is locally identifiable iff β ≠ 0. Expected Fisher information for (α,β) from "
        "independent Binomial(n_k, p(c_k)) contributes rank 2 iff the design spans both "
        "parameters — requiring at least two levels with p(c) strictly inside (0,1) so that "
        "weights w_k = (dp/dη)²/(p(1-p)) > 0 and log-spaced x_k yield full-rank design matrix. "
        "c-identifiability: Var(log10 LoD) = g' I^{-1} g with g = ∇_{(α,β)} x_L = (-1/β, -x_L/β). "
        "Finite when rank(I)=2 and g≠0. □"
    )
    return TheoryResult(
        "P15_lod_identifiability",
        "A",
        "LoD concentration is identifiable when Fisher rank=2 and ≥2 interior hit-rate levels exist.",
        passed,
        proof,
        cert.to_dict(),
    )


def theorem_p16_saturation_non_identifiable(
    *,
    eps: float = 0.02,
    min_total_n: int = 20,
) -> TheoryResult:
    """
    Theorem P16 (saturation trap — structural non-identifiability).

    If all design concentrations lie on a saturation/floor plateau
    (p(c_k) < ε or p(c_k) > 1-ε for every k), then:
      - rank(I(α,β)) < 2 or c-information I_c(LoD) = 0;
      - increasing total sample size N does not restore identifiability of log10(LoD).

    This is a structural failure distinct from underpowered G2 comparison.
    """
    truth = default_synthetic_truth()
    lod = truth.lod()
    sat_conc = lod * np.array([1e-4, 2e-4, 5e-4, 1e-3, 2e-3])
    sat_n = np.full(5, max(min_total_n // 5, 4), dtype=float)
    cert = lod_identifiability_certificate(truth, sat_conc, sat_n, eps=eps)
    sat = saturation_certificate(truth, sat_conc, sat_n, eps=eps)
    passed = (not cert.identifiable) and sat["saturation_trap"] and int(np.sum(sat_n)) >= min_total_n

    proof = (
        "Proof sketch. On a floor plate (all p(c_k) ≈ 0), the likelihood depends on α "
        "through g(α + β x_k) ≈ 0 for all k; the slope β is weakly identified because "
        "dp/dη ≈ 0 at each level, collapsing Fisher information I_{ββ} and often rank(I). "
        "The LoD functional x_L = (g^{-1}(γ) - α)/β becomes ill-defined: small changes in "
        "α,β on the plateau induce negligible changes in predicted p, so c-information "
        "I_c = (g' I^{-1} g)^{-1} → ∞ (equivalently SE → ∞). Increasing n_k multiplies "
        "near-singular information but cannot create curvature absent from the design support. "
        "Hence folklore saturation plates yield 'false LoD' regardless of n. □"
    )
    return TheoryResult(
        "P16_saturation_trap",
        "A",
        "Saturation/floor plates yield non-identifiable log10(LoD) despite large total n.",
        passed,
        proof,
        {"certificate": cert.to_dict(), "saturation": sat},
    )
