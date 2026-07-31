"""Tests for precision-profile LoQ, estradiol analysis helpers, Type I grid."""

from __future__ import annotations

import numpy as np

from lod_guide.research.precision_profile import (
    PoolPrecision,
    evaluate_precision_profile,
    loq_from_profile,
    pool_stats,
)
from lod_guide.research.type1_calibration import empirical_type1


def test_pool_stats_cv():
    x = np.array([10.0, 10.0, 12.0, 8.0])
    p = pool_stats(x, "P1")
    assert p.n == 4
    assert abs(p.mean - 10.0) < 1e-12
    assert p.cv_pct > 0


def test_loq_interpolation():
    pools = [
        PoolPrecision("a", 20, 0.05, 0.02, 40.0),
        PoolPrecision("b", 20, 0.10, 0.015, 15.0),
        PoolPrecision("c", 20, 0.20, 0.02, 10.0),
    ]
    loq, method = loq_from_profile(pools, target_cv_pct=20.0)
    assert loq is not None
    assert 0.05 < loq < 0.10
    assert "interpolat" in method


def test_evaluate_synthetic_profile():
    pools = [
        PoolPrecision("p1", 30, 0.05, 0.025, 50.0, "R1"),
        PoolPrecision("p2", 30, 0.08, 0.024, 30.0, "R1"),
        PoolPrecision("p3", 30, 0.12, 0.018, 15.0, "R1"),
        PoolPrecision("p4", 30, 0.25, 0.025, 10.0, "R1"),
    ]
    res = evaluate_precision_profile(pools, target_cv_pct=20.0, evidence_tier="S")
    assert res.loq_estimate is not None
    assert res.fit.get("ok") is True


def test_type1_fisher_conservative_at_n20():
    row = empirical_type1(n=20, p_null=0.5, n_sims=2000, seed=0, include_boschloo=False)
    # Fisher typically <= alpha + Monte Carlo noise
    assert row["type1_fisher"] <= 0.08
    assert 0.02 <= row["type1_pooled_z"] <= 0.09
