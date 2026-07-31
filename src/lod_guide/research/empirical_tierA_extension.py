"""
Empirical extension: non-demo continuous/precision public datasets (tier A).

1) Zenodo radioimmuno Precision + Linearity (Anal. Chem. / 12664367)
2) Zenodo RMN qualification replicates (17108929)

Runs precision-profile / diagnostics and writes stratified findings.
Does NOT re-label tier C/S as empirical validation.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from lod_guide.data.download_real import REMOTE_DATASETS, download_dataset, parse_real_dataset
from lod_guide.pipeline import run_guidance
from lod_guide.research.precision_profile import PoolPrecision, evaluate_precision_profile
from lod_guide.s0_goal import Goal
from lod_guide.s2_diagnostics import run_diagnostics
from lod_guide.s4_models import lob_nonparametric, lob_parametric_normal

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def _analyze_precision_rows(rows: list[dict], *, label: str, tier: str) -> dict:
    pools = [
        PoolPrecision(
            pool_id=str(r.get("sample_name") or r.get("level") or i),
            n=int(r.get("n") or 3),
            mean=float(r["mean"] if "mean" in r else r.get("mean_DPM") or r.get("mean")),
            sd=float(r["sd"] if "sd" in r else r.get("sd_DPM") or float("nan")),
            cv_pct=float(r.get("cv_pct") if r.get("cv_pct") is not None else float("nan")),
            stratum=label,
        )
        for i, r in enumerate(rows)
        if (r.get("mean") is not None or r.get("mean_DPM") is not None)
    ]
    # fill cv if missing
    fixed = []
    for p in pools:
        cv = p.cv_pct
        if not np.isfinite(cv) and p.mean and np.isfinite(p.sd):
            cv = 100.0 * p.sd / p.mean
        fixed.append(PoolPrecision(p.pool_id, p.n, p.mean, p.sd, cv, p.stratum))
    res = evaluate_precision_profile(fixed, target_cv_pct=20.0, evidence_tier=tier)
    return {
        "label": label,
        "evidence_tier": tier,
        "n_pools": len(fixed),
        "loq_at_cv20": res.loq_estimate,
        "loq_method": res.loq_method,
        "fit": res.fit,
        "n_design": res.n_design_at_loq_adjacent,
        "cv_range": (
            [min(p.cv_pct for p in fixed if np.isfinite(p.cv_pct)), max(p.cv_pct for p in fixed if np.isfinite(p.cv_pct))]
            if any(np.isfinite(p.cv_pct) for p in fixed)
            else None
        ),
    }


def _continuous_blank_low(blank: list[float], low: list[float], *, label: str, tier: str) -> dict:
    b = np.asarray(blank, dtype=float)
    low_a = np.asarray(low, dtype=float) if low else np.array([])
    if b.size < 5:
        return {"label": label, "evidence_tier": tier, "error": "insufficient blank n"}
    diag = run_diagnostics(b)
    guide = run_guidance(
        goal=Goal.G1_VERIFY_LOD,
        result_type="continuous",
        values=b,
        low_level=low_a if low_a.size else None,
        use_case="ldt_lod_establishment",
        run_sensitivity=False,
    )
    return {
        "label": label,
        "evidence_tier": tier,
        "n_blank": int(b.size),
        "n_low": int(low_a.size),
        "parametric_candidate": diag.parametric_candidate,
        "skewness": diag.skewness,
        "lob_parametric": lob_parametric_normal(b),
        "lob_nonparametric_p95": lob_nonparametric(b, 95.0),
        "model_path": guide.model_path.value,
        "guidance_n": guide.sample_size.n_per_arm,
        "supports_assumption_gate": (not diag.parametric_candidate) or diag.parametric_candidate,
    }


def run_empirical_tierA_extension() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    by_id = {d.dataset_id: d for d in REMOTE_DATASETS}
    blocks = []

    # 1) radioimmuno precision
    meta = by_id["zenodo_radioimmuno_precision"]
    path = download_dataset(meta)
    parsed = parse_real_dataset(meta.dataset_id, path)
    rows = []
    for r in parsed.get("pool_rows") or []:
        rows.append({"sample_name": r["sample_name"], "mean": r["mean"], "sd": r["sd"], "cv_pct": r["cv_pct"], "n": 3})
    blocks.append(
        {
            "dataset_id": meta.dataset_id,
            "citation": meta.citation,
            "evidence_tier": meta.evidence_tier,
            "analysis": _analyze_precision_rows(rows, label="radioimmuno_precision", tier="A"),
        }
    )

    # 2) radioimmuno linearity → precision by concentration + continuous values
    meta = by_id["zenodo_radioimmuno_linearity"]
    path = download_dataset(meta)
    parsed = parse_real_dataset(meta.dataset_id, path)
    lin_rows = []
    for r in parsed.get("by_concentration") or []:
        lin_rows.append(
            {
                "sample_name": f"ng={r['concentration_ng']}",
                "mean": r["mean_DPM"],
                "sd": r["sd_DPM"],
                "cv_pct": r["cv_pct"],
                "n": r["n"],
            }
        )
    blocks.append(
        {
            "dataset_id": meta.dataset_id,
            "citation": meta.citation,
            "evidence_tier": meta.evidence_tier,
            "analysis_precision": _analyze_precision_rows(lin_rows, label="radioimmuno_linearity", tier="A"),
            "analysis_continuous": _continuous_blank_low(
                parsed.get("blank_values") or [],
                parsed.get("low_level_values") or [],
                label="radioimmuno_linearity_DPM",
                tier="A",
            ),
        }
    )

    # 3) RMN qualification
    meta = by_id["zenodo_rmn_qualification"]
    path = download_dataset(meta)
    parsed = parse_real_dataset(meta.dataset_id, path)
    rmn_rows = []
    for lev in parsed.get("levels") or []:
        rmn_rows.append(
            {
                "sample_name": lev["level"],
                "mean": lev["mean"],
                "sd": lev["sd"],
                "cv_pct": lev["cv_pct"],
                "n": lev["n"],
            }
        )
    blocks.append(
        {
            "dataset_id": meta.dataset_id,
            "citation": meta.citation,
            "evidence_tier": meta.evidence_tier,
            "analysis_precision": _analyze_precision_rows(rmn_rows, label="rmn_dilution_levels", tier="A"),
            "analysis_continuous": _continuous_blank_low(
                parsed.get("blank_values") or [],
                parsed.get("low_level_values") or [],
                label="rmn_id50",
                tier="A",
            ),
        }
    )

    # 4) Carobene Lombardy EQA — routine clinical chemistry multi-lab
    meta = by_id["mendeley_carobene_lombardy_eqa"]
    path = download_dataset(meta)
    parsed = parse_real_dataset(meta.dataset_id, path)
    crea_rows = [
        {
            "sample_name": lev["level"],
            "mean": lev["mean"],
            "sd": lev["sd"],
            "cv_pct": lev["cv_pct"],
            "n": lev["n"],
        }
        for lev in (parsed.get("levels") or [])
        if lev.get("analyte") == "Creatinine" and lev.get("n", 0) >= 2
    ]
    blocks.append(
        {
            "dataset_id": meta.dataset_id,
            "citation": meta.citation,
            "evidence_tier": meta.evidence_tier,
            "n_labs": parsed.get("n_labs"),
            "analysis_precision": _analyze_precision_rows(
                crea_rows[:40], label="carobene_creatinine_multilab", tier="A"
            ),
            "claim_note": (
                "Routine chemistry multi-lab precision/DE evidence — not blank-LoB EP17 design."
            ),
        }
    )

    # 5) CPTAC / MSstatsLOBD — proteomics blank–LoB
    meta = by_id["bioc_msstats_lobd_cptac"]
    path = download_dataset(meta)
    parsed = parse_real_dataset(meta.dataset_id, path)
    blocks.append(
        {
            "dataset_id": meta.dataset_id,
            "citation": meta.citation,
            "evidence_tier": meta.evidence_tier,
            "n_peptides": parsed.get("n_peptides"),
            "focus_peptide": parsed.get("focus_peptide"),
            "analysis_continuous": _continuous_blank_low(
                parsed.get("blank_values") or [],
                parsed.get("low_level_values") or [],
                label="cptac_msstats_focus_peptide_blank",
                tier="A",
            ),
            "claim_note": (
                "Proteomics blank–LoB (Concentration=0 light areas) — not clinical chemistry analyzer LoB."
            ),
        }
    )

    payload = {
        "study_id": "EMPIRICAL-TIERA-EXT-v1",
        "purpose": (
            "Add non-demo, citable continuous/precision raw public datasets "
            "and analyze them under the lod_guide gate — stratified as tier A."
        ),
        "blocks": blocks,
        "claim_boundary": (
            "These results illustrate assumption-gated continuous/precision analysis on "
            "independent public deposits, including routine clinical chemistry multi-lab "
            "replicates (Carobene) and proteomics blank–LoB (CPTAC/MSstatsLOBD). "
            "They do not imply blank-LoB validation across all clinical chemistry panels. "
            "Tier C (troponin demo) and tier S (simulations) remain non-substitutes for tier A."
        ),
    }
    out = OUT / "empirical_tierA_extension.json"
    payload["path"] = str(out)
    out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return payload


if __name__ == "__main__":
    print(json.dumps(run_empirical_tierA_extension(), indent=2, default=str)[:2500])
