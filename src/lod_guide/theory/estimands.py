"""
Formal estimands for LoD studies (Clinical Chemistry / ICH E9(R1) spirit).

Each study locks exactly one primary estimand before seeing confirmatory data.

LoD_95 operational semantics: at the LoD benchmark, p(c*)=0.95 so Pr(miss)=0.05
(analytical rare miss). Verification adds inferential alpha/beta on finite n; see
`theory.detection_limit_semantics`.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class EstimandID(str, Enum):
    E1_DETECTION_PROBABILITY = "E1_DETECTION_PROBABILITY"
    E1_LOD_CONCENTRATION = "E1_LOD_CONCENTRATION"
    E2_RATE_DIFFERENCE = "E2_RATE_DIFFERENCE"
    LOQ_CV_AT_CONCENTRATION = "LOQ_CV_AT_CONCENTRATION"
    E3_KN_PROBABILITY = "E3_KN_PROBABILITY"


@dataclass(frozen=True)
class Estimand:
    """Mathematical target of estimation / testing."""

    id: EstimandID
    symbol: str
    definition: str
    null_hypothesis: str | None
    alternative: str | None
    identification_assumptions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["id"] = self.id.value
        return d


ESTIMANDS: dict[EstimandID, Estimand] = {
    EstimandID.E1_DETECTION_PROBABILITY: Estimand(
        id=EstimandID.E1_DETECTION_PROBABILITY,
        symbol="θ₁ = p(c*)",
        definition="Single-trial positivity probability at fixed concentration c* near claimed LoD.",
        null_hypothesis="H0: p(c*) = p0 (manufacturer / protocol claim)",
        alternative="H1: p(c*) = p_alt ≠ p0 (typically p_alt < p0 for underperformance)",
        identification_assumptions=(
            "IID Bernoulli trials at c*",
            "No misclassification beyond the binary rule",
        ),
    ),
    EstimandID.E1_LOD_CONCENTRATION: Estimand(
        id=EstimandID.E1_LOD_CONCENTRATION,
        symbol="θ₁^conc = LoD_α",
        definition="Concentration at which detection probability equals a target (e.g. 95%), or blank-based LoB/LoD functional.",
        null_hypothesis=None,
        alternative=None,
        identification_assumptions=(
            "Chosen LoB/LoD functional matches data law (parametric or nonparametric)",
            "Commutable materials",
        ),
    ),
    EstimandID.E2_RATE_DIFFERENCE: Estimand(
        id=EstimandID.E2_RATE_DIFFERENCE,
        symbol="θ₂ = p_A(c*) − p_B(c*)",
        definition="Difference in single-trial detection probabilities between reagents/lots at c*.",
        null_hypothesis="H0: θ₂ = 0",
        alternative="H1: |θ₂| = Δ* > 0",
        identification_assumptions=(
            "Independent arms (or known dependence structure)",
            "Common concentration c*",
            "Comparative metric is hat{p}, NOT 1-(1-p)^n",
        ),
    ),
    EstimandID.LOQ_CV_AT_CONCENTRATION: Estimand(
        id=EstimandID.LOQ_CV_AT_CONCENTRATION,
        symbol="CV(c) = σ(c)/μ(c)",
        definition="Relative precision at concentration c (LoQ-type claim).",
        null_hypothesis="H0: CV(c) ≤ τ (acceptance)",
        alternative="H1: CV(c) > τ",
        identification_assumptions=(
            "Finite mean and variance at c",
            "Variance function correctly modelled if heteroscedastic",
        ),
    ),
    EstimandID.E3_KN_PROBABILITY: Estimand(
        id=EstimandID.E3_KN_PROBABILITY,
        symbol="θ₃ = P(S_n ≥ k), S_n ~ Bin(n,p)",
        definition="Probability of at least k positives in n replicates.",
        null_hypothesis=None,
        alternative="Require θ₃ ≥ γ",
        identification_assumptions=("IID Bernoulli(p)", "k,n fixed by protocol"),
    ),
}


def estimand_for_goal(goal_value: str) -> Estimand:
    mapping = {
        "E1_VERIFY_LOD": EstimandID.E1_DETECTION_PROBABILITY,
        "E2_COMPARE_REAGENTS": EstimandID.E2_RATE_DIFFERENCE,
        "LOQ_PRECISION": EstimandID.LOQ_CV_AT_CONCENTRATION,
        "E3_QUALITATIVE_KN": EstimandID.E3_KN_PROBABILITY,
    }
    return ESTIMANDS[mapping[goal_value]]
