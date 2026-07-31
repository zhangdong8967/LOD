"""
Operating-characteristic Monte Carlo: folklore n=20 vs powered n*.

Estimates Type I error under H0: p_A=p_B and power under H1 for pooled z-test.
Results written to data/research/ for transparent auditing.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from scipy.stats import norm

from lod_guide.s5_sample_size import sample_size_two_proportions

OUT_DIR = Path(__file__).resolve().parents[3] / "data" / "research"


@dataclass
class OCRow:
    setting: str
    p_a: float
    p_b: float
    n: int
    alpha: float
    n_sims: int
    reject_rate: float
    truth: str  # H0 or H1


def pooled_z_reject(xa: np.ndarray, xb: np.ndarray, n: int, alpha: float) -> np.ndarray:
    p_pool = (xa + xb) / (2 * n)
    se = np.sqrt(np.maximum(p_pool * (1 - p_pool) * (2 / n), 1e-16))
    z = np.where(se > 1e-12, (xa / n - xb / n) / se, 0.0)
    pvals = 2 * norm.sf(np.abs(z))
    return (pvals < alpha) & (se > 1e-12)


def run_oc_cell(
    p_a: float,
    p_b: float,
    n: int,
    *,
    alpha: float = 0.05,
    n_sims: int = 20_000,
    seed: int = 0,
    setting: str = "",
) -> OCRow:
    rng = np.random.default_rng(seed)
    xa = rng.binomial(n, p_a, size=n_sims)
    xb = rng.binomial(n, p_b, size=n_sims)
    rate = float(np.mean(pooled_z_reject(xa, xb, n, alpha)))
    truth = "H0" if abs(p_a - p_b) < 1e-15 else "H1"
    return OCRow(setting, p_a, p_b, n, alpha, n_sims, rate, truth)


def run_operating_characteristics(
    *,
    n_sims: int = 20_000,
    seed: int = 1,
) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[OCRow] = []

    # Type I: equal rates
    for p in (0.5, 0.8, 0.9, 0.95):
        for n, tag in ((20, "folklore_n20"), (50, "n50"), (199, "n199")):
            rows.append(
                run_oc_cell(
                    p,
                    p,
                    n,
                    n_sims=n_sims,
                    seed=seed + int(1000 * p) + n,
                    setting=f"typeI_p{p}_{tag}",
                )
            )

    # Power: 0.90 vs 0.80
    n_star = int(np.ceil(sample_size_two_proportions(0.90, 0.80)))
    for n, tag in ((20, "folklore_n20"), (50, "n50"), (100, "n100"), (n_star, "n_star")):
        rows.append(
            run_oc_cell(
                0.90,
                0.80,
                n,
                n_sims=n_sims,
                seed=seed + 10_000 + n,
                setting=f"power_90v80_{tag}",
            )
        )

    # Power: smaller delta 0.90 vs 0.85
    n_star2 = int(np.ceil(sample_size_two_proportions(0.90, 0.85)))
    for n, tag in ((20, "folklore_n20"), (n_star2, "n_star")):
        rows.append(
            run_oc_cell(
                0.90,
                0.85,
                n,
                n_sims=n_sims,
                seed=seed + 20_000 + n,
                setting=f"power_90v85_{tag}",
            )
        )

    payload = {
        "n_sims": n_sims,
        "seed_base": seed,
        "n_star_90_80": n_star,
        "n_star_90_85": n_star2,
        "rows": [asdict(r) for r in rows],
        "summary": {
            "typeI_folklore_mean": float(
                np.mean([r.reject_rate for r in rows if r.truth == "H0" and r.n == 20])
            ),
            "power_90v80_n20": next(
                r.reject_rate for r in rows if r.setting == "power_90v80_folklore_n20"
            ),
            "power_90v80_n_star": next(
                r.reject_rate for r in rows if r.setting.startswith("power_90v80_n_star")
            ),
        },
    }
    path = OUT_DIR / "operating_characteristics.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    out = run_operating_characteristics()
    print(json.dumps(out["summary"], indent=2))
    print("n* 90vs80 =", out["n_star_90_80"])
