"""Tests for S5 multilevel LoD design integration (P15/P16 gate + minimax)."""

from __future__ import annotations

import numpy as np
import pytest

from lod_guide.pipeline import run_guidance
from lod_guide.s5_lod_design import LoDDesignBlockedError, recommend_multilevel_lod_design
from lod_guide.s0_goal import Goal
from lod_guide.s1_result_type import ResultType
from lod_guide.theory.lod_dose_response import default_synthetic_truth


def test_identifiable_design_returns_minimax():
    out = recommend_multilevel_lod_design(total_n=60, n_levels=5)
    assert not out.blocked
    assert out.identifiable
    assert out.recommended_design is not None
    assert out.recommended_design["pattern"] == "dense_near_lod"
    assert out.worst_case_se is not None
    assert out.improvement_worst_case_ratio is not None
    assert out.improvement_worst_case_ratio >= 1.0


def test_saturation_plateau_blocked():
    truth = default_synthetic_truth()
    lod = truth.lod()
    sat_conc = lod * np.array([1e-4, 2e-4, 5e-4, 1e-3, 2e-3])
    sat_n = np.full(5, 12.0)
    with pytest.raises(LoDDesignBlockedError) as exc:
        recommend_multilevel_lod_design(
            truth=truth,
            concentrations=sat_conc,
            n_per_level=sat_n,
            block_on_non_identifiable=True,
        )
    assert "P16" in str(exc.value) or "saturation" in str(exc.value).lower()


def test_pipeline_multilevel_lod_flag():
    out = run_guidance(
        goal=Goal.G1_VERIFY_LOD,
        result_type=ResultType.BINARY,
        p=0.95,
        p0=0.95,
        plan_multilevel_lod=True,
        run_sensitivity=False,
    )
    assert out.multilevel_lod_design is not None
    assert out.multilevel_lod_design.identifiable
    assert "multilevel_lod_design" in out.report.sample_size
