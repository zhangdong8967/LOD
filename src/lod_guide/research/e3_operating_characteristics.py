"""
E3 qualitative pass-rule operating characteristics (k/n positives).

Exports supplement Table 9: P(X >= k | p, n) and minimal n for reliability targets.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from lod_guide.s4_models import detect_prob_at_least_k
from lod_guide.s5_sample_size import power_two_proportions
from lod_guide.theory.exact_tests import exact_power_two_proportions

OUT = Path(__file__).resolve().parents[3] / "data" / "research"
PAPER_TABLES = Path(__file__).resolve().parents[3] / "paper_artifacts" / "tables"

E3_N_VALUES = (10, 20, 30, 60)
E3_P_PCT = tuple(range(80, 100))  # 80–99% integers
RELIABILITY_TARGET = 0.95


def k_values_for_n(n: int) -> tuple[int, ...]:
    """Folklore-aligned pass rules: k ∈ {n−1, n−2, n−3} (e.g. 19/20 at n=20)."""
    return tuple(k for k in (n - 1, n - 2, n - 3) if k >= 1)


def pass_probability(*, p: float, n: int, k: int) -> float:
    """P(X >= k | Binomial(n, p))."""
    k = int(k)
    n = int(n)
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return detect_prob_at_least_k(float(p), n, k)


def min_n_for_pass(*, p: float, k: int, target: float = RELIABILITY_TARGET, n_max: int = 200) -> int | None:
    """Smallest n in [k, n_max] with P(X >= k | p, n) >= target."""
    for n in range(int(k), n_max + 1):
        if pass_probability(p=p, n=n, k=k) >= target:
            return n
    return None


def e3_grid_rows() -> list[dict]:
    rows: list[dict] = []
    for p_pct in E3_P_PCT:
        p = p_pct / 100.0
        for n in E3_N_VALUES:
            for k in k_values_for_n(n):
                p_pass = pass_probability(p=p, n=n, k=k)
                rows.append(
                    {
                        "p_pct": p_pct,
                        "p": round(p, 4),
                        "n": n,
                        "k": k,
                        "pass_rule": f"{k}/{n}",
                        "P_pass": round(p_pass, 6),
                        "P_fail": round(1.0 - p_pass, 6),
                    }
                )
    return rows


def e3_reliability_summary_rows(*, target: float = RELIABILITY_TARGET) -> list[dict]:
    """Minimal n for P(pass | p) >= target (folklore k rules at n=20 scale)."""
    rows: list[dict] = []
    for p_pct in (90, 95, 99):
        p = p_pct / 100.0
        for k in (19, 18, 17):
            n_min = min_n_for_pass(p=p, k=k, target=target)
            rows.append(
                {
                    "k": k,
                    "p_pct": p_pct,
                    "target_P_pass": target,
                    "min_n": n_min,
                    "pass_rule_at_min_n": f"{k}/{n_min}" if n_min else "",
                    "P_pass_at_min_n": (
                        round(pass_probability(p=p, n=n_min, k=k), 6) if n_min else None
                    ),
                }
            )
    return rows


def e3_vs_e2_confusion_rows(*, n: int = 20, alpha: float = 0.05) -> list[dict]:
    """
    Same (p_A, p_B): both arms pass k/n while Fisher still has high miss β.
    Headline + three adjacent pairs.
    """
    pairs = (
        (0.90, 0.80, 19),  # folklore 19/20 @ n=20
        (0.95, 0.85, 19),
        (0.90, 0.70, 19),
        (0.95, 0.90, 19),
    )
    rows: list[dict] = []
    for pa, pb, k in pairs:
        pw_f = exact_power_two_proportions(pa, pb, n, alpha, test="fisher")
        p_pass_a = pass_probability(p=pa, n=n, k=k)
        p_pass_b = pass_probability(p=pb, n=n, k=k)
        p_both = p_pass_a * p_pass_b
        rows.append(
            {
                "pair": f"{int(round(pa*100))}/{int(round(pb*100))}",
                "p_a": pa,
                "p_b": pb,
                "n_per_arm": n,
                "k": k,
                "pass_rule": f"{k}/{n}",
                "P_pass_arm_a": round(p_pass_a, 6),
                "P_pass_arm_b": round(p_pass_b, 6),
                "P_both_arms_pass": round(p_both, 6),
                "exact_fisher_power": round(pw_f, 6),
                "miss_beta_fisher": round(1.0 - pw_f, 6),
                "asymptotic_power_pooled_z": round(power_two_proportions(pa, pb, n, alpha), 6),
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})
    return path


def run_e3_operating_characteristics_study() -> dict:
    grid = e3_grid_rows()
    summary = e3_reliability_summary_rows()
    confusion = e3_vs_e2_confusion_rows()

    payload = {
        "study_id": "E3-OPERATING-CHARACTERISTICS-v1",
        "grid": grid,
        "reliability_summary": summary,
        "e3_vs_e2_confusion": confusion,
        "policy": {
            "interpretation": (
                "E3 pass rules (k/n) quantify rule reliability; they do not substitute "
                "for E2 two-proportion power planning."
            ),
            "reliability_target": RELIABILITY_TARGET,
        },
    }
    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "e3_operating_characteristics.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    grid_path = _write_csv(
        PAPER_TABLES / "Table09_e3_operating_characteristics.csv",
        grid,
        ["p_pct", "p", "n", "k", "pass_rule", "P_pass", "P_fail"],
    )
    summary_path = _write_csv(
        PAPER_TABLES / "Table09b_e3_reliability_min_n.csv",
        summary,
        ["k", "p_pct", "target_P_pass", "min_n", "pass_rule_at_min_n", "P_pass_at_min_n"],
    )
    confusion_path = _write_csv(
        PAPER_TABLES / "Table09c_e3_vs_e2_confusion_n20.csv",
        confusion,
        [
            "pair",
            "p_a",
            "p_b",
            "n_per_arm",
            "k",
            "pass_rule",
            "P_pass_arm_a",
            "P_pass_arm_b",
            "P_both_arms_pass",
            "exact_fisher_power",
            "miss_beta_fisher",
            "asymptotic_power_pooled_z",
        ],
    )
    payload["path"] = str(json_path)
    payload["tables"] = {
        "grid": str(grid_path),
        "reliability_summary": str(summary_path),
        "g4_vs_g2": str(confusion_path),
    }
    return payload


if __name__ == "__main__":
    out = run_e3_operating_characteristics_study()
    print(json.dumps({k: out[k] for k in ("study_id", "tables", "path")}, indent=2))
