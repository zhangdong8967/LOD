"""Tests for elevated analysis: decision risk, tier-A meta, E1 coverage, figure style."""

from __future__ import annotations

from pathlib import Path

import pytest

from lod_guide.paper.figure_style import panel_label
from lod_guide.research.decision_risk import evaluate_standard_scenarios, loss
from lod_guide.research.one_proportion_coverage import (
    claim_pass_probability,
    coverage_study,
    run_one_proportion_coverage_study,
)
from lod_guide.research.tierA_meta_analysis import run_tierA_meta_analysis
from lod_guide.research.tierA_protocol_audit import run_tierA_protocol_audit
from lod_guide.theory.propositions import prop7_all_positive_trap, prop8_exact_vs_asymptotic_gap


def test_loss_increases_with_beta():
    assert loss(type_i=0.05, beta=0.9, mismatch=0.0) > loss(type_i=0.05, beta=0.2, mismatch=0.0)


def test_decision_risk_scenarios():
    out = evaluate_standard_scenarios()
    assert out["study_id"].startswith("DECISION-RISK")
    assert Path(out["path"]).exists()
    ids = {s["scenario_id"] for s in out["scenarios"]}
    assert "E2_folklore_n20_90_vs_80" in ids
    assert sum(1 for i in ids if i.startswith("E2_folklore_n20_")) == 8
    ratio = out["comparisons"]["E2_loss_ratio_folklore_over_powered"]
    assert ratio is not None and ratio > 1.0


def test_prop7_prop8():
    assert prop7_all_positive_trap().passed
    assert prop8_exact_vs_asymptotic_gap().passed


def test_g1_coverage_smoke():
    row = coverage_study(p_true=0.95, n=20, n_sims=500, seed=0)
    assert 0.8 <= row["coverage_clopper_pearson"] <= 1.0
    p_pass = claim_pass_probability(p_true=0.80, n=20, claim=0.95)
    assert p_pass < 0.2


def test_one_proportion_study_writes():
    out = run_one_proportion_coverage_study()
    assert Path(out["path"]).exists()
    assert Path(out["table"]).exists()
    assert Path(out["claim_pass_table"]).exists()


def test_tierA_protocol_audit():
    out = run_tierA_protocol_audit()
    assert out["n_rows"] == 16
    assert out["n_with_guidance_n_star"] == 15
    assert out["n_oc_below_target_at_archived_n"] == 16
    assert out["mapped_claim_counts"] == {"E1": 12, "E2": 3, "E3": 1}
    assert out["n_empirical_rate_below_p0"] == 5
    assert Path(out["summary_table"]).exists()
    assert Path(out["table"]).exists()
    text = Path(out["table"]).read_text(encoding="utf-8")
    assert "jcm_hansen2020_abbott" in text
    assert "scirep_jiang2025_mp" in text
    assert "plos_bzdok2024_trec_cxce_1to100" in text
    assert "plos_bzdok2024_trec_lod" in text
    assert "analyseit_ep17_estradiol" in text


def test_tierA_meta():
    if not (Path("data/raw/Precision_radioimmuno.txt")).exists():
        pytest.skip("raw deposits missing")
    out = run_tierA_meta_analysis()
    assert out["n_datasets"] >= 6
    assert all(r.get("evidence_tier") == "A" for r in out["rows"] if "error" not in r)
    assert not any("error" in r for r in out["rows"]), f"errors: {[r for r in out['rows'] if 'error' in r]}"
    assert Path(out["table"]).exists()
    text = Path(out["table"]).read_text(encoding="utf-8")
    assert "zenodo_radioimmuno_precision" in text
    assert "analyseit_ep17_troponin" not in text  # tier C excluded


def test_panel_label_callable():
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    panel_label(ax, "A")
    plt.close(fig)
