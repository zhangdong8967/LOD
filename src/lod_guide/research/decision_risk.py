"""
Assumption-gated decision risk for LoD evaluation (G1–G4).

Defines a transparent weighted loss that makes S0–S7 path selection a
risk-minimization problem rather than a folklore SOP checklist:

  L = w_I * TypeI + w_II * β + w_M * 1{parametric mismatch} + w_C * (DE - 1)

Numerical exhibits use existing OC / exact power / LoB coverage machinery.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from lod_guide.s4_models import lob_nonparametric, lob_parametric_normal
from lod_guide.s5_sample_size import design_effect, power_two_proportions, sample_size_two_proportions
from lod_guide.theory.exact_tests import exact_power_two_proportions

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


@dataclass(frozen=True)
class RiskWeights:
    w_type_i: float = 1.0
    w_type_ii: float = 1.0
    w_mismatch: float = 1.0
    w_cluster: float = 0.5


@dataclass
class ScenarioRisk:
    scenario_id: str
    estimand: str
    type_i: float
    beta: float
    mismatch: float
    de_penalty: float
    loss: float
    notes: str


def loss(
    *,
    type_i: float,
    beta: float,
    mismatch: float,
    de: float = 1.0,
    weights: RiskWeights | None = None,
) -> float:
    w = weights or RiskWeights()
    return float(
        w.w_type_i * type_i
        + w.w_type_ii * beta
        + w.w_mismatch * mismatch
        + w.w_cluster * max(0.0, de - 1.0)
    )


def _parametric_mismatch_exp(alpha: float = 0.05, n: int = 200, seed: int = 1) -> float:
    """Fraction of Exp(1) blanks exceeding parametric LoB (should be ≈α if calibrated)."""
    rng = np.random.default_rng(seed)
    # use a large reference sample to set LoB, then fresh draws for exceedance
    ref = rng.exponential(1.0, size=n)
    lob_p = lob_parametric_normal(ref, alpha=alpha)
    lob_np = lob_nonparametric(ref, 100.0 * (1.0 - alpha))
    test = rng.exponential(1.0, size=5000)
    rate_p = float(np.mean(test > lob_p))
    rate_np = float(np.mean(test > lob_np))
    return rate_p, rate_np, float(lob_p), float(lob_np)


def evaluate_standard_scenarios(weights: RiskWeights | None = None) -> dict:
    w = weights or RiskWeights()
    rows: list[ScenarioRisk] = []

    # G2 folklore n=20 for 90 vs 80
    beta_asym = 1.0 - power_two_proportions(0.90, 0.80, 20)
    beta_fish = 1.0 - exact_power_two_proportions(0.90, 0.80, 20, test="fisher")
    n_star = int(np.ceil(sample_size_two_proportions(0.90, 0.80)))
    rows.append(
        ScenarioRisk(
            "G2_folklore_n20_90vs80",
            "G2",
            type_i=0.05,
            beta=float(beta_fish),
            mismatch=0.0,
            de_penalty=0.0,
            loss=loss(type_i=0.05, beta=float(beta_fish), mismatch=0.0, weights=w),
            notes=f"Fisher miss β; asym β={beta_asym:.3f}; n*≈{n_star}",
        )
    )
    rows.append(
        ScenarioRisk(
            "G2_powered_nstar_90vs80",
            "G2",
            type_i=0.05,
            beta=float(1.0 - power_two_proportions(0.90, 0.80, n_star)),
            mismatch=0.0,
            de_penalty=0.0,
            loss=loss(
                type_i=0.05,
                beta=float(1.0 - power_two_proportions(0.90, 0.80, n_star)),
                mismatch=0.0,
                weights=w,
            ),
            notes=f"n*={n_star}; beta from asymptotic at design n* (exact enumeration infeasible at this n)",
        )
    )

    # parametric mismatch on Exp blanks
    rate_p, rate_np, lob_p, lob_np = _parametric_mismatch_exp()
    mismatch_cost = min(1.0, abs(rate_p - 0.05) / 0.05)
    rows.append(
        ScenarioRisk(
            "G1_parametric_LoB_on_Exp",
            "G1",
            type_i=float(rate_p),
            beta=0.0,
            mismatch=float(mismatch_cost),
            de_penalty=0.0,
            loss=loss(type_i=float(rate_p), beta=0.0, mismatch=float(mismatch_cost), weights=w),
            notes=f"lob_par={lob_p:.3f}, lob_np={lob_np:.3f}, exceed_np={rate_np:.3f}",
        )
    )
    rows.append(
        ScenarioRisk(
            "G1_nonparametric_LoB_on_Exp",
            "G1",
            type_i=float(rate_np),
            beta=0.0,
            mismatch=0.0,
            de_penalty=0.0,
            loss=loss(type_i=float(rate_np), beta=0.0, mismatch=0.0, weights=w),
            notes="S2/S4 gate prefers nonparametric when diagnostics fail",
        )
    )

    # cluster DE
    de = design_effect(0.2, 5)
    rows.append(
        ScenarioRisk(
            "G2_ignored_ICC_DE",
            "G2",
            type_i=0.05,
            beta=float(beta_fish),
            mismatch=0.0,
            de_penalty=float(de - 1.0),
            loss=loss(type_i=0.05, beta=float(beta_fish), mismatch=0.0, de=de, weights=w),
            notes=f"DE={de} if ICC=0.2, m=5 ignored",
        )
    )

    # folklore vs gated comparison
    folklore = next(r for r in rows if r.scenario_id == "G2_folklore_n20_90vs80")
    powered = next(r for r in rows if r.scenario_id == "G2_powered_nstar_90vs80")
    para = next(r for r in rows if r.scenario_id == "G1_parametric_LoB_on_Exp")
    nonpar = next(r for r in rows if r.scenario_id == "G1_nonparametric_LoB_on_Exp")

    payload = {
        "study_id": "DECISION-RISK-v1",
        "loss_definition": (
            "L = w_I*TypeI + w_II*beta + w_M*1{parametric mismatch} + w_C*(DE-1)"
        ),
        "weights": asdict(w),
        "scenarios": [asdict(r) for r in rows],
        "comparisons": {
            "G2_loss_ratio_folklore_over_powered": folklore.loss / powered.loss if powered.loss else None,
            "G1_loss_ratio_parametric_over_nonparametric": para.loss / nonpar.loss if nonpar.loss else None,
        },
        "interpretation": (
            "Under equal weights, folklore n=20 for 90 vs 80 incurs substantially higher "
            "decision risk than powered n*; parametric LoB on Exp blanks incurs higher "
            "risk than the nonparametric path — justifying the S2→S4 assumption gate."
        ),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "decision_risk.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload


if __name__ == "__main__":
    print(json.dumps(evaluate_standard_scenarios(), indent=2, default=str)[:2000])
