"""
Minimax-robust multi-concentration LoD design under slope uncertainty.

For planning slope β_plan and true β ∈ [β_min, β_max], search designs that
minimize worst-case asymptotic SE(log10 LoD).  Extends probit_design_robustness
with formal minimax selection over candidate grids (P13).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.special import logit

from lod_guide.research.probit_design_grid import (
    allocate_n,
    evaluate_design_grid,
    make_concentration_grid,
)
from lod_guide.theory.lod_dose_response import (
    DoseResponseTruth,
    asymptotic_lod_se_log10,
    default_synthetic_truth,
    truth_with_slope,
)

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def worst_case_se_log10_lod(
    plan: DoseResponseTruth,
    concentrations: np.ndarray,
    n_per_level: np.ndarray,
    *,
    slope_ratios: list[float],
) -> dict:
    """Max asymptotic SE(log10 LoD) over multiplicative slope perturbations."""
    rows = []
    for ratio in slope_ratios:
        b_true = plan.slope * ratio
        true = truth_with_slope(plan.intercept, b_true, link=plan.link, target_p=plan.target_p)
        se = asymptotic_lod_se_log10(true, concentrations, n_per_level)
        rows.append(
            {
                "slope_ratio": float(ratio),
                "slope_true": float(b_true),
                "se_log10_lod": se["se_log10_lod"],
            }
        )
    worst = max(rows, key=lambda r: r["se_log10_lod"])
    return {
        "worst": worst,
        "all": rows,
        "worst_case_se": float(worst["se_log10_lod"]),
    }


def minimax_design_search(
    plan: DoseResponseTruth | None = None,
    *,
    slope_ratios: list[float] | None = None,
    total_n: int = 60,
    n_levels: int = 5,
) -> dict:
    """
    Select among heuristic design patterns minimizing worst-case SE over slope ratios.
    """
    plan = plan or default_synthetic_truth()
    if slope_ratios is None:
        slope_ratios = [0.5, 0.75, 1.0, 1.25, 1.5]

    lod = plan.lod()
    candidates = []
    for pattern in ("equal_log", "dense_near_lod"):
        conc = make_concentration_grid(lod, n_levels=n_levels, pattern=pattern)
        for scheme in ("equal", "lod_weighted"):
            n_vec = allocate_n(total_n, n_levels, scheme=scheme, lod=lod, concentrations=conc)
            wc = worst_case_se_log10_lod(plan, conc, n_vec, slope_ratios=slope_ratios)
            candidates.append(
                {
                    "pattern": pattern,
                    "allocation": scheme,
                    "concentrations": conc.tolist(),
                    "n_per_level": n_vec.tolist(),
                    "worst_case_se": wc["worst_case_se"],
                    "worst_slope_ratio": wc["worst"]["slope_ratio"],
                    "se_at_plan": asymptotic_lod_se_log10(plan, conc, n_vec)["se_log10_lod"],
                }
            )

    minimax = min(candidates, key=lambda r: r["worst_case_se"])
    folklore = next(c for c in candidates if c["pattern"] == "equal_log" and c["allocation"] == "equal")
    return {
        "plan_truth": {"slope": plan.slope, "lod": lod},
        "slope_ratios": slope_ratios,
        "minimax_design": minimax,
        "folklore_equal_log_equal": folklore,
        "worst_case_improvement_vs_folklore": (
            folklore["worst_case_se"] / minimax["worst_case_se"]
            if minimax["worst_case_se"] > 0
            else None
        ),
        "candidates": candidates,
    }


def run_minimax_probit_design() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    plan = default_synthetic_truth()
    search = minimax_design_search(plan)
    grid = evaluate_design_grid(plan, total_n_grid=[60], n_levels_grid=[5])

    payload = {
        "study_id": "MINIMAX-PROBIT-DESIGN-v1",
        "minimax_search": search,
        "grid_best_at_plan": grid.get("best"),
        "headline": {
            "minimax_pattern": search["minimax_design"]["pattern"],
            "minimax_allocation": search["minimax_design"]["allocation"],
            "minimax_worst_case_se": search["minimax_design"]["worst_case_se"],
            "folklore_worst_case_se": search["folklore_equal_log_equal"]["worst_case_se"],
            "improvement_ratio": search["worst_case_improvement_vs_folklore"],
        },
        "claim_boundary": (
            "Minimax over a discrete slope-ratio set and heuristic design family; "
            "not a global continuous minimax theorem."
        ),
    }
    path = OUT / "minimax_probit_design.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_minimax_probit_design()["headline"], indent=2))
