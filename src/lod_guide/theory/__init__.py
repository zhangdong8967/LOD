"""Theory subpackage: estimands, three-layer proofs, audit, exact intervals/tests."""

from lod_guide.theory.audit import AuditRecord, new_audit, sha256_hex
from lod_guide.theory.estimands import ESTIMANDS, estimand_for_goal
from lod_guide.theory.exact import clopper_pearson_interval, wilson_interval
from lod_guide.theory.exact_tests import (
    analyze_two_proportions_exact,
    boschloo_pvalue,
    compare_asymptotic_vs_exact,
    exact_power_two_proportions,
    fisher_pvalue,
    sample_size_exact_search,
)
from lod_guide.theory.types import PropositionCertificate, TheoryResult

__all__ = [
    "ESTIMANDS",
    "estimand_for_goal",
    "verify_all_propositions",
    "verify_by_layer",
    "TheoryResult",
    "PropositionCertificate",
    "AuditRecord",
    "new_audit",
    "sha256_hex",
    "wilson_interval",
    "clopper_pearson_interval",
    "fisher_pvalue",
    "boschloo_pvalue",
    "analyze_two_proportions_exact",
    "exact_power_two_proportions",
    "sample_size_exact_search",
    "compare_asymptotic_vs_exact",
]


def __getattr__(name: str):
    if name in ("verify_all_propositions", "verify_by_layer"):
        from lod_guide.theory import propositions as mod

        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
