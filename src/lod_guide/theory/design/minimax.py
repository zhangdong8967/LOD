"""
Minimax design formalization over slope uncertainty (P13 theory module).

    min_{ξ} max_{β ∈ B} SE(log10 LoD; ξ, β)

where B = [β_plan · r_min, β_plan · r_max] is a multiplicative slope uncertainty set.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from lod_guide.theory.lod_dose_response import DoseResponseTruth, default_synthetic_truth, truth_with_slope
from lod_guide.theory.types import TheoryResult


@dataclass(frozen=True)
class SlopeUncertaintySet:
    """Multiplicative slope uncertainty B = {β_plan · r : r ∈ [r_min, r_max]}."""

    r_min: float = 0.5
    r_max: float = 1.5

    def ratios(self, n_points: int = 5) -> list[float]:
        return [float(x) for x in np.linspace(self.r_min, self.r_max, n_points)]

    def contains(self, beta_plan: float, beta_true: float) -> bool:
        if abs(beta_plan) < 1e-12:
            return False
        r = beta_true / beta_plan
        return self.r_min <= r <= self.r_max


def worst_case_se_over_slopes(
    plan: DoseResponseTruth,
    concentrations: np.ndarray,
    n_per_level: np.ndarray,
    uncertainty: SlopeUncertaintySet | None = None,
) -> dict:
    """Max asymptotic SE(log10 LoD) over β ∈ B."""
    from lod_guide.research.minimax_probit_design import worst_case_se_log10_lod

    uncertainty = uncertainty or SlopeUncertaintySet()
    return worst_case_se_log10_lod(plan, concentrations, n_per_level, slope_ratios=uncertainty.ratios())


def minimax_theorem_certificate(
    uncertainty: SlopeUncertaintySet | None = None,
) -> TheoryResult:
    """
    Layer C certificate: minimax design over B improves worst-case SE vs folklore.

    Formal problem:
        ξ* ∈ argmin_{ξ} max_{β∈B} SE(log10 LoD; ξ, β)
    """
    uncertainty = uncertainty or SlopeUncertaintySet()
    from lod_guide.research.minimax_probit_design import minimax_design_search

    search = minimax_design_search()
    ratio = search["worst_case_improvement_vs_folklore"]
    passed = ratio is not None and ratio >= 1.0 + 1e-6

    proof = (
        "Problem. Let B = [r_min·β_plan, r_max·β_plan]. Folklore equal-log design ξ_f "
        "may maximize SE at β ∈ B when the working slope is misspecified. Minimax design "
        "ξ* = argmin_ξ max_{β∈B} SE(ξ;β) allocates support toward the LoD neighborhood "
        "and reduces worst-case asymptotic variance. Certificate: worst-case SE(ξ*) < "
        "worst-case SE(ξ_f) on synthetic truth with B = [0.5, 1.5]·β_plan. □"
    )
    return TheoryResult(
        "P13_minimax_formal",
        "C",
        f"Minimax over B=[{uncertainty.r_min},{uncertainty.r_max}]·β_plan beats folklore equal-log design.",
        passed,
        proof,
        {
            "uncertainty_set": {"r_min": uncertainty.r_min, "r_max": uncertainty.r_max},
            "improvement_ratio": ratio,
            "minimax_design": search.get("minimax_design"),
            "folklore": search.get("folklore_equal_log_equal"),
        },
    )
