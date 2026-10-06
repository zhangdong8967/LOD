"""End-to-end demos for E1–E3 guidance runs."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lod_guide import run_guidance
from lod_guide.s0_goal import Goal


def demo_g2_compare_reagents() -> None:
    print("=" * 60)
    print("E2: Compare reagents p=0.90 vs 0.80")
    print("=" * 60)
    res = run_guidance(
        goal=Goal.E2_COMPARE_REAGENTS,
        result_type="binary",
        use_case="kit_a_vs_kit_b_near_lod",
        p_a=0.90,
        p_b=0.80,
        power=0.80,
    )
    print(res.report.to_markdown())


def demo_continuous_skewed() -> None:
    print("=" * 60)
    print("Continuous near-LoD blanks (right-skewed) → correction / S4b")
    print("=" * 60)
    rng = np.random.default_rng(0)
    # lognormal blanks (skewed)
    values = rng.lognormal(mean=0.0, sigma=1.0, size=80)
    strata = np.repeat(np.arange(4), 20)
    res = run_guidance(
        goal=Goal.E1_VERIFY_LOD,
        result_type="continuous",
        values=values,
        strata=strata,
        use_case="ldt_lod_establishment",
        p=0.95,
        p0=0.95,
        cluster_size=20,
    )
    print(res.report.to_markdown())


def demo_g4_kn() -> None:
    print("=" * 60)
    print("E3: qualitative k/n")
    print("=" * 60)
    res = run_guidance(
        goal=Goal.E3_QUALITATIVE_KN,
        result_type="binary",
        use_case="nat_hit_rate_kn",
        p=0.95,
        k=19,
        power=0.95,
    )
    print(f"n_per_arm={res.sample_size.n_per_arm}, details={res.sample_size.details}")


if __name__ == "__main__":
    demo_g2_compare_reagents()
    demo_continuous_skewed()
    demo_g4_kn()
