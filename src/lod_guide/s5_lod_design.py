"""
S5 extension — multi-concentration hit-rate LoD design (EP17 probit class).

Before recommending concentrations and allocation for log10(LoD_95) estimation:
  1. P15/P16 identifiability gate (hard stop if saturation/floor plate).
  2. Minimax-over-slopes design search (P13) when identifiable.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from lod_guide.theory.identification import lod_identifiability_certificate
from lod_guide.theory.lod_dose_response import (
    DoseResponseTruth,
    default_synthetic_truth,
)


class LoDDesignBlockedError(ValueError):
    """Concentration grid fails P16 identifiability; do not proceed with LoD planning."""

    def __init__(self, message: str, certificate: dict):
        super().__init__(message)
        self.certificate = certificate


@dataclass
class MultilevelLoDDesignResult:
    blocked: bool
    identifiable: bool
    identifiability: dict
    plan_truth: dict
    proposed_design: dict
    recommended_design: dict | None
    folklore_reference: dict | None
    se_at_plan: float | None
    worst_case_se: float | None
    improvement_worst_case_ratio: float | None
    method: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "blocked": self.blocked,
            "identifiable": self.identifiable,
            "identifiability": self.identifiability,
            "plan_truth": self.plan_truth,
            "proposed_design": self.proposed_design,
            "recommended_design": self.recommended_design,
            "folklore_reference": self.folklore_reference,
            "se_at_plan": self.se_at_plan,
            "worst_case_se": self.worst_case_se,
            "improvement_worst_case_ratio": self.improvement_worst_case_ratio,
            "method": self.method,
            "warnings": self.warnings,
        }


def _folklore_design(truth: DoseResponseTruth, total_n: int, n_levels: int) -> dict:
    from lod_guide.research.probit_design_grid import allocate_n, make_concentration_grid
    from lod_guide.theory.lod_dose_response import asymptotic_lod_se_log10

    lod = truth.lod()
    conc = make_concentration_grid(lod, n_levels=n_levels, pattern="equal_log")
    n_vec = allocate_n(total_n, n_levels, scheme="equal", lod=lod, concentrations=conc)
    se = asymptotic_lod_se_log10(truth, conc, n_vec)
    return {
        "pattern": "equal_log",
        "allocation": "equal",
        "concentrations": conc.tolist(),
        "n_per_level": n_vec.tolist(),
        "total_n": int(n_vec.sum()),
        "se_log10_lod": se["se_log10_lod"],
    }


def recommend_multilevel_lod_design(
    *,
    truth: DoseResponseTruth | None = None,
    concentrations: np.ndarray | None = None,
    n_per_level: np.ndarray | None = None,
    total_n: int = 60,
    n_levels: int = 5,
    block_on_non_identifiable: bool = True,
    slope_ratios: list[float] | None = None,
) -> MultilevelLoDDesignResult:
    """
    S5 probit-path design recommender with P15/P16 gate and P13 minimax fallback.

    Raises LoDDesignBlockedError when ``block_on_non_identifiable`` and the grid
    is on a saturation/floor plateau (P16).
    """
    from lod_guide.research.minimax_probit_design import minimax_design_search
    from lod_guide.research.probit_design_grid import allocate_n, make_concentration_grid

    truth = truth or default_synthetic_truth()
    lod = truth.lod()
    warnings: list[str] = []

    if concentrations is None or n_per_level is None:
        conc = make_concentration_grid(lod, n_levels=n_levels, pattern="equal_log")
        n_vec = allocate_n(total_n, n_levels, scheme="equal", lod=lod, concentrations=conc)
    else:
        conc = np.asarray(concentrations, dtype=float)
        n_vec = np.asarray(n_per_level, dtype=float)

    cert = lod_identifiability_certificate(truth, conc, n_vec)
    cert_dict = cert.to_dict()
    proposed = {
        "concentrations": conc.tolist(),
        "n_per_level": n_vec.tolist(),
        "total_n": int(n_vec.sum()),
        "se_log10_lod": cert.se_log10_lod,
    }

    if not cert.identifiable:
        msg = (
            "LoD design blocked (P16): concentration grid is on a saturation/floor plateau "
            f"or Fisher rank deficient ({', '.join(cert.reasons)}). "
            "Revise concentrations to span the inflection region near the working LoD."
        )
        if block_on_non_identifiable:
            raise LoDDesignBlockedError(msg, cert_dict)
        return MultilevelLoDDesignResult(
            blocked=True,
            identifiable=False,
            identifiability=cert_dict,
            plan_truth={"slope": truth.slope, "lod": lod, "link": truth.link},
            proposed_design=proposed,
            recommended_design=None,
            folklore_reference=None,
            se_at_plan=cert.se_log10_lod,
            worst_case_se=None,
            improvement_worst_case_ratio=None,
            method="blocked_non_identifiable",
            warnings=[msg],
        )

    search = minimax_design_search(truth, total_n=total_n, n_levels=n_levels, slope_ratios=slope_ratios)
    mm = search["minimax_design"]
    folk = search["folklore_equal_log_equal"]
    mm_conc = np.asarray(mm["concentrations"])
    mm_n = np.asarray(mm["n_per_level"])

    recommended = {
        "pattern": mm["pattern"],
        "allocation": mm["allocation"],
        "concentrations": mm["concentrations"],
        "n_per_level": mm["n_per_level"],
        "total_n": int(np.sum(mm_n)),
        "se_at_plan": mm["se_at_plan"],
        "worst_case_se": mm["worst_case_se"],
        "worst_slope_ratio": mm["worst_slope_ratio"],
    }

    if mm["worst_case_se"] >= folk["worst_case_se"]:
        warnings.append("Minimax search did not improve worst-case SE over folklore; review grid.")

    if cert.se_log10_lod > mm["se_at_plan"] * 1.05:
        warnings.append(
            "Proposed equal-log grid has higher plan-slope SE than minimax recommendation; "
            "prefer recommended concentrations/allocation."
        )

    return MultilevelLoDDesignResult(
        blocked=False,
        identifiable=True,
        identifiability=cert_dict,
        plan_truth={"slope": truth.slope, "lod": lod, "link": truth.link},
        proposed_design=proposed,
        recommended_design=recommended,
        folklore_reference={
            "pattern": folk["pattern"],
            "allocation": folk["allocation"],
            "concentrations": folk["concentrations"],
            "n_per_level": folk["n_per_level"],
            "se_at_plan": folk["se_at_plan"],
            "worst_case_se": folk["worst_case_se"],
        },
        se_at_plan=float(mm["se_at_plan"]),
        worst_case_se=float(mm["worst_case_se"]),
        improvement_worst_case_ratio=search.get("worst_case_improvement_vs_folklore"),
        method="minimax_over_slope_ratios",
        warnings=warnings,
    )


def quick_identifiability_check(
    concentrations: np.ndarray,
    n_per_level: np.ndarray,
    *,
    truth: DoseResponseTruth | None = None,
) -> dict:
    """Lightweight P15/P16 check for audits without full minimax search."""
    truth = truth or default_synthetic_truth()
    cert = lod_identifiability_certificate(truth, concentrations, n_per_level)
    return cert.to_dict()
