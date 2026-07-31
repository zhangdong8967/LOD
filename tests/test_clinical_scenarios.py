"""Tests for clinical scenario catalogue."""

from __future__ import annotations

from lod_guide.scenarios import (
    SCENARIOS,
    Coverage,
    coverage_summary,
    get_scenario,
    run_scenario_demo,
)


def test_catalogue_has_core_lab_needs():
    ids = {s.scenario_id for s in SCENARIOS}
    assert "CS01_VERIFY_SINGLE_HITRATE" in ids
    assert "CS05_COMPARE_KITS_90_VS_80" in ids
    assert "CS06_COMPARE_KITS_90_VS_50" in ids
    assert "CS08_MISS_PROBABILITY_AUDIT" in ids


def test_coverage_counts():
    c = coverage_summary()
    assert c[Coverage.COVERED.value] >= 11
    assert sum(c.values()) == len(SCENARIOS)


def test_demo_single_and_compare():
    r1 = run_scenario_demo("CS01_VERIFY_SINGLE_HITRATE")
    assert "guidance_n" in r1
    r2 = run_scenario_demo("CS05_COMPARE_KITS_90_VS_80")
    assert r2["n_star_80"] >= 190
    r3 = run_scenario_demo("CS14_SKEW_HETERO_GATE")
    assert r3["parametric_ok"] is False or "nonparametric" in r3["model_path"]


def test_get_scenario():
    s = get_scenario("CS07_LOT_TO_LOT")
    assert s.goal.value == "G2_COMPARE_REAGENTS"
