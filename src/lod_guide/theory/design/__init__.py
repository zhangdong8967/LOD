"""Design theory: c-optimal equivalence and minimax formalization."""

from lod_guide.theory.design.equivalence import check_c_optimal_equivalence, theorem_c_optimal_equivalence
from lod_guide.theory.design.minimax import (
    SlopeUncertaintySet,
    minimax_theorem_certificate,
    worst_case_se_over_slopes,
)

__all__ = [
    "check_c_optimal_equivalence",
    "theorem_c_optimal_equivalence",
    "SlopeUncertaintySet",
    "worst_case_se_over_slopes",
    "minimax_theorem_certificate",
]
