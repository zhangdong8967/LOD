"""
Probit / logistic multi-concentration LoD design grid.

For hit-rate vs concentration experiments (EP17 Appendix C class), compare
allocation designs under a working dose–response:

  logit(p) = α + β · log10(c)     (logistic; default)
  probit(p) = α + β · log10(c)    (optional)

LoD_γ solves p(c)=γ (default γ=0.95). Designs are scored by the delta-method
asymptotic SE of log10(LoD) from the expected binomial information matrix —
a transparent planning surface, not a claim of finite-sample exact optimality.

Also reports one-level verification n* for a claimed concentration (E1).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.special import logit
from scipy.stats import norm

from lod_guide.data.download_real import RAW_DIR, download_dataset, parse_real_dataset, REMOTE_DATASETS
from lod_guide.research.deep_qpcr import fit_logistic_lod
from lod_guide.s5_sample_size import sample_size_one_proportion
from lod_guide.theory.lod_dose_response import (
    DoseResponseTruth,
    asymptotic_lod_se_log10,
    default_synthetic_truth,
)

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def make_concentration_grid(
    lod: float,
    *,
    n_levels: int,
    span_decades: float = 2.0,
    pattern: str = "equal_log",
) -> np.ndarray:
    """
    Build positive concentrations spanning ±span_decades/2 around true LoD (log10).
    pattern:
      equal_log — uniform in log10
      dense_near_lod — quadratic denser near LoD
      wide_sparse — same endpoints, fewer interior near edges (still n_levels points)
    """
    lo = np.log10(lod) - span_decades / 2
    hi = np.log10(lod) + span_decades / 2
    if pattern == "dense_near_lod":
        # More points near center via inverse-CDF of Beta(2,2) on [0,1]
        u = np.linspace(0.05, 0.95, n_levels)
        # Beta(2,2) CDF is 3u^2 - 2u^3; invert numerically by grid
        grid = np.linspace(0, 1, 2001)
        cdf = 3 * grid**2 - 2 * grid**3
        z = np.interp(u, cdf, grid)
        x = lo + z * (hi - lo)
    else:
        x = np.linspace(lo, hi, n_levels)
    return 10**x


def allocate_n(total_n: int, n_levels: int, *, scheme: str, lod: float, concentrations: np.ndarray) -> np.ndarray:
    """Equal vs weight toward levels closest to LoD."""
    if scheme == "equal":
        base = np.full(n_levels, total_n // n_levels, dtype=int)
        base[: total_n % n_levels] += 1
        return base.astype(float)
    # triangular weights by |log10(c)-log10(LoD)|
    d = np.abs(np.log10(concentrations) - np.log10(lod))
    w = 1.0 / (0.15 + d)  # closer → larger weight
    w = w / w.sum()
    raw = w * total_n
    n = np.floor(raw).astype(int)
    # ensure at least 1 each if total allows
    n = np.maximum(n, 1)
    while n.sum() > total_n:
        i = int(np.argmax(n))
        if n[i] > 1:
            n[i] -= 1
        else:
            break
    while n.sum() < total_n:
        i = int(np.argmax(w - n / max(n.sum(), 1)))
        n[i] += 1
    return n.astype(float)


def evaluate_design_grid(
    truth: DoseResponseTruth,
    *,
    total_n_grid: list[int] | None = None,
    n_levels_grid: list[int] | None = None,
    patterns: list[str] | None = None,
    schemes: list[str] | None = None,
) -> dict:
    if total_n_grid is None:
        total_n_grid = [40, 60, 80, 120]
    if n_levels_grid is None:
        n_levels_grid = [4, 5, 6, 8]
    if patterns is None:
        patterns = ["equal_log", "dense_near_lod"]
    if schemes is None:
        schemes = ["equal", "lod_weighted"]

    lod = truth.lod()
    rows = []
    for n_levels in n_levels_grid:
        for total_n in total_n_grid:
            if total_n < n_levels:
                continue
            for pattern in patterns:
                conc = make_concentration_grid(lod, n_levels=n_levels, pattern=pattern)
                for scheme in schemes:
                    n_vec = allocate_n(total_n, n_levels, scheme=scheme, lod=lod, concentrations=conc)
                    se = asymptotic_lod_se_log10(truth, conc, n_vec)
                    rows.append(
                        {
                            "n_levels": n_levels,
                            "total_n": total_n,
                            "pattern": pattern,
                            "allocation": scheme,
                            "concentrations": conc.tolist(),
                            "n_per_level": n_vec.tolist(),
                            "se_log10_lod": se["se_log10_lod"],
                            "cv_lod_approx": se["cv_lod_approx"],
                            "info_ok": se["info_ok"],
                        }
                    )

    ok = [r for r in rows if r["info_ok"] and np.isfinite(r["se_log10_lod"])]
    best = min(ok, key=lambda r: r["se_log10_lod"]) if ok else None
    # Reference: folklore-ish 5 levels × 20 = 100? or 5×12; use equal_log equal at N=60, K=5
    ref = next(
        (
            r
            for r in ok
            if r["n_levels"] == 5 and r["total_n"] == 60 and r["pattern"] == "equal_log" and r["allocation"] == "equal"
        ),
        None,
    )
    return {
        "truth": {
            "intercept": truth.intercept,
            "slope": truth.slope,
            "link": truth.link,
            "target_p": truth.target_p,
            "lod": lod,
            "lod_log10": truth.lod_log10(),
        },
        "n_designs": len(rows),
        "best": best,
        "reference_equal_K5_N60": ref,
        "se_ratio_best_over_reference": (
            (best["se_log10_lod"] / ref["se_log10_lod"]) if best and ref and ref["se_log10_lod"] else None
        ),
        "rows": rows,
    }


def truth_from_ep17_probit() -> DoseResponseTruth | None:
    """Fit working logistic truth from Analyse-it EP17 probit workbook if present."""
    meta = next(d for d in REMOTE_DATASETS if d.dataset_id == "analyseit_ep17_probit")
    path = RAW_DIR / meta.filename
    if not path.exists():
        try:
            path = download_dataset(meta)
        except Exception:  # noqa: BLE001
            return None
    parsed = parse_real_dataset(meta.dataset_id, path)
    summary = parsed.get("hit_summary") or {}
    if len(summary) < 3:
        return None
    cs, rates, ns = [], [], []
    for c, rec in sorted(summary.items(), key=lambda kv: float(kv[0])):
        c = float(c)
        if c <= 0:
            continue
        cs.append(c)
        rates.append(float(rec["rate"]))
        ns.append(float(rec["n"]))
    fit = fit_logistic_lod(np.asarray(cs), np.asarray(rates), np.asarray(ns), target_p=0.95)
    if fit.get("lod_sq") is None or not np.isfinite(fit["slope"]):
        return None
    return DoseResponseTruth(intercept=fit["intercept"], slope=fit["slope"], link="logistic", target_p=0.95)


def run_probit_design_grid() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    synthetic = default_synthetic_truth()
    grid_syn = evaluate_design_grid(synthetic)
    grid_syn_probit = evaluate_design_grid(
        DoseResponseTruth(
            intercept=float(norm.ppf(0.95)),
            slope=float(norm.ppf(0.95) - norm.ppf(0.25)),
            link="probit",
            target_p=0.95,
        )
    )

    # E1 verification n: alternative p=0.80 vs reference claim p0=0.95
    n_g1 = int(np.ceil(sample_size_one_proportion(0.80, 0.95, alpha=0.05, power=0.80)))

    ep17_truth = truth_from_ep17_probit()
    grid_ep17 = evaluate_design_grid(ep17_truth) if ep17_truth is not None else None

    payload = {
        "study_id": "PROBIT-DESIGN-GRID-v1",
        "purpose": (
            "Compare multi-concentration hit-rate designs for estimating LoD95 under "
            "logistic/probit working models via expected-information delta-method SE(log10 LoD)."
        ),
        "g1_verification_n_note": {
            "description": "One-level verification n* for H1: p=0.80 vs H0 claim region near p0=0.95 (engine example).",
            "n_star_example": n_g1,
        },
        "synthetic_logistic": grid_syn,
        "synthetic_probit": {
            "truth": grid_syn_probit["truth"],
            "best": grid_syn_probit["best"],
            "reference_equal_K5_N60": grid_syn_probit["reference_equal_K5_N60"],
            "se_ratio_best_over_reference": grid_syn_probit["se_ratio_best_over_reference"],
            "n_designs": grid_syn_probit["n_designs"],
        },
        "ep17_probit_workbook_fit": (
            {
                "truth": grid_ep17["truth"],
                "best": grid_ep17["best"],
                "reference_equal_K5_N60": grid_ep17["reference_equal_K5_N60"],
                "se_ratio_best_over_reference": grid_ep17["se_ratio_best_over_reference"],
                "n_designs": grid_ep17["n_designs"],
            }
            if grid_ep17
            else {"error": "EP17 probit workbook unavailable or <3 concentration levels"}
        ),
        "headline": {
            "synthetic_best": grid_syn.get("best"),
            "synthetic_reference_K5_N60": grid_syn.get("reference_equal_K5_N60"),
            "se_ratio_best_over_ref": grid_syn.get("se_ratio_best_over_reference"),
            "ep17_available": grid_ep17 is not None,
        },
        "claim_boundary": (
            "Asymptotic design scores are planning aids. They do not replace exact small-sample "
            "confirmation, nor claim D-optimality under all misspecifications. "
            "Complement EP17 multi-level options; do not redefine LoD legally."
        ),
    }
    # Drop bulky full row lists from ep17/probit copies already trimmed; keep synthetic rows for audit
    out = OUT / "probit_design_grid.json"
    # Store compact: keep synthetic rows, omit duplicate huge lists in nested copies
    compact = dict(payload)
    compact["synthetic_logistic"] = {
        **{k: v for k, v in grid_syn.items() if k != "rows"},
        "rows_top": sorted(
            [r for r in grid_syn["rows"] if r["info_ok"]],
            key=lambda r: r["se_log10_lod"],
        )[:12],
        "n_rows_total": len(grid_syn["rows"]),
    }
    out.write_text(json.dumps(compact, indent=2, default=str), encoding="utf-8")
    compact["path"] = str(out)
    return compact


if __name__ == "__main__":
    print(json.dumps(run_probit_design_grid()["headline"], indent=2, default=str))
