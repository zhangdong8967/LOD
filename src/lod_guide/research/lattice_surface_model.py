"""
E2 planning surfaces over the full integer hit-rate lattice.

Primary objects (mathematical model):
  π_Fisher(p_A, p_B; n) — exact two-proportion power at folklore n=20
  n*(p_A, p_B)         — Fleiss–Chow asymptotic design (Eq. 2 in manuscript)
  Δ = p_A − p_B        — contrast margin; marginal summaries by Δ collapse the surface

Exports JSON summary + marginal-by-delta CSV for supplement Table 3f.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from lod_guide.research.comparison_grid_export import (
    FOLKLORE_N,
    MIN_DELTA,
    PA_GRID,
    PB_GRID,
    build_comparison_grid,
    grid_arrays,
)
from lod_guide.s5_sample_size import sample_size_two_proportions

OUT = Path(__file__).resolve().parents[3] / "data" / "research"
PAPER_TABLES = Path(__file__).resolve().parents[3] / "paper_artifacts" / "tables"
SPEC_VERSION = "lattice_surface_v2"

# Author-reported Δp bands in Results (percentage points). Not a field prevalence.
DELTA_BANDS_PP: tuple[tuple[str, int, int], ...] = (
    ("1-5", 1, 5),
    ("6-10", 6, 10),
    ("11-20", 11, 20),
    (">20", 21, 49),
)


def marginal_by_delta(
    pa: np.ndarray,
    pb: np.ndarray,
    surface: np.ndarray,
    *,
    stat: str = "median",
) -> list[dict]:
    """Aggregate a lattice surface by integer percentage-point contrast Δ."""
    rows: list[dict] = []
    for delta_pp in range(1, 50):
        delta = delta_pp / 100.0
        mask = np.isfinite(surface) & (pa[:, None] - pb[None, :] >= delta - 0.001) & (
            pa[:, None] - pb[None, :] <= delta + 0.001
        )
        vals = surface[mask]
        if vals.size == 0:
            continue
        if stat == "median":
            agg = float(np.nanmedian(vals))
        elif stat == "mean":
            agg = float(np.nanmean(vals))
        else:
            raise ValueError(stat)
        rows.append(
            {
                "delta_p": round(delta, 4),
                "delta_pp": delta_pp,
                "n_cells": int(mask.sum()),
                f"{stat}_value": agg,
            }
        )
    return rows


def marginal_power_by_delta(pa: np.ndarray, pb: np.ndarray, power: np.ndarray) -> list[dict]:
    rows = marginal_by_delta(pa, pb, power, stat="median")
    for r in rows:
        r["median_power_exact_fisher"] = r.pop("median_value")
        r["frac_power_lt_0.2"] = None
    # attach underpowered fraction per delta band
    for r in rows:
        delta = r["delta_p"]
        mask = np.isfinite(power) & (pa[:, None] - pb[None, :] >= delta - 0.001) & (
            pa[:, None] - pb[None, :] <= delta + 0.001
        )
        vals = power[mask]
        r["frac_power_lt_0.2"] = float((vals < 0.2).mean()) if vals.size else None
    return rows


def marginal_nstar_by_delta(pa: np.ndarray, pb: np.ndarray, nstar: np.ndarray) -> list[dict]:
    rows = marginal_by_delta(pa, pb, nstar, stat="median")
    for r in rows:
        r["median_n_star_asymptotic"] = r.pop("median_value")
        r["median_n_star_ceiling"] = int(np.ceil(r["median_n_star_asymptotic"]))
    return rows


def summarize_delta_bands(
    pa: np.ndarray,
    pb: np.ndarray,
    miss: np.ndarray,
    nstar: np.ndarray,
) -> list[dict]:
    """Collapse the lattice into the Δp bands quoted in Results.

    The global median n* is a property of equal spacing on 50–99%, not a typical
    laboratory contrast. Band summaries are the objects that should be displayed.
    """
    delta_pp = np.round((pa[:, None] - pb[None, :]) * 100.0)
    rows: list[dict] = []
    for label, lo, hi in DELTA_BANDS_PP:
        mask = np.isfinite(nstar) & (delta_pp >= lo) & (delta_pp <= hi)
        n_cells = int(mask.sum())
        if n_cells == 0:
            continue
        miss_vals = miss[mask]
        nstar_vals = nstar[mask]
        rows.append(
            {
                "band": label,
                "delta_pp_lo": lo,
                "delta_pp_hi": hi,
                "n_cells": n_cells,
                "frac_beta_gt_0.8": float((miss_vals > 0.8).mean()),
                "median_n_star_asymptotic": float(np.nanmedian(nstar_vals)),
                "median_n_star_ceiling": int(np.ceil(float(np.nanmedian(nstar_vals)))),
            }
        )
    return rows


def asymptotic_surface_error(pa: np.ndarray, pb: np.ndarray, nstar_grid: np.ndarray) -> dict:
    """Validate cached n* grid against closed-form Fleiss–Chow recomputation."""
    recomputed = np.full_like(nstar_grid, np.nan)
    valid = np.isfinite(nstar_grid)
    for i, p_a in enumerate(pa):
        for j, p_b in enumerate(pb):
            if p_b < p_a - MIN_DELTA:
                recomputed[i, j] = float(sample_size_two_proportions(float(p_a), float(p_b)))
    diff = recomputed - nstar_grid
    mask = valid & np.isfinite(recomputed)
    if not mask.any():
        return {"max_abs_error": None, "median_abs_error": None}
    abs_err = np.abs(diff[mask])
    return {
        "max_abs_error": float(np.max(abs_err)),
        "median_abs_error": float(np.median(abs_err)),
        "cells_checked": int(mask.sum()),
    }


def build_lattice_surface_model(*, force: bool = False) -> dict:
    """Cache full-surface summary + marginal Δ slices."""
    cache_path = OUT / "lattice_surface_model.json"
    if not force and cache_path.is_file():
        loaded = json.loads(cache_path.read_text(encoding="utf-8"))
        if loaded.get("spec_version") == SPEC_VERSION:
            return loaded

    grid = build_comparison_grid()
    pa, pb, power, miss, nstar = grid_arrays(grid)
    valid = np.isfinite(power)

    power_marg = marginal_power_by_delta(pa, pb, power)
    nstar_marg = marginal_nstar_by_delta(pa, pb, nstar)
    asym_check = asymptotic_surface_error(pa, pb, nstar)

    # merge marginals on delta_pp
    nstar_by_pp = {r["delta_pp"]: r for r in nstar_marg}
    merged_marginal: list[dict] = []
    for pr in power_marg:
        ns = nstar_by_pp.get(pr["delta_pp"], {})
        merged_marginal.append({**pr, **{k: v for k, v in ns.items() if k != "delta_p" and k != "delta_pp" and k != "n_cells"}})

    payload = {
        "spec_version": SPEC_VERSION,
        "n_per_arm": FOLKLORE_N,
        "lattice": {
            "pa_pct_min": 50,
            "pa_pct_max": 99,
            "pb_pct_min": 50,
            "pb_pct_max": 99,
            "n_valid_cells": int(valid.sum()),
        },
        "surfaces": {
            "power_exact_fisher_n20": "π_Fisher(p_A,p_B; n=20, α=0.05)",
            "miss_beta_n20": "1 − π_Fisher",
            "n_star_asymptotic": "Fleiss–Chow n*(p_A,p_B; 1−β=0.80)",
        },
        "summary": {
            **(grid.get("summary") or {}),
            "median_power_at_n20": float(np.nanmedian(power[valid])),
            "frac_miss_gt_0.5": float((miss[valid] > 0.5).mean()),
            "asymptotic_surface_check": asym_check,
        },
        "delta_bands": summarize_delta_bands(pa, pb, miss, nstar),
        "marginal_by_delta": merged_marginal,
        "illustrative_pair": {
            "p_a": 0.90,
            "p_b": 0.80,
            "label": "90/80",
            "note": (
                "Worked example at Δp=10 pp; not the lattice median and not the "
                "median of the 6–10 pp band."
            ),
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def export_lattice_surface_tables(out_dir: Path | None = None) -> dict[str, str]:
    """Write Table03f marginal-by-delta CSV."""
    model = build_lattice_surface_model()
    out_dir = out_dir or PAPER_TABLES
    rows = model["marginal_by_delta"]
    path = out_dir / "Table03f_marginal_by_delta.csv"
    out_dir.mkdir(parents=True, exist_ok=True)
    fields = [
        "delta_pp",
        "delta_p",
        "n_cells",
        "median_power_exact_fisher",
        "frac_power_lt_0.2",
        "median_n_star_asymptotic",
        "median_n_star_ceiling",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})
    return {"marginal_by_delta": str(path), "model_json": str(OUT / "lattice_surface_model.json")}


if __name__ == "__main__":
    paths = export_lattice_surface_tables()
    print(json.dumps(paths, indent=2))
