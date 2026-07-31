"""Tests for Berry–Esseen, OVL, and sample-split theory extensions."""

from __future__ import annotations

from lod_guide.theory.bounds.berry_esseen import (
    berry_esseen_cdf_error,
    berry_esseen_power_gap_lower_bound,
    third_central_moment_w,
)
from lod_guide.theory.bounds.finite_sample import bound_p8_asymptotic_fisher_gap
from lod_guide.theory.selective.sample_split import (
    gated_lob_sample_split,
    monte_carlo_compare_split_vs_unsplit,
    theorem_p17_sample_split_remedy,
)
from lod_guide.theory.theorems.ovl import (
    ovl_tv_identity,
    theorem_p6_ovl_monotone,
    verify_ovl_monotone_inductive,
)


def test_berry_esseen_epsilon_positive():
    eps = berry_esseen_cdf_error(20, 0.90, 0.80)
    assert eps > 0.0
    rho = third_central_moment_w(0.90, 0.80)
    assert rho > 0.0


def test_p8_be_gap_bound():
    b = bound_p8_asymptotic_fisher_gap(0.90, 0.80, 20)
    assert b["gap"] >= 0.05
    assert b["berry_esseen_gap_lower_bound"] > 0.0
    assert b["berry_esseen_epsilon"] > 0.0


def test_p8_be_formula_at_folklore_n():
    be = berry_esseen_power_gap_lower_bound(20, 0.90, 0.80)
    assert be["underpowered_regime"]
    assert be["power_gap_lower_bound"] > 0.0


def test_p6_tv_identity():
    ident = ovl_tv_identity(0.90, 0.80, 30)
    assert ident["identity_holds"]


def test_p6_inductive_monotone():
    ind = verify_ovl_monotone_inductive(0.90, 0.80, n_max=200)
    assert ind["monotone_ovl"]
    assert ind["monotone_tv"]


def test_p6_theorem_layer_a():
    c = theorem_p6_ovl_monotone()
    assert c.layer == "A"
    assert c.passed


def test_sample_split_api():
    import numpy as np

    rng = np.random.default_rng(0)
    blank = rng.gamma(4.0, 0.25, size=80)
    result = gated_lob_sample_split(blank, alpha=0.05)
    assert result.n_gate + result.n_lob == 80
    assert result.alpha_lob == 0.025


def test_sample_split_remedy_theorem():
    c = theorem_p17_sample_split_remedy(n_mc=800)
    assert c.layer == "B"
    assert c.passed
    assert c.details["split_inflation"] < c.details["unsplit_inflation"]


def test_split_vs_unsplit_mc():
    import numpy as np

    def draw(n: int, r: np.random.Generator) -> np.ndarray:
        return r.gamma(4.0, 0.25, size=n)

    cmp = monte_carlo_compare_split_vs_unsplit(draw, n_blank=80, n_mc=300, seed=1)
    assert "split_exceedance" in cmp
    assert "unsplit_exceedance" in cmp
