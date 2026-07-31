"""
LoD Laboratory Guidance Algorithm (lod_guide)

Assumption-gated, estimand-specific path selection and sample-size
framework that operationalizes EP17-class options for clinical laboratories.

Step IDs S0–S7 mirror docs/methodology/ and must stay in sync.
"""

from lod_guide.challenge import (
    CLAIMS_WE_DO_NOT_MAKE,
    CLAIMS_WE_MAY_MAKE,
    POSITIONING_STATEMENT,
    RELATION_TO_STANDARDS,
    manifesto_markdown,
)

__all__ = [
    "GuidanceResult",
    "run_guidance",
    "LoDDesignBlockedError",
    "recommend_multilevel_lod_design",
    "POSITIONING_STATEMENT",
    "RELATION_TO_STANDARDS",
    "CLAIMS_WE_MAY_MAKE",
    "CLAIMS_WE_DO_NOT_MAKE",
    "manifesto_markdown",
    "SCENARIOS",
    "coverage_summary",
    "run_scenario_demo",
    "__version__",
]
__version__ = "0.5.0"


def __getattr__(name: str):
    if name in ("GuidanceResult", "run_guidance"):
        from lod_guide.pipeline import GuidanceResult, run_guidance

        return GuidanceResult if name == "GuidanceResult" else run_guidance
    if name in ("LoDDesignBlockedError", "recommend_multilevel_lod_design"):
        from lod_guide.s5_lod_design import LoDDesignBlockedError, recommend_multilevel_lod_design

        return LoDDesignBlockedError if name == "LoDDesignBlockedError" else recommend_multilevel_lod_design
    if name in ("SCENARIOS", "coverage_summary", "run_scenario_demo"):
        from lod_guide.scenarios import SCENARIOS, coverage_summary, run_scenario_demo

        return {
            "SCENARIOS": SCENARIOS,
            "coverage_summary": coverage_summary,
            "run_scenario_demo": run_scenario_demo,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
