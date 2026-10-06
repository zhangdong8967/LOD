"""Tests for reliability charter and TOST extension branch."""

from __future__ import annotations

import json
from pathlib import Path

from lod_guide.research.reliability_summaries import run_reliability_summaries
from lod_guide.research.tost_equivalence_branch import run_tost_equivalence_branch
from lod_guide.theory.claim_types import claim_type_for


def test_claim_type_headline_certificates():
    assert claim_type_for("P7_all_positive_trap") == "enumeration"
    assert claim_type_for("P8_exact_vs_asymptotic_gap") == "analytic_plus_enum"
    assert claim_type_for("P18_folklore_pareto_dominated") == "enumeration"
    assert claim_type_for("P15_lod_identifiability") == "extension"


def test_reliability_summary_has_p8_fraction():
    out = run_reliability_summaries()
    assert out["e2_lattice_cells"] == 1225
    assert out["p8_gap_cells_gt_0p05"] >= 700
    assert 0.5 < out["p8_gap_fraction"] < 0.75
    assert Path(out["path"]).is_file()


def test_tost_branch_discrimination_vs_equivalence():
    out = run_tost_equivalence_branch()
    hl = out["headline"]
    assert hl["discrimination_pair"]["n_80pct"] == 199
    assert hl["equivalence_pair"]["n_tost_80pct"] > 0
    assert "incompatible" in out["interpretation"].lower()
    assert Path(out["path"]).is_file()
