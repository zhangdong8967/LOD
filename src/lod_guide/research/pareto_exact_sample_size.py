"""
Pareto / exact sample-size analysis for E2 LoD discrimination (P18).

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


@lru_cache(maxsize=4096)
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
            other[type_i_key] < point[type_i_key] - 1e-12
            or other[power_key] > point[power_key] + 1e-12
        )
    )


def cell_has_pareto_dominator(
    p_a: float,
    p_b: float,
    *,
    folklore_n: int = 20,
    alpha: float = 0.05,
    max_extra_n: int = 15,
) -> bool:
    """True if some n' in (folklore_n, folklore_n+max_extra_n] Pareto-dominates folklore_n."""
    p_null = (p_a + p_b) / 2
    folk = _oc_point(folklore_n, p_a=p_a, p_b=p_b, p_null=p_null, alpha=alpha)
    for n in range(folklore_n + 1, folklore_n + max_extra_n + 1):
        row = _oc_point(n, p_a=p_a, p_b=p_b, p_null=p_null, alpha=alpha)
        if is_pareto_dominated(folk, row):
            return True
    return False


def lattice_pareto_dominance_summary(
    *,
    folklore_n: int = 20,
    alpha: float = 0.05,
    max_extra_n: int = 15,
    force: bool = False,
) -> dict:
    """Scan the integer 50–99% E2 lattice at folklore n for Pareto dominators."""
    cache_path = OUT / "pareto_lattice_scan.json"
    if cache_path.is_file() and not force:
        return json.loads(cache_path.read_text(encoding="utf-8"))

    dominated = 0
    n_cells = 0
    for pa_pct in range(50, 100):
        p_a = pa_pct / 100.0
        for pb_pct in range(50, pa_pct):
            p_b = pb_pct / 100.0
            n_cells += 1
            if cell_has_pareto_dominator(
                p_a,
                p_b,
                folklore_n=folklore_n,
                alpha=alpha,
                max_extra_n=max_extra_n,
            ):
                dominated += 1
    result = {
        "n_cells": n_cells,
        "n_pareto_dominated": dominated,
        "fraction_pareto_dominated": round(dominated / n_cells, 4) if n_cells else 0.0,
        "folklore_n": folklore_n,
        "alpha": alpha,
        "max_extra_n_scan": max_extra_n,
        "scan_note": (
            "For each lattice cell, search n' in {folklore_n+1, …, folklore_n+max_extra_n} "
            "for a strict Pareto dominator on exact Fisher (Type I, power). "
            "Headline pair (0.90, 0.80) has dominator at n=25 within this window."
        ),
    }
    cache_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    _write_undominated_characterization(
        folklore_n=folklore_n,
        alpha=alpha,
        max_extra_n=max_extra_n,
        force=force,
    )
    return result


def _write_undominated_characterization(
    *,
    folklore_n: int,
    alpha: float,
    max_extra_n: int,
    force: bool,
) -> dict:
    """Summarize lattice cells with no local Pareto dominator in the scan window."""
    out_path = OUT / "pareto_lattice_undominated.json"
    if out_path.is_file() and not force:
        return json.loads(out_path.read_text(encoding="utf-8"))

    undominated: list[dict] = []
    for pa_pct in range(50, 100):
        p_a = pa_pct / 100.0
        for pb_pct in range(50, pa_pct):
            p_b = pb_pct / 100.0
            if cell_has_pareto_dominator(
                p_a,
                p_b,
                folklore_n=folklore_n,
                alpha=alpha,
                max_extra_n=max_extra_n,
            ):
                continue
            folk = _oc_point(folklore_n, p_a=p_a, p_b=p_b, p_null=(p_a + p_b) / 2, alpha=alpha)
            undominated.append(
                {
                    "p_a_pct": pa_pct,
                    "p_b_pct": pb_pct,
                    "delta_pct": pa_pct - pb_pct,
                    "power_folk": folk["power_fisher"],
                    "beta_folk": folk["beta"],
                }
            )

    deltas = [r["delta_pct"] for r in undominated]
    powers = [r["power_folk"] for r in undominated]
    summary = {
        "n_undominated": len(undominated),
        "n_cells": 1225,
        "scan_window": f"n' in {{{folklore_n + 1},...,{folklore_n + max_extra_n}}}",
        "undominated_delta_pct": {
            "min": min(deltas) if deltas else None,
            "max": max(deltas) if deltas else None,
            "median": float(np.median(deltas)) if deltas else None,
        },
        "undominated_power_at_n20": {
            "min": min(powers) if powers else None,
            "max": max(powers) if powers else None,
            "median": float(np.median(powers)) if powers else None,
        },
        "interpretation": (
            "Within the local scan n'<=folklore_n+max_extra_n, no strict Pareto dominator exists. "
            "These cells are not powered exemptions: median exact Fisher power at n=20 remains low "
            "(see undominated_power_at_n20). Powered n* for discrimination often exceeds the scan window."
        ),
        "examples_largest_delta": sorted(undominated, key=lambda r: -r["delta_pct"])[:6],
        "examples_smallest_delta": sorted(undominated, key=lambda r: r["delta_pct"])[:5],
    }
    out_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


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
    lattice = lattice_pareto_dominance_summary()
    payload = {
        "study_id": "PARETO-EXACT-SAMPLE-SIZE-v1",
        "certificate": cert,
        "lattice_scan": lattice,
        "headline": {
            "folklore_n": cert["folklore_n"],
            "powered_n_star": cert["powered_n_star"],
            "folklore_power": cert["folklore"]["power_fisher"],
            "powered_power": cert["powered"]["power_fisher"],
            "pareto_dominated": cert["folklore_pareto_dominated"],
            "loss_ratio": cert["loss_ratio_folklore_over_powered"],
            "lattice_fraction_pareto_dominated": lattice["fraction_pareto_dominated"],
            "lattice_n_dominated": lattice["n_pareto_dominated"],
            "lattice_n_cells": lattice["n_cells"],
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
