"""
Proteomics blank–LoB case study: CPTAC / MSstatsLOBD calibration data.

Tier A public deposit with Concentration==0 blanks + spike grid (43 peptides).
Runs EP17-style parametric/nonparametric LoB on light peak areas after vignette
fragment summation. Does NOT reimplement nonlinear_quantlim; claim boundary is
proteomics, not routine clinical chemistry analyzer validation.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from lod_guide.data.download_real import REMOTE_DATASETS, download_dataset, parse_real_dataset
from lod_guide.research.ep17_estradiol import analyze_reagent
from lod_guide.s4_models import lob_nonparametric, lob_parametric_normal

OUT = Path(__file__).resolve().parents[3] / "data" / "research"
FOCUS = "LPPGLLANFTLLR"


def _peptide_lob_row(blank: list[float], low: list[float], *, peptide: str) -> dict:
    b = np.asarray(blank, dtype=float)
    low_a = np.asarray(low, dtype=float)
    if b.size < 3:
        return {"peptide": peptide, "error": "insufficient blank n", "n_blank": int(b.size)}
    lob_par = lob_parametric_normal(b)
    lob_np = lob_nonparametric(b, 95.0)
    low_mean = float(low_a.mean()) if low_a.size else None
    return {
        "peptide": peptide,
        "n_blank": int(b.size),
        "n_low": int(low_a.size),
        "blank_mean": float(b.mean()),
        "blank_sd": float(b.std(ddof=1)) if b.size > 1 else None,
        "lob_parametric": lob_par,
        "lob_nonparametric_p95": lob_np,
        "low_mean": low_mean,
        "low_above_lob_par": (low_mean > lob_par) if low_mean is not None else None,
        "low_above_lob_np": (low_mean > lob_np) if low_mean is not None else None,
    }


def run_msstats_lob_study() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    meta = next(d for d in REMOTE_DATASETS if d.dataset_id == "bioc_msstats_lobd_cptac")
    path = download_dataset(meta)
    parsed = parse_real_dataset(meta.dataset_id, path)

    focus_blank = np.asarray(parsed.get("blank_values") or [], dtype=float)
    focus_low = np.asarray(parsed.get("low_level_values") or [], dtype=float)
    focus_detail = analyze_reagent(focus_blank, focus_low, label=parsed.get("focus_peptide") or FOCUS)

    peptide_rows = []
    for pep in parsed.get("per_peptide") or []:
        peptide_rows.append(
            _peptide_lob_row(
                pep.get("blank_values") or [],
                pep.get("low_level_values") or [],
                peptide=pep["peptide"],
            )
        )
    ok_rows = [r for r in peptide_rows if "error" not in r]
    n_low_above_par = sum(1 for r in ok_rows if r.get("low_above_lob_par") is True)
    n_low_above_np = sum(1 for r in ok_rows if r.get("low_above_lob_np") is True)

    payload = {
        "study_id": "MSSTATS-CPTAC-LOB-v1",
        "evidence_tier": "A",
        "dataset_id": meta.dataset_id,
        "citation": meta.citation,
        "path": str(path),
        "n_peptides": parsed.get("n_peptides"),
        "focus_peptide": parsed.get("focus_peptide"),
        "focus_analysis": focus_detail,
        "peptide_lob_summary": {
            "n_peptides_analyzed": len(ok_rows),
            "frac_low_mean_above_lob_parametric": (n_low_above_par / len(ok_rows)) if ok_rows else None,
            "frac_low_mean_above_lob_nonparametric": (n_low_above_np / len(ok_rows)) if ok_rows else None,
            "median_lob_parametric": float(np.median([r["lob_parametric"] for r in ok_rows])) if ok_rows else None,
            "median_lob_nonparametric_p95": (
                float(np.median([r["lob_nonparametric_p95"] for r in ok_rows])) if ok_rows else None
            ),
        },
        "per_peptide": peptide_rows,
        "claim_boundary": (
            "Proteomics (CPTAC / MSstatsLOBD) blank–LoB case study with raw blank "
            "Concentration=0 replicates. Complements EP17 immunoassay continuous LoB "
            "(estradiol). Does not validate routine clinical chemistry analyzer blank–LoB "
            "for ALT/creatinine/electrolytes, and does not claim equivalence to "
            "MSstats nonlinear_quantlim LOD. Note: light peak-area blanks can exceed the "
            "lowest spike mean for some peptides (matrix/background); MSstats vignette "
            "uses heavy-normalized intensities for curve-based LOD — we report EP17-style "
            "blank LoB on light areas as a transparent continuous blank gate."
        ),
        "headline": {
            "focus_peptide": parsed.get("focus_peptide"),
            "n_blank_focus": focus_detail.get("n_blank"),
            "lob_parametric_focus": focus_detail.get("lob_parametric"),
            "lob_nonparametric_p95_focus": focus_detail.get("lob_nonparametric_p95"),
            "parametric_candidate_focus": (focus_detail.get("diagnostics") or {}).get("parametric_candidate"),
            "n_peptides": parsed.get("n_peptides"),
            "frac_low_above_lob_par": (n_low_above_par / len(ok_rows)) if ok_rows else None,
        },
    }
    out = OUT / "msstats_cptac_lob_analysis.json"
    out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["out_path"] = str(out)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_msstats_lob_study()["headline"], indent=2))
