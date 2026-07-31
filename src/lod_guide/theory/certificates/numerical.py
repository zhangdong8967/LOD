"""
Layer C — Numerical certificates (Monte Carlo / grid verification).

These are machine-checkable but not analytic theorems. Each carries
proof_sketch = "Numerical certificate via enumeration/Monte Carlo."
"""

from __future__ import annotations

import numpy as np
from scipy.stats import binom

from lod_guide.s5_sample_size import (
    design_effect,
    power_two_proportions,
    sample_size_two_proportions,
    simulate_power_two_proportions,
)
from lod_guide.theory.types import TheoryResult

_MC_NOTE = "Numerical certificate via Monte Carlo or grid enumeration."


def certificate_p3_fleiss_chow(
    p_a: float = 0.90,
    p_b: float = 0.80,
    alpha: float = 0.05,
    power: float = 0.80,
    tol: float = 0.05,
    n_sims: int = 8000,
    seed: int = 0,
) -> TheoryResult:
    """Certificate P3: Fleiss–Chow n yields MC power ≈ target (large-n regime)."""
    n_cont = sample_size_two_proportions(p_a, p_b, alpha, power)
    n = int(np.ceil(n_cont))
    asym = power_two_proportions(p_a, p_b, n, alpha)
    mc = simulate_power_two_proportions(p_a, p_b, n, alpha, n_sims=n_sims, seed=seed)
    passed = abs(mc - power) <= tol and abs(asym - power) <= tol
    return TheoryResult(
        "P3_two_proportion_power",
        "C",
        "Fleiss–Chow n yields asymptotic and MC power near target.",
        passed,
        _MC_NOTE,
        {
            "n_continuous": n_cont,
            "n_ceil": n,
            "power_asymptotic": asym,
            "power_monte_carlo": mc,
            "target": power,
            "tol": tol,
        },
    )


def certificate_p4_design_effect() -> TheoryResult:
    """Certificate P4: DE = 1 + (m-1)ρ (standard Kish formula)."""
    de = design_effect(0.2, 5)
    passed = abs(de - 1.8) < 1e-12
    return TheoryResult(
        "P4_design_effect",
        "C",
        "DE=1+(m-1)ρ under compound symmetry.",
        passed,
        "Analytic identity (Kish 1965); numeric spot-check.",
        {"DE": de, "expected": 1.8},
    )


def certificate_p6_ovl(
    p_a: float = 0.90,
    p_b: float = 0.80,
) -> TheoryResult:
    """Certificate P6: OVL of Binomial sampling laws decreases with n (grid check)."""

    def ovl(n: int) -> float:
        ks = np.arange(0, n + 1)
        return float(np.minimum(binom.pmf(ks, n, p_a), binom.pmf(ks, n, p_b)).sum())

    ns = (20, 40, 80, 120, 200)
    ovls = {f"OVL_{n}": ovl(n) for n in ns}
    vals = [ovls[f"OVL_{n}"] for n in ns]
    passed = all(vals[i + 1] <= vals[i] + 1e-12 for i in range(len(vals) - 1)) and vals[-1] < vals[0]
    return TheoryResult(
        "P6_ovl_separation",
        "C",
        "Overlap coefficient of hat{p} laws decreases as n increases (separation).",
        passed,
        _MC_NOTE,
        ovls,
    )


def certificate_p9_holm_fwer(
    m: int = 3,
    n: int = 15,
    n_mc: int = 400,
    alpha: float = 0.05,
    seed: int = 3,
) -> TheoryResult:
    """Certificate P9: Holm FWER ≤ α under global null (MC sketch; theorem is Holm 1979)."""
    from lod_guide.research.multiplicity_sequential import holm_adjust
    from lod_guide.theory.exact_tests import fisher_pvalue

    rng = np.random.default_rng(seed)
    false = 0
    for _ in range(n_mc):
        ps = []
        for _j in range(m):
            a = int(rng.binomial(n, 0.5))
            b = int(rng.binomial(n, 0.5))
            ps.append(fisher_pvalue(a, n, b, n))
        if any(p < alpha for p in holm_adjust(ps)):
            false += 1
    fwer = false / n_mc
    passed = fwer <= alpha + 0.03
    return TheoryResult(
        "P9_holm_fwer",
        "C",
        "Holm–Bonferroni keeps FWER near/below α under a global null (MC sketch).",
        passed,
        "Theorem: Holm (1979) controls FWER; MC verifies finite-n behavior.",
        {"m": m, "n": n, "n_mc": n_mc, "fwer": fwer, "alpha": alpha},
    )


def certificate_p10_weight_scale() -> TheoryResult:
    """Certificate P10: decision loss L is homogeneous of degree 1 in weights."""
    from lod_guide.research.decision_risk import RiskWeights, loss

    l1 = loss(type_i=0.05, beta=0.5, mismatch=0.2, de=1.8, weights=RiskWeights(1, 1, 1, 0.5))
    l2 = loss(type_i=0.05, beta=0.5, mismatch=0.2, de=1.8, weights=RiskWeights(2, 2, 2, 1.0))
    passed = abs(l2 - 2 * l1) < 1e-9
    return TheoryResult(
        "P10_weight_scale_invariance",
        "C",
        "Decision loss L is homogeneous of degree 1 in the weight vector.",
        passed,
        "Axiom A2 (linear scale invariance); numeric verification.",
        {"L_w": l1, "L_2w": l2},
    )


