"""
Risk-calibrated S2 thresholds.

Search a 1-D skew-fail cutoff that minimizes empirical decision loss on a
calibration suite (normal + exponential blanks), subject to keeping Type-I-like
false nonparametric switches on Gaussian blanks below a budget.

Defaults in the package remain frozen v0.1; this module proposes a calibrated
candidate and documents the gap.
"""

from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

from lod_guide.data.simulate import sim_normal_blanks, sim_skewed_hetero_blanks
from lod_guide.research.decision_risk import RiskWeights, loss
from lod_guide.s2_diagnostics import DEFAULT_THRESHOLDS, run_diagnostics
from lod_guide.s4_models import lob_nonparametric, lob_parametric_normal

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def _path_loss_for_blank(x: np.ndarray, *, parametric_candidate: bool, weights: RiskWeights) -> float:
    """Proxy loss: parametric vs NP path scored by holdout exceedance + mismatch."""
    n = x.size
    mid = n // 2
    train, test = x[:mid], x[mid:]
    if test.size < 5:
        test = x
        train = x
    if parametric_candidate:
        lob = lob_parametric_normal(train, 0.05)
        type_i = float(np.mean(test > lob))
        mismatch = min(1.0, abs(type_i - 0.05) / 0.05)
        return loss(type_i=type_i, beta=0.0, mismatch=mismatch, weights=weights)
    lob = lob_nonparametric(train, 95.0)
    type_i = float(np.mean(test > lob))
    return loss(type_i=type_i, beta=0.0, mismatch=0.0, weights=weights)


def run_s2_risk_calibrated_thresholds() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    w = RiskWeights()
    normal = np.asarray(sim_normal_blanks(0).values, dtype=float)
    skew = np.asarray(sim_skewed_hetero_blanks(1).values, dtype=float)

    grid = np.linspace(0.5, 2.0, 16)
    rows = []
    for skew_fail in grid:
        thr = replace(
            DEFAULT_THRESHOLDS,
            abs_skew_fail=float(skew_fail),
            abs_skew_warn=float(min(DEFAULT_THRESHOLDS.abs_skew_warn, skew_fail * 0.5)),
        )
        d_n = run_diagnostics(normal, thresholds=thr)
        d_s = run_diagnostics(skew, thresholds=thr)
        # False NP switch on normal: parametric_candidate should be True ideally
        false_np = 0.0 if d_n.parametric_candidate else 1.0
        # Missed gate on skew: should be False ideally
        missed = 0.0 if (not d_s.parametric_candidate) else 1.0
        L_n = _path_loss_for_blank(normal, parametric_candidate=d_n.parametric_candidate, weights=w)
        L_s = _path_loss_for_blank(skew, parametric_candidate=d_s.parametric_candidate, weights=w)
        L = L_n + L_s + 0.5 * false_np + 0.5 * missed
        rows.append(
            {
                "abs_skew_fail": float(skew_fail),
                "normal_parametric_candidate": d_n.parametric_candidate,
                "skew_parametric_candidate": d_s.parametric_candidate,
                "loss_total": float(L),
                "loss_normal": float(L_n),
                "loss_skew": float(L_s),
            }
        )

    best = min(rows, key=lambda r: r["loss_total"])
    default_row = min(rows, key=lambda r: abs(r["abs_skew_fail"] - DEFAULT_THRESHOLDS.abs_skew_fail))

    payload = {
        "study_id": "S2-RISK-CALIBRATED-THRESHOLDS-v1",
        "default_thresholds": asdict(DEFAULT_THRESHOLDS),
        "calibration_grid": rows,
        "best": best,
        "default_row": default_row,
        "headline": {
            "default_skew_fail": DEFAULT_THRESHOLDS.abs_skew_fail,
            "calibrated_skew_fail": best["abs_skew_fail"],
            "default_loss": default_row["loss_total"],
            "calibrated_loss": best["loss_total"],
            "improvement": default_row["loss_total"] - best["loss_total"],
        },
        "claim_boundary": (
            "Calibration is on a small simulation suite and a 1-D skew cutoff; "
            "package defaults stay frozen until a versioned threshold release. "
            "This study shows how defaults could be risk-tuned."
        ),
    }
    path = OUT / "s2_risk_calibrated_thresholds.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_s2_risk_calibrated_thresholds()["headline"], indent=2))
