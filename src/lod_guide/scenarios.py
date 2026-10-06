"""
Clinical scenario catalogue for lod_guide.

Maps real laboratory needs → Goal (E1–E3) → result type → runner entry.
Coverage status is honest: covered | partial | planned.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Callable

import numpy as np

from lod_guide.pipeline import run_guidance
from lod_guide.s0_goal import Goal
from lod_guide.s1_result_type import ResultType


class Coverage(str, Enum):
    COVERED = "covered"  # dedicated path + scripted demo
    PARTIAL = "partial"  # runnable via pipeline but thin specialty logic
    PLANNED = "planned"  # documented need, not yet first-class


class ClinicalDomain(str, Enum):
    MOLECULAR = "molecular_nat_qpcr"
    IMMUNOASSAY = "immunoassay"
    CLINICAL_CHEMISTRY = "clinical_chemistry_quantitative"
    HEMATOLOGY = "hematology_count"
    BLOOD_BANK = "blood_bank_multiclass"
    GENERAL = "general_cross_cutting"


@dataclass(frozen=True)
class ClinicalScenario:
    scenario_id: str
    title: str
    lab_question: str
    domain: ClinicalDomain
    goal: Goal
    result_type: ResultType
    use_case: str
    coverage: Coverage
    script_entry: str
    notes: str
    related_modules: tuple[str, ...] = ()


SCENARIOS: tuple[ClinicalScenario, ...] = (
    # ----- Single reagent / method -----
    ClinicalScenario(
        "CS01_VERIFY_SINGLE_HITRATE",
        "Verify a single reagent LoD hit-rate claim",
        "At the claimed LoD concentration, is detection probability ≥ p0 (e.g. 95%)?",
        ClinicalDomain.GENERAL,
        Goal.E1_VERIFY_LOD,
        ResultType.BINARY,
        "verify_manufacturer_lod_claim",
        Coverage.COVERED,
        "examples/scenarios/cs01_verify_single_hitrate.py",
        "Includes all-positive trap warning for small n.",
        ("pipeline", "research.all_positive_trap"),
    ),
    ClinicalScenario(
        "CS02_ESTABLISH_CONTINUOUS_LOB_LOD",
        "Establish / verify continuous LoB–LoD (clinical chemistry style)",
        "From blank and low-level continuous signals, what LoB/LoD and which path (parametric vs nonparametric)?",
        ClinicalDomain.CLINICAL_CHEMISTRY,
        Goal.E1_VERIFY_LOD,
        ResultType.CONTINUOUS,
        "ldt_lod_establishment",
        Coverage.COVERED,
        "examples/scenarios/cs02_continuous_lob_lod.py",
        "Diagnostics + correction gate; real clinical chemistry raw panels still limited.",
        ("pipeline", "s2_diagnostics", "s3_correction", "research.lob_coverage"),
    ),
    ClinicalScenario(
        "CS03_QUALITATIVE_KN",
        "Qualitative k/n LoD claim (e.g. NAT)",
        "What n is needed so P(at least k positives) ≥ target at assumed p?",
        ClinicalDomain.MOLECULAR,
        Goal.E3_QUALITATIVE_KN,
        ResultType.BINARY,
        "nat_hit_rate_kn",
        Coverage.COVERED,
        "examples/scenarios/cs03_qualitative_kn.py",
        "Classic molecular / qualitative immunoassay design.",
        ("pipeline", "s5_sample_size"),
    ),
    ClinicalScenario(
        "CS04_ALL_POSITIVE_TRAP",
        "Small-n 100% detection illusion",
        "We saw 5/5 or 10/10 positives — does that prove a 95% LoD?",
        ClinicalDomain.GENERAL,
        Goal.E1_VERIFY_LOD,
        ResultType.BINARY,
        "verify_manufacturer_lod_claim",
        Coverage.COVERED,
        "examples/scenarios/cs04_all_positive_trap.py",
        "Mandatory education scenario; not a claim verification by itself.",
        ("research.all_positive_trap",),
    ),
    # ----- Compare reagents / lots -----
    ClinicalScenario(
        "CS05_COMPARE_KITS_90_VS_80",
        "Compare two kits with modest LoD gap (90% vs 80%)",
        "How many replicates to detect Δp=0.10? What is miss probability at n=20?",
        ClinicalDomain.GENERAL,
        Goal.E2_COMPARE_REAGENTS,
        ResultType.BINARY,
        "kit_a_vs_kit_b_near_lod",
        Coverage.COVERED,
        "examples/scenarios/cs05_compare_kits_90_vs_80.py",
        "Core E2 challenge to folklore n=20.",
        ("research.reagent_discrimination",),
    ),
    ClinicalScenario(
        "CS06_COMPARE_KITS_90_VS_50",
        "Compare two kits with large LoD gap (90% vs 50%)",
        "How many replicates to detect Δp=0.40? Relative concentration vs LoD95?",
        ClinicalDomain.GENERAL,
        Goal.E2_COMPARE_REAGENTS,
        ResultType.BINARY,
        "kit_a_vs_kit_b_near_lod",
        Coverage.COVERED,
        "examples/scenarios/cs06_compare_kits_90_vs_50.py",
        "Easier discrimination; still requires explicit power language.",
        ("research.reagent_discrimination",),
    ),
    ClinicalScenario(
        "CS07_LOT_TO_LOT",
        "Lot-to-lot LoD consistency check",
        "Do two lots differ in near-LoD hit rate enough to matter?",
        ClinicalDomain.GENERAL,
        Goal.E2_COMPARE_REAGENTS,
        ResultType.BINARY,
        "lot_to_lot_lod_check",
        Coverage.COVERED,
        "examples/scenarios/cs07_lot_to_lot.py",
        "Same math as kit comparison; estimand is lot Δp.",
        ("pipeline", "research.reagent_discrimination"),
    ),
    ClinicalScenario(
        "CS08_MISS_PROBABILITY_AUDIT",
        "Audit risk of false 'no difference' conclusions",
        "For planned n, how often will we miss a true reagent gap?",
        ClinicalDomain.GENERAL,
        Goal.E2_COMPARE_REAGENTS,
        ResultType.BINARY,
        "kit_a_vs_kit_b_near_lod",
        Coverage.COVERED,
        "examples/scenarios/cs08_miss_probability_audit.py",
        "Mandatory companion to any E2 study.",
        ("research.reagent_discrimination", "research.operating_characteristics"),
    ),
    # ----- LoQ / precision -----
    ClinicalScenario(
        "CS09_LOQ_PRECISION",
        "LoQ / functional sensitivity (precision claim)",
        "At low concentration, what n yields CV or CI width meeting acceptance?",
        ClinicalDomain.CLINICAL_CHEMISTRY,
        Goal.LOQ_PRECISION,
        ResultType.CONTINUOUS,
        "functional_sensitivity_loq",
        Coverage.PARTIAL,
        "examples/scenarios/cs09_loq_precision.py",
        "Precision-profile LoQ engine + CV design table (troponin EP17 Example 3); see research.precision_profile.",
        ("pipeline", "s5_sample_size"),
    ),
    # ----- Domain-specific -----
    ClinicalScenario(
        "CS10_MOLECULAR_QPCR_CURVE",
        "Molecular qPCR LoD from hit-rate vs concentration",
        "From multi-level standards, estimate logistic LoD95 and blank path.",
        ClinicalDomain.MOLECULAR,
        Goal.E1_VERIFY_LOD,
        ResultType.CONTINUOUS,
        "ldt_lod_establishment",
        Coverage.COVERED,
        "examples/scenarios/cs10_molecular_qpcr_curve.py",
        "Uses Zenodo public qPCR LoD/LoQ CSVs when available.",
        ("research.deep_qpcr", "data.download_real"),
    ),
    ClinicalScenario(
        "CS11_HEMATOLOGY_LOW_COUNT",
        "Hematology / particle low-count detection",
        "Poisson/NB counts near zero — detection probability and replicate plan.",
        ClinicalDomain.HEMATOLOGY,
        Goal.E1_VERIFY_LOD,
        ResultType.COUNT,
        "ldt_lod_establishment",
        Coverage.PARTIAL,
        "examples/scenarios/cs11_hematology_low_count.py",
        "Count routing exists; specialty hematology protocols still partial.",
        ("pipeline", "data.simulate"),
    ),
    ClinicalScenario(
        "CS12_IMMUNOASSAY_QUALITATIVE",
        "Qualitative immunoassay cutoff / reactive claim",
        "k/n or hit-rate verification at cutoff / LoD material.",
        ClinicalDomain.IMMUNOASSAY,
        Goal.E3_QUALITATIVE_KN,
        ResultType.BINARY,
        "immunoassay_qualitative_cutoff",
        Coverage.COVERED,
        "examples/scenarios/cs12_immunoassay_qualitative.py",
        "Shares E3 engine with NAT-style claims.",
        ("pipeline",),
    ),
    ClinicalScenario(
        "CS13_BLOOD_BANK_MULTICLASS",
        "Blood-bank multiclass (e.g. ABO) near decision boundary",
        "Success = correct class; how many replicates for reliability?",
        ClinicalDomain.BLOOD_BANK,
        Goal.E3_QUALITATIVE_KN,
        ResultType.MULTICLASS,
        "immunoassay_qualitative_cutoff",
        Coverage.PARTIAL,
        "examples/scenarios/cs13_blood_bank_multiclass.py",
        "Success definition required; not classic LoD but included for type coverage.",
        ("pipeline", "s1_result_type"),
    ),
    ClinicalScenario(
        "CS14_SKEW_HETERO_GATE",
        "Skewed / heterogeneous blanks force nonparametric path",
        "When near-LoD data fail normality/poolability, what does the algorithm do?",
        ClinicalDomain.CLINICAL_CHEMISTRY,
        Goal.E1_VERIFY_LOD,
        ResultType.CONTINUOUS,
        "ldt_lod_establishment",
        Coverage.COVERED,
        "examples/scenarios/cs14_skew_hetero_gate.py",
        "Core assumption-gate demonstration for Clinical Chemistry narrative.",
        ("s2_diagnostics", "s3_correction", "research.lob_coverage"),
    ),
    ClinicalScenario(
        "CS15_CONCENTRATION_RELATIVE_LOD",
        "Challenge material below / at / above LoD",
        "How does c/LoD change single-kit pass rates and kit-comparison miss β?",
        ClinicalDomain.GENERAL,
        Goal.E2_COMPARE_REAGENTS,
        ResultType.BINARY,
        "kit_a_vs_kit_b_near_lod",
        Coverage.COVERED,
        "examples/scenarios/cs15_concentration_relative_lod.py",
        "Mandatory: concentration mis-location causes easy-pass or false fail / false equivalence.",
        ("research.concentration_relative",),
    ),
)


def coverage_summary() -> dict[str, int]:
    counts = {c.value: 0 for c in Coverage}
    for s in SCENARIOS:
        counts[s.coverage.value] += 1
    return counts


def scenarios_table() -> list[dict[str, Any]]:
    return [asdict(s) for s in SCENARIOS]


def get_scenario(scenario_id: str) -> ClinicalScenario:
    for s in SCENARIOS:
        if s.scenario_id == scenario_id:
            return s
    raise KeyError(scenario_id)


def run_scenario_demo(scenario_id: str) -> dict[str, Any]:
    """
    Lightweight in-process demo for each scenario (used by the catalogue runner).
    Dedicated scripts under examples/scenarios/ mirror these demos for labs.
    """
    s = get_scenario(scenario_id)
    out: dict[str, Any] = {
        "scenario_id": s.scenario_id,
        "title": s.title,
        "coverage": s.coverage.value,
        "goal": s.goal.value,
        "result_type": s.result_type.value,
    }

    if scenario_id == "CS01_VERIFY_SINGLE_HITRATE":
        res = run_guidance(
            goal=Goal.E1_VERIFY_LOD,
            result_type="binary",
            use_case=s.use_case,
            p=0.90,
            p0=0.95,
            run_sensitivity=False,
        )
        from lod_guide.research.all_positive_trap import inference_after_all_positive

        trap = inference_after_all_positive(10, claim_p0=0.95)
        out["guidance_n"] = res.sample_size.n_per_arm
        out["after_10of10_cp_low"] = trap.cp_low

    elif scenario_id == "CS02_ESTABLISH_CONTINUOUS_LOB_LOD":
        rng = np.random.default_rng(0)
        values = rng.normal(0.05, 0.02, size=60)
        res = run_guidance(
            goal=Goal.E1_VERIFY_LOD,
            result_type="continuous",
            values=values,
            use_case=s.use_case,
            run_sensitivity=False,
        )
        out["model_path"] = res.model_path.value
        out["parametric_ok"] = res.report.parametric_ok
        out["n"] = res.sample_size.n_per_arm

    elif scenario_id in {"CS03_QUALITATIVE_KN", "CS12_IMMUNOASSAY_QUALITATIVE"}:
        res = run_guidance(
            goal=Goal.E3_QUALITATIVE_KN,
            result_type="binary",
            use_case=s.use_case,
            p=0.95,
            k=19,
            power=0.95,
            run_sensitivity=False,
        )
        out["n"] = res.sample_size.n_per_arm
        out["details"] = res.sample_size.details

    elif scenario_id == "CS04_ALL_POSITIVE_TRAP":
        from lod_guide.research.all_positive_trap import run_all_positive_trap_study

        out["highlights"] = run_all_positive_trap_study()["highlights"]

    elif scenario_id in {
        "CS05_COMPARE_KITS_90_VS_80",
        "CS06_COMPARE_KITS_90_VS_50",
        "CS07_LOT_TO_LOT",
        "CS08_MISS_PROBABILITY_AUDIT",
    }:
        from lod_guide.research.reagent_discrimination import evaluate_pair

        pair = {
            "CS05_COMPARE_KITS_90_VS_80": (0.90, 0.80),
            "CS06_COMPARE_KITS_90_VS_50": (0.90, 0.50),
            "CS07_LOT_TO_LOT": (0.92, 0.85),
            "CS08_MISS_PROBABILITY_AUDIT": (0.90, 0.80),
        }[scenario_id]
        sc = evaluate_pair(pair[0], pair[1], label=scenario_id)
        out["n_star_80"] = sc.n_star_80
        out["miss_at_n20"] = sc.miss_prob_at_n[20]
        out["relative_c_a"] = sc.relative_c_a
        out["relative_c_b"] = sc.relative_c_b

    elif scenario_id == "CS09_LOQ_PRECISION":
        res = run_guidance(
            goal=Goal.LOQ_PRECISION,
            result_type="continuous",
            use_case=s.use_case,
            target_cv_pct=20.0,
            sigma_over_mu=0.25,
            run_sensitivity=False,
        )
        out["n"] = res.sample_size.n_per_arm
        out["method"] = res.sample_size.method.value
        try:
            from lod_guide.research.precision_profile import run_precision_profile_study

            pp = run_precision_profile_study()
            out["loq_at_cv20"] = pp.get("target_20", {}).get("loq")
            out["loq_method"] = pp.get("target_20", {}).get("method")
            out["n_design_at_loq"] = pp.get("target_20", {}).get("n_design")
        except Exception as exc:  # noqa: BLE001
            out["precision_profile_error"] = str(exc)
        out["coverage_note"] = "improved: precision_profile LoQ@CV% + n design; tier-C troponin demo"

    elif scenario_id == "CS10_MOLECULAR_QPCR_CURVE":
        from lod_guide.data.download_real import RAW_DIR
        from lod_guide.research.deep_qpcr import analyze_dataset

        path = RAW_DIR / "zenodo_mus_wt_lod_loq.csv"
        if path.exists():
            block = analyze_dataset(path, "zenodo_mus_wt_qpcr")
            out["blank_path"] = block["blank_guidance"]["model_path"]
            out["lod95"] = block.get("logistic_lod_95")
        else:
            out["error"] = "Zenodo file missing — run download_real first"

    elif scenario_id == "CS11_HEMATOLOGY_LOW_COUNT":
        from lod_guide.data.simulate import sim_poisson_counts

        ds = sim_poisson_counts(seed=5)
        res = run_guidance(
            goal=Goal.E1_VERIFY_LOD,
            result_type="count",
            values=ds.values,
            strata=ds.strata,
            use_case=s.use_case,
            cluster_size=40,
            run_sensitivity=False,
        )
        out["model_path"] = res.model_path.value
        out["n"] = res.sample_size.n_per_arm

    elif scenario_id == "CS13_BLOOD_BANK_MULTICLASS":
        res = run_guidance(
            goal=Goal.E3_QUALITATIVE_KN,
            result_type="multiclass",
            n_classes=4,
            success_definition="correct_class",
            p=0.98,
            k=1,
            power=0.95,
            run_sensitivity=False,
        )
        out["n"] = res.sample_size.n_per_arm
        out["coverage_note"] = "partial multiclass LoD analogue"

    elif scenario_id == "CS14_SKEW_HETERO_GATE":
        from lod_guide.data.simulate import sim_skewed_hetero_blanks

        ds = sim_skewed_hetero_blanks(seed=1)
        res = run_guidance(
            goal=Goal.E1_VERIFY_LOD,
            result_type="continuous",
            values=ds.values,
            strata=ds.strata,
            use_case=s.use_case,
            cluster_size=40,
            run_sensitivity=False,
        )
        out["parametric_ok"] = res.report.parametric_ok
        out["correction"] = res.report.correction_method
        out["model_path"] = res.model_path.value

    elif scenario_id == "CS15_CONCENTRATION_RELATIVE_LOD":
        from lod_guide.research.concentration_relative import run_concentration_relative_study

        study = run_concentration_relative_study()
        out["headlines"] = study["headlines"]
        out["zone_narrative"] = study["zone_narrative"]

    else:
        out["error"] = "no demo mapped"

    return out


def run_all_scenario_demos() -> list[dict[str, Any]]:
    return [run_scenario_demo(s.scenario_id) for s in SCENARIOS]