def certificate_p11_tobit_agreement(
    n: int = 80,
    seed: int = 0,
    tol: float = 0.05,
) -> TheoryResult:
    """Certificate P11: Tobit LoB ≈ mean+z·SD when nothing is censored."""
    from lod_guide.research.censored_lob import lob_tobit_normal
    from lod_guide.s4_models import lob_parametric_normal

    rng = np.random.default_rng(seed)
    x = rng.normal(0.05, 0.02, size=n)
    naive = lob_parametric_normal(x, 0.05)
    tob = lob_tobit_normal(x, censor_at=float(np.min(x) - 1.0), alpha=0.05)
    passed = bool(tob.get("ok")) and abs(tob["lob"] - naive) <= tol
    return TheoryResult(
        "P11_tobit_uncensored_agreement",
        "C",
        "Tobit Normal LoB agrees with mean+z·SD when nothing is left-censored.",
        passed,
        _MC_NOTE,
        {"naive": naive, "tobit": tob.get("lob"), "tol": tol},
    )


def certificate_p12_c_optimal(min_efficiency: float = 1.02) -> TheoryResult:
    """Certificate P12: c-optimal design beats equal log/equal n reference."""
    from lod_guide.theory.c_optimal_lod_design import compare_to_reference_designs

    cmp = compare_to_reference_designs(seed=0)
    eff = cmp["efficiency_vs_reference"]["efficiency"]
    passed = eff is not None and eff >= min_efficiency
    return TheoryResult(
        "P12_c_optimal_efficiency",
        "C",
        "Locally c-optimal multi-level design has higher asymptotic efficiency than equal log/equal n.",
        passed,
        _MC_NOTE,
        {
            "efficiency": eff,
            "min_efficiency": min_efficiency,
            "c_optimal_se": cmp["c_optimal"]["se_log10_lod"],
        },
    )


def certificate_p13_minimax() -> TheoryResult:
    """Certificate P13: minimax slope-robust design lowers worst-case SE."""
    from lod_guide.research.minimax_probit_design import minimax_design_search

    search = minimax_design_search()
    ratio = search["worst_case_improvement_vs_folklore"]
    passed = ratio is not None and ratio >= 1.0 + 1e-6
    return TheoryResult(
        "P13_minimax_robust_design",
        "C",
        "Minimax slope-robust design has lower worst-case SE(log10 LoD) than equal log/equal n.",
        passed,
        _MC_NOTE,
        {
            "improvement_ratio": ratio,
            "minimax_worst_se": search["minimax_design"]["worst_case_se"],
            "folklore_worst_se": search["folklore_equal_log_equal"]["worst_case_se"],
        },
    )


def certificate_p14_efficiency() -> TheoryResult:
    """Certificate P14: c-efficiency (variance ratio) > 1 for reference vs c-optimal."""
    from lod_guide.theory.c_optimal_lod_design import asymptotic_efficiency, compare_to_reference_designs

    cmp = compare_to_reference_designs(seed=1)
    ref_se = cmp["reference_equal_log_equal_n"]["se_log10_lod"]
    opt_se = cmp["c_optimal"]["se_log10_lod"]
    eff = asymptotic_efficiency(ref_se, opt_se)
    passed = eff["efficiency"] is not None and eff["efficiency"] > 1.0
    return TheoryResult(
        "P14_efficiency_ratio",
        "C",
        "Asymptotic c-efficiency (variance ratio) exceeds 1 for reference vs c-optimal design.",
        passed,
        _MC_NOTE,
        eff,
    )


def certificate_p17_gated_inflation(
    min_cond_inflation: float = 0.005,
    n_mc: int = 300,
) -> TheoryResult:
    """Certificate P17: gated parametric LoB inflates Type I on non-Gaussian blanks."""
    from lod_guide.s2_diagnostics import DEFAULT_THRESHOLDS, run_diagnostics
    from lod_guide.s4_models import lob_parametric_normal

    rng = np.random.default_rng(7)
    alpha = 0.05

    def draw_gamma(n: int, r: np.random.Generator) -> np.ndarray:
        return r.gamma(shape=4.0, scale=0.25, size=n)

    cond_rates: list[float] = []
    n_par = 0
    for _ in range(n_mc):
        blank = draw_gamma(60, rng)
        flags = run_diagnostics(blank, thresholds=DEFAULT_THRESHOLDS)
        if not flags.parametric_candidate:
            continue
        n_par += 1
        lob = lob_parametric_normal(blank, alpha=alpha)
        test = draw_gamma(500, rng)
        cond_rates.append(float(np.mean(test > lob)))

    cond_mean = float(np.mean(cond_rates)) if cond_rates else 0.0
    cond_infl = cond_mean - alpha
    par_frac = n_par / n_mc
    passed = par_frac >= 0.05 and cond_infl >= min_cond_inflation

    return TheoryResult(
        "P17_gated_lob_inflation",
        "C",
        "When S2 selects parametric LoB on Gamma blanks, exceedance can exceed nominal α (MC).",
        passed,
        "Selective inference: conditional Type I | G=1 may exceed α; see theory/selective/.",
        {
            "conditional_mean_exceedance": cond_mean,
            "conditional_inflation": cond_infl,
            "parametric_fraction": par_frac,
            "alpha": alpha,
        },
    )
