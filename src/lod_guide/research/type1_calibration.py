"""
Finite-sample Type I error calibration for two-proportion tests.

Under H0: p_A = p_B = p (nuisance), simulate empirical rejection rates for:
  - pooled-z
  - Fisher exact
  - Boschloo (optional; slower — used for small n grid)

Supports the reporting policy: asymptotic design OK; confirmatory small-n needs exact.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import binom

from lod_guide.theory.exact_tests import boschloo_pvalue, fisher_pvalue, pooled_z_pvalue

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def empirical_type1(
    *,
    n: int,
    p_null: float,
    alpha: float = 0.05,
    n_sims: int = 5000,
    seed: int = 0,
    include_boschloo: bool = False,
) -> dict:
    rng = np.random.default_rng(seed)
    xa = rng.binomial(n, p_null, size=n_sims)
    xb = rng.binomial(n, p_null, size=n_sims)
    rej_z = rej_f = rej_b = 0
    for a, b in zip(xa, xb):
        if pooled_z_pvalue(int(a), n, int(b), n) < alpha:
            rej_z += 1
        if fisher_pvalue(int(a), n, int(b), n) < alpha:
            rej_f += 1
        if include_boschloo:
            if boschloo_pvalue(int(a), n, int(b), n, n_grid=51) < alpha:
                rej_b += 1
    out = {
        "n": n,
        "p_null": p_null,
        "alpha": alpha,
        "n_sims": n_sims,
        "type1_pooled_z": rej_z / n_sims,
        "type1_fisher": rej_f / n_sims,
    }
    if include_boschloo:
        out["type1_boschloo"] = rej_b / n_sims
    return out


def run_type1_calibration_study(
    *,
    n_list: tuple[int, ...] = (10, 20, 30, 50),
    p_list: tuple[float, ...] = (0.5, 0.8, 0.9),
    n_sims: int = 4000,
    seed: int = 42,
    include_boschloo_n: int = -1,
    boschloo_demo_sims: int = 200,
) -> dict:
    """
    Grid Type I study for pooled-z and Fisher.
    Optional Boschloo demo at a single (n,p) — expensive; off by default (include_boschloo_n=-1).
    """
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    k = 0
    for n in n_list:
        for p in p_list:
            row = empirical_type1(
                n=n,
                p_null=p,
                n_sims=n_sims,
                seed=seed + k,
                include_boschloo=False,
            )
            rows.append(row)
            k += 1
    if include_boschloo_n > 0:
        row_b = empirical_type1(
            n=include_boschloo_n,
            p_null=0.8,
            n_sims=boschloo_demo_sims,
            seed=seed + 999,
            include_boschloo=True,
        )
        row_b["note"] = "boschloo_demo_only"
        rows.append(row_b)

    # max absolute deviation from nominal alpha for fisher vs z at n=20
    n20 = [r for r in rows if r["n"] == 20]
    summary = {
        "nominal_alpha": 0.05,
        "max_abs_err_fisher_n20": max(abs(r["type1_fisher"] - 0.05) for r in n20) if n20 else None,
        "max_abs_err_pooled_z_n20": max(abs(r["type1_pooled_z"] - 0.05) for r in n20) if n20 else None,
        "interpretation": (
            "Fisher is typically conservative (Type I < α); pooled-z may be closer to α "
            "but can inflate at boundary p. Prefer Boschloo/Fisher for confirmatory small-n."
        ),
    }
    payload = {
        "study_id": "TYPE1-CALIBRATION-v1",
        "seed_base": seed,
        "rows": rows,
        "summary": summary,
    }
    path = OUT / "type1_calibration.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["path"] = str(path)
    return payload


if __name__ == "__main__":
    out = run_type1_calibration_study(n_sims=2000)
    print(json.dumps(out["summary"], indent=2))
