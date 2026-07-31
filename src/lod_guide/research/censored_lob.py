"""
Left-censored blank LoB (Tobit-style Normal MLE) + nonparametric Kaplan–Meier-style
percentile on censored blanks.

When a non-trivial fraction of blanks sit on a floor (instrument LoB / zero),
uncensored mean+z·SD is biased. This path complements S2 censoring flags.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.optimize import minimize

from lod_guide.data.simulate import sim_censored_floor, sim_normal_blanks
from lod_guide.s4_models import lob_nonparametric, lob_parametric_normal

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def tobit_normal_mle(
    x: np.ndarray,
    *,
    censor_at: float,
    left_censored: np.ndarray | None = None,
) -> dict:
    """
    Left-censored Normal(μ,σ) MLE.
    Observations with x <= censor_at (or left_censored mask) contribute Φ((c-μ)/σ).
    """
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if left_censored is None:
        cens = x <= censor_at
    else:
        cens = np.asarray(left_censored, dtype=bool)
        assert cens.shape == x.shape
    xc = x[~cens]
    n_c = int(cens.sum())
    n_o = int(xc.size)
    if n_o < 2:
        return {"ok": False, "error": "need ≥2 uncensored"}

    def nll(theta: np.ndarray) -> float:
        mu, log_s = theta
        s = np.exp(log_s)
        if s < 1e-12:
            return 1e100
        ll = 0.0
        if n_o:
            ll += float(np.sum(stats.norm.logpdf(xc, mu, s)))
        if n_c:
            # P(X <= c) = Φ((c-μ)/σ)
            ll += float(n_c * stats.norm.logcdf(censor_at, mu, s))
        return -ll

    mu0 = float(np.mean(xc))
    s0 = float(np.std(xc, ddof=1))
    res = minimize(nll, x0=np.array([mu0, np.log(max(s0, 1e-6))]), method="L-BFGS-B")
    if not res.success:
        return {"ok": False, "error": str(res.message)}
    mu = float(res.x[0])
    sigma = float(np.exp(res.x[1]))
    return {
        "ok": True,
        "mu": mu,
        "sigma": sigma,
        "n_censored": n_c,
        "n_observed": n_o,
        "censor_at": float(censor_at),
        "censoring_rate": n_c / max(1, n_c + n_o),
    }


def lob_tobit_normal(x: np.ndarray, *, censor_at: float, alpha: float = 0.05) -> dict:
    fit = tobit_normal_mle(x, censor_at=censor_at)
    if not fit.get("ok"):
        return fit
    z = float(stats.norm.ppf(1 - alpha))
    lob = fit["mu"] + z * fit["sigma"]
    return {**fit, "lob": float(lob), "alpha": alpha, "path": "tobit_normal"}


def lob_km_percentile_censored(
    x: np.ndarray,
    *,
    censor_at: float,
    percentile: float = 95.0,
) -> dict:
    """
    Treat values at/below floor as left-censored; estimate upper percentile via
    a simple redistribution: assign censored mass uniformly below floor and use
    empirical quantile of the completed sample (hot-deck on floor). Transparent proxy.
    """
    x = np.asarray(x, dtype=float)
    cens = x <= censor_at
    # Place censored points uniformly on [censor_at - spread, censor_at]
    spread = float(np.std(x[~cens], ddof=1)) if np.sum(~cens) > 1 else 1.0
    rng = np.random.default_rng(0)
    completed = x.copy()
    n_c = int(cens.sum())
    if n_c:
        completed[cens] = censor_at - rng.uniform(0, max(spread, 1e-6), size=n_c)
    lob = float(np.percentile(completed, percentile))
    return {
        "ok": True,
        "lob": lob,
        "percentile": percentile,
        "n_censored": n_c,
        "path": "km_hotdeck_percentile",
        "censor_at": float(censor_at),
    }


def run_censored_lob_study() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    # Simulated left-censored blanks
    cens = sim_censored_floor(seed=3)
    x = np.asarray(cens.values, dtype=float)
    floor = float(np.min(x))
    # If many at min, use that floor
    tobit = lob_tobit_normal(x, censor_at=floor, alpha=0.05)
    km = lob_km_percentile_censored(x, censor_at=floor, percentile=95.0)
    naive = lob_parametric_normal(x, alpha=0.05)
    np_lob = lob_nonparametric(x, 95.0)

    # Clean normal control (little censoring)
    clean = sim_normal_blanks(seed=0)
    y = np.asarray(clean.values, dtype=float)
    tobit_clean = lob_tobit_normal(y, censor_at=float(np.min(y)), alpha=0.05)

    payload = {
        "study_id": "CENSORED-LOB-TOBIT-v1",
        "censored_sim": {
            "dataset": cens.dataset_id,
            "naive_parametric_lob": naive,
            "nonparametric_p95": np_lob,
            "tobit": tobit,
            "km_hotdeck": km,
            "delta_tobit_minus_naive": (tobit.get("lob") - naive) if tobit.get("ok") else None,
        },
        "normal_control": {
            "tobit": tobit_clean,
            "naive": lob_parametric_normal(y, 0.05),
            "agree_closely": (
                abs(tobit_clean.get("lob", 0) - lob_parametric_normal(y, 0.05)) < 0.05
                if tobit_clean.get("ok")
                else False
            ),
        },
        "headline": {
            "tobit_ok": bool(tobit.get("ok")),
            "censoring_rate": tobit.get("censoring_rate"),
            "lob_tobit": tobit.get("lob"),
            "lob_naive": naive,
            "lob_np": np_lob,
        },
        "claim_boundary": (
            "Tobit LoB assumes left-censored Normal blanks. Hot-deck KM percentile is a "
            "transparent nonparametric proxy, not a full Turnbull estimator."
        ),
    }
    path = OUT / "censored_lob_tobit.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload


# Wire into s4 enum usage
def estimate_lob_censored(blank: np.ndarray, *, censor_at: float | None = None, alpha: float = 0.05) -> dict:
    x = np.asarray(blank, dtype=float)
    c = float(np.min(x)) if censor_at is None else float(censor_at)
    return lob_tobit_normal(x, censor_at=c, alpha=alpha)


if __name__ == "__main__":
    print(json.dumps(run_censored_lob_study()["headline"], indent=2, default=str))
