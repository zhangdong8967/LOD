"""
LoB coverage study: parametric vs nonparametric under Gaussian vs skew laws.

For each law, estimate the empirical blank exceedance rate of LoB estimators
(should be ≈ α for a correctly calibrated upper LoB).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import norm

from lod_guide.s4_models import lob_nonparametric, lob_parametric_normal

OUT_DIR = Path(__file__).resolve().parents[3] / "data" / "research"


def _draw(law: str, n: int, rng: np.random.Generator) -> np.ndarray:
    if law == "normal":
        return rng.normal(0.0, 1.0, size=n)
    if law == "lognormal":
        return rng.lognormal(0.0, 1.0, size=n)
    if law == "exponential":
        return rng.exponential(1.0, size=n)
    raise ValueError(law)


def population_exceedance(lob: float, law: str) -> float:
    """Closed-form or high-accuracy reference exceedance P(X > LoB)."""
    if law == "normal":
        return float(norm.sf(lob, loc=0.0, scale=1.0))
    if law == "exponential":
        return float(np.exp(-lob)) if lob > 0 else 1.0
    if law == "lognormal":
        # X=exp(Z), Z~N(0,1); P(X>lob)=P(Z>log(lob))
        if lob <= 0:
            return 1.0
        return float(norm.sf(np.log(lob)))
    raise ValueError(law)


def run_lob_coverage(
    *,
    alpha: float = 0.05,
    n_blank: int = 60,
    n_mc: int = 2000,
    seed: int = 0,
) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    laws = ("normal", "lognormal", "exponential")
    results = {}

    for law in laws:
        exc_par = []
        exc_np = []
        for _ in range(n_mc):
            blank = _draw(law, n_blank, rng)
            lob_p = lob_parametric_normal(blank, alpha=alpha)
            lob_n = lob_nonparametric(blank, percentile=100 * (1 - alpha))
            exc_par.append(population_exceedance(lob_p, law))
            exc_np.append(population_exceedance(lob_n, law))
        results[law] = {
            "alpha_target": alpha,
            "n_blank": n_blank,
            "n_mc": n_mc,
            "parametric_mean_exceedance": float(np.mean(exc_par)),
            "parametric_sd": float(np.std(exc_par, ddof=1)),
            "nonparametric_mean_exceedance": float(np.mean(exc_np)),
            "nonparametric_sd": float(np.std(exc_np, ddof=1)),
            "parametric_abs_bias_vs_alpha": float(abs(np.mean(exc_par) - alpha)),
            "nonparametric_abs_bias_vs_alpha": float(abs(np.mean(exc_np) - alpha)),
        }

    z = float(norm.ppf(1 - alpha))
    results["theory_exponential"] = {
        "lob_parametric_population": 1.0 + z,
        "lob_true_quantile": float(-np.log(alpha)),
        "population_exceedance_of_parametric": float(np.exp(-(1.0 + z))),
    }

    path = OUT_DIR / "lob_coverage.json"
    path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    r = run_lob_coverage()
    for law, block in r.items():
        if law == "theory_exponential":
            print(law, block)
        else:
            print(
                law,
                "par=",
                round(block["parametric_mean_exceedance"], 4),
                "np=",
                round(block["nonparametric_mean_exceedance"], 4),
            )
