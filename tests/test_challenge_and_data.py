"""Tests for challenge positioning and diverse data catalogue."""

from __future__ import annotations

import pytest

from lod_guide.challenge import (
    CHALLENGE_CLAIMS,
    CLAIMS_WE_DO_NOT_MAKE,
    CLAIMS_WE_MAY_MAKE,
    POSITIONING_STATEMENT,
    RELATION_TO_STANDARDS,
    manifesto_markdown,
)
from lod_guide.data.simulate import generate_all_simulated, sim_skewed_hetero_blanks
from lod_guide.data.download_real import RAW_DIR, REMOTE_DATASETS, load_zenodo_qpcr_cq
from lod_guide.data import build_catalogue, run_guidance_on_entry
from lod_guide.s6_report import GuidanceReport


def test_locked_positioning_stance():
    """Blueprint stance: complement EP17; challenge practice; do not supersede standards."""
    text = POSITIONING_STATEMENT.lower()
    assert "bridges ep17" in text or "complement" in text
    assert "does not claim" in text
    assert "supersede" in text
    assert "ep17" in text
    assert "challenge" in text
    assert any("must be replaced" in c.lower() for c in CLAIMS_WE_DO_NOT_MAKE)
    assert len(CLAIMS_WE_MAY_MAKE) >= 4
    assert "ep17" in RELATION_TO_STANDARDS.lower()


def test_challenge_manifesto_present():
    assert len(CHALLENGE_CLAIMS) >= 5
    md = manifesto_markdown()
    assert "C1" in md and "C4" in md
    assert "do not claim" in md.lower()


def test_s6_report_uses_locked_positioning():
    rep = GuidanceReport(
        goal="E1",
        use_case=None,
        result_type="binary",
        diagnostics_summary={},
        correction_method="none",
        model_path="x",
        parametric_ok=True,
        sample_size={},
        assumptions_passed=[],
        assumptions_failed=[],
    )
    assert rep.positioning == POSITIONING_STATEMENT


def test_simulate_diverse():
    ds = generate_all_simulated()
    ids = {d.dataset_id for d in ds}
    assert "sim_skewed_hetero_blanks" in ids
    assert "sim_binary_reagents_90_vs_80" in ids
    assert len(ds) >= 8


def test_skewed_triggers_nonparametric_path():
    from lod_guide.pipeline import run_guidance
    from lod_guide.s0_goal import Goal

    raw = sim_skewed_hetero_blanks(seed=99)
    res = run_guidance(
        goal=Goal.E1_VERIFY_LOD,
        result_type="continuous",
        values=raw.values,
        strata=raw.strata,
        use_case="ldt_lod_establishment",
        run_sensitivity=False,
    )
    assert (
        res.report.parametric_ok is False
        or res.model_path.value.startswith("nonparametric")
        or res.report.correction_method != "none"
    )


def test_zenodo_files_or_skip():
    path = RAW_DIR / REMOTE_DATASETS[0].filename
    if not path.exists():
        pytest.skip("Zenodo file not downloaded yet")
    parsed = load_zenodo_qpcr_cq(path)
    assert parsed["n_rows"] > 10
    assert "hit_summary" in parsed


def test_catalogue_and_benchmark_entry():
    cat = build_catalogue(download=False, regenerate_sim=True)
    assert any(e.source == "simulated" for e in cat)
    sim_entries = [e for e in cat if e.dataset_id == "sim_binary_reagents_90_vs_80"]
    assert sim_entries
    out = run_guidance_on_entry(sim_entries[0])
    assert out["n_per_arm"] >= 190
    assert out.get("challenges_folklore_n20") is True
