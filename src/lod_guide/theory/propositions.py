"""
Machine-checkable theory results (facade over three-layer architecture).

Layer A — Analytic theorems:     theory/theorems/
Layer B — Finite-sample bounds:  theory/bounds/
Layer C — Numerical certificates: theory/certificates/

Legacy ``prop*`` names are preserved as aliases for backward compatibility.
"""

from __future__ import annotations

from lod_guide.theory.bounds.finite_sample import theorem_p8_exact_vs_asymptotic_gap
from lod_guide.theory.certificates.numerical import (
    certificate_p10_weight_scale,
    certificate_p11_tobit_agreement,
    certificate_p12_c_optimal,
    certificate_p13_minimax,
    certificate_p14_efficiency,
    certificate_p17_gated_inflation,
    certificate_p3_fleiss_chow,
    certificate_p4_design_effect,
    certificate_p9_holm_fwer,
)
from lod_guide.theory.theorems.admissibility import theorem_p18_folklore_inadmissible
from lod_guide.theory.theorems.analytic import (
    theorem_p1_saturation,
    theorem_p2_binomial_identity,
    theorem_p5_parametric_lob_mismatch,
    theorem_p7_all_positive_cp_lower,
)
from lod_guide.theory.theorems.identification import (
    theorem_p15_lod_identifiable,
    theorem_p16_saturation_non_identifiable,
)
from lod_guide.theory.theorems.ovl import theorem_p6_ovl_monotone
from lod_guide.theory.types import PropositionCertificate, TheoryResult

# Re-export types
__all__ = [
    "PropositionCertificate",
    "TheoryResult",
    "verify_all_propositions",
    "verify_by_layer",
    "prop1_saturation",
    "prop2_binomial_identity",
    "prop3_fleiss_chow_certificate",
    "prop4_design_effect",
    "prop5_gaussian_lob_mismatch_exponential",
    "prop6_ovl_decreases_with_n",
    "prop7_all_positive_trap",
    "prop8_exact_vs_asymptotic_gap",
    "prop9_holm_fwer_control_sketch",
    "prop10_weight_scale_invariance",
    "prop11_tobit_reduces_to_gaussian_without_censoring",
    "prop12_c_optimal_beats_equal_reference",
    "prop13_minimax_worst_case_improves",
    "prop14_asymptotic_efficiency_certificate",
    "prop15_lod_identifiable_on_good_grid",
    "prop16_saturation_non_identifiable",
    "prop17_gated_lob_inflation",
    "prop18_folklore_pareto_dominated",
]

# Legacy aliases (prop* → theorem/certificate)
prop1_saturation = theorem_p1_saturation
prop2_binomial_identity = theorem_p2_binomial_identity
prop3_fleiss_chow_certificate = certificate_p3_fleiss_chow
prop4_design_effect = certificate_p4_design_effect
prop5_gaussian_lob_mismatch_exponential = theorem_p5_parametric_lob_mismatch
prop6_ovl_decreases_with_n = theorem_p6_ovl_monotone
prop7_all_positive_trap = theorem_p7_all_positive_cp_lower
prop8_exact_vs_asymptotic_gap = theorem_p8_exact_vs_asymptotic_gap
prop9_holm_fwer_control_sketch = certificate_p9_holm_fwer
prop10_weight_scale_invariance = certificate_p10_weight_scale
prop11_tobit_reduces_to_gaussian_without_censoring = certificate_p11_tobit_agreement
prop12_c_optimal_beats_equal_reference = certificate_p12_c_optimal
prop13_minimax_worst_case_improves = certificate_p13_minimax
prop14_asymptotic_efficiency_certificate = certificate_p14_efficiency
prop15_lod_identifiable_on_good_grid = theorem_p15_lod_identifiable
prop16_saturation_non_identifiable = theorem_p16_saturation_non_identifiable
prop17_gated_lob_inflation = certificate_p17_gated_inflation
prop18_folklore_pareto_dominated = theorem_p18_folklore_inadmissible


def verify_all_propositions() -> list[TheoryResult]:
    """Run all P1–P18 plus supplementary c-optimal equivalence and selective inflation."""
    from lod_guide.theory.design.equivalence import theorem_c_optimal_equivalence
    from lod_guide.theory.design.minimax import minimax_theorem_certificate
    from lod_guide.theory.selective.gated_error import theorem_selective_inflation
    from lod_guide.theory.selective.sample_split import theorem_p17_sample_split_remedy

    return [
        prop1_saturation(),
        prop2_binomial_identity(),
        prop3_fleiss_chow_certificate(),
        prop4_design_effect(),
        prop5_gaussian_lob_mismatch_exponential(),
        prop6_ovl_decreases_with_n(),
        prop7_all_positive_trap(),
        prop8_exact_vs_asymptotic_gap(),
        prop9_holm_fwer_control_sketch(),
        prop10_weight_scale_invariance(),
        prop11_tobit_reduces_to_gaussian_without_censoring(),
        prop12_c_optimal_beats_equal_reference(),
        prop13_minimax_worst_case_improves(),
        prop14_asymptotic_efficiency_certificate(),
        prop15_lod_identifiable_on_good_grid(),
        prop16_saturation_non_identifiable(),
        prop17_gated_lob_inflation(),
        prop18_folklore_pareto_dominated(),
        theorem_c_optimal_equivalence(),
        theorem_selective_inflation(),
        theorem_p17_sample_split_remedy(),
        minimax_theorem_certificate(),
    ]


def verify_by_layer(layer: str) -> list[TheoryResult]:
    """Return results filtered by layer A, B, or C."""
    return [r for r in verify_all_propositions() if r.layer == layer.upper()]
