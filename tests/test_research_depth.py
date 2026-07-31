"""Tests for deep research modules."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from lod_guide.data.download_real import RAW_DIR
from lod_guide.research.bootstrap_ci import bootstrap_quantile_lob
from lod_guide.research.deep_qpcr import hit_rates_by_target
from lod_guide.research.lob_coverage import population_exceedance, run_lob_coverage
from lod_guide.research.operating_characteristics import run_oc_cell


def test_oc_typeI_near_alpha():
    row = run_oc_cell(0.9, 0.9, 50, n_sims=3000, seed=0, setting="t")
    assert abs(row.reject_rate - 0.05) < 0.03


def test_oc_power_n20_low():
    row = run_oc_cell(0.9, 0.8, 20, n_sims=4000, seed=1, setting="p")
    assert row.reject_rate < 0.30


def test_lob_coverage_normal_parametric_near_alpha():
    r = run_lob_coverage(n_mc=400, n_blank=80, seed=0)
    assert abs(r["normal"]["parametric_mean_exceedance"] - 0.05) < 0.03
    # exponential parametric should be clearly off
    assert r["exponential"]["parametric_abs_bias_vs_alpha"] > 0.02


def test_population_exceedance_exponential():
    assert abs(population_exceedance(-np.log(0.05), "exponential") - 0.05) < 1e-12


def test_bootstrap_lob_interval_ordered():
    rng = np.random.default_rng(0)
    x = rng.normal(size=80)
    ci = bootstrap_quantile_lob(x, n_boot=500, seed=1)
    assert ci.low <= ci.estimate <= ci.high


def test_qpcr_hit_rates_if_present():
    path = RAW_DIR / "zenodo_mus_wt_lod_loq.csv"
    if not path.exists():
        return
    rows = hit_rates_by_target(path, "zenodo_mus_wt_qpcr")
    assert len(rows) >= 3
    assert any(r.sq == 0.0 or r.n > 0 for r in rows)
