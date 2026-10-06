"""
Aggregate reliability statistics for Supplement §S2c (P8 lattice, assumptions).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "research"
TABLE03E = ROOT / "paper_artifacts" / "tables" / "Table03e_p8_gap_cells.csv"
PARETO_JSON = OUT / "pareto_exact_sample_size.json"
UNDOM_JSON = OUT / "pareto_lattice_undominated.json"


def _count_table03e_cells() -> int:
    if not TABLE03E.is_file():
        return 0
    with TABLE03E.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def run_reliability_summaries() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    n_gap = _count_table03e_cells()
    n_lattice = 1225
    payload: dict = {
        "study_id": "RELIABILITY-SUMMARY-v1",
        "e2_lattice_cells": n_lattice,
        "p8_gap_cells_gt_0p05": n_gap,
        "p8_gap_fraction": round(n_gap / n_lattice, 4) if n_lattice else None,
        "p8_interpretation": (
            f"{n_gap}/{n_lattice} lattice cells at n=20 have asymptotic pooled-z power "
            "exceeding exact Fisher power by >0.05 (Table03e)."
        ),
        "assumptions_default_loop": {
            "independence": "replicates independent within arm (DE=1 unless stated)",
            "binary_hit_rate": "detection is Bernoulli at c*",
            "e2_test": "two-sided exact Fisher at H0: p_A = p_B",
            "e2_type_i": "exact rejection rate under pooled-null simulator (Supplement S2c)",
            "design_vs_confirm": "Fleiss-Chow pooled-z for S5; exact Fisher for S6 ledger",
        },
    }
    if PARETO_JSON.is_file():
        p = json.loads(PARETO_JSON.read_text(encoding="utf-8"))
        payload["p18_lattice_scan"] = p.get("lattice_scan") or p.get("headline", {})
    if UNDOM_JSON.is_file():
        payload["p18_undominated"] = json.loads(UNDOM_JSON.read_text(encoding="utf-8"))

    path = OUT / "reliability_summary.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload
