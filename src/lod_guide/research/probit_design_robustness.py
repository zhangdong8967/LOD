"""
Probit/logistic design robustness under slope misspecification.

Plans with a working slope β_plan, evaluates asymptotic SE(log10 LoD) when the
true slope is β_true ≠ β_plan (same LoD location). Reports inflation factors
and cross-links minimax design selection.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.special import logit

from lod_guide.research.minimax_probit_design import minimax_design_search
from lod_guide.research.probit_design_grid import (
    allocate_n,
    asymptotic_lod_se_log10,
    default_synthetic_truth,
    make_concentration_grid,
)
from lod_guide.theory.lod_dose_response import truth_with_slope

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def truth_with_lod_slope(slope: float, lod: float = 1.0, target_p: float = 0.95):
    alpha = float(logit(target_p) - slope * np.log10(lod))
    return truth_with_slope(alpha, slope, link="logistic", target_p=target_p)


def run_probit_design_robustness() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    plan = default_synthetic_truth()
    lod = plan.lod()
    conc = make_concentration_grid(lod, n_levels=5, pattern="equal_log")
    n_vec = allocate_n(60, 5, scheme="equal", lod=lod, concentrations=conc)
    se_plan = asymptotic_lod_se_log10(plan, conc, n_vec)

    slopes = [0.5 * plan.slope, 0.75 * plan.slope, plan.slope, 1.25 * plan.slope, 1.5 * plan.slope]
    rows = []
    for b in slopes:
        true = truth_with_lod_slope(float(b), lod=lod)
        se = asymptotic_lod_se_log10(true, conc, n_vec)
        rows.append(
            {
                "slope_true": float(b),
                "slope_ratio_true_over_plan": float(b / plan.slope),
                "se_log10_lod": se["se_log10_lod"],
                "se_inflation_vs_plan": (
                    se["se_log10_lod"] / se_plan["se_log10_lod"] if se_plan["se_log10_lod"] else None
                ),
                "cv_lod_approx": se["cv_lod_approx"],
            }
        )

    conc2 = make_concentration_grid(lod, n_levels=5, pattern="dense_near_lod")
    n2 = allocate_n(60, 5, scheme="lod_weighted", lod=lod, concentrations=conc2)
    miss = truth_with_lod_slope(0.5 * plan.slope, lod=lod)
    se_eq = asymptotic_lod_se_log10(miss, conc, n_vec)
    se_dense = asymptotic_lod_se_log10(miss, conc2, n2)

    minimax = minimax_design_search(plan, total_n=60, n_levels=5)
    mm = minimax["minimax_design"]
    mm_conc = np.asarray(mm["concentrations"])
    mm_n = np.asarray(mm["n_per_level"])
    se_mm_plan = asymptotic_lod_se_log10(plan, mm_conc, mm_n)
    se_mm_miss = asymptotic_lod_se_log10(miss, mm_conc, mm_n)

    payload = {
        "study_id": "PROBIT-DESIGN-ROBUSTNESS-v1",
        "plan_truth": {"slope": plan.slope, "lod": lod, "se_at_plan": se_plan},
        "misspecification_grid": rows,
        "under_half_slope": {
            "se_equal_log": se_eq["se_log10_lod"],
            "se_dense_weighted": se_dense["se_log10_lod"],
            "dense_helps": se_dense["se_log10_lod"] < se_eq["se_log10_lod"],
        },
        "minimax_design": {
            "pattern": mm["pattern"],
            "allocation": mm["allocation"],
            "worst_case_se": mm["worst_case_se"],
            "se_at_plan": se_mm_plan["se_log10_lod"],
            "se_under_half_slope": se_mm_miss["se_log10_lod"],
            "improvement_vs_folklore_worst_case": minimax["worst_case_improvement_vs_folklore"],
        },
        "headline": {
            "max_se_inflation": max(r["se_inflation_vs_plan"] for r in rows if r["se_inflation_vs_plan"]),
            "min_se_inflation": min(r["se_inflation_vs_plan"] for r in rows if r["se_inflation_vs_plan"]),
            "dense_helps_under_half_slope": se_dense["se_log10_lod"] < se_eq["se_log10_lod"],
            "minimax_worst_case_se": mm["worst_case_se"],
        },
        "claim_boundary": (
            "Asymptotic SE under wrong slope is a robustness diagnostic for planning, "
            "not a finite-sample guarantee. Minimax selection is over discrete heuristics."
        ),
    }
    path = OUT / "probit_design_robustness.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_probit_design_robustness()["headline"], indent=2))
