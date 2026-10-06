"""
Claim-type taxonomy for P1–P18 (theorem vs certificate vs enumeration).

Used in Table 4 and Supplement §S2c so reviewers can see what is proved,
what is enumerated, and what is Monte Carlo.
"""

from __future__ import annotations

from typing import Literal

ClaimType = Literal[
    "logical",           # D1-style; no numeric DGP
    "analytic",          # closed-form proof sketch
    "enumeration",       # exact finite enumeration
    "analytic_plus_enum",  # scale bound + enumeration (P8)
    "mc_certificate",    # Monte Carlo verification
    "extension",         # outside default E1–E3 loop
]

_CLAIM_TYPES: dict[str, ClaimType] = {
    "P1_saturation": "analytic",
    "P2_binomial_reliability": "analytic",
    "P3_two_proportion_power": "mc_certificate",
    "P4_design_effect": "analytic",
    "P5_parametric_lob_inconsistency": "analytic",
    "P6_ovl_separation": "analytic",
    "P7_all_positive_trap": "enumeration",
    "P8_exact_vs_asymptotic_gap": "analytic_plus_enum",
    "P9_holm_fwer": "mc_certificate",
    "P10_weight_scale_invariance": "analytic",
    "P11_tobit_uncensored_agreement": "mc_certificate",
    "P12_c_optimal_efficiency": "extension",
    "P13_minimax_robust_design": "extension",
    "P14_efficiency_ratio": "extension",
    "P15_lod_identifiability": "extension",
    "P16_saturation_trap": "extension",
    "P17_gated_lob_inflation": "extension",
    "P18_folklore_pareto_dominated": "enumeration",
    "T1_e3_pass_fisher_separation": "enumeration",
    "T2a_pooled_z_fisher_distinct": "analytic_plus_enum",
    "T2b_berry_esseen_design_scale": "analytic_plus_enum",
    "T4_fleiss_nstar_delta_scaling": "analytic",
    "T5_tost_vs_e2_non_nested": "analytic",
    "C_optimal_equivalence": "extension",
    "P17_selective_inflation": "extension",
    "P13_minimax_formal": "extension",
    "P17_sample_split_remedy": "mc_certificate",
}


def claim_type_for(result_id: str) -> ClaimType:
    if result_id in _CLAIM_TYPES:
        return _CLAIM_TYPES[result_id]
    if result_id.startswith(("P12_", "P13_", "P14_", "P15_", "P16_", "P17_")):
        return "extension"
    return "mc_certificate"


def claim_type_note(claim: ClaimType) -> str:
    notes = {
        "logical": "Inferential; no sampling model required",
        "analytic": "Closed-form or limit argument; numeric check only sanity",
        "enumeration": "Exact finite enumeration; reproducible bit-for-bit",
        "analytic_plus_enum": "Analytic scale where valid; enumeration authoritative",
        "mc_certificate": "Monte Carlo or grid MC; fixed seeds in audit JSON",
        "extension": "Documented branch; not default E1–E3 verification engine",
    }
    return notes.get(claim, "")
