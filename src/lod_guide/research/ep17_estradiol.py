"""
Deep continuous-assay analysis: CLSI EP17-A2 Appendix A estradiol (Analyse-it).

Tier A public worked example: blank + low-level replicates, two reagents.
Runs S2 diagnostics, parametric vs nonparametric LoB, bootstrap CIs, LoD proxy.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from lod_guide.data.download_real import REMOTE_DATASETS, download_dataset, parse_real_dataset
from lod_guide.pipeline import run_guidance
from lod_guide.research.bootstrap_ci import bootstrap_parametric_lob, bootstrap_quantile_lob
from lod_guide.s0_goal import Goal
from lod_guide.s2_diagnostics import run_diagnostics
from lod_guide.s3_correction import attempt_correction
from lod_guide.s4_models import estimate_lob_lod, lob_nonparametric, lob_parametric_normal, lod_from_lob_sd, select_model_path

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def analyze_reagent(blank: np.ndarray, low: np.ndarray, *, label: str) -> dict:
    blank = np.asarray(blank, dtype=float)
    low = np.asarray(low, dtype=float)
    diag = run_diagnostics(blank)
    corr = attempt_correction(blank)
    path = select_model_path(
        parametric_ok=corr.parametric_ok,
        result_type="continuous",
        correction_method=corr.method.value if hasattr(corr.method, "value") else str(corr.method),
    )
    data = corr.transformed if corr.transformed is not None else blank
    est = estimate_lob_lod(data, low if low.size else None, path=path)

    lob_par = lob_parametric_normal(blank)
    lob_np = lob_nonparametric(blank, 95.0)
    sd_low = float(np.std(low, ddof=1)) if low.size > 1 else float("nan")
    lod_par = lod_from_lob_sd(lob_par, sd_low) if np.isfinite(sd_low) else None

    boot_np = bootstrap_quantile_lob(blank, percentile=95.0, n_boot=1500, seed=17)
    boot_par = bootstrap_parametric_lob(blank, n_boot=1500, seed=19)

    guide = run_guidance(
        goal=Goal.E1_VERIFY_LOD,
        result_type="continuous",
        values=blank,
        low_level=low if low.size else None,
        use_case="ldt_lod_establishment",
        p0=0.95,
        cluster_size=max(1, blank.size // 6),
        run_sensitivity=False,
    )

    return {
        "label": label,
        "n_blank": int(blank.size),
        "n_low": int(low.size),
        "blank_mean": float(np.mean(blank)),
        "blank_sd": float(np.std(blank, ddof=1)),
        "low_mean": float(np.mean(low)) if low.size else None,
        "low_sd": sd_low if low.size else None,
        "diagnostics": {
            "parametric_candidate": diag.parametric_candidate,
            "shape_ok": diag.shape_ok,
            "censoring_ok": diag.censoring_ok,
            "heterogeneity_ok": diag.heterogeneity_ok,
            "skewness": diag.skewness,
            "messages": diag.messages,
        },
        "correction": {
            "method": corr.method.value if hasattr(corr.method, "value") else str(corr.method),
            "parametric_ok": corr.parametric_ok,
        },
        "model_path": path.value,
        "lob_parametric": lob_par,
        "lob_nonparametric_p95": lob_np,
        "lod_parametric_proxy": lod_par,
        "pipeline_lob": guide.report.lob,
        "pipeline_lod": guide.report.lod,
        "bootstrap_lob_nonparametric": {
            "estimate": boot_np.estimate,
            "ci95": [boot_np.low, boot_np.high],
        },
        "bootstrap_lob_parametric": {
            "estimate": boot_par.estimate,
            "ci95": [boot_par.low, boot_par.high],
        },
        "guidance_n": guide.sample_size.n_per_arm,
        "guidance_warnings": guide.report.warnings[:8],
    }


def run_ep17_estradiol_study() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    meta = next(d for d in REMOTE_DATASETS if d.dataset_id == "analyseit_ep17_estradiol")
    path = download_dataset(meta, force=False)
    parsed = parse_real_dataset("analyseit_ep17_estradiol", path)

    reagents = []
    for sheet, block in (parsed.get("reagents") or {}).items():
        blank = np.asarray(block.get("blank_values") or [], dtype=float)
        low = np.asarray(block.get("low_level_values") or [], dtype=float)
        if blank.size == 0:
            continue
        reagents.append(analyze_reagent(blank, low, label=sheet))

    # primary combined if reagents empty — use top-level blanks
    if not reagents and parsed.get("blank_values"):
        reagents.append(
            analyze_reagent(
                np.asarray(parsed["blank_values"], dtype=float),
                np.asarray(parsed.get("low_level_values") or [], dtype=float),
                label=parsed.get("primary_sheet") or "primary",
            )
        )

    payload = {
        "study_id": "EP17-ESTRADIOL-v1",
        "evidence_tier": "A",
        "citation": meta.citation,
        "path": str(path),
        "n_reagents": len(reagents),
        "reagents": reagents,
        "headline": {
            "parametric_ok_any": any(r["correction"]["parametric_ok"] for r in reagents),
            "lob_par_range": (
                [min(r["lob_parametric"] for r in reagents), max(r["lob_parametric"] for r in reagents)]
                if reagents
                else None
            ),
            "lob_np_range": (
                [
                    min(r["lob_nonparametric_p95"] for r in reagents),
                    max(r["lob_nonparametric_p95"] for r in reagents),
                ]
                if reagents
                else None
            ),
        },
        "note": (
            "CLSI EP17-A2 Appendix A worked example redistributed by Analyse-it; "
            "cite CLSI for republication of numbers."
        ),
    }
    out = OUT / "ep17_estradiol_analysis.json"
    out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["out_path"] = str(out)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_ep17_estradiol_study()["headline"], indent=2))
