"""Pipeline integration for sample-split LoB (S0–S7)."""

from __future__ import annotations

import numpy as np

from lod_guide import run_guidance
from lod_guide.s0_goal import Goal
from lod_guide.s4_gated_lob import LoBEstimationMode
from lod_guide.data.simulate import sim_skewed_hetero_blanks


def test_pipeline_sample_split_modes():
    ds = sim_skewed_hetero_blanks(seed=1)
    blank = np.asarray(ds.values, dtype=float)

    std = run_guidance(
        goal=Goal.G1_VERIFY_LOD,
        result_type="continuous",
        values=blank,
        lob_estimation_mode=LoBEstimationMode.STANDARD,
    )
    split = run_guidance(
        goal=Goal.G1_VERIFY_LOD,
        result_type="continuous",
        values=blank,
        lob_estimation_mode=LoBEstimationMode.GATED_SAMPLE_SPLIT,
    )

    assert std.lob_lod is not None
    assert split.lob_lod is not None
    assert split.lob_lod["details"]["lob_mode"] == "gated_sample_split"
    assert split.report.lob is not None


def test_estimate_gated_lob_modes():
    from lod_guide.s4_gated_lob import estimate_gated_lob
    from lod_guide.s4_models import ModelPath

    rng = np.random.default_rng(2)
    x = rng.gamma(4.0, 0.25, size=80)

    for mode in LoBEstimationMode:
        est = estimate_gated_lob(x, model_path=ModelPath.PARAMETRIC_NORMAL, mode=mode)
        assert est.lob is not None
        if mode != LoBEstimationMode.STANDARD:
            assert est.details.get("lob_mode") == mode.value
