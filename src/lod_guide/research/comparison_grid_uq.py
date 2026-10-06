"""
Tier-2 UQ — sensitivity bands for E2 comparison-grid heatmaps (Fig 1B–C).

Closed-form asymptotic surfaces bracket exact Fisher @ n=20 (panel B) and
Fleiss–Chow n* @ 80% power (panel C). Exported to supplement CSV/JSON.
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
from lod_guide.s5_sample_size import power_two_proportions, sample_size_two_proportions

OUT = Path(__file__).resolve().parents[3] / "data" / "research"
PAPER_TABLES = Path(__file__).resolve().parents[3] / "paper_artifacts" / "tables"

ALPHA_BANDS = (0.01, 0.05, 0.10)
POWER_TARGETS = (0.70, 0.80, 0.90)
P8_GAP_THRESHOLD = 0.05


def _valid_mask() -> np.ndarray:
    pa = PA_GRID[:, None]
    pb = PB_GRID[None, :]
    return pa > pb + MIN_DELTA


def asymptotic_miss_beta_surface(
    *,
    alpha: float = 0.05,
    n: int = FOLKLORE_N,
) -> np.ndarray:
    """Miss β = 1 − asymptotic pooled-z power on the integer lattice."""
    miss = np.full((PA_GRID.size, PB_GRID.size), np.nan)
    valid = _valid_mask()
    for i, pa in enumerate(PA_GRID):
        for j, pb in enumerate(PB_GRID):
            if valid[i, j]:
                pw = power_two_proportions(float(pa), float(pb), n, alpha)
                miss[i, j] = 1.0 - pw
    return miss


def nstar_surface(*, alpha: float = 0.05, target_power: float = 0.80) -> np.ndarray:
    """Fleiss–Chow n* per arm on the integer lattice."""
    nstar = np.full((PA_GRID.size, PB_GRID.size), np.nan)
    valid = _valid_mask()
    for i, pa in enumerate(PA_GRID):
        for j, pb in enumerate(PB_GRID):
            if valid[i, j]:
                nstar[i, j] = float(sample_size_two_proportions(float(pa), float(pb), alpha, target_power))
    return nstar


def p8_gap_mask(*, alpha: float = 0.05, n: int = FOLKLORE_N) -> np.ndarray:
    """Cells where asymptotic power exceeds exact Fisher by > threshold (P8 regime)."""
    grid = build_comparison_grid()
    _, _, power_exact, _, _ = grid_arrays(grid)
    miss_asym = asymptotic_miss_beta_surface(alpha=alpha, n=n)
    power_asym = 1.0 - miss_asym
    gap = power_asym - power_exact
    return np.isfinite(gap) & (gap > P8_GAP_THRESHOLD)


def build_grid_uq_summary(*, force: bool = False) -> dict:
    """Cache sensitivity summaries for heatmap overlays and supplement export."""
    cache_path = OUT / "comparison_grid_uq.json"
    spec_version = "tier2_v1"
    if not force and cache_path.is_file():
        loaded = json.loads(cache_path.read_text(encoding="utf-8"))
        if loaded.get("spec_version") == spec_version:
            return loaded

    grid = build_comparison_grid()
    pa, pb, power_exact, miss_exact, nstar_80 = grid_arrays(grid)
    valid = _valid_mask()

    miss_by_alpha = {
        str(a): asymptotic_miss_beta_surface(alpha=a).tolist()
        for a in ALPHA_BANDS
    }
    nstar_by_power = {
        str(p): nstar_surface(target_power=p).tolist()
        for p in POWER_TARGETS
    }
    gap_mask = p8_gap_mask()

    frac_beta08 = {}
    for a in ALPHA_BANDS:
        miss_a = np.array(miss_by_alpha[str(a)])
        frac_beta08[f"alpha_{a:.2f}"] = float((miss_a[valid] > 0.8).mean())

    payload = {
        "spec_version": spec_version,
        "n_per_arm": FOLKLORE_N,
        "alpha_bands": list(ALPHA_BANDS),
        "power_targets": list(POWER_TARGETS),
        "p8_gap_threshold": P8_GAP_THRESHOLD,
        "miss_beta_asymptotic_by_alpha": miss_by_alpha,
        "n_star_by_target_power": nstar_by_power,
        "p8_gap_mask": gap_mask.tolist(),
        "summary": {
            "frac_miss_gt_0.8_exact_fisher": float((miss_exact[valid] > 0.8).mean()),
            **frac_beta08,
            "frac_p8_gap_cells": float(gap_mask[valid].mean()),
            "median_n_star_70": float(np.nanmedian(nstar_by_power["0.7"])),
            "median_n_star_80": float(np.nanmedian(nstar_by_power["0.8"])),
            "median_n_star_90": float(np.nanmedian(nstar_by_power["0.9"])),
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def export_grid_uq_tables(out_dir: Path | None = None) -> dict[str, str]:
    """Supplement: headline sensitivity rows + P8 gap cell counts."""
    uq = build_grid_uq_summary()
    out = out_dir or PAPER_TABLES
    out.mkdir(parents=True, exist_ok=True)

    summary_path = out / "Table03d_grid_uq_sensitivity.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        for k, v in uq["summary"].items():
            w.writerow([k, v])
        w.writerow(["alpha_bands", ";".join(str(a) for a in uq["alpha_bands"])])
        w.writerow(["power_targets", ";".join(str(p) for p in uq["power_targets"])])

    p8_path = out / "Table03e_p8_gap_cells.csv"
    gap = np.array(uq["p8_gap_mask"], dtype=bool)
    valid = _valid_mask()
    with p8_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["p_a_pct", "p_b_pct", "p8_gap_flag"])
        for i, pa in enumerate(PA_GRID):
            for j, pb in enumerate(PB_GRID):
                if valid[i, j] and gap[i, j]:
                    w.writerow([int(round(pa * 100)), int(round(pb * 100)), 1])

    return {"summary": str(summary_path), "p8_gap": str(p8_path)}


def sensitivity_contour_levels(panel: str) -> dict:
    """Levels and labels for Fig 1 embedded overlays."""
    uq = build_grid_uq_summary()
    if panel == "miss_beta":
        return {
            "surfaces": {
                "lo": np.array(uq["miss_beta_asymptotic_by_alpha"]["0.01"], float),
                "mid": np.array(uq["miss_beta_asymptotic_by_alpha"]["0.05"], float),
                "hi": np.array(uq["miss_beta_asymptotic_by_alpha"]["0.1"], float),
            },
            "level": 0.8,
            "labels": (r"$\alpha=0.01$", r"$\alpha=0.10$"),
        }
    if panel == "n_star":
        return {
            "surfaces": {
                "lo": np.array(uq["n_star_by_target_power"]["0.7"], float),
                "mid": np.array(uq["n_star_by_target_power"]["0.8"], float),
                "hi": np.array(uq["n_star_by_target_power"]["0.9"], float),
            },
            "level": None,
            "labels": (r"70% power", r"90% power"),
        }
    raise ValueError(f"unknown panel: {panel}")
