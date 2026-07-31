"""
G1 one-proportion coverage: Wilson vs Clopper–Pearson for LoD hit-rate claims.

Complements the G2 exact Fisher/Boschloo layer so referees cannot dismiss the
package as asymptotic-only for verification (G1).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import binom

from lod_guide.theory.exact import clopper_pearson_interval, wilson_interval

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def coverage_study(
    *,
    p_true: float,
    n: int,
    alpha: float = 0.05,
    n_sims: int = 5000,
    seed: int = 42,
) -> dict:
    rng = np.random.default_rng(seed)
    hits_w = hits_cp = 0
    widths_w: list[float] = []
    widths_cp: list[float] = []
    for _ in range(n_sims):
        x = int(rng.binomial(n, p_true))
        wl, wh = wilson_interval(x, n, alpha=alpha)
        cl, ch = clopper_pearson_interval(x, n, alpha=alpha)
        if wl <= p_true <= wh:
            hits_w += 1
        if cl <= p_true <= ch:
            hits_cp += 1
        widths_w.append(wh - wl)
        widths_cp.append(ch - cl)
    return {
        "p_true": p_true,
        "n": n,
        "alpha": alpha,
        "n_sims": n_sims,
        "coverage_wilson": hits_w / n_sims,
        "coverage_clopper_pearson": hits_cp / n_sims,
        "mean_width_wilson": float(np.mean(widths_w)),
        "mean_width_clopper_pearson": float(np.mean(widths_cp)),
        "nominal": 1.0 - alpha,
    }


def claim_pass_probability(
    *,
    p_true: float,
    n: int,
    claim: float = 0.95,
    alpha: float = 0.05,
    method: str = "wilson",
) -> float:
    """Exact P(lower bound >= claim) under Binomial(n, p_true)."""
    ok = 0.0
    for x in range(0, n + 1):
        pmf = float(binom.pmf(x, n, p_true))
        if method == "wilson":
            low, _ = wilson_interval(x, n, alpha=alpha)
        else:
            low, _ = clopper_pearson_interval(x, n, alpha=alpha)
        if low >= claim:
            ok += pmf
    return ok


def run_one_proportion_coverage_study() -> dict:
    scenarios = []
    for p, n in [(0.95, 20), (0.95, 60), (0.80, 20), (0.90, 40), (0.99, 20)]:
        scenarios.append(coverage_study(p_true=p, n=n, n_sims=4000, seed=hash((p, n)) % 10_000))
    claim_rows = []
    for p, n in [(0.95, 20), (0.90, 20), (0.80, 20), (0.95, 60)]:
        claim_rows.append(
            {
                "p_true": p,
                "n": n,
                "claim": 0.95,
                "P_pass_wilson_lower_ge_claim": claim_pass_probability(p_true=p, n=n, method="wilson"),
                "P_pass_CP_lower_ge_claim": claim_pass_probability(p_true=p, n=n, method="cp"),
            }
        )
    payload = {
        "study_id": "G1-ONE-PROPORTION-COVERAGE-v1",
        "coverage": scenarios,
        "claim_pass": claim_rows,
        "policy": {
            "primary_interval": "Clopper–Pearson for confirmatory G1 reporting",
            "design_approximation": "Wilson acceptable for planning / continuous surfaces",
            "note": "At folklore n=20 and p=0.95, claim-pass probability remains modest.",
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "one_proportion_coverage.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    # also write paper table
    paper = Path(__file__).resolve().parents[3] / "paper_artifacts" / "tables"
    paper.mkdir(parents=True, exist_ok=True)
    import csv

    csv_path = paper / "Table08_g1_one_proportion_coverage.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "p_true",
                "n",
                "coverage_wilson",
                "coverage_clopper_pearson",
                "mean_width_wilson",
                "mean_width_clopper_pearson",
            ],
        )
        w.writeheader()
        for row in scenarios:
            w.writerow({k: row[k] for k in w.fieldnames})
    payload["path"] = str(path)
    payload["table"] = str(csv_path)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_one_proportion_coverage_study(), indent=2)[:1800])
