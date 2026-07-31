"""
Deep research runner — not a paper draft.

Executes:
  0) Theory + all-positive + discrimination + concentration + continuous fields
  1) Zenodo qPCR hit-rate / logistic LoD
  2) Folklore vs powered operating characteristics (MC)
  3) Parametric vs nonparametric LoB coverage under skew
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lod_guide.research import (
    build_all_continuous_models,
    run_all_positive_trap_study,
    run_concentration_relative_study,
    run_deep_qpcr_research,
    run_exact_power_study,
    run_precision_profile_study,
    run_ep17_estradiol_study,
    run_msstats_lob_study,
    run_type1_calibration_study,
    build_reproducibility_deposit,
    run_empirical_tierA_extension,
    build_evidence_stratified_report,
    evaluate_standard_scenarios,
    run_tierA_meta_analysis,
    run_one_proportion_coverage_study,
    run_s2_threshold_sensitivity,
    run_probit_design_grid,
    run_lob_coverage,
    run_operating_characteristics,
    run_reagent_discrimination_study,
)
from lod_guide.research.all_positive_figures import generate_all_positive_trap_figures
from lod_guide.research.continuous_figures import generate_continuous_model_figures
from lod_guide.research.discrimination_figures import generate_discrimination_figures
from lod_guide.theory.propositions import verify_all_propositions


def main() -> None:
    print("=" * 72)
    print("0) Theory certificates P1–P8")
    for c in verify_all_propositions():
        print(("PASS" if c.passed else "FAIL"), c.result_id, c.details)

    print("=" * 72)
    print("0b) All-positive trap (n/n ≠ reliable LoD)")
    trap = run_all_positive_trap_study()
    print(json.dumps(trap["formulae"], indent=2))
    print(json.dumps(trap["highlights"], indent=2))
    for p in generate_all_positive_trap_figures():
        print(" figure:", p)

    print("=" * 72)
    print("0c) Reagent discrimination (90vs80, 90vs50) + miss β")
    disc = run_reagent_discrimination_study(n_sims_check=3000, seed=7)
    print(json.dumps(disc["headline"], indent=2))
    print(json.dumps(disc["algorithm"]["false_conclusion"], indent=2))
    for p in generate_discrimination_figures():
        print(" figure:", p)

    print("=" * 72)
    print("0d) Concentration relative to LoD (below / at / above)")
    conc = run_concentration_relative_study()
    for key in ("at_r0.5_below", "at_r1.0_lod", "at_r2.0_above"):
        row = conc["headlines"][key]
        print(
            key,
            "pA/pB=",
            round(row["p_A"], 3),
            round(row["p_B"], 3),
            "passA=",
            round(row["P_pass_A_rate_ge_claim"], 3),
            "miss=",
            round(row["compare_miss_beta"], 3),
        )
    from lod_guide.research.concentration_figures import generate_concentration_figures

    for p in generate_concentration_figures():
        print(" figure:", p)

    print("=" * 72)
    print("0e) Continuous parameter-space models (CS04–CS06 are slices only)")
    cm = build_all_continuous_models(fine=True)
    print(json.dumps(cm["philosophy"], indent=2))
    print(json.dumps(cm["discrimination_summary"]["example_points"], indent=2))
    for p in generate_continuous_model_figures(fine_build=False):
        print(" figure:", p)

    print("=" * 72)
    print("0f) Exact vs asymptotic small-sample power (Fisher / Boschloo)")
    exact = run_exact_power_study()
    print(json.dumps(exact["highlights"], indent=2))
    print(json.dumps(exact["reporting_policy"], indent=2))

    print("=" * 72)
    print("0f2) Tier-A empirical extension (radioimmuno precision/linearity + RMN) + stratified report")
    emp = run_empirical_tierA_extension()
    print("empirical blocks", len(emp.get("blocks", [])))
    ev = build_evidence_stratified_report(download=False)
    print("evidence counts", ev.get("counts"))

    print("=" * 72)
    print("0f3) Decision risk + tier-A meta + G1 coverage + S2 threshold sens + probit grid")
    risk = evaluate_standard_scenarios()
    print("decision risk comparisons", risk.get("comparisons"))
    meta = run_tierA_meta_analysis()
    print("tierA meta n=", meta.get("n_datasets"), "para false=", meta.get("parametric_candidate_false"))
    g1 = run_one_proportion_coverage_study()
    print("G1 coverage table", g1.get("table"))
    s2s = run_s2_threshold_sensitivity()
    print("S2 threshold sensitivity", json.dumps(s2s.get("headline"), indent=2))
    pgrid = run_probit_design_grid()
    print("probit design grid", json.dumps(pgrid.get("headline"), indent=2, default=str)[:800])

    print("=" * 72)
    print("0g) Precision-profile LoQ + EP17 estradiol + CPTAC proteomics LoB + Type I")
    pp = run_precision_profile_study()
    print("LoQ@20%", pp.get("target_20", {}).get("loq"), "method", pp.get("target_20", {}).get("method"))
    estr = run_ep17_estradiol_study()
    print("estradiol headline", json.dumps(estr.get("headline"), indent=2))
    msstats = run_msstats_lob_study()
    print("msstats CPTAC headline", json.dumps(msstats.get("headline"), indent=2))
    t1 = run_type1_calibration_study(n_sims=2000)
    print("type1 summary", json.dumps(t1["summary"], indent=2))

    print("=" * 72)
    print("1) Deep qPCR (real data)")
    qpcr = run_deep_qpcr_research()
    for block in qpcr:
        print("-", block.get("dataset_id"), "path=", block.get("blank_guidance", {}).get("model_path"))
        for t, fit in (block.get("logistic_lod_95") or {}).items():
            print(f"    LoD95 {t[:50]}: {fit.get('lod_sq')}")

    print("=" * 72)
    print("2) Operating characteristics (Monte Carlo)")
    oc = run_operating_characteristics(n_sims=10_000, seed=1)
    print(json.dumps(oc["summary"], indent=2))

    print("=" * 72)
    print("3) LoB coverage under Gaussian / lognormal / exponential")
    lob = run_lob_coverage(n_mc=800, n_blank=60, seed=2)
    for law in ("normal", "lognormal", "exponential"):
        b = lob[law]
        print(
            f"  {law:12} parametric exceedance={b['parametric_mean_exceedance']:.4f} "
            f"| nonparametric={b['nonparametric_mean_exceedance']:.4f} "
            f"(target α={b['alpha_target']})"
        )

    repro = build_reproducibility_deposit()
    print("repro deposit", repro.get("path"))

    summary_path = ROOT / "data" / "research" / "deep_research_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(
            {
                "oc_summary": oc["summary"],
                "lob_coverage": {k: lob[k] for k in ("normal", "lognormal", "exponential", "theory_exponential")},
                "qpcr_datasets": [b.get("dataset_id") for b in qpcr],
                "all_positive_highlights": trap["highlights"],
                "discrimination_headline": disc["headline"],
                "concentration_headlines": {
                    k: conc["headlines"][k] for k in ("at_r0.5_below", "at_r1.0_lod", "at_r2.0_above")
                },
                "continuous_models": cm,
                "exact_vs_asymptotic_highlights": exact["highlights"],
                "exact_reporting_policy": exact["reporting_policy"],
                "precision_profile_loq20": pp.get("target_20"),
                "estradiol_headline": estr.get("headline"),
                "msstats_cptac_headline": msstats.get("headline"),
                "type1_summary": t1.get("summary"),
                "reproducibility": repro.get("deposit_id"),
                "empirical_tierA": emp.get("study_id"),
                "evidence_counts": ev.get("counts"),
                "decision_risk": risk.get("comparisons"),
                "tierA_meta": {"n": meta.get("n_datasets"), "path": meta.get("path")},
                "g1_coverage": g1.get("path"),
                "s2_threshold_sensitivity": s2s.get("headline"),
                "probit_design_grid": pgrid.get("headline"),
            },
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )
    print("=" * 72)
    print("Wrote", summary_path)


if __name__ == "__main__":
    main()
