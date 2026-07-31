"""
Selective inference for assumption-gated LoB (P17 theory module).

Decomposes exceedance error into:
  - Marginal: E[1{test > LoB}] under the data-generating law
  - Conditional on gate G=1 (parametric selected): E[... | G=1]
  - Conditional on gate G=0 (nonparametric selected): E[... | G=0]

When G depends on the same blank sample used to estimate LoB, conditional
Type I can exceed nominal α even if each path is calibrated in isolation.
"""

from __future__ import annotations

import numpy as np

from lod_guide.theory.gated_inference import gated_lob_from_sample
from lod_guide.theory.types import TheoryResult


def selective_error_decomposition(
    draw_fn,
    *,
    n_blank: int = 60,
    alpha: float = 0.05,
    n_mc: int = 2000,
    seed: int = 0,
) -> dict:
    """
    Monte Carlo decomposition of gated LoB exceedance rates.

    Returns marginal, conditional-on-parametric, and conditional-on-nonparametric rates.
    """
    rng = np.random.default_rng(seed)
    marginal: list[float] = []
    cond_par: list[float] = []
    cond_np: list[float] = []
    n_par = 0
    n_np = 0

    for _ in range(n_mc):
        blank = draw_fn(n_blank, rng)
        gated = gated_lob_from_sample(blank, alpha=alpha)
        test = draw_fn(500, rng)
        ex = float(np.mean(test > gated.lob_used))
        marginal.append(ex)
        if gated.path == "parametric":
            n_par += 1
            cond_par.append(ex)
        else:
            n_np += 1
            cond_np.append(ex)

    return {
        "alpha_nominal": alpha,
        "n_mc": n_mc,
        "marginal_exceedance": float(np.mean(marginal)),
        "conditional_parametric": float(np.mean(cond_par)) if cond_par else None,
        "conditional_nonparametric": float(np.mean(cond_np)) if cond_np else None,
        "marginal_inflation": float(np.mean(marginal)) - alpha,
        "conditional_parametric_inflation": (
            float(np.mean(cond_par)) - alpha if cond_par else None
        ),
        "parametric_fraction": n_par / n_mc,
        "nonparametric_fraction": n_np / n_mc,
    }


def theorem_selective_inflation(
    *,
    min_cond_inflation: float = 0.005,
    n_mc: int = 1500,
) -> TheoryResult:
    """
    Proposition (selective Type I inflation under gated LoB).

    ∃ skew law F such that when S2 selects parametric path with positive probability,
        E[Exceedance | G=1] > α,
    while the nonparametric path may remain calibrated. Marginal rate is a mixture.

    Remedies (not implemented): sample splitting, cross-fitting, conditional calibration.
    """
    def draw_gamma(n: int, r: np.random.Generator) -> np.ndarray:
        return r.gamma(shape=4.0, scale=0.25, size=n)

    dec = selective_error_decomposition(draw_gamma, n_mc=n_mc, seed=42)
    cond = dec["conditional_parametric_inflation"]
    par_frac = dec["parametric_fraction"]
    passed = cond is not None and par_frac >= 0.05 and cond >= min_cond_inflation

    proof = (
        "Proposition (selective inference). Let G = 1{parametric candidate} be a function "
        "of blank sample B. LoB = T(B, G). Under F ≠ Gaussian, the parametric functional "
        "μ(B) + z·σ(B) need not equal F^{-1}(1-α). Conditional on G=1, the gate selects "
        "a subpopulation of blank draws where parametric approximations appear adequate, "
        "but Type I on fresh test draws can still exceed α. Marginal rate mixes conditional "
        "rates: E[R] = P(G=1)E[R|G=1] + P(G=0)E[R|G=0]. This is distinct from post-hoc "
        "multiplicity; it is post-model-selection calibration failure (cf. Berk et al. 2013). "
        "Remedies: sample splitting or conditional inference on G. □"
    )
    return TheoryResult(
        "P17_selective_inflation",
        "C",
        "Conditional Type I | G=1 can exceed nominal α under skew when S2 selects parametric LoB.",
        passed,
        proof,
        dec,
    )
