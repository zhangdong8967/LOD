"""Tests for Berry-Esseen, OVL analytic proof, and sample-split remedy."""

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
    assert eps > 0
    assert third_central_moment_w(0.90, 0.80) > 0


def test_be_gap_lower_bound_conservative_at_folklore_n():
    b = bound_p8_asymptotic_fisher_gap(0.90, 0.80, 20)
    assert b["gap"] >= 0.05
    assert b["berry_esseen_gap_lower_bound"] > 0
    assert b["be_bound_conservative"]


def test_p6_ovl_tv_identity():
    ident = ovl_tv_identity(0.90, 0.80, 50)
    assert ident["identity_holds"]


def test_p6_ovl_inductive_monotone():
    ind = verify_ovl_monotone_inductive(0.90, 0.80, n_max=200)
    assert ind["monotone_ovl"]
    assert ind["monotone_tv"]


def test_p6_theorem_layer_a():
    c = theorem_p6_ovl_monotone()
    assert c.layer == "A"
    assert c.passed


def test_sample_split_runs():
    import numpy as np

    rng = np.random.default_rng(0)
    blank = rng.gamma(4.0, 0.25, size=60)
    result = gated_lob_sample_split(blank)
    assert result.n_gate >= 10
    assert result.n_lob >= 10
    assert result.lob_used > 0


def test_sample_split_remedy_reduces_inflation():
    import numpy as np

    def draw(n: int, r):
        return r.gamma(4.0, 0.25, size=n)

    cmp = monte_carlo_compare_split_vs_unsplit(draw, n_mc=400, seed=1)
    assert cmp["unsplit_inflation"] > cmp["split_inflation"]


def test_p17_sample_split_theorem():
    c = theorem_p17_sample_split_remedy(n_mc=800, seed=0)
    assert c.layer == "B"
    assert c.passed
