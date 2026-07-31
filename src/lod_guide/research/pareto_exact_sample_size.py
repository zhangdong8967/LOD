"""
Pareto / exact sample-size analysis for G2 LoD discrimination (P18).

Shows folklore n=20 is dominated in the Type I – power plane by powered n*
under exact Fisher enumeration.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np

from lod_guide.research.decision_risk import RiskWeights, loss
from lod_guide.s5_sample_size import sample_size_two_proportions
from lod_guide.theory.exact_tests import exact_power_two_proportions, fisher_pvalue

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


@lru_cache(maxsize=256)
def _cached_exact_power(p_a: float, p_b: float, n: int, alpha: float) -> float:
    return float(exact_power_two_proportions(p_a, p_b, n, test="fisher", alpha=alpha))


@lru_cache(maxsize=256)
def _fisher_null_rejection_rate(p_null: float, n: int, alpha: float = 0.05) -> float:
    """Exact null rejection rate of two-sided Fisher at H0: p_A = p_B = p_null."""
    rate = 0.0
    q = 1.0 - p_null
    for a in range(n + 1):
        pa = p_null**a * q ** (n - a) * math.comb(n, a)
        for b in range(n + 1):
            if fisher_pvalue(a, n, b, n) <= alpha:
                rate += pa * (p_null**b * q ** (n - b) * math.comb(n, b))
    return float(rate)


def _oc_point(
    n: int,
    *,
    p_a: float,
    p_b: float,
    p_null: float,
    alpha: float,
) -> dict:
    power = _cached_exact_power(p_a, p_b, n, alpha)
    type_i = _fisher_null_rejection_rate(p_null, n, alpha)
    return {"n": n, "type_i_fisher": type_i, "power_fisher": power, "beta": 1 - power}


def is_pareto_dominated(
    point: dict,
    other: dict,
    *,
    type_i_key: str = "type_i_fisher",
    power_key: str = "power_fisher",
) -> bool:
    """True if `point` is dominated by `other` (lower Type I, higher power)."""
    return (
        other[type_i_key] <= point[type_i_key] + 1e-12
        and other[power_key] >= point[power_key] - 1e-12
        and (
            other[type_i_key] < point[type_i_key] - 1e-12 or other[power_key] > point[power_key] + 1e-12
        )
    )


def folklore_pareto_certificate(
    p_a: float = 0.90,
    p_b: float = 0.80,
    folklore_n: int = 20,
    *,
    alpha: float = 0.05,
    power_target: float = 0.80,
    p_null: float | None = None,
) -> dict:
    """P18: powered n* Pareto-dominates folklore_n on exact Fisher metrics."""
    if p_null is None:
        p_null = (p_a + p_b) / 2

    folk = _oc_point(folklore_n, p_a=p_a, p_b=p_b, p_null=p_null, alpha=alpha)
    n_star = int(np.ceil(sample_size_two_proportions(p_a, p_b, alpha, power_target)))
    powered = _oc_point(n_star, p_a=p_a, p_b=p_b, p_null=p_null, alpha=alpha)

    dominators: list[dict] = []
    if is_pareto_dominated(folk, powered):
        dominators.append(powered)
    else:
        # Cheap scan on small n only (Type I enumeration is O(n^2))
        for n in range(folklore_n + 1, min(folklore_n + 30, n_star)):
            row = _oc_point(n, p_a=p_a, p_b=p_b, p_null=p_null, alpha=alpha)
            if is_pareto_dominated(folk, row):
                dominators.append(row)
                break

    best_dominator = max(dominators, key=lambda r: r["power_fisher"]) if dominators else powered
    dominated = len(dominators) > 0

    w = RiskWeights()
    l_folk = loss(type_i=folk["type_i_fisher"], beta=folk["beta"], mismatch=0.0, de=1.0, weights=w)
    l_pow = loss(type_i=powered["type_i_fisher"], beta=powered["beta"], mismatch=0.0, de=1.0, weights=w)
    l_best = loss(type_i=best_dominator["type_i_fisher"], beta=best_dominator["beta"], mismatch=0.0, de=1.0, weights=w)

    return {
        "folklore_n": folklore_n,
        "folklore": folk,
        "powered_n_star": n_star,
        "powered": powered,
        "best_pareto_dominator": best_dominator,
        "n_dominators": len(dominators),
        "folklore_pareto_dominated": dominated,
        "loss_folklore": l_folk,
        "loss_powered": l_pow,
        "loss_best_dominator": l_best,
        "loss_ratio_folklore_over_powered": l_folk / l_pow if l_pow > 0 else None,
    }


def run_pareto_exact_sample_size() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    cert = folklore_pareto_certificate()
    payload = {
        "study_id": "PARETO-EXACT-SAMPLE-SIZE-v1",
        "certificate": cert,
        "headline": {
            "folklore_n": cert["folklore_n"],
            "powered_n_star": cert["powered_n_star"],
            "folklore_power": cert["folklore"]["power_fisher"],
            "powered_power": cert["powered"]["power_fisher"],
            "pareto_dominated": cert["folklore_pareto_dominated"],
            "loss_ratio": cert["loss_ratio_folklore_over_powered"],
        },
        "claim_boundary": (
            "Pareto dominance in (exact Fisher Type I at pooled null, exact Fisher power) "
            "plane; loss uses equal RiskWeights."
        ),
    }
    path = OUT / "pareto_exact_sample_size.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_pareto_exact_sample_size()["headline"], indent=2))
