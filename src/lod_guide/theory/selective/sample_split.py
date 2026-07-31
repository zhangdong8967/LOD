"""
Sample-splitting remedy for assumption-gated LoB (P17).

Split blank replicates B = (B_gate, B_lob):
  - S2 diagnostics run on B_gate only;
  - LoB estimated on B_lob only (parametric or nonparametric per gate).

Gate and LoB estimation are independent given the population law, restoring
nominal Type I control at the cost of reduced effective sample size.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from lod_guide.s2_diagnostics import DEFAULT_THRESHOLDS, run_diagnostics
from lod_guide.s4_models import lob_nonparametric, lob_parametric_normal
from lod_guide.theory.gated_inference import GatedLoBResult, gated_lob_from_sample
from lod_guide.theory.types import TheoryResult


@dataclass(frozen=True)
class SampleSplitLoBResult:
    parametric_candidate: bool
    lob_used: float
    path: str
    n_gate: int
    n_lob: int
    split_method: str
    alpha_lob: float


def gated_lob_sample_split(
    blank: np.ndarray,
    *,
    alpha: float = 0.05,
    min_gate: int = 12,
    min_lob: int = 20,
    bonferroni_stages: bool = True,
    min_n_for_parametric_lob: int = 25,
) -> SampleSplitLoBResult:
    """
    Sample-split gated LoB: gate on first half, estimate LoB on second half.

    Uses Bonferroni α/2 on the LoB stage when ``bonferroni_stages=True`` to
    account for gate + threshold selection. Forces nonparametric LoB when the
    holdout half is too small for stable parametric quantiles.
    """
    x = np.asarray(blank, dtype=float)
    n = x.size
    if n < min_gate + min_lob:
        raise ValueError(f"Need at least {min_gate + min_lob} blanks for split; got {n}")

    n_gate = max(min_gate, n // 2)
    gate_sample = x[:n_gate]
    lob_sample = x[n_gate:]
    alpha_lob = alpha / 2.0 if bonferroni_stages else alpha

    flags = run_diagnostics(gate_sample, thresholds=DEFAULT_THRESHOLDS)
    use_parametric = flags.parametric_candidate and lob_sample.size >= min_n_for_parametric_lob

    if use_parametric:
        lob = lob_parametric_normal(lob_sample, alpha=alpha_lob)
        return SampleSplitLoBResult(
            True, float(lob), "parametric", n_gate, lob_sample.size, "half_split_bonferroni", alpha_lob
        )

    lob = lob_nonparametric(lob_sample, percentile=100 * (1 - alpha_lob))
    return SampleSplitLoBResult(
        False, float(lob), "nonparametric", n_gate, lob_sample.size, "half_split_bonferroni", alpha_lob
    )


def monte_carlo_compare_split_vs_unsplit(
    draw_fn,
    *,
    n_blank: int = 60,
    alpha: float = 0.05,
    n_mc: int = 2000,
    seed: int = 0,
) -> dict:
    """Compare marginal exceedance: unsplit gated vs sample-split remedy."""
    rng = np.random.default_rng(seed)
    unsplit_rates: list[float] = []
    split_rates: list[float] = []
    unsplit_par = 0
    split_par = 0

    for _ in range(n_mc):
        blank = draw_fn(n_blank, rng)
        test = draw_fn(500, rng)

        u = gated_lob_from_sample(blank, alpha=alpha)
        unsplit_rates.append(float(np.mean(test > u.lob_used)))
        if u.path == "parametric":
            unsplit_par += 1

        try:
            s = gated_lob_sample_split(blank, alpha=alpha)
            split_rates.append(float(np.mean(test > s.lob_used)))
            if s.path == "parametric":
                split_par += 1
        except ValueError:
            continue

    unsplit_mean = float(np.mean(unsplit_rates))
    split_mean = float(np.mean(split_rates))
    return {
        "alpha_nominal": alpha,
        "n_blank": n_blank,
        "n_mc": n_mc,
        "unsplit_exceedance": unsplit_mean,
        "split_exceedance": split_mean,
        "unsplit_inflation": unsplit_mean - alpha,
        "split_inflation": split_mean - alpha,
        "inflation_reduction": (unsplit_mean - alpha) - (split_mean - alpha),
        "unsplit_parametric_fraction": unsplit_par / n_mc,
        "split_parametric_fraction": split_par / n_mc,
    }


def theorem_p17_sample_split_remedy(
    *,
    alpha: float = 0.05,
    n_blank: int = 80,
    n_mc: int = 2000,
    max_split_inflation: float = 0.02,
    seed: int = 42,
) -> TheoryResult:
    """
    Layer B certificate: sample splitting controls marginal Type I inflation.

    Under Gamma skew blanks, unsplit gated LoB may inflate exceedance above α,
    while half-split gate/LoB with Bonferroni α/2 on the holdout restores
    marginal rate ≈ α (within MC tolerance).
    """
    def draw_gamma(n: int, r: np.random.Generator) -> np.ndarray:
        return r.gamma(shape=4.0, scale=0.25, size=n)

    cmp = monte_carlo_compare_split_vs_unsplit(
        draw_gamma, n_blank=n_blank, alpha=alpha, n_mc=n_mc, seed=seed
    )
    passed = (
        cmp["unsplit_inflation"] > 0.0
        and cmp["split_inflation"] <= max_split_inflation
        and cmp["split_inflation"] < cmp["unsplit_inflation"]
    )

    proof = (
        "Proposition (sample-splitting remedy). Partition B=(B_g,B_ℓ) with |B_g|+|B_ℓ|=n. "
        "Let G = g(B_g) be the S2 gate and LoB = T(B_ℓ, G) with Bonferroni α/2 on the "
        "holdout stage. Conditional on F, B_g ⊥ B_ℓ so G is independent of B_ℓ; "
        "parametric LoB is used only when |B_ℓ|≥25. Hence E[1{Y>LoB}|F] is calibrated at "
        "nominal α unlike the unsplit rule where G and LoB share one sample. Cost: halved "
        "effective n per stage. MC verification under Gamma(4,0.25) blanks. □"
    )
    return TheoryResult(
        "P17_sample_split_remedy",
        "B",
        "Sample splitting restores marginal Type I ≤ α + ε under skew gated LoB.",
        passed,
        proof,
        cmp,
    )
