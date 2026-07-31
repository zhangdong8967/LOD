"""Asymptotic vs exact small-sample power study for reagent discrimination."""

from __future__ import annotations

import json
from pathlib import Path

from lod_guide.theory.exact_tests import (
    compare_asymptotic_vs_exact,
    exact_power_two_proportions,
    sample_size_exact_search,
    analyze_two_proportions_exact,
)

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def run_exact_power_study(*, include_boschloo_demo: bool = True) -> dict:
    table = compare_asymptotic_vs_exact()
    # exact n* for the easy discrimination case (feasible enumeration)
    n_star_90_50 = sample_size_exact_search(0.90, 0.50, test="fisher", n_max=80)
    # Fisher power at folklore n for hard case (exact n* deferred when asym large)
    fisher_90_80_n20 = exact_power_two_proportions(0.90, 0.80, 20, test="fisher")
    fisher_90_80_n199 = exact_power_two_proportions(0.90, 0.80, 199, test="fisher")

    demo = None
    if include_boschloo_demo:
        # Illustrative table: 18/20 vs 14/20
        demo = analyze_two_proportions_exact(18, 20, 14, 20)

    payload = {
        **table,
        "highlights": {
            "fisher_power_90vs80_n20": fisher_90_80_n20,
            "fisher_power_90vs80_n199": fisher_90_80_n199,
            "exact_n_star_90vs50_fisher": n_star_90_50,
            "boschloo_demo_18of20_vs_14of20": None
            if demo is None
            else {
                "fisher_p": demo.fisher_p_two_sided,
                "boschloo_p": demo.boschloo_p_two_sided,
                "pooled_z_p": demo.pooled_z_p_two_sided,
            },
        },
        "reporting_policy": {
            "design_surface": "asymptotic Fleiss-Chow / pooled-z (continuous models)",
            "primary_small_n_test": "Boschloo unconditional exact (Fisher as conditional reference)",
            "primary_small_n_power": "exact enumeration under independent binomials",
            "do_not_claim": "asymptotic power alone is exact at n=20",
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "exact_vs_asymptotic_power.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["path"] = str(path)
    return payload


if __name__ == "__main__":
    out = run_exact_power_study()
    print(json.dumps(out["highlights"], indent=2))
    print("wrote", out["path"])
