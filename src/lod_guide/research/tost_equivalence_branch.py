"""
TOST / formal equivalence extension for E2 (Supplement §S2d).

Default main-text E2 engine is two-sided discrimination (H0: theta_2 = 0).
When the protocol states equivalence within margin delta, TOST is required.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from lod_guide.s5_sample_size import sample_size_two_proportions

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def asymptotic_equivalence_n_per_arm(
    p_a: float,
    p_b: float,
    delta: float,
    *,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """
    Asymptotic per-arm n for TOST-style equivalence |p_A - p_B| <= delta.

    Planning formula (Chow, Shao, Wang 2008, two proportions):
        n = (z_{1-alpha} + z_{power})^2 * (p_A(1-p_A) + p_B(1-p_B)) / (delta - |p_A-p_B|)^2
    when |p_A - p_B| < delta. Requires prespecified margin delta > |p_A - p_B| at planning.
    """
    from scipy.stats import norm

    if delta <= 0:
        raise ValueError("equivalence margin delta must be positive")
    gap = delta - abs(p_a - p_b)
    if gap <= 0:
        raise ValueError(
            "planning point must satisfy |p_A - p_B| < delta for equivalence sample size"
        )
    z_alpha = norm.ppf(1 - alpha)
    z_beta = norm.ppf(power)
    num = (z_alpha + z_beta) ** 2 * (p_a * (1 - p_a) + p_b * (1 - p_b))
    return int(math.ceil(num / (gap**2)))


def run_tost_equivalence_branch() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    p_disc_a, p_disc_b = 0.90, 0.80
    n_disc = int(math.ceil(sample_size_two_proportions(p_disc_a, p_disc_b, 0.05, 0.80)))

    # Equivalence planning inside margin: small true gap, delta = 5 pp
    p_eq_a, p_eq_b, delta = 0.92, 0.88, 0.05
    n_tost = asymptotic_equivalence_n_per_arm(p_eq_a, p_eq_b, delta)

    rows = [
        {
            "scenario": "discrimination_90_80",
            "p_a": p_disc_a,
            "p_b": p_disc_b,
            "margin_delta": None,
            "n_80pct": n_disc,
            "engine": "two_sided_discrimination (default E2)",
        },
        {
            "scenario": "equivalence_92_88_delta5pp",
            "p_a": p_eq_a,
            "p_b": p_eq_b,
            "margin_delta": delta,
            "n_80pct": n_tost,
            "engine": "TOST |theta_2|<=delta (extension)",
        },
        {
            "scenario": "incompatible_90_80_delta5pp",
            "p_a": p_disc_a,
            "p_b": p_disc_b,
            "margin_delta": 0.05,
            "n_80pct": None,
            "engine": "invalid planning: |p_A-p_B|=0.10 > delta=0.05",
        },
    ]

    payload = {
        "study_id": "TOST-EQUIVALENCE-BRANCH-v1",
        "scope": "Extension branch only; not the default E1–E3 verification engine",
        "rows": rows,
        "headline": {
            "discrimination_pair": {"p_a": p_disc_a, "p_b": p_disc_b, "n_80pct": n_disc},
            "equivalence_pair": {
                "p_a": p_eq_a,
                "p_b": p_eq_b,
                "delta": delta,
                "n_tost_80pct": n_tost,
            },
            "incompatible_example": {
                "p_a": p_disc_a,
                "p_b": p_disc_b,
                "delta": 0.05,
                "note": "|p_A-p_B| exceeds delta — equivalence claim incompatible with planning point",
            },
        },
        "interpretation": (
            "Protocols that say 'equivalent at LoD' require a prespecified margin and TOST "
            "(or noninferiority)—not the default two-sided discrimination engine. "
            "At 90/80, |theta_2|=0.10 exceeds a 5 pp margin, so equivalence wording is "
            "incompatible with that truth unless the margin is widened or the claim rewritten."
        ),
    }
    path = OUT / "tost_equivalence_branch.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload
