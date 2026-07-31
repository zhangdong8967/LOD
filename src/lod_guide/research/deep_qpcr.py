"""
Deep analysis of public qPCR LoD/LoQ datasets (Zenodo 12609243).

Produces hit-rate tables, logistic LoD (concentration at target p), and
guidance recommendations — transparent CSV/JSON for statisticians.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.special import expit
from scipy.stats import linregress

from lod_guide.data.download_real import RAW_DIR, download_all_real, load_zenodo_qpcr_cq
from lod_guide.pipeline import run_guidance
from lod_guide.s0_goal import Goal
from lod_guide.theory.exact import clopper_pearson_interval, wilson_interval

OUT_DIR = Path(__file__).resolve().parents[3] / "data" / "research"


@dataclass
class HitRateRow:
    dataset_id: str
    target: str
    sq: float
    n: int
    hits: int
    rate: float
    wilson_low: float
    wilson_high: float
    cp_low: float
    cp_high: float


def _parse_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


def hit_rates_by_target(path: Path, dataset_id: str) -> list[HitRateRow]:
    rows = _parse_rows(path)
    # key: (target, sq) -> list of hit 0/1
    buckets: dict[tuple[str, float], list[int]] = {}
    for r in rows:
        sample = (r.get("Sample") or "").strip()
        target = (r.get("Target") or "unknown").strip()
        sq_raw = (r.get("SQ") or "").strip()
        cq_raw = (r.get("Cq") or "").strip()
        if sample.upper().startswith("NTC") or sq_raw in {"", "Undetermined", "N/A", "NA"}:
            # NTC: sq := 0
            sq = 0.0
        else:
            try:
                sq = float(sq_raw)
            except ValueError:
                continue
        hit = 1
        if cq_raw in {"", "N/A", "NA", "Undetermined", "undetermined"}:
            hit = 0
        buckets.setdefault((target, sq), []).append(hit)

    out: list[HitRateRow] = []
    for (target, sq), hits_list in sorted(buckets.items(), key=lambda x: (x[0][0], x[0][1])):
        n = len(hits_list)
        h = int(sum(hits_list))
        rate = h / n if n else float("nan")
        w = wilson_interval(h, n)
        cp = clopper_pearson_interval(h, n)
        out.append(
            HitRateRow(
                dataset_id=dataset_id,
                target=target,
                sq=sq,
                n=n,
                hits=h,
                rate=rate,
                wilson_low=w[0],
                wilson_high=w[1],
                cp_low=cp[0],
                cp_high=cp[1],
            )
        )
    return out


def fit_logistic_lod(
    sq: np.ndarray,
    rate: np.ndarray,
    n: np.ndarray,
    target_p: float = 0.95,
) -> dict:
    """
    Weighted logit regression on log10(SQ) for SQ>0.
    Model: logit(p) = a + b * log10(SQ).
    LoD = 10 ** ((logit(target_p) - a) / b).
    """
    mask = (sq > 0) & np.isfinite(rate) & (n > 0)
    x = np.log10(sq[mask])
    p = np.clip(rate[mask], 1e-6, 1 - 1e-6)
    w = n[mask].astype(float)
    # linearize: logit(p) ~ a + b x
    y = np.log(p / (1 - p))
    # weighted least squares via sqrt weights
    sw = np.sqrt(w)
    slope, intercept, r_value, p_value, stderr = linregress(x * sw, y * sw)
    # linregress on weighted coords is approximate; refine with unweighted on logit scale
    slope, intercept, r_value, p_value, stderr = linregress(x, y)

    def pred_p(log10_sq: float) -> float:
        return float(expit(intercept + slope * log10_sq))

    lod = None
    if abs(slope) > 1e-8:
        try:
            # solve pred_p(z) = target_p
            z_lo, z_hi = float(np.min(x) - 2), float(np.max(x) + 2)

            def f(z):
                return pred_p(z) - target_p

            if f(z_lo) * f(z_hi) < 0:
                z_star = brentq(f, z_lo, z_hi)
                lod = float(10**z_star)
            else:
                # extrapolate
                z_star = (np.log(target_p / (1 - target_p)) - intercept) / slope
                lod = float(10**z_star)
        except ValueError:
            lod = None

    return {
        "intercept": float(intercept),
        "slope": float(slope),
        "r_value": float(r_value),
        "target_p": target_p,
        "lod_sq": lod,
        "n_levels": int(mask.sum()),
    }


def analyze_dataset(path: Path, dataset_id: str) -> dict:
    rows = hit_rates_by_target(path, dataset_id)
    # guidance on blanks
    parsed = load_zenodo_qpcr_cq(path)
    blanks = np.asarray(parsed["blank_values"], dtype=float)
    strata = np.asarray(parsed["blank_strata"]) if parsed["blank_strata"] else None
    g1 = run_guidance(
        goal=Goal.G1_VERIFY_LOD,
        result_type="continuous",
        values=blanks if blanks.size else np.array([45.0]),
        strata=strata if strata is not None and strata.size == blanks.size else None,
        use_case="ldt_lod_establishment",
        p0=0.95,
        run_sensitivity=False,
    )

    # logistic LoD per target
    by_target: dict[str, list[HitRateRow]] = {}
    for r in rows:
        by_target.setdefault(r.target, []).append(r)

    lod_fits = {}
    for target, trs in by_target.items():
        pos = [t for t in trs if t.sq > 0]
        if len(pos) < 3:
            continue
        sq = np.array([t.sq for t in pos], dtype=float)
        rate = np.array([t.rate for t in pos], dtype=float)
        n = np.array([t.n for t in pos], dtype=float)
        lod_fits[target] = fit_logistic_lod(sq, rate, n, target_p=0.95)

    # G2 between two lowest positive SQ hit rates if available
    g2 = None
    all_pos = [r for r in rows if r.sq > 0]
    if all_pos:
        # pick overall two distinct sq with rates
        sqs = sorted({r.sq for r in all_pos})
        if len(sqs) >= 2:
            # pool across targets for same sq for a coarse contrast
            def pool(sq):
                subset = [r for r in all_pos if r.sq == sq]
                h = sum(r.hits for r in subset)
                n = sum(r.n for r in subset)
                return h / n if n else 0.0, n

            p1, n1 = pool(sqs[0])
            p2, n2 = pool(sqs[1])
            pa, pb = max(p1, p2), min(p1, p2)
            if abs(pa - pb) > 0.01 and min(n1, n2) >= 5:
                g2_res = run_guidance(
                    goal=Goal.G2_COMPARE_REAGENTS,
                    result_type="binary",
                    use_case="kit_a_vs_kit_b_near_lod",
                    p_a=pa,
                    p_b=pb,
                    run_sensitivity=False,
                )
                g2 = {
                    "sq_low": sqs[0],
                    "sq_high": sqs[1],
                    "p_low": p1,
                    "p_high": p2,
                    "n_required_per_arm": g2_res.sample_size.n_per_arm,
                    "folklore_n20_warning": g2_res.report.warnings,
                }

    return {
        "dataset_id": dataset_id,
        "path": str(path),
        "hit_rates": [asdict(r) for r in rows],
        "blank_guidance": {
            "parametric_ok": g1.report.parametric_ok,
            "correction": g1.report.correction_method,
            "model_path": g1.model_path.value,
            "n_per_arm": g1.sample_size.n_per_arm,
            "diagnostics": g1.report.diagnostics_summary,
        },
        "logistic_lod_95": lod_fits,
        "g2_adjacent_sq": g2,
        "n_blank": int(blanks.size),
    }


def run_deep_qpcr_research() -> list[dict]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    download_all_real()
    results = []
    mapping = {
        "zenodo_mus_wt_qpcr": RAW_DIR / "zenodo_mus_wt_lod_loq.csv",
        "zenodo_mus_multiplex_qpcr": RAW_DIR / "zenodo_mus_multiplex_lod_loq.csv",
    }
    for did, path in mapping.items():
        if not path.exists():
            results.append({"dataset_id": did, "error": "missing file"})
            continue
        results.append(analyze_dataset(path, did))

    out_json = OUT_DIR / "deep_qpcr_analysis.json"
    out_json.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")

    # flat CSV of hit rates
    out_csv = OUT_DIR / "deep_qpcr_hit_rates.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "dataset_id",
                "target",
                "sq",
                "n",
                "hits",
                "rate",
                "wilson_low",
                "wilson_high",
                "cp_low",
                "cp_high",
            ],
        )
        w.writeheader()
        for block in results:
            for row in block.get("hit_rates", []):
                w.writerow(row)

    return results


if __name__ == "__main__":
    for block in run_deep_qpcr_research():
        print(block["dataset_id"], "blank_path=", block.get("blank_guidance", {}).get("model_path"))
        for t, fit in (block.get("logistic_lod_95") or {}).items():
            print(f"  LoD95[{t[:40]}]= {fit.get('lod_sq')}")
