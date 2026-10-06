"""
Full (p_A, p_B) comparison grid for E2 folklore vs powered planning.

Caches exact Fisher power / miss β at n=20 and asymptotic n*; exports Table 3 extensions.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from lod_guide.s5_sample_size import power_two_proportions, sample_size_two_proportions
from lod_guide.theory.exact_tests import exact_power_two_proportions

OUT = Path(__file__).resolve().parents[3] / "data" / "research"
PAPER_TABLES = Path(__file__).resolve().parents[3] / "paper_artifacts" / "tables"

# Cap expensive exact OC enumeration (Fisher null rate is O(n^2)).
MAX_OC_N = 120
# Reference-pair exact power @ n* (only 8 rows; n* up to ~435 for 99/95).
MAX_REF_NSTAR_EXACT = 450

# Reference pairs annotated on Fig 1 heatmaps (Table 3 rows); primary analysis is the full lattice.
REF_PAIRS: tuple[tuple[float, float, str], ...] = (
    (0.90, 0.80, "90/80"),
    (0.95, 0.85, "95/85"),
    (0.90, 0.70, "90/70"),
    (0.90, 0.50, "90/50"),
    (0.95, 0.90, "95/90"),
    (0.80, 0.70, "80/70"),
    (0.99, 0.95, "99/95"),
    (0.85, 0.75, "85/75"),
)

FOLKLORE_N = 20
# Integer hit-rate lattice 50%–99% (inclusive): all valid E2 pairs with p_A > p_B.
PCT_GRID = np.arange(50, 100, dtype=int)
PA_GRID = PCT_GRID / 100.0
PB_GRID = PCT_GRID / 100.0
MIN_DELTA = 0.005  # require p_A > p_B (at least 1 percentage point)


def pair_slug(lab: str) -> str:
    """'90/80' -> '90_vs_80' for scenario IDs."""
    return lab.replace("/", "_vs_")


def pair_label(lab: str, n: int = FOLKLORE_N) -> str:
    """Stable Table 3 label, e.g. '90/80' -> '90_vs_80_n20'."""
    return f"{pair_slug(lab)}_n{n}"


def build_comparison_grid(*, force: bool = False) -> dict:
    """Full grid: exact power & miss β at folklore n, asymptotic n* (cached JSON)."""
    cache_path = OUT / "fig_comparison_grid_full.json"
    spec = {
        "pa_grid": PA_GRID.tolist(),
        "pb_grid": PB_GRID.tolist(),
        "pct_grid": PCT_GRID.tolist(),
        "grid_version": "integer_50_99_v2",
    }
    if not force and cache_path.is_file():
        loaded = json.loads(cache_path.read_text(encoding="utf-8"))
        if loaded.get("grid_version") == spec["grid_version"]:
            return loaded

    power = np.full((PA_GRID.size, PB_GRID.size), np.nan)
    nstar = np.full_like(power, np.nan)
    for i, pa in enumerate(PA_GRID):
        for j, pb in enumerate(PB_GRID):
            if pa > pb + MIN_DELTA:
                power[i, j] = exact_power_two_proportions(float(pa), float(pb), FOLKLORE_N, test="fisher")
                nstar[i, j] = float(sample_size_two_proportions(float(pa), float(pb)))
    miss = 1.0 - power
    valid = np.isfinite(power)
    payload = {
        **spec,
        "n_per_arm": FOLKLORE_N,
        "power_n20": np.where(np.isnan(power), None, power).tolist(),
        "miss_beta_n20": np.where(np.isnan(miss), None, miss).tolist(),
        "n_star_asymptotic": np.where(np.isnan(nstar), None, nstar).tolist(),
        "summary": {
            "n_valid_cells": int(valid.sum()),
            "frac_miss_gt_0.8": float((miss[valid] > 0.8).mean()) if valid.any() else None,
            "frac_power_lt_0.2": float((power[valid] < 0.2).mean()) if valid.any() else None,
            "median_n_star": float(np.nanmedian(nstar)),
            "max_n_star": float(np.nanmax(nstar)),
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def grid_arrays(grid: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    pa = np.array(grid["pa_grid"], float)
    pb = np.array(grid["pb_grid"], float)
    power = np.array([[np.nan if v is None else float(v) for v in row] for row in grid["power_n20"]], float)
    miss = np.array([[np.nan if v is None else float(v) for v in row] for row in grid["miss_beta_n20"]], float)
    nstar = np.array([[np.nan if v is None else float(v) for v in row] for row in grid["n_star_asymptotic"]], float)
    return pa, pb, power, miss, nstar


def reference_pair_rows(*, alpha: float = 0.05) -> list[dict]:
    """One row per REF_PAIRS with power, β, n* at folklore n=20."""
    rows: list[dict] = []
    for pa, pb, lab in REF_PAIRS:
        pw_asym = power_two_proportions(pa, pb, FOLKLORE_N, alpha)
        pw_f = exact_power_two_proportions(pa, pb, FOLKLORE_N, alpha, test="fisher")
        n_asym = float(sample_size_two_proportions(pa, pb, alpha, 0.80))
        n_star = int(np.ceil(n_asym))
        row: dict = {
            "label": pair_label(lab, FOLKLORE_N),
            "pair": lab,
            "p_a": pa,
            "p_b": pb,
            "delta_p": round(pa - pb, 4),
            "n": FOLKLORE_N,
            "power_asymptotic_pooled_z": pw_asym,
            "power_exact_fisher": pw_f,
            "miss_beta_exact_fisher": 1.0 - pw_f,
            "n_star_asymptotic": n_asym,
            "n_star_ceiling": n_star,
            "power_asymptotic_pooled_z_at_n_star": None,
            "power_exact_fisher_at_n_star": None,
            "note": "",
        }
        if n_star <= MAX_REF_NSTAR_EXACT:
            row["power_asymptotic_pooled_z_at_n_star"] = power_two_proportions(
                pa, pb, n_star, alpha
            )
            row["power_exact_fisher_at_n_star"] = exact_power_two_proportions(
                pa, pb, n_star, alpha, test="fisher"
            )
        else:
            row["note"] = f"exact power at n*={n_star} deferred (>{MAX_REF_NSTAR_EXACT})"
        rows.append(row)
    return rows


def grid_csv_rows(grid: dict | None = None) -> list[dict]:
    """Flat rows for every valid grid cell."""
    grid = grid or build_comparison_grid()
    pa, pb, power, miss, nstar = grid_arrays(grid)
    rows: list[dict] = []
    for i, pa_v in enumerate(pa):
        for j, pb_v in enumerate(pb):
            if np.isnan(power[i, j]):
                continue
            rows.append(
                {
                    "p_a": float(pa_v),
                    "p_b": float(pb_v),
                    "delta_p": round(float(pa_v - pb_v), 4),
                    "n": FOLKLORE_N,
                    "power_exact_fisher": float(power[i, j]),
                    "miss_beta_exact_fisher": float(miss[i, j]),
                    "n_star_asymptotic": float(nstar[i, j]),
                    "n_star_ceiling": int(np.ceil(nstar[i, j])),
                }
            )
    return rows


def pareto_plane_points(*, folklore_n: int = FOLKLORE_N, alpha: float = 0.05) -> list[dict]:
    """Folklore and powered OC points for each reference pair (Fig 1E)."""
    from lod_guide.research.pareto_exact_sample_size import _oc_point

    points: list[dict] = []
    for pa, pb, lab in REF_PAIRS:
        p_null = (pa + pb) / 2
        folk = _oc_point(folklore_n, p_a=pa, p_b=pb, p_null=p_null, alpha=alpha)
        n_star = int(np.ceil(sample_size_two_proportions(pa, pb, alpha, 0.80)))
        n_oc = min(n_star, MAX_OC_N)
        powered = _oc_point(n_oc, p_a=pa, p_b=pb, p_null=p_null, alpha=alpha)
        powered["n_star_requested"] = n_star
        powered["oc_n_capped"] = n_star > MAX_OC_N
        points.append(
            {
                "pair": lab,
                "p_a": pa,
                "p_b": pb,
                "folklore": folk,
                "powered_n_star": n_star,
                "powered": powered,
            }
        )
    return points


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})
    return path


def export_comparison_grid_tables(out_dir: Path | None = None) -> dict[str, str]:
    """Write Table 3 extension CSVs (reference pairs + full grid + marginal by Δ)."""
    from lod_guide.research.lattice_surface_model import export_lattice_surface_tables

    out_dir = out_dir or PAPER_TABLES
    build_comparison_grid()
    ref_rows = reference_pair_rows()
    grid_rows = grid_csv_rows()

    ref_path = _write_csv(
        out_dir / "Table03_reference_pairs_n20.csv",
        ref_rows,
        [
            "label",
            "pair",
            "p_a",
            "p_b",
            "delta_p",
            "n",
            "power_asymptotic_pooled_z",
            "power_exact_fisher",
            "miss_beta_exact_fisher",
            "n_star_asymptotic",
            "n_star_ceiling",
            "power_asymptotic_pooled_z_at_n_star",
            "power_exact_fisher_at_n_star",
            "note",
        ],
    )
    grid_path = _write_csv(
        out_dir / "Table03_comparison_grid_n20.csv",
        grid_rows,
        [
            "p_a",
            "p_b",
            "delta_p",
            "n",
            "power_exact_fisher",
            "miss_beta_exact_fisher",
            "n_star_asymptotic",
            "n_star_ceiling",
        ],
    )
    lattice_paths = export_lattice_surface_tables(out_dir)
    return {"reference_pairs": str(ref_path), "full_grid": str(grid_path), **lattice_paths}


def compare_asymptotic_scenarios() -> list[tuple[str, float, float, int]]:
    """Default scenarios for compare_asymptotic_vs_exact (Table 3 primary)."""
    scenarios: list[tuple[str, float, float, int]] = [
        (pair_label(lab, FOLKLORE_N), pa, pb, FOLKLORE_N)
        for pa, pb, lab in REF_PAIRS
    ]
    scenarios.extend(
        [
            ("90_vs_80_n30", 0.90, 0.80, 30),
            ("90_vs_80_n50", 0.90, 0.80, 50),
            ("90_vs_80_n199", 0.90, 0.80, 199),
            ("95_vs_85_n30", 0.95, 0.85, 30),
            ("95_vs_90_n40", 0.95, 0.90, 40),
        ]
    )
    return scenarios


if __name__ == "__main__":
    paths = export_comparison_grid_tables()
    print(json.dumps(paths, indent=2))
    print(f"grid cells: {len(grid_csv_rows())}")
