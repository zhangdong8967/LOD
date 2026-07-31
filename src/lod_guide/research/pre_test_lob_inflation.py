"""
Pre-test LoB gate Type I inflation study (P17).

Deposits Monte Carlo exceedance rates for assumption-gated vs always-parametric
LoB under skew-prone blank laws.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from lod_guide.theory.gated_inference import inflation_lower_bound_skew_family, monte_carlo_gated_type_i

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def run_pre_test_lob_inflation() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    skew_scan = inflation_lower_bound_skew_family(n_mc=800, seed=1)

    def draw_exp(n: int, rng: np.random.Generator) -> np.ndarray:
        return rng.exponential(1.0, size=n)

    exponential = monte_carlo_gated_type_i(
        law="exponential",
        n_blank=60,
        alpha=0.05,
        n_mc=800,
        seed=2,
        draw_fn=draw_exp,
    )

    payload = {
        "study_id": "PRE-TEST-LOB-INFLATION-v1",
        "skew_family_scan": skew_scan,
        "exponential_gate": exponential,
        "headline": {
            "best_law": skew_scan["law"],
            "gated_inflation": skew_scan["inflation"],
            "gated_exceedance": skew_scan["mean_exceedance"],
            "parametric_fraction": skew_scan["parametric_fraction"],
            "always_parametric_exceedance": skew_scan["always_parametric_exceedance"],
            "exp_gated_exceedance": exponential["mean_exceedance"],
            "exp_nonparametric_fraction": exponential["path_counts"]["nonparametric"] / 800,
        },
        "claim_boundary": (
            "Monte Carlo inflation under fixed S2 thresholds; not a uniform-in-F theorem."
        ),
    }
    path = OUT / "pre_test_lob_inflation.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_pre_test_lob_inflation()["headline"], indent=2))
