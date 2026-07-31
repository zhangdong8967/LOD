"""
Tier-A meta-analysis: one gate summary per public primary empirical deposit.

Produces Table 7 (manuscript primary empirical table). Tier C/S are excluded.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from lod_guide.data.download_real import RAW_DIR, REMOTE_DATASETS, download_dataset, parse_real_dataset
from lod_guide.pipeline import run_guidance
from lod_guide.research.precision_profile import PoolPrecision, evaluate_precision_profile
from lod_guide.s0_goal import Goal
from lod_guide.s2_diagnostics import run_diagnostics
from lod_guide.s5_sample_size import sample_size_two_proportions

OUT = Path(__file__).resolve().parents[3] / "data" / "research"
PAPER = Path(__file__).resolve().parents[3] / "paper_artifacts"


def _safe_guidance_continuous(values: list[float], low: list[float] | None = None) -> dict:
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if v.size < 5:
        return {"error": "insufficient_n", "n": int(v.size)}
    diag = run_diagnostics(v)
    low_a = np.asarray(low, dtype=float) if low else None
    if low_a is not None:
        low_a = low_a[np.isfinite(low_a)]
    guide = run_guidance(
        goal=Goal.G1_VERIFY_LOD,
        result_type="continuous",
        values=v,
        low_level=low_a if low_a is not None and low_a.size else None,
        use_case="ldt_lod_establishment",
        run_sensitivity=False,
    )
    return {
        "n_blank": int(v.size),
        "parametric_candidate": bool(diag.parametric_candidate),
        "skewness": float(diag.skewness) if diag.skewness is not None else None,
        "model_path": guide.model_path.value,
        "guidance_n": guide.sample_size.n_per_arm,
        "folklore_n": 20,
        "n_ratio_vs_folklore": (guide.sample_size.n_per_arm / 20.0) if guide.sample_size.n_per_arm else None,
    }


def _precision_summary(rows: list[dict], *, tier: str = "A") -> dict:
    pools = []
    for i, r in enumerate(rows):
        mean = float(r.get("mean") if r.get("mean") is not None else r.get("mean_DPM"))
        sd = float(r.get("sd") if r.get("sd") is not None else r.get("sd_DPM", float("nan")))
        cv = r.get("cv_pct")
        if cv is None or not np.isfinite(float(cv)):
            cv = 100.0 * sd / mean if mean else float("nan")
        else:
            cv = float(cv)
        pools.append(PoolPrecision(str(r.get("sample_name") or i), int(r.get("n") or 3), mean, sd, cv, "meta"))
    res = evaluate_precision_profile(pools, target_cv_pct=20.0, evidence_tier=tier)
    return {
        "n_pools": len(pools),
        "loq_at_cv20": res.loq_estimate,
        "loq_method": res.loq_method,
        "cv_min": min((p.cv_pct for p in pools if np.isfinite(p.cv_pct)), default=None),
        "cv_max": max((p.cv_pct for p in pools if np.isfinite(p.cv_pct)), default=None),
    }


def _summarize_dataset(dataset_id: str) -> dict:
    meta = next(d for d in REMOTE_DATASETS if d.dataset_id == dataset_id)
    assert meta.evidence_tier == "A"
    path = download_dataset(meta)
    parsed = parse_real_dataset(dataset_id, path)
    row = {
        "dataset_id": dataset_id,
        "evidence_tier": "A",
        "result_family": meta.result_family,
        "citation": meta.citation,
        "n_rows": parsed.get("n_rows"),
        "assay_family": parsed.get("assay_family"),
        "allowed_claim": "primary_empirical_illustration",
        "parametric_candidate": None,
        "model_path": None,
        "guidance_n": None,
        "folklore_n": 20,
        "n_ratio_vs_folklore": None,
        "loq_at_cv20": None,
        "notes": parsed.get("evidence_note", ""),
    }

    # continuous gate when blank-like values exist
    blanks = parsed.get("blank_values") or []
    lows = parsed.get("low_level_values") or []
    if len(blanks) >= 5:
        g = _safe_guidance_continuous(blanks, lows[: min(len(lows), 40)] if lows else None)
        if "error" not in g:
            row.update(
                {
                    "parametric_candidate": g["parametric_candidate"],
                    "model_path": g["model_path"],
                    "guidance_n": g["guidance_n"],
                    "n_ratio_vs_folklore": g["n_ratio_vs_folklore"],
                }
            )

    # precision profile when pool rows or levels exist
    if parsed.get("pool_rows"):
        ps = _precision_summary(
            [
                {
                    "sample_name": r["sample_name"],
                    "mean": r["mean"],
                    "sd": r["sd"],
                    "cv_pct": r["cv_pct"],
                    "n": 3,
                }
                for r in parsed["pool_rows"]
            ]
        )
        row["loq_at_cv20"] = ps["loq_at_cv20"]
        row["notes"] = (row["notes"] + f"; LoQ@CV20≈{ps['loq_at_cv20']}").strip("; ")
    elif parsed.get("by_concentration"):
        ps = _precision_summary(
            [
                {
                    "sample_name": f"c={r['concentration_ng']}",
                    "mean": r["mean_DPM"],
                    "sd": r["sd_DPM"],
                    "cv_pct": r["cv_pct"],
                    "n": r["n"],
                }
                for r in parsed["by_concentration"]
            ]
        )
        row["loq_at_cv20"] = ps["loq_at_cv20"]
    elif parsed.get("levels"):
        # for multilab chemistry, summarize creatinine CV across labs (precision, not LoQ)
        if dataset_id == "mendeley_carobene_lombardy_eqa":
            crea = [lev for lev in parsed["levels"] if lev.get("analyte") == "Creatinine" and lev.get("n", 0) >= 2]
            cvs = [float(lev["cv_pct"]) for lev in crea if lev.get("cv_pct") == lev.get("cv_pct")]
            row["guidance_n"] = row["guidance_n"] or int(parsed.get("n_labs") or 10)
            row["n_ratio_vs_folklore"] = None
            row["notes"] = (
                f"n_labs={parsed.get('n_labs')}; creatinine within-lab CV% "
                f"median={float(np.median(cvs)):.2f} (n_cells={len(cvs)}); "
                "multi-lab precision/DE — not blank-LoB"
            )
            # still run precision engine on pool means for Creatinine at one lab if available
            one_lab = sorted({lev["lab"] for lev in crea})[:1]
            if one_lab:
                ps = _precision_summary(
                    [
                        {
                            "sample_name": lev["material"],
                            "mean": lev["mean"],
                            "sd": lev["sd"],
                            "cv_pct": lev["cv_pct"],
                            "n": lev["n"],
                        }
                        for lev in crea
                        if lev["lab"] == one_lab[0]
                    ]
                )
                row["loq_at_cv20"] = ps["loq_at_cv20"]
        elif dataset_id == "bioc_msstats_lobd_cptac":
            row["notes"] = (
                f"n_peptides={parsed.get('n_peptides')}; focus={parsed.get('focus_peptide')}; "
                "proteomics blank–LoB (Concentration=0) — not clinical chemistry analyzer"
            )
        else:
            ps = _precision_summary(
                [
                    {
                        "sample_name": lev["level"],
                        "mean": lev["mean"],
                        "sd": lev["sd"],
                        "cv_pct": lev["cv_pct"],
                        "n": lev["n"],
                    }
                    for lev in parsed["levels"]
                ]
            )
            row["loq_at_cv20"] = ps["loq_at_cv20"]
    # hit-rate / probit / qPCR: primary LoD planning = G2 reference discrimination n*
    if "probit" in meta.result_family or "qpcr" in meta.result_family:
        n_star = int(np.ceil(sample_size_two_proportions(0.90, 0.80)))
        row["guidance_n"] = n_star
        row["n_ratio_vs_folklore"] = n_star / 20.0
        row["notes"] = (row["notes"] + f"; LoD G2 ref n*(90vs80)={n_star}").strip("; ")

    return row


def run_tierA_meta_analysis() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    (PAPER / "tables").mkdir(parents=True, exist_ok=True)
    (PAPER / "tables" / "manuscript").mkdir(parents=True, exist_ok=True)

    tier_a_ids = [d.dataset_id for d in REMOTE_DATASETS if d.evidence_tier == "A"]
    rows = []
    for did in tier_a_ids:
        try:
            rows.append(_summarize_dataset(did))
        except Exception as exc:  # noqa: BLE001
            rows.append(
                {
                    "dataset_id": did,
                    "evidence_tier": "A",
                    "error": str(exc),
                    "allowed_claim": "primary_empirical_illustration",
                }
            )

    n_para = sum(1 for r in rows if r.get("parametric_candidate") is True)
    n_nonpara = sum(1 for r in rows if r.get("parametric_candidate") is False)
    n_loq = sum(1 for r in rows if r.get("loq_at_cv20") is not None)

    payload = {
        "study_id": "TIERA-META-v1",
        "n_datasets": len(rows),
        "parametric_candidate_true": n_para,
        "parametric_candidate_false": n_nonpara,
        "with_loq_profile": n_loq,
        "rows": rows,
        "claim_boundary": (
            "Table restricted to evidence tier A. Tier C demos and tier S simulations "
            "must not be pooled into these counts."
        ),
    }

    json_path = OUT / "tierA_meta_analysis.json"
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    fields = [
        "dataset_id",
        "evidence_tier",
        "result_family",
        "parametric_candidate",
        "model_path",
        "guidance_n",
        "folklore_n",
        "n_ratio_vs_folklore",
        "loq_at_cv20",
        "allowed_claim",
        "citation",
    ]
    raw_csv = PAPER / "tables" / "Table07_tierA_meta.csv"
    ms_csv = PAPER / "tables" / "manuscript" / "Table07_tierA_meta.csv"
    for dest in (raw_csv, ms_csv):
        with dest.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                out = {k: r.get(k) for k in fields}
                # manuscript-friendly names already; keep citation truncated
                if out.get("citation") and len(str(out["citation"])) > 120:
                    out["citation"] = str(out["citation"])[:117] + "..."
                w.writerow(out)

    payload["path"] = str(json_path)
    payload["table"] = str(raw_csv)
    payload["manuscript_table"] = str(ms_csv)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_tierA_meta_analysis(), indent=2, default=str)[:2500])
