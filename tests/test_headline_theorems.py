"""Tests for headline theorems T1(ii), T2a–T2b, T4, T5."""

from lod_guide.theory.theorems.acceptance_events import (
    theorem_t1_e3_pass_fisher_separation,
    theorem_t5_tost_vs_e2_non_nested,
)
from lod_guide.theory.theorems.design_confirmation import (
    theorem_t2a_pooled_z_fisher_distinct,
    theorem_t2b_berry_esseen_design_scale,
)
from lod_guide.theory.theorems.sample_size_asymptotics import (
    fleiss_leading_coefficient,
    theorem_t4_fleiss_nstar_delta_scaling,
)


def test_t1_e3_pass_fisher_separation():
    r = theorem_t1_e3_pass_fisher_separation()
    assert r.passed
    assert r.details["power_fisher"] < 0.10


def test_t2a_distinct_tests():
    r = theorem_t2a_pooled_z_fisher_distinct()
    assert r.passed
    assert r.details["gap"] > 0.01


def test_t2b_berry_esseen_scale():
    r = theorem_t2b_berry_esseen_design_scale()
    assert r.passed
    assert r.details["berry_esseen_epsilon"] > 0


def test_t4_fleiss_leading_term():
    c = fleiss_leading_coefficient(0.85)
    assert c > 0
    r = theorem_t4_fleiss_nstar_delta_scaling(p_bar=0.85)
    assert r.passed
    assert r.details["C_leading"] == c


def test_t5_tost_non_nested():
    r = theorem_t5_tost_vs_e2_non_nested()
    assert r.passed
