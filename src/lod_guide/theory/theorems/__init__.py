"""Layer A analytic theorems with proof sketches."""

__all__ = [
    "theorem_p1_saturation",
    "theorem_p2_binomial_identity",
    "theorem_p5_parametric_lob_mismatch",
    "theorem_p7_all_positive_cp_lower",
    "theorem_p15_lod_identifiable",
    "theorem_p16_saturation_non_identifiable",
    "theorem_p18_folklore_inadmissible",
]


def __getattr__(name: str):
    if name in (
        "theorem_p1_saturation",
        "theorem_p2_binomial_identity",
        "theorem_p5_parametric_lob_mismatch",
        "theorem_p7_all_positive_cp_lower",
    ):
        from lod_guide.theory.theorems import analytic as mod

        return getattr(mod, name)
    if name in ("theorem_p15_lod_identifiable", "theorem_p16_saturation_non_identifiable"):
        from lod_guide.theory.theorems import identification as mod

        return getattr(mod, name)
    if name == "theorem_p18_folklore_inadmissible":
        from lod_guide.theory.theorems import admissibility as mod

        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
