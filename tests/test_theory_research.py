"""Tests for unified theory research pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lod_guide.paper.theory_research import (
    DEFECTS_JSON,
    TABLE4_CANONICAL,
    TABLE4_JSON,
    VERIFICATION_DEFECTS,
    audit_check,
    build_defects_bundle,
    build_table4,
    copy_audit_bundle,
    run_theory_verification,
    write_theory_summary,
)


def test_verification_defects_map_headline_certificates():
    assert set(VERIFICATION_DEFECTS) == {"D1", "D2", "D3"}
    assert "P7_all_positive_trap" in VERIFICATION_DEFECTS["D1"]["certificate_ids"]
    assert "T1_e3_pass_fisher_separation" in VERIFICATION_DEFECTS["D1"]["certificate_ids"]
    assert "P8_exact_vs_asymptotic_gap" in VERIFICATION_DEFECTS["D2"]["certificate_ids"]
    assert "T2a_pooled_z_fisher_distinct" in VERIFICATION_DEFECTS["D2"]["certificate_ids"]
    assert "T2b_berry_esseen_design_scale" in VERIFICATION_DEFECTS["D2"]["certificate_ids"]
    assert "T4_fleiss_nstar_delta_scaling" in VERIFICATION_DEFECTS["D2"]["certificate_ids"]
    assert "P18_folklore_pareto_dominated" in VERIFICATION_DEFECTS["D3"]["certificate_ids"]


def test_audit_check_uses_existing_audit():
    from lod_guide.paper.theory_audit import theory_bundle_ok

    result = audit_check()
    assert "ok" in result
    assert "bundle_ok" in result
    if result["exists"]:
        assert result.get("n_total", 0) >= 27
    if theory_bundle_ok():
        assert result["ok"] is True


def test_ensure_theory_research_skips_when_bundle_ok():
    from lod_guide.paper.theory_audit import theory_bundle_ok
    from lod_guide.paper.theory_research import ensure_theory_research

    if not theory_bundle_ok():
        pytest.skip("theory bundle not built in this environment")
    result = ensure_theory_research(force=False)
    assert result.get("skipped") is True


def test_build_table4_writes_canonical_and_json(tmp_path, monkeypatch):
    import lod_guide.paper.theory_research as tr

    monkeypatch.setattr(tr, "PAPER_TABLES", tmp_path / "tables")
    monkeypatch.setattr(tr, "PAPER_AUDIT", tmp_path / "audit")

    out = build_table4(force_verify=False)
    canonical = Path(out["Table4_csv"])
    assert canonical.name == TABLE4_CANONICAL
    assert canonical.exists()
    assert Path(out["Table4_json"]).name == TABLE4_JSON
    payload = json.loads(Path(out["Table4_json"]).read_text(encoding="utf-8"))
    assert payload["n_total"] >= 27
    assert "content_sha256" in payload
    assert all("layer" in row for row in payload["propositions"])
    assert all("role" in row for row in payload["propositions"])
    roles = {row["proposition_id"]: row["role"] for row in payload["propositions"]}
    assert roles["P7_all_positive_trap"] == "headline"
    assert roles["T1_e3_pass_fisher_separation"] == "headline extension"
    assert roles["T4_fleiss_nstar_delta_scaling"] == "headline extension"
    assert roles["P15_lod_identifiability"] == "extension"


def test_proposition_role_mapping():
    from lod_guide.paper.theory_research import proposition_role

    assert proposition_role("P7_all_positive_trap") == "headline"
    assert proposition_role("T2a_pooled_z_fisher_distinct") == "headline extension"
    assert proposition_role("P3_two_proportion_power") == "core"
    assert proposition_role("P15_lod_identifiability") == "extension"
    assert proposition_role("P13_minimax_formal") == "extension"


def test_build_defects_bundle_links_d1_d3(tmp_path, monkeypatch):
    import lod_guide.paper.theory_research as tr

    monkeypatch.setattr(tr, "PAPER_AUDIT", tmp_path / "audit")
    out = build_defects_bundle(force_verify=False)
    path = Path(out["defects_json"])
    assert path.name == DEFECTS_JSON
    payload = json.loads(path.read_text(encoding="utf-8"))
    for defect_id in ("D1", "D2", "D3"):
        block = payload["defects"][defect_id]
        assert block["certificates"]
        assert block["certificates"][0]["found"] is True
        assert block["certificates"][0]["passed"] is True


def test_copy_audit_bundle(tmp_path, monkeypatch):
    import lod_guide.paper.theory_research as tr

    src_audit = tmp_path / "data" / "audit"
    src_audit.mkdir(parents=True)
    sample = {"n_total": 22, "n_failed": 0, "content_sha256": "abc"}
    (src_audit / "theory_verification_latest.json").write_text(
        json.dumps(sample), encoding="utf-8"
    )
    monkeypatch.setattr(tr, "THEORY_AUDIT_JSON", src_audit / "theory_verification_latest.json")
    monkeypatch.setattr(tr, "PAPER_AUDIT", tmp_path / "paper_audit")

    written = copy_audit_bundle()
    assert "theory_verification" in written
    assert Path(written["theory_verification"]).exists()


def test_write_theory_summary(tmp_path, monkeypatch):
    import lod_guide.paper.theory_research as tr

    monkeypatch.setattr(tr, "PAPER_REVIEW", tmp_path / "review")
    path = write_theory_summary(force_verify=False)
    text = path.read_text(encoding="utf-8")
    assert "D1" in text and "P18" in text


@pytest.mark.slow
def test_run_theory_verification_live(tmp_path, monkeypatch):
    import lod_guide.paper.theory_research as tr

    audit_dir = tmp_path / "audit"
    monkeypatch.setattr(tr, "AUDIT_DIR", audit_dir)
    monkeypatch.setattr(tr, "THEORY_AUDIT_JSON", audit_dir / "theory_verification_latest.json")

    result = run_theory_verification(force=True)
    assert result["n_failed"] == 0
    assert result["n_total"] >= 27
    assert (audit_dir / "theory_verification_latest.json").exists()
