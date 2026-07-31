"""
S7 — Sensitivity / what-if layer (lab education).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from lod_guide.s0_goal import Goal
from lod_guide.s5_sample_size import (
    power_two_proportions,
    recommend_sample_size,
    sample_size_two_proportions,
)


@dataclass
class SensitivityGrid:
    parameter: str
    values: list[float]
    recommended_n: list[int]
    power_at_n20: list[float] | None = None


def sensitivity_compare_reagents(
    p_a: float = 0.90,
    deltas: list[float] | None = None,
    alpha: float = 0.05,
    power: float = 0.80,
    icc_grid: list[float] | None = None,
) -> dict:
    """Vary Δ and ICC; show how recommended n and folklore n=20 power move."""
    if deltas is None:
        deltas = [0.05, 0.10, 0.15, 0.20]
    if icc_grid is None:
        icc_grid = [0.0, 0.1, 0.2]

    by_delta = []
    for d in deltas:
        p_b = p_a - d
        if not (0 < p_b < 1):
            continue
        n = int(np.ceil(sample_size_two_proportions(p_a, p_b, alpha, power)))
        by_delta.append(
            {
                "delta": d,
                "p_a": p_a,
                "p_b": p_b,
                "n_80": n,
                "power_n20": power_two_proportions(p_a, p_b, 20, alpha),
            }
        )

    by_icc = []
    for icc in icc_grid:
        res = recommend_sample_size(
            Goal.G2_COMPARE_REAGENTS,
            p_a=p_a,
            p_b=p_a - 0.10,
            alpha=alpha,
            power=power,
            icc=icc,
            cluster_size=5,
        )
        by_icc.append(
            {
                "icc": icc,
                "design_effect": res.design_effect,
                "n_per_arm": res.n_per_arm,
            }
        )

    return {"by_delta": by_delta, "by_icc": by_icc, "p_a": p_a}
