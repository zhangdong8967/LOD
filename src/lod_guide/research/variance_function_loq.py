"""
Variance-function LoQ (Rocke–Lorenzato style).

Model: σ²(μ) = β0² + (β1 · μ)²
CV(μ) = σ(μ)/μ. LoQ@target solves CV(μ)=target (e.g. 0.20).

Fits pool (mean, sd) rows by nonlinear least squares on sd.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit

from lod_guide.data.download_real import RAW_DIR, download_dataset, parse_real_dataset, REMOTE_DATASETS
from lod_guide.research.precision_profile import PoolPrecision, evaluate_precision_profile

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def rocke_lorenzato_sd(mu: np.ndarray, beta0: float, beta1: float) -> np.ndarray:
    return np.sqrt(beta0**2 + (beta1 * mu) ** 2)


def fit_rocke_lorenzato(means: np.ndarray, sds: np.ndarray) -> dict:
    means = np.asarray(means, dtype=float)
    sds = np.asarray(sds, dtype=float)
    mask = np.isfinite(means) & np.isfinite(sds) & (means > 0) & (sds >= 0)
    m, s = means[mask], sds[mask]
    if m.size < 3:
        return {"ok": False, "error": "need ≥3 pools"}

    def f(mu, b0, b1):
        return rocke_lorenzato_sd(mu, b0, b1)

    p0 = (float(np.min(s)), float(np.median(s / m)))
    try:
        popt, pcov = curve_fit(f, m, s, p0=p0, bounds=(0, np.inf), maxfev=5000)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}
    b0, b1 = float(popt[0]), float(popt[1])
    pred = rocke_lorenzato_sd(m, b0, b1)
    ss_res = float(np.sum((s - pred) ** 2))
    ss_tot = float(np.sum((s - np.mean(s)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {
        "ok": True,
        "beta0": b0,
        "beta1": b1,
        "r2_sd": r2,
        "n_pools": int(m.size),
        "cov": pcov.tolist() if pcov is not None else None,
    }


def loq_from_variance_function(beta0: float, beta1: float, target_cv: float = 0.20) -> float | None:
    """
    CV(μ)=sqrt(β0²+(β1 μ)²)/μ = t
    => β0² + β1² μ² = t² μ² => μ² (t² - β1²) = β0² => μ = β0 / sqrt(t² - β1²)
    Requires t > |β1|.
    """
    if target_cv <= abs(beta1) + 1e-15:
        return None
    return float(beta0 / np.sqrt(target_cv**2 - beta1**2))


def _pools_from_radioimmuno() -> list[PoolPrecision] | None:
    meta = next(d for d in REMOTE_DATASETS if d.dataset_id == "zenodo_radioimmuno_precision")
    path = RAW_DIR / meta.filename
    if not path.exists():
        try:
            path = download_dataset(meta)
        except Exception:  # noqa: BLE001
            return None
    parsed = parse_real_dataset(meta.dataset_id, path)
    pools = []
    for r in parsed.get("pool_rows") or []:
        pools.append(
            PoolPrecision(
                str(r["sample_name"]),
                3,
                float(r["mean"]),
                float(r["sd"]),
                float(r["cv_pct"]),
                "radioimmuno",
            )
        )
    return pools or None


def run_variance_function_loq_study() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    pools = _pools_from_radioimmuno()
    if not pools:
        # synthetic RL truth
        rng = np.random.default_rng(1)
        mu = np.array([10, 20, 50, 100, 200, 500], dtype=float)
        b0, b1 = 2.0, 0.08
        sd = rocke_lorenzato_sd(mu, b0, b1) * rng.uniform(0.9, 1.1, size=mu.size)
        means, sds = mu, sd
        source = "synthetic_RL"
        emp = None
    else:
        means = np.array([p.mean for p in pools], dtype=float)
        sds = np.array([p.sd for p in pools], dtype=float)
        source = "zenodo_radioimmuno_precision"
        emp = evaluate_precision_profile(pools, target_cv_pct=20.0, evidence_tier="A")

    fit = fit_rocke_lorenzato(means, sds)
    loq20 = loq_from_variance_function(fit["beta0"], fit["beta1"], 0.20) if fit.get("ok") else None
    loq10 = loq_from_variance_function(fit["beta0"], fit["beta1"], 0.10) if fit.get("ok") else None

    payload = {
        "study_id": "VARIANCE-FUNCTION-LOQ-v1",
        "source": source,
        "model": "sigma^2(mu) = beta0^2 + (beta1*mu)^2",
        "fit": fit,
        "loq_at_cv20": loq20,
        "loq_at_cv10": loq10,
        "empirical_profile_loq20": None if emp is None else emp.loq_estimate,
        "headline": {
            "ok": fit.get("ok"),
            "beta0": fit.get("beta0"),
            "beta1": fit.get("beta1"),
            "loq_cv20": loq20,
            "empirical_loq20": None if emp is None else emp.loq_estimate,
        },
        "claim_boundary": (
            "Rocke–Lorenzato is a working variance function for planning LoQ; "
            "empirical precision-profile interpolation remains the primary tier-A figure."
        ),
    }
    path = OUT / "variance_function_loq.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_variance_function_loq_study()["headline"], indent=2, default=str))
