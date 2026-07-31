"""
Continuous parameter-space models for LoD guidance (not discrete anecdotes).

Examples like n∈{5,10} or (p_A,p_B)∈{(0.9,0.8),(0.9,0.5)} are *slices*
of the following fields defined on continuous (or finely discretized) domains:

1. All-positive field
       f(p, n) = P(X=n | p) = p^n,           p ∈ (0,1], n ≥ 1
       L(n; α) = α^{1/n}                     (one-sided lower after n/n)
       B(n; p0) = p0^{n+1}                   (Uniform-prior P(p<p0|X=n))

2. Discrimination fields
       n*(p_A, p_B; α, 1-β)                  Fleiss–Chow continuous surface
       β(n; p_A, p_B, α) = 1 - power(...)    miss-probability field

3. Concentration field
       p(r), pass(r), miss(r) for r = c/LoD ∈ (0, ∞)  (log-grid in practice)

Grids are written under data/research/continuous_models/ for transparent reuse.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from lod_guide.research.concentration_relative import (
    KitCurve,
    evaluate_concentration_grid,
)
from lod_guide.s5_sample_size import power_two_proportions, sample_size_two_proportions

OUT_DIR = Path(__file__).resolve().parents[3] / "data" / "research" / "continuous_models"


def build_all_positive_field(
    *,
    p_grid: np.ndarray | None = None,
    n_grid: np.ndarray | None = None,
    alpha: float = 0.05,
    claim_p0: float = 0.95,
) -> dict:
    """Dense field f(p,n)=p^n plus L(n), B(n;p0)."""
    if p_grid is None:
        p_grid = np.linspace(0.01, 1.0, 200)
    if n_grid is None:
        n_grid = np.arange(1, 121)  # n=1..120 continuous-enough for practice
    P, N = np.meshgrid(p_grid, n_grid, indexing="xy")
    # avoid 0**0; p in (0,1]
    F = np.power(P, N)

    n_vec = n_grid.astype(float)
    L_one = alpha ** (1.0 / n_vec)
    L_two = (alpha / 2.0) ** (1.0 / n_vec)
    B = claim_p0 ** (n_vec + 1.0)
    # n required so one-sided lower >= claim: alpha**(1/n) >= p0 => n >= log(alpha)/log(p0)
    n_min_claim = float(np.ceil(np.log(alpha) / np.log(claim_p0))) if 0 < claim_p0 < 1 else np.nan

    return {
        "model_id": "ALLPOS-FIELD-v1",
        "formulae": {
            "f_p_n": "p**n",
            "L_one_sided": "alpha**(1/n)",
            "L_two_sided_CP": "(alpha/2)**(1/n)",
            "B_uniform": "p0**(n+1)",
            "n_min_for_L_one_ge_p0": "ceil(log(alpha)/log(p0))",
        },
        "p_grid": p_grid.tolist(),
        "n_grid": n_grid.tolist(),
        "F_p_n": F.tolist(),
        "L_one_sided": L_one.tolist(),
        "L_two_sided": L_two.tolist(),
        "B_p_below_claim": B.tolist(),
        "alpha": alpha,
        "claim_p0": claim_p0,
        "n_min_onesided_lower_ge_claim": n_min_claim,
    }


def build_discrimination_field(
    *,
    p_a_grid: np.ndarray | None = None,
    p_b_grid: np.ndarray | None = None,
    n_grid: np.ndarray | None = None,
    alpha: float = 0.05,
    power_target: float = 0.80,
    n_star_cap: float = 5000.0,
) -> dict:
    """
    Surfaces on (p_A, p_B):
      n_star(p_A,p_B), and for each n in n_grid: miss β(n;p_A,p_B).
    Only upper triangle p_A > p_B is scientifically comparative; diagonal = H0.
    """
    if p_a_grid is None:
        p_a_grid = np.linspace(0.05, 0.99, 95)
    if p_b_grid is None:
        p_b_grid = np.linspace(0.05, 0.99, 95)
    if n_grid is None:
        n_grid = np.array([5, 10, 20, 30, 50, 100, 150, 200, 300], dtype=int)

    n_star = np.full((p_a_grid.size, p_b_grid.size), np.nan)
    delta = np.full_like(n_star, np.nan)
    for i, pa in enumerate(p_a_grid):
        for j, pb in enumerate(p_b_grid):
            if pa <= pb + 1e-15:
                continue
            delta[i, j] = pa - pb
            try:
                ns = sample_size_two_proportions(float(pa), float(pb), alpha, power_target)
                n_star[i, j] = min(ns, n_star_cap) if np.isfinite(ns) else n_star_cap
            except Exception:
                n_star[i, j] = n_star_cap

    miss = {}
    for n in n_grid:
        m = np.full_like(n_star, np.nan)
        for i, pa in enumerate(p_a_grid):
            for j, pb in enumerate(p_b_grid):
                if pa <= pb + 1e-15:
                    continue
                m[i, j] = 1.0 - power_two_proportions(float(pa), float(pb), int(n), alpha)
        miss[str(int(n))] = m.tolist()

    # continuous Δ view: fix p_bar, vary delta — p_a=p_bar+d/2, p_b=p_bar-d/2
    p_bar_grid = np.linspace(0.2, 0.9, 36)
    delta_grid = np.linspace(0.02, 0.6, 40)
    n_star_pbardelta = np.full((p_bar_grid.size, delta_grid.size), np.nan)
    for i, p_bar in enumerate(p_bar_grid):
        for j, d in enumerate(delta_grid):
            pa = p_bar + d / 2
            p_lo = p_bar - d / 2
            if not (0.01 < p_lo < pa < 0.99):
                continue
            ns = sample_size_two_proportions(float(pa), float(p_lo), alpha, power_target)
            n_star_pbardelta[i, j] = min(ns, n_star_cap) if np.isfinite(ns) else n_star_cap

    return {
        "model_id": "DISCRIM-FIELD-v1",
        "formulae": {
            "n_star": "Fleiss-Chow equal-arm two-proportion",
            "miss_beta": "1 - asymptotic two-proportion power",
        },
        "alpha": alpha,
        "power_target": power_target,
        "p_a_grid": p_a_grid.tolist(),
        "p_b_grid": p_b_grid.tolist(),
        "delta_pa_pb": delta.tolist(),
        "n_star_pa_pb": n_star.tolist(),
        "n_grid_for_miss": n_grid.tolist(),
        "miss_beta_by_n": miss,
        "p_bar_grid": p_bar_grid.tolist(),
        "delta_grid": delta_grid.tolist(),
        "n_star_pbar_delta": n_star_pbardelta.tolist(),
        "n_star_cap": n_star_cap,
        "note": "Discrete examples (0.9 vs 0.8, 0.9 vs 0.5) are points on these surfaces.",
    }


def build_concentration_field(
    *,
    r_grid: np.ndarray | None = None,
    n_verify: int = 20,
    n_compare: int = 20,
    claim_p0: float = 0.95,
) -> dict:
    """
    Continuous r = c/LoD from near 0+ to large (practical log-grid ~ (0,∞)).
    """
    if r_grid is None:
        # (0, ∞) practically: 0.05 .. 20 on log scale
        r_grid = np.logspace(np.log10(0.05), np.log10(20.0), 120)

    # Kit B shifted so p_B(1)=0.80
    slope = 2.0
    gamma = 0.95
    from scipy.special import logit

    shift = (logit(gamma) - logit(0.80)) / slope
    kit_a = KitCurve("A", slope=slope, gamma=gamma, lod_shift_log10=0.0)
    kit_b = KitCurve("B", slope=slope, gamma=gamma, lod_shift_log10=float(shift))

    payload = evaluate_concentration_grid(
        relative_levels=tuple(float(x) for x in r_grid),
        n_verify=n_verify,
        n_compare=n_compare,
        claim_p0=claim_p0,
        kit_a=kit_a,
        kit_b=kit_b,
    )
    # denser continuous vectors
    r = np.array([row["r_c_over_LoD_ref"] for row in payload["rows"]], dtype=float)
    return {
        "model_id": "CONC-FIELD-v1",
        "domain": "r=c/LoD in (0, ∞) via log-grid",
        "r_grid": r.tolist(),
        "p_A": [row["p_A"] for row in payload["rows"]],
        "p_B": [row["p_B"] for row in payload["rows"]],
        "delta_p": [row["delta_p"] for row in payload["rows"]],
        "P_pass_A_rate_ge_claim": [row["P_pass_A_rate_ge_claim"] for row in payload["rows"]],
        "P_pass_A_all_positive": [row["P_pass_A_all_positive_n"] for row in payload["rows"]],
        "compare_miss_beta": [row["compare_miss_beta"] for row in payload["rows"]],
        "n_star_80": [row["n_star_80_for_this_delta"] for row in payload["rows"]],
        "kit_a": payload["kit_a"],
        "kit_b": payload["kit_b"],
        "n_verify": n_verify,
        "n_compare": n_compare,
        "claim_p0": claim_p0,
        "zone_narrative": payload["zone_narrative"],
    }


def query_all_positive(p: float, n: float, *, alpha: float = 0.05, claim_p0: float = 0.95) -> dict:
    """Point query on the continuous all-positive model (n may be non-integer theoretically)."""
    n_i = max(int(np.floor(n)), 1)
    return {
        "p": p,
        "n": n_i,
        "P_all_positive": float(p**n_i),
        "L_one_sided": float(alpha ** (1.0 / n_i)),
        "L_two_sided": float((alpha / 2.0) ** (1.0 / n_i)),
        "B_p_below_claim": float(claim_p0 ** (n_i + 1)),
    }


def query_discrimination(p_a: float, p_b: float, n: int, *, alpha: float = 0.05) -> dict:
    if p_a < p_b:
        p_a, p_b = p_b, p_a
    n_star = sample_size_two_proportions(p_a, p_b, alpha, 0.80)
    power = power_two_proportions(p_a, p_b, n, alpha)
    return {
        "p_a": p_a,
        "p_b": p_b,
        "delta": p_a - p_b,
        "n": n,
        "n_star_80": float(n_star),
        "power": float(power),
        "miss_beta": float(1.0 - power),
    }


def build_all_continuous_models(*, fine: bool = True) -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if fine:
        allpos = build_all_positive_field(
            p_grid=np.linspace(0.01, 1.0, 200),
            n_grid=np.arange(1, 121),
        )
        disc = build_discrimination_field(
            p_a_grid=np.linspace(0.05, 0.99, 95),
            p_b_grid=np.linspace(0.05, 0.99, 95),
        )
    else:
        # coarser for quick CI
        allpos = build_all_positive_field(
            p_grid=np.linspace(0.05, 1.0, 40),
            n_grid=np.arange(1, 61),
        )
        disc = build_discrimination_field(
            p_a_grid=np.linspace(0.1, 0.95, 30),
            p_b_grid=np.linspace(0.1, 0.95, 30),
            n_grid=np.array([5, 10, 20, 50, 100]),
        )
    conc = build_concentration_field()

    # save npz for numeric arrays + json metadata
    np.savez_compressed(
        OUT_DIR / "all_positive_field.npz",
        p_grid=np.array(allpos["p_grid"]),
        n_grid=np.array(allpos["n_grid"]),
        F=np.array(allpos["F_p_n"]),
        L_one=np.array(allpos["L_one_sided"]),
        L_two=np.array(allpos["L_two_sided"]),
        B=np.array(allpos["B_p_below_claim"]),
    )
    np.savez_compressed(
        OUT_DIR / "discrimination_field.npz",
        p_a_grid=np.array(disc["p_a_grid"]),
        p_b_grid=np.array(disc["p_b_grid"]),
        n_star=np.array(disc["n_star_pa_pb"]),
        delta=np.array(disc["delta_pa_pb"]),
        p_bar_grid=np.array(disc["p_bar_grid"]),
        delta_grid=np.array(disc["delta_grid"]),
        n_star_pbar_delta=np.array(disc["n_star_pbar_delta"]),
    )
    # miss fields separately (dict of n)
    for n_key, mat in disc["miss_beta_by_n"].items():
        np.savez_compressed(
            OUT_DIR / f"discrimination_miss_n{n_key}.npz",
            miss=np.array(mat),
            p_a_grid=np.array(disc["p_a_grid"]),
            p_b_grid=np.array(disc["p_b_grid"]),
        )
    np.savez_compressed(
        OUT_DIR / "concentration_field.npz",
        r=np.array(conc["r_grid"]),
        p_A=np.array(conc["p_A"]),
        p_B=np.array(conc["p_B"]),
        delta_p=np.array(conc["delta_p"]),
        pass_A=np.array(conc["P_pass_A_rate_ge_claim"]),
        miss=np.array(conc["compare_miss_beta"]),
        n_star=np.array([np.nan if v is None else v for v in conc["n_star_80"]], dtype=float),
    )

    meta = {
        "models": ["ALLPOS-FIELD-v1", "DISCRIM-FIELD-v1", "CONC-FIELD-v1"],
        "all_positive_summary": {
            "n_min_onesided_lower_ge_0.95": allpos["n_min_onesided_lower_ge_claim"],
            "shape_F": list(np.array(allpos["F_p_n"]).shape),
        },
        "discrimination_summary": {
            "shape_n_star": list(np.array(disc["n_star_pa_pb"]).shape),
            "example_points": {
                "0.90_vs_0.80": query_discrimination(0.90, 0.80, 20),
                "0.90_vs_0.50": query_discrimination(0.90, 0.50, 20),
            },
        },
        "concentration_summary": {
            "r_min": conc["r_grid"][0],
            "r_max": conc["r_grid"][-1],
            "n_points": len(conc["r_grid"]),
        },
        "philosophy": (
            "Discrete CS04/CS05/CS06 numbers are illustrations only; "
            "the scientific object is the continuous field on (p,n), (p_A,p_B), and r∈(0,∞)."
        ),
    }
    # lightweight JSON without huge F matrix
    (OUT_DIR / "continuous_models_meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    # save formulae-only companion
    (OUT_DIR / "all_positive_formulae.json").write_text(
        json.dumps(
            {
                "model_id": allpos["model_id"],
                "formulae": allpos["formulae"],
                "n_min_onesided_lower_ge_claim": allpos["n_min_onesided_lower_ge_claim"],
                "alpha": allpos["alpha"],
                "claim_p0": allpos["claim_p0"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return meta


if __name__ == "__main__":
    # default fine build
    meta = build_all_continuous_models(fine=True)
    print(json.dumps(meta, indent=2))
    print("Wrote fields to", OUT_DIR)
