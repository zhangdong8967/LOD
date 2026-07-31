"""
Locally c-optimal multi-level designs for log10(LoD_γ).

Minimizes asymptotic Var(log10 LoD) = grad' I^{-1} grad under binomial GLM
information, following the c-optimality criterion (Atkinson–Donev; Fedorov).

Uses fast grid enumeration over support/allocation patterns, then optional
local refinement — suitable for planning surfaces and machine certificates.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from scipy.optimize import minimize

from lod_guide.theory.lod_dose_response import (
    DoseResponseTruth,
    asymptotic_lod_se_log10,
    default_synthetic_truth,
)


@dataclass(frozen=True)
class DesignSpec:
    log10_concentrations: np.ndarray
    n_per_level: np.ndarray

    @property
    def concentrations(self) -> np.ndarray:
        return 10 ** np.asarray(self.log10_concentrations, dtype=float)

    def to_dict(self) -> dict:
        return {
            "log10_concentrations": self.log10_concentrations.tolist(),
            "concentrations": self.concentrations.tolist(),
            "n_per_level": self.n_per_level.tolist(),
            "total_n": int(self.n_per_level.sum()),
        }


def _pack_design(x_log10: np.ndarray, weights: np.ndarray, total_n: int) -> DesignSpec:
    w = np.asarray(weights, dtype=float)
    w = np.maximum(w, 1e-6)
    w = w / w.sum()
    raw = w * total_n
    n = np.floor(raw).astype(int)
    n = np.maximum(n, 1)
    while n.sum() > total_n:
        i = int(np.argmax(n))
        if n[i] > 1:
            n[i] -= 1
        else:
            break
    while n.sum() < total_n:
        deficit = int(total_n - n.sum())
        order = np.argsort(-(w - n / max(n.sum(), 1)))[:deficit]
        for i in order:
            n[i] += 1
            if n.sum() >= total_n:
                break
    return DesignSpec(log10_concentrations=np.sort(x_log10), n_per_level=n.astype(float))


def _make_support_grids(lod_x: float, n_levels: int, span_decades: float) -> list[np.ndarray]:
    """Candidate log10 support sets for c-optimal search."""
    x_lo = lod_x - span_decades / 2
    x_hi = lod_x + span_decades / 2
    grids: list[np.ndarray] = [np.linspace(x_lo, x_hi, n_levels)]

    u = np.linspace(0.05, 0.95, n_levels)
    grid = np.linspace(0, 1, 2001)
    cdf = 3 * grid**2 - 2 * grid**3
    z = np.interp(u, cdf, grid)
    grids.append(x_lo + z * (x_hi - x_lo))

    # Shifted supports emphasizing inflection / LoD neighborhood
    for center_bias in (-0.15, 0.0, 0.15):
        t = np.linspace(-1, 1, n_levels)
        grids.append(lod_x + center_bias + t * (span_decades / 2) * 0.85)

    return grids


def _allocation_weights(
    x_log10: np.ndarray,
    lod_x: float,
    scheme: str,
) -> np.ndarray:
    if scheme == "equal":
        return np.ones_like(x_log10, dtype=float)
    d = np.abs(x_log10 - lod_x)
    if scheme == "lod_weighted":
        return 1.0 / (0.15 + d)
    if scheme == "inflection":
        # Weight toward p≈0.5 region on log scale (roughly one decade below LoD for steep curves)
        return 1.0 / (0.05 + np.abs(x_log10 - (lod_x - 0.35)))
    return np.ones_like(x_log10, dtype=float)


def _se_for_spec(truth: DoseResponseTruth, spec: DesignSpec) -> float:
    return float(asymptotic_lod_se_log10(truth, spec.concentrations, spec.n_per_level)["se_log10_lod"])


def _grid_search_c_optimal(
    truth: DoseResponseTruth,
    *,
    n_levels: int,
    total_n: int,
    span_decades: float,
) -> tuple[DesignSpec, float]:
    lod_x = truth.lod_log10()
    best_spec: DesignSpec | None = None
    best_se = float("inf")

    for x_grid in _make_support_grids(lod_x, n_levels, span_decades):
        for scheme in ("equal", "lod_weighted", "inflection"):
            spec = _pack_design(x_grid, _allocation_weights(x_grid, lod_x, scheme), total_n)
            se = _se_for_spec(truth, spec)
            if se < best_se:
                best_se = se
                best_spec = spec

    assert best_spec is not None
    return best_spec, best_se


def _refine_support(
    truth: DoseResponseTruth,
    spec: DesignSpec,
    *,
    total_n: int,
    span_decades: float,
) -> tuple[DesignSpec, float]:
    """Polish log10 support with fixed allocation weights via L-BFGS-B."""
    lod_x = truth.lod_log10()
    x0 = np.array(spec.log10_concentrations, dtype=float)
    w0 = np.array(spec.n_per_level, dtype=float)
    x_lo = lod_x - span_decades / 2
    x_hi = lod_x + span_decades / 2

    def obj(x: np.ndarray) -> float:
        x_sorted = np.sort(np.clip(x, x_lo, x_hi))
        trial = _pack_design(x_sorted, w0, total_n)
        se = _se_for_spec(truth, trial)
        return se if np.isfinite(se) else 1e6

    res = minimize(obj, x0, method="L-BFGS-B", bounds=[(x_lo, x_hi)] * len(x0))
    refined = _pack_design(np.sort(res.x), w0, total_n)
    return refined, _se_for_spec(truth, refined)


@lru_cache(maxsize=32)
def _cached_c_optimal_key(
    intercept: float,
    slope: float,
    link: str,
    target_p: float,
    n_levels: int,
    total_n: int,
    span_decades: float,
    seed: int,
) -> tuple[float, tuple[float, ...], tuple[float, ...]]:
    truth = DoseResponseTruth(intercept, slope, link, target_p)
    spec, se = _grid_search_c_optimal(truth, n_levels=n_levels, total_n=total_n, span_decades=span_decades)
    spec2, se2 = _refine_support(truth, spec, total_n=total_n, span_decades=span_decades)
    if se2 < se:
        spec, se = spec2, se2
    return (
        se,
        tuple(float(x) for x in spec.log10_concentrations),
        tuple(float(n) for n in spec.n_per_level),
    )


def local_c_optimal_design(
    truth: DoseResponseTruth,
    *,
    n_levels: int = 5,
    total_n: int = 60,
    span_decades: float = 2.0,
    seed: int = 0,
) -> dict:
    """Search a locally c-optimal design minimizing asymptotic SE(log10 LoD)."""
    se, x_tuple, n_tuple = _cached_c_optimal_key(
        truth.intercept,
        truth.slope,
        truth.link,
        truth.target_p,
        n_levels,
        total_n,
        span_decades,
        seed,
    )
    spec = DesignSpec(np.array(x_tuple), np.array(n_tuple))
    return {
        "design": spec.to_dict(),
        "se_log10_lod": float(se),
        "truth_lod": truth.lod(),
        "n_levels": n_levels,
        "total_n": total_n,
        "method": "grid_enumeration_plus_lbfgs",
    }


def asymptotic_efficiency(
    reference_se: float,
    optimal_se: float,
) -> dict:
    """
    P14: efficiency = (SE_ref / SE_opt)^2 for c-optimal target (variance ratio).
    """
    if not np.isfinite(reference_se) or not np.isfinite(optimal_se) or optimal_se <= 0:
        return {"efficiency": None, "variance_ratio": None, "se_reference": reference_se, "se_optimal": optimal_se}
    ratio = reference_se / optimal_se
    return {
        "efficiency": float(ratio**2),
        "variance_ratio": float(ratio**2),
        "se_ratio": float(ratio),
        "se_reference": float(reference_se),
        "se_optimal": float(optimal_se),
    }


def compare_to_reference_designs(
    truth: DoseResponseTruth | None = None,
    *,
    n_levels: int = 5,
    total_n: int = 60,
    seed: int = 0,
) -> dict:
    """Run c-optimal search and compare to equal log-spacing + equal allocation."""
    truth = truth or default_synthetic_truth()
    c_opt = local_c_optimal_design(truth, n_levels=n_levels, total_n=total_n, seed=seed)
    lod = truth.lod()
    x = np.linspace(np.log10(lod) - 1.0, np.log10(lod) + 1.0, n_levels)
    ref_conc = 10**x
    ref_n = np.full(n_levels, total_n // n_levels, dtype=float)
    ref_n[: total_n % n_levels] += 1
    ref_se = asymptotic_lod_se_log10(truth, ref_conc, ref_n)["se_log10_lod"]
    eff = asymptotic_efficiency(ref_se, c_opt["se_log10_lod"])
    return {
        "c_optimal": c_opt,
        "reference_equal_log_equal_n": {
            "concentrations": ref_conc.tolist(),
            "n_per_level": ref_n.tolist(),
            "se_log10_lod": ref_se,
        },
        "efficiency_vs_reference": eff,
        "truth": {"lod": lod, "slope": truth.slope, "link": truth.link},
    }
