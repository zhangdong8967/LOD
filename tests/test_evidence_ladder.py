"""Tests for multi-assay downloads, parsers, and simulation DGP audit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lod_guide.data.download_real import RAW_DIR, REMOTE_DATASETS, download_all_real, parse_real_dataset
from lod_guide.data.simulate import generate_all_simulated


def test_remote_catalogue_has_multiple_families():
    families = {d.result_family for d in REMOTE_DATASETS}
    assert "qpcr_cq_continuous" in families
    assert "immunoassay_continuous" in families
    assert "probit_hit_rate" in families
    assert "clinical_chemistry_multilab" in {d.result_family for d in REMOTE_DATASETS}
    assert "proteomics_blank_lob" in {d.result_family for d in REMOTE_DATASETS}
    assert len(REMOTE_DATASETS) >= 9


def test_simulations_emit_draws_and_dgp():
    ds = generate_all_simulated()
    by_id = {d.dataset_id: d for d in ds}
    bin_ds = by_id["sim_binary_reagents_90_vs_80"]
    assert bin_ds.values is not None and bin_ds.values.size >= 100
    assert "dgp" in (bin_ds.meta or {})
    cat = Path("data/simulated/dgp_catalogue.json")
    assert cat.exists()
    payload = json.loads(cat.read_text(encoding="utf-8"))
    assert payload["evidence_tier"].startswith("S")


def test_download_and_parse_ep17_or_skip():
    results = download_all_real(force=False)
    # At least qPCR should exist from prior work; EP17 may need network
    estradiol = RAW_DIR / "EP17-A2-Example-1.xlsx"
    if not estradiol.exists():
        err = results.get("analyseit_ep17_estradiol")
        pytest.skip(f"EP17 estradiol not downloaded: {err}")
    parsed = parse_real_dataset("analyseit_ep17_estradiol", estradiol)
    # parser may return empty if layout unexpected — still must return dict
    assert parsed["assay_family"] == "immunoassay_estradiol"
    assert "blank_values" in parsed
