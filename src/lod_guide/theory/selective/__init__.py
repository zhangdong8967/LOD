"""Selective / post-selection inference for assumption-gated LoB paths."""

from lod_guide.theory.selective.gated_error import (
    selective_error_decomposition,
    theorem_selective_inflation,
)
from lod_guide.theory.selective.sample_split import (
    gated_lob_sample_split,
    monte_carlo_compare_split_vs_unsplit,
    theorem_p17_sample_split_remedy,
)

__all__ = [
    "selective_error_decomposition",
    "theorem_selective_inflation",
    "gated_lob_sample_split",
    "monte_carlo_compare_split_vs_unsplit",
    "theorem_p17_sample_split_remedy",
]
