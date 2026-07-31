"""Finite-sample bounds and exact operating characteristics (Layer B)."""

from lod_guide.theory.bounds.berry_esseen import (
    berry_esseen_cdf_error,
    berry_esseen_power_gap_lower_bound,
)
from lod_guide.theory.bounds.finite_sample import (
    bound_p8_asymptotic_fisher_gap,
    theorem_p8_exact_vs_asymptotic_gap,
)

__all__ = [
    "theorem_p8_exact_vs_asymptotic_gap",
    "bound_p8_asymptotic_fisher_gap",
    "berry_esseen_cdf_error",
    "berry_esseen_power_gap_lower_bound",
]
