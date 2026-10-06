"""
Decision-weight axioms for the LoD risk functional L.

L = w_I·TypeI + w_II·β + w_M·mismatch + w_C·(DE−1)

We do not claim a unique utility. We axiomatize admissible weight cones,
map qualitative lab preferences → weight vectors, and report the Pareto
frontier of scenario losses under a weight grid (sensitivity of rankings).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from lod_guide.research.decision_risk import RiskWeights, evaluate_standard_scenarios, loss

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


AXIOMS = [
    {
        "id": "A1_nonnegativity",
        "statement": "All weights w_I, w_II, w_M, w_C ≥ 0 (losses are costs).",
    },
    {
        "id": "A2_scale_invariance",
        "statement": "L and argmin_path are invariant to positive rescaling of the weight vector.",
    },
    {
        "id": "A3_preference_representation",
        "statement": (
            "Qualitative rankings (e.g. 'miss-β worse than mild Type I inflation') "
            "map to inequalities among weights, not to a unique point."
        ),
    },
    {
        "id": "A4_transparency",
        "statement": (
            "Equal weights (1,1,1,0.5) are a published default convention for "
            "comparability; confirmatory reports must declare the weight vector used."
        ),
    },
]


@dataclass(frozen=True)
class PreferenceProfile:
    name: str
    description: str
    weights: RiskWeights


def preference_library() -> list[PreferenceProfile]:
    return [
        PreferenceProfile(
            "equal_default",
            "Equal TypeI / β / mismatch; milder cluster penalty (package default).",
            RiskWeights(1.0, 1.0, 1.0, 0.5),
        ),
        PreferenceProfile(
            "patient_safety_miss_beta",
            "Prioritize avoiding false 'no difference' / missed LoD failures (w_II ≫ w_I).",
            RiskWeights(0.5, 2.0, 1.0, 0.5),
        ),
        PreferenceProfile(
            "regulator_type_i",
            "Prioritize controlling false-positive LoB / blank claims (w_I ≫ w_II).",
            RiskWeights(2.0, 0.5, 1.0, 0.5),
        ),
        PreferenceProfile(
            "model_mismatch_averse",
            "Heavily penalize parametric LoB on skewed blanks (w_M large).",
            RiskWeights(1.0, 1.0, 3.0, 0.5),
        ),
        PreferenceProfile(
            "multilab_cluster_averse",
            "Heavily penalize ignored ICC / design effect.",
            RiskWeights(1.0, 1.0, 1.0, 2.0),
        ),
    ]


def _scenario_components() -> list[dict]:
    """Fixed TypeI/β/mismatch/DE components from the standard scenario catalogue."""
    base = evaluate_standard_scenarios(RiskWeights())
    return [
        {
            "scenario_id": s["scenario_id"],
            "type_i": s["type_i"],
            "beta": s["beta"],
            "mismatch": s["mismatch"],
            "de": 1.0 + float(s["de_penalty"]),
        }
        for s in base["scenarios"]
    ]


def weight_grid(n_per_axis: int = 3) -> list[RiskWeights]:
    vals = np.linspace(0.5, 2.0, n_per_axis)
    out: list[RiskWeights] = []
    for wi in vals:
        for wii in vals:
            for wm in vals:
                for wc in (0.25, 0.5, 1.0):
                    out.append(RiskWeights(float(wi), float(wii), float(wm), float(wc)))
    return out


def run_decision_weight_axioms(*, n_per_axis: int = 3) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    comps = _scenario_components()
    profiles = preference_library()

    profile_rows = []
    for pref in profiles:
        losses = {
            c["scenario_id"]: loss(
                type_i=c["type_i"],
                beta=c["beta"],
                mismatch=c["mismatch"],
                de=c["de"],
                weights=pref.weights,
            )
            for c in comps
        }
        folklore = losses["E2_folklore_n20_90_vs_80"]
        powered = losses["E2_powered_nstar_90_vs_80"]
        para = losses["E1_parametric_LoB_on_Exp"]
        nonpar = losses["E1_nonparametric_LoB_on_Exp"]
        profile_rows.append(
            {
                "name": pref.name,
                "description": pref.description,
                "weights": asdict(pref.weights),
                "losses": losses,
                "E2_ratio_folklore_over_powered": folklore / powered if powered else None,
                "E1_ratio_para_over_nonpar": para / nonpar if nonpar else None,
                "prefers_powered_over_folklore": folklore > powered,
                "prefers_nonpar_over_para_on_Exp": para > nonpar,
            }
        )

    # Pareto: minimize (L_folklore_gap proxy) — record ranking stability
    grid = weight_grid(n_per_axis=n_per_axis)
    ranking_votes = 0
    for w in grid:
        lf = loss(
            type_i=next(c["type_i"] for c in comps if c["scenario_id"] == "E2_folklore_n20_90_vs_80"),
            beta=next(c["beta"] for c in comps if c["scenario_id"] == "E2_folklore_n20_90_vs_80"),
            mismatch=0.0,
            de=1.0,
            weights=w,
        )
        lp = loss(
            type_i=next(c["type_i"] for c in comps if c["scenario_id"] == "E2_powered_nstar_90_vs_80"),
            beta=next(c["beta"] for c in comps if c["scenario_id"] == "E2_powered_nstar_90_vs_80"),
            mismatch=0.0,
            de=1.0,
            weights=w,
        )
        if lf > lp:
            ranking_votes += 1

    # Scale invariance check (A2)
    w0 = RiskWeights(1, 1, 1, 0.5)
    w1 = RiskWeights(2, 2, 2, 1.0)
    c0 = comps[0]
    l0 = loss(type_i=c0["type_i"], beta=c0["beta"], mismatch=c0["mismatch"], de=c0["de"], weights=w0)
    l1 = loss(type_i=c0["type_i"], beta=c0["beta"], mismatch=c0["mismatch"], de=c0["de"], weights=w1)
    scale_ok = abs(l1 - 2.0 * l0) < 1e-9

    payload = {
        "study_id": "DECISION-WEIGHT-AXIOMS-v1",
        "axioms": AXIOMS,
        "preference_profiles": profile_rows,
        "weight_grid": {
            "n_weights": len(grid),
            "frac_prefer_powered_over_folklore_G2": ranking_votes / len(grid),
            "interpretation": (
                "If fraction≈1, the folklore≻powered ranking is robust across the weight cone."
            ),
        },
        "axiom_checks": {
            "A2_scale_invariance_numeric": scale_ok,
            "A1_all_library_weights_nonneg": all(
                min(asdict(p.weights).values()) >= 0 for p in profiles
            ),
        },
        "headline": {
            "n_profiles": len(profile_rows),
            "all_profiles_prefer_powered": all(r["prefers_powered_over_folklore"] for r in profile_rows),
            "all_profiles_prefer_nonpar_on_Exp": all(
                r["prefers_nonpar_over_para_on_Exp"] for r in profile_rows
            ),
            "grid_frac_prefer_powered": ranking_votes / len(grid),
            "scale_invariance_ok": scale_ok,
        },
        "claim_boundary": (
            "Weights are preference parameters under axioms A1–A4, not estimated utilities. "
            "Equal weights remain the default reporting convention."
        ),
    }
    path = OUT / "decision_weight_axioms.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_decision_weight_axioms()["headline"], indent=2))
