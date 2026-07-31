"""Tests for new tier-A continuous/precision public datasets."""

from __future__ import annotations

from pathlib import Path

import pytest

from lod_guide.data.download_real import RAW_DIR, REMOTE_DATASETS, download_dataset, parse_real_dataset
from lod_guide.research.empirical_tierA_extension import run_empirical_tierA_extension
from lod_guide.research.evidence_stratified_report import build_evidence_stratified_report


def test_remote_catalogue_includes_new_tier_a():
    ids = {d.dataset_id for d in REMOTE_DATASETS}
    assert "zenodo_radioimmuno_precision" in ids
    assert "zenodo_radioimmuno_linearity" in ids
    assert "zenodo_rmn_qualification" in ids
    assert "mendeley_carobene_lombardy_eqa" in ids
    assert "bioc_msstats_lobd_cptac" in ids
    assert "zenodo_anion_ic_lod" in ids
    tiers = {d.dataset_id: d.evidence_tier for d in REMOTE_DATASETS}
    assert tiers["zenodo_radioimmuno_precision"] == "A"
    assert tiers["zenodo_rmn_qualification"] == "A"
    assert tiers["mendeley_carobene_lombardy_eqa"] == "A"
    assert tiers["bioc_msstats_lobd_cptac"] == "A"
    assert tiers["zenodo_anion_ic_lod"] == "B"
    assert tiers["analyseit_ep17_troponin_precision"] == "C"
    families = {d.result_family for d in REMOTE_DATASETS}
    assert "proteomics_blank_lob" in families


@pytest.mark.parametrize(
    "dataset_id",
    [
        "zenodo_radioimmuno_precision",
        "zenodo_radioimmuno_linearity",
        "zenodo_rmn_qualification",
        "mendeley_carobene_lombardy_eqa",
        "bioc_msstats_lobd_cptac",
        "zenodo_anion_ic_lod",
    ],
)
def test_parse_new_datasets(dataset_id):
    meta = next(d for d in REMOTE_DATASETS if d.dataset_id == dataset_id)
    path = RAW_DIR / meta.filename
    if not path.exists():
        try:
            path = download_dataset(meta)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(str(exc))
    parsed = parse_real_dataset(dataset_id, path)
    assert parsed.get("n_rows", 0) > 0
    assert "assay_family" in parsed


def test_carobene_multilab_structure():
    meta = next(d for d in REMOTE_DATASETS if d.dataset_id == "mendeley_carobene_lombardy_eqa")
    path = RAW_DIR / meta.filename
    if not path.exists():
        try:
            path = download_dataset(meta)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(str(exc))
    parsed = parse_real_dataset(meta.dataset_id, path)
    assert parsed.get("n_labs", 0) >= 8
    assert "Creatinine" in (parsed.get("analytes") or [])
    assert any(lev.get("analyte") == "Creatinine" for lev in parsed.get("levels") or [])


def test_cptac_msstats_blank_lob_structure():
    meta = next(d for d in REMOTE_DATASETS if d.dataset_id == "bioc_msstats_lobd_cptac")
    path = RAW_DIR / meta.filename
    if not path.exists():
        try:
            path = download_dataset(meta)
        except Exception as exc:  # noqa: BLE001
            pytest.skip(str(exc))
    parsed = parse_real_dataset(meta.dataset_id, path)
    assert parsed.get("n_peptides", 0) >= 40
    assert len(parsed.get("blank_values") or []) >= 5
    assert 0.0 in (parsed.get("concentrations") or [])
    assert "proteomics" in (parsed.get("assay_family") or "")


def test_empirical_extension_and_stratified_report():
    # require at least precision file
    if not (RAW_DIR / "Precision_radioimmuno.txt").exists():
        pytest.skip("precision file missing")
    emp = run_empirical_tierA_extension()
    assert len(emp["blocks"]) >= 2
    assert "claim_boundary" in emp
    assert any(b.get("dataset_id") == "bioc_msstats_lobd_cptac" for b in emp["blocks"])
    rep = build_evidence_stratified_report(download=False)
    assert rep["counts"]["A"] >= 8  # includes Carobene + CPTAC
    assert rep["counts"]["B"] >= 3  # cation + anion + radioimmuno summary
    assert Path(rep["report"]).exists()
    text = Path(rep["report"]).read_text(encoding="utf-8")
    assert "Tier A" in text and "Forbidden overclaims" in text
    assert "mendeley_carobene_lombardy_eqa" in text
    assert "bioc_msstats_lobd_cptac" in text
    assert "zenodo_anion_ic_lod" in text
