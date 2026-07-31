"""Tests for three-layer theory architecture."""

from __future__ import annotations

from lod_guide.theory.bounds.finite_sample import bound_p8_asymptotic_fisher_gap
from lod_guide.theory.design.equivalence import check_c_optimal_equivalence
from lod_guide.theory.design.minimax import SlopeUncertaintySet, minimax_theorem_certificate
from lod_guide.theory.propositions import verify_all_propositions, verify_by_layer
from lod_guide.theory.selective.gated_error import selective_error_decomposition
from lod_guide.theory.theorems.analytic import theorem_p7_all_positive_cp_lower
from lod_guide.theory.theorems.identification import theorem_p16_saturation_non_identifiable
from lod_guide.theory.types import TheoryResult


def test_layer_counts():
    all_c = verify_all_propositions()
    a = verify_by_layer("A")
    b = verify_by_layer("B")
    c = verify_by_layer("C")
    assert len(a) + len(b) + len(c) == len(all_c)
    assert len(a) >= 6
    assert len(b) >= 2
    assert len(c) >= 10


def test_layer_a_has_proof_sketches():
    for r in verify_by_layer("A"):
        assert isinstance(r, TheoryResult)
        assert r.layer == "A"
        assert len(r.proof_sketch) > 50
        assert "Numerical certificate" not in r.proof_sketch


def test_p7_cp_lower_matches_theory():
    c = theorem_p7_all_positive_cp_lower(n=20, claim=0.95)
    assert c.passed
    assert c.details["CP_onesided_lower"] < 0.95
    assert c.details["CP_onesided_lower"] > 0.85


def test_p8_bound_underpowered_flag():
    b = bound_p8_asymptotic_fisher_gap(0.90, 0.80, 20)
    assert b["underpowered_regime"]
    assert b["gap"] >= 0.05


def test_p16_saturation_structural():
    c = theorem_p16_saturation_non_identifiable()
    assert c.passed
    assert c.details["saturation"]["saturation_trap"]


def test_c_optimal_equivalence_check():
    chk = check_c_optimal_equivalence(tol=0.55)
    assert chk["equivalence_ok"]
    assert chk["max_trace_ratio"] <= 1.55


def test_minimax_uncertainty_set():
    u = SlopeUncertaintySet(0.5, 1.5)
    assert u.contains(2.0, 2.5)
    assert not u.contains(2.0, 4.0)
    cert = minimax_theorem_certificate(u)
    assert cert.passed


def test_selective_decomposition_fields():
    import numpy as np

    rng = np.random.default_rng(0)

    def draw(n: int, r) -> np.ndarray:
        return r.gamma(4.0, 0.25, size=n)

    dec = selective_error_decomposition(draw, n_mc=200, seed=0)
    assert "marginal_exceedance" in dec
    assert "conditional_parametric" in dec or dec["parametric_fraction"] == 0
