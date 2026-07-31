"""
Identifiability certificates for log10(LoD) under binomial dose–response models.

P15: LoD concentration is identifiable when β ≠ 0, Fisher rank = 2, and at least
     two levels carry interior hit rates.
P16: On saturation plates (all p ≈ 0 or ≈ 1), Fisher information for log10(LoD)
     collapses — large n cannot rescue a bad concentration grid.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from lod_guide.theory.lod_dose_response import (
    DoseResponseTruth,
    asymptotic_lod_se_log10,
    fisher_info_alpha_beta,
    grad_log10_lod,
)


@dataclass(frozen=True)
class IdentifiabilityCertificate:
    identifiable: bool
    fisher_rank: int
    n_interior_levels: int
    min_interior_p: float
    max_interior_p: float
    se_log10_lod: float
    reasons: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "identifiable": self.identifiable,
            "fisher_rank": self.fisher_rank,
            "n_interior_levels": self.n_interior_levels,
            "min_interior_p": self.min_interior_p,
            "max_interior_p": self.max_interior_p,
            "se_log10_lod": self.se_log10_lod,
            "reasons": list(self.reasons),
        }


def _interior_levels(
    truth: DoseResponseTruth,
    concentrations: np.ndarray,
    *,
    eps: float,
) -> tuple[int, float, float]:
    p = truth.p_at_log10(np.log10(np.asarray(concentrations, dtype=float)))
    interior = (p > eps) & (p < 1.0 - eps)
    n_int = int(np.sum(interior))
    if n_int == 0:
        return 0, float(np.min(p)), float(np.max(p))
    return n_int, float(np.min(p[interior])), float(np.max(p[interior]))


def lod_identifiability_certificate(
    truth: DoseResponseTruth,
    concentrations: np.ndarray,
    n_per_level: np.ndarray,
    *,
    eps: float = 0.02,
    min_interior_levels: int = 2,
    max_se: float = 10.0,
) -> IdentifiabilityCertificate:
    """
    Return an auditable identifiability verdict for log10(LoD_γ).

    Conditions (P15):
      - |β| > 1e-8
      - Fisher information rank = 2
      - ≥ min_interior_levels with p(c) ∈ (eps, 1-eps)
      - finite asymptotic SE(log10 LoD) below max_se
    """
    reasons: list[str] = []
    c = np.asarray(concentrations, dtype=float)
    n = np.asarray(n_per_level, dtype=float)

    if abs(truth.slope) < 1e-8:
        reasons.append("slope_near_zero")

    info = fisher_info_alpha_beta(truth, c, n)
    rank = int(np.linalg.matrix_rank(info))
    if rank < 2:
        reasons.append("fisher_rank_deficient")

    n_int, p_min, p_max = _interior_levels(truth, c, eps=eps)
    if n_int < min_interior_levels:
        reasons.append("saturation_or_floor_plateau")

    se_block = asymptotic_lod_se_log10(truth, c, n)
    se = float(se_block["se_log10_lod"])
    if not np.isfinite(se) or se > max_se:
        reasons.append("se_log10_lod_nonfinite_or_large")

    # Gradient of x_L w.r.t. (α,β) must be nonzero for c-identifiability
    grad = grad_log10_lod(truth)
    if float(np.linalg.norm(grad)) < 1e-10:
        reasons.append("lod_gradient_degenerate")

    identifiable = len(reasons) == 0
    return IdentifiabilityCertificate(
        identifiable=identifiable,
        fisher_rank=rank,
        n_interior_levels=n_int,
        min_interior_p=p_min,
        max_interior_p=p_max,
        se_log10_lod=se,
        reasons=tuple(reasons),
    )


def saturation_certificate(
    truth: DoseResponseTruth,
    concentrations: np.ndarray,
    n_per_level: np.ndarray,
    *,
    eps: float = 0.02,
) -> dict:
    """
    P16: demonstrate information collapse on all-saturated grids even when N is large.
    """
    cert = lod_identifiability_certificate(truth, concentrations, n_per_level, eps=eps)
    info = fisher_info_alpha_beta(truth, concentrations, n_per_level)
    grad = grad_log10_lod(truth)
    # c-information: (grad' I^{-1} grad)^{-1} when invertible
    try:
        cov = np.linalg.inv(info)
        c_info = float(1.0 / max(grad @ cov @ grad, 1e-300))
    except np.linalg.LinAlgError:
        c_info = 0.0

    return {
        "identifiable": cert.identifiable,
        "c_information": c_info,
        "fisher_rank": cert.fisher_rank,
        "n_interior_levels": cert.n_interior_levels,
        "total_n": int(np.sum(n_per_level)),
        "se_log10_lod": cert.se_log10_lod,
        "saturation_trap": not cert.identifiable and int(np.sum(n_per_level)) >= 20,
    }
