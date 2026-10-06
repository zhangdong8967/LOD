"""
Multiplicity and sequential LoD verification.

1) Multi-reagent / multi-lot E2: Holm–Bonferroni on Boschloo (or Fisher) p-values.
2) Sequential E1 hit-rate looks: Pocock and O'Brien–Fleming style α-spending
   approximations for K interim analyses of a binomial claim.

These close the algorithm gap on family-wise error when labs test many kits
or peek at accumulating hits.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from lod_guide.theory.exact_tests import analyze_two_proportions_exact

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def holm_adjust(pvalues: list[float]) -> list[float]:
    """Holm–Bonferroni adjusted p-values (step-down), same order as input."""
    m = len(pvalues)
    order = np.argsort(pvalues)
    adj = np.empty(m, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        factor = m - rank
        cand = factor * pvalues[idx]
        running = max(running, cand)
        adj[idx] = min(1.0, running)
    return adj.tolist()


def multi_reagent_holm(
    tables: list[dict],
    *,
    alpha: float = 0.05,
    method: str = "boschloo",
) -> dict:
    """
    tables: list of {label, a, n_a, b, n_b}
    """
    raw = []
    for t in tables:
        res = analyze_two_proportions_exact(t["a"], t["n_a"], t["b"], t["n_b"])
        if method == "fisher":
            p = res.fisher_p_two_sided
        elif method == "barnard_diff":
            p = res.barnard_diff_p_two_sided
        else:
            p = res.boschloo_p_two_sided
        raw.append(
            {
                "label": t["label"],
                "raw_p": p,
                "fisher_p": res.fisher_p_two_sided,
                "boschloo_p": res.boschloo_p_two_sided,
                "barnard_diff_p": res.barnard_diff_p_two_sided,
            }
        )
    adj = holm_adjust([r["raw_p"] for r in raw])
    rows = []
    for r, p_adj in zip(raw, adj, strict=True):
        rows.append(
            {
                "label": r["label"],
                "raw_p": r["raw_p"],
                "holm_p": p_adj,
                "reject_at_alpha": p_adj < alpha,
                "fisher_p": r["fisher_p"],
                "boschloo_p": r["boschloo_p"],
                "barnard_diff_p": r["barnard_diff_p"],
            }
        )
    return {
        "alpha": alpha,
        "method": method,
        "n_tests": len(rows),
        "n_reject_raw": sum(1 for r in rows if r["raw_p"] < alpha),
        "n_reject_holm": sum(1 for r in rows if r["reject_at_alpha"]),
        "rows": rows,
    }


def alpha_spending_boundaries(k: int, alpha: float = 0.05, *, spending: str = "obf") -> list[float]:
    """
    Approximate two-sided Z critical values at equally spaced information fractions.
    Pocock: constant critical value; OBF: decreasing α early, more at end.
    """
    if k < 1:
        raise ValueError("k>=1")
    # Information fractions
    t = np.arange(1, k + 1) / k
    if spending == "pocock":
        # Solve approx: α_k ≈ 1 - Φ(c)^2... use known Pocock constants table for common K
        pocock_c = {1: 1.96, 2: 2.178, 3: 2.289, 4: 2.361, 5: 2.413}
        c = pocock_c.get(k, 2.5)
        return [float(c)] * k
    # O'Brien–Fleming: c / sqrt(t)
    # Choose c so final boundary ≈ 1.96
    c = 1.96
    return [float(c / np.sqrt(ti)) for ti in t]


def sequential_binomial_looks(
    hits: list[int],
    ns: list[int],
    *,
    p0: float = 0.95,
    alpha: float = 0.05,
    spending: str = "obf",
) -> dict:
    """
    Score-test Z for H0: p = p0 at each look; compare to spending boundaries.
    hits[i], ns[i] are cumulative.
    """
    assert len(hits) == len(ns)
    k = len(ns)
    bounds = alpha_spending_boundaries(k, alpha, spending=spending)
    rows = []
    stopped = None
    for i, (h, n, zcrit) in enumerate(zip(hits, ns, bounds, strict=True)):
        phat = h / n if n else 0.0
        se = np.sqrt(p0 * (1 - p0) / n) if n else np.inf
        z = (phat - p0) / se if se > 0 else 0.0
        # two-sided
        reject = abs(z) >= zcrit
        rows.append(
            {
                "look": i + 1,
                "n": n,
                "hits": h,
                "phat": phat,
                "z": float(z),
                "z_critical": zcrit,
                "reject_H0": bool(reject),
            }
        )
        if reject and stopped is None:
            stopped = i + 1
    return {
        "p0": p0,
        "alpha": alpha,
        "spending": spending,
        "boundaries": bounds,
        "stop_look": stopped,
        "rows": rows,
    }


def run_multiplicity_sequential_study() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    # Illustrative multi-lot tables near LoD
    tables = [
        {"label": "lotA_vs_lotB", "a": 18, "n_a": 20, "b": 14, "n_b": 20},
        {"label": "lotA_vs_lotC", "a": 18, "n_a": 20, "b": 16, "n_b": 20},
        {"label": "lotB_vs_lotC", "a": 14, "n_a": 20, "b": 16, "n_b": 20},
        {"label": "kit1_vs_kit2", "a": 19, "n_a": 20, "b": 12, "n_b": 20},
    ]
    holm = multi_reagent_holm(tables, alpha=0.05, method="boschloo")

    # Sequential looks: accumulating hits under true p=0.90 while claiming 0.95
    rng = np.random.default_rng(7)
    true_p = 0.90
    schedule = [10, 20, 30, 40]
    draws = rng.binomial(1, true_p, size=schedule[-1])
    hits_c, ns_c = [], []
    for n in schedule:
        hits_c.append(int(draws[:n].sum()))
        ns_c.append(n)
    seq_obf = sequential_binomial_looks(hits_c, ns_c, p0=0.95, spending="obf")
    seq_poc = sequential_binomial_looks(hits_c, ns_c, p0=0.95, spending="pocock")

    # Family-wise: probability ≥1 false reject if m independent true-null Fisher
    # (Boschloo MC is too heavy here; Fisher sketch for FWER education)
    m = 4
    n_mc = 1500
    false_raw = 0
    false_holm = 0
    from lod_guide.theory.exact_tests import fisher_pvalue

    for _ in range(n_mc):
        ps = []
        for _j in range(m):
            a = int(rng.binomial(20, 0.5))
            b = int(rng.binomial(20, 0.5))
            ps.append(fisher_pvalue(a, 20, b, 20))
        if any(p < 0.05 for p in ps):
            false_raw += 1
        if any(p < 0.05 for p in holm_adjust(ps)):
            false_holm += 1

    payload = {
        "study_id": "MULTIPLICITY-SEQUENTIAL-v1",
        "holm_example": holm,
        "sequential_example": {"obf": seq_obf, "pocock": seq_poc, "true_p": true_p},
        "fwer_mc": {
            "m": m,
            "n_per_arm": 20,
            "n_mc": n_mc,
            "fwer_raw": false_raw / n_mc,
            "fwer_holm": false_holm / n_mc,
            "nominal_alpha": 0.05,
        },
        "headline": {
            "holm_rejects": holm["n_reject_holm"],
            "raw_rejects": holm["n_reject_raw"],
            "fwer_raw": false_raw / n_mc,
            "fwer_holm": false_holm / n_mc,
            "sequential_stop_obf": seq_obf["stop_look"],
        },
        "claim_boundary": (
            "Holm controls FWER under arbitrary dependence of tests. "
            "α-spending boundaries are large-sample approximations for binomial looks; "
            "use as planning/education, confirm with exact methods at the terminal look."
        ),
    }
    path = OUT / "multiplicity_sequential.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_multiplicity_sequential_study()["headline"], indent=2))
