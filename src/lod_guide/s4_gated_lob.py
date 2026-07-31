"""
S4 extension — assumption-gated LoB estimation (unsplit vs sample-split).

Integrates theory/selective/sample_split.py into the S0–S7 pipeline.
"""

from __future__ import annotations

from enum import Enum

import numpy as np

from lod_guide.s4_models import LoBLoDEstimate, ModelPath, estimate_lob_lod, lod_from_lob_sd
from lod_guide.theory.gated_inference import gated_lob_from_sample
from lod_guide.theory.selective.sample_split import gated_lob_sample_split


class LoBEstimationMode(str, Enum):
    """How to estimate LoB when S2 diagnostics gate parametric paths."""

    STANDARD = "standard"  # legacy: model_path from S4, same sample for diag + LoB
    GATED_UNSPLIT = "gated_unsplit"  # S2 gate + LoB on full blank (selective risk)
    GATED_SAMPLE_SPLIT = "gated_sample_split"  # gate on B_g, LoB on B_l (P17 remedy)


def estimate_gated_lob(
    blank: np.ndarray,
    *,
    model_path: ModelPath,
    alpha: float = 0.05,
    beta: float = 0.05,
    mode: LoBEstimationMode | str = LoBEstimationMode.STANDARD,
    low_level: np.ndarray | None = None,
) -> LoBLoDEstimate:
    """
    Estimate LoB (and optional LoD) under the chosen gating mode.

    ``GATED_SAMPLE_SPLIT`` requires len(blank) ≥ 32 (12 gate + 20 holdout minimum).
    """
    mode = LoBEstimationMode(mode)
    blank = np.asarray(blank, dtype=float)

    if mode == LoBEstimationMode.STANDARD:
        return estimate_lob_lod(blank, low_level, path=model_path, alpha=alpha, beta=beta)

    if mode == LoBEstimationMode.GATED_UNSPLIT:
        gated = gated_lob_from_sample(blank, alpha=alpha)
        lod = None
        details: dict = {
            "lob_mode": mode.value,
            "gate_path": gated.path,
            "parametric_candidate": gated.parametric_candidate,
        }
        if low_level is not None and gated.lob_used is not None:
            sd_low = float(np.std(low_level, ddof=1))
            lod = lod_from_lob_sd(float(gated.lob_used), sd_low, beta=beta)
            details["sd_low"] = sd_low
        path = (
            ModelPath.PARAMETRIC_NORMAL
            if gated.path == "parametric"
            else ModelPath.NONPARAMETRIC_PERCENTILE
        )
        return LoBLoDEstimate(path, gated.lob_used, lod, details)

    # GATED_SAMPLE_SPLIT
    split = gated_lob_sample_split(blank, alpha=alpha)
    lod = None
    details = {
        "lob_mode": mode.value,
        "gate_path": split.path,
        "parametric_candidate": split.parametric_candidate,
        "n_gate": split.n_gate,
        "n_lob": split.n_lob,
        "alpha_lob": split.alpha_lob,
        "split_method": split.split_method,
    }
    if low_level is not None and split.lob_used is not None:
        sd_low = float(np.std(low_level, ddof=1))
        lod = lod_from_lob_sd(float(split.lob_used), sd_low, beta=beta)
        details["sd_low"] = sd_low
    path = (
        ModelPath.PARAMETRIC_NORMAL
        if split.path == "parametric"
        else ModelPath.NONPARAMETRIC_PERCENTILE
    )
    return LoBLoDEstimate(path, split.lob_used, lod, details)
