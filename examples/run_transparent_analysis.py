"""
Transparent, auditable analysis for Clinical Chemistry–grade reporting.

Runs pre-specified blocks A1–A4, writes SHA-256 audit JSON under data/audit/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lod_guide import __version__, run_guidance
from lod_guide.data.simulate import sim_skewed_hetero_blanks
from lod_guide.s0_goal import Goal
from lod_guide.theory.audit import AuditStep, new_audit
from lod_guide.theory.estimands import estimand_for_goal
from lod_guide.theory.exact import (
    clopper_pearson_interval,
    parametric_vs_quantile_lob_exponential,
    wilson_interval,
)
from lod_guide.theory.propositions import verify_all_propositions

PROTOCOL_ID = "LOD-GUIDE-CC-2026-v1"


def main() -> None:
    print(f"lod_guide {__version__} | protocol {PROTOCOL_ID}")
    print("=" * 72)

    # ---- A4 propositions first (theory certificates) ----
    certs = verify_all_propositions()
    for c in certs:
        status = "PASS" if c.passed else "FAIL"
        print(f"[{status}] {c.proposition_id}: {c.statement}")
        print(f"       {c.details}")

    if not all(c.passed for c in certs):
        raise SystemExit("Proposition battery failed — stop confirmatory analysis.")

    # ---- A1 G2 discrimination ----
    est_g2 = estimand_for_goal(Goal.G2_COMPARE_REAGENTS.value)
    audit = new_audit(PROTOCOL_ID, est_g2.to_dict())
    res_g2 = run_guidance(
        goal=Goal.G2_COMPARE_REAGENTS,
        result_type="binary",
        use_case="kit_a_vs_kit_b_near_lod",
        p_a=0.90,
        p_b=0.80,
        alpha=0.05,
        power=0.80,
        run_sensitivity=True,
    )
    audit.add_step(
        AuditStep(
            "A1",
            "G2_reagent_discrimination",
            inputs={"p_a": 0.90, "p_b": 0.80, "alpha": 0.05, "power": 0.80},
            outputs={
                "n_per_arm": res_g2.sample_size.n_per_arm,
                "method": res_g2.sample_size.method.value,
                "expected_power": res_g2.sample_size.expected_power_or_precision,
                "warnings": res_g2.report.warnings,
            },
        )
    )

    # Wilson / CP intervals for a hypothetical observed 18/20 vs 16/20 (illustration)
    w_a = wilson_interval(18, 20)
    cp_a = clopper_pearson_interval(18, 20)
    audit.add_step(
        AuditStep(
            "A1b",
            "interval_transparency_example",
            inputs={"successes": 18, "n": 20},
            outputs={"wilson": w_a, "clopper_pearson": cp_a},
            notes="Illustrative intervals for reporting transparency; not primary estimand.",
        )
    )

    # ---- A2 skewed blanks ----
    est_g1 = estimand_for_goal(Goal.G1_VERIFY_LOD.value)
    skewed = sim_skewed_hetero_blanks(seed=1)
    res_sk = run_guidance(
        goal=Goal.G1_VERIFY_LOD,
        result_type="continuous",
        values=skewed.values,
        strata=skewed.strata,
        use_case="ldt_lod_establishment",
        p0=0.95,
        cluster_size=40,
        run_sensitivity=False,
    )
    audit.add_step(
        AuditStep(
            "A2",
            "skewed_hetero_blanks_path",
            inputs={
                "dataset": skewed.dataset_id,
                "n": int(skewed.values.size),
                "challenge_tags": skewed.challenge_tags,
            },
            outputs={
                "parametric_ok": res_sk.report.parametric_ok,
                "correction": res_sk.report.correction_method,
                "model_path": res_sk.model_path.value,
                "n_per_arm": res_sk.sample_size.n_per_arm,
                "diagnostics": res_sk.report.diagnostics_summary,
            },
        )
    )

    # ---- Prop 5 numeric exhibit ----
    audit.add_step(
        AuditStep(
            "A2b",
            "prop5_exponential_lob_mismatch",
            inputs={"alpha": 0.05},
            outputs=parametric_vs_quantile_lob_exponential(0.05),
        )
    )

    # Attach certificates & finalize
    audit.proposition_certificates = [
        {"id": c.proposition_id, "passed": c.passed, "details": c.details} for c in certs
    ]
    audit.final = {
        "primary_conclusion": (
            "Folklore n=20 is underpowered for Δ=0.10 at p≈0.85–0.90; "
            "comparative LoD must use hat{p} with powered n; parametric LoB "
            "requires passed diagnostics or nonparametric replacement."
        ),
        "g2_n_star": res_g2.sample_size.n_per_arm,
        "skew_path": res_sk.model_path.value,
        "software_version": __version__,
        "protocol_id": PROTOCOL_ID,
    }

    path = audit.save()
    print("=" * 72)
    print(res_g2.report.to_markdown())
    print("=" * 72)
    print(f"Audit written: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(f"sha256_content: {payload['sha256_content']}")
    print(f"sha256_full:    {payload['sha256_full']}")


if __name__ == "__main__":
    main()
