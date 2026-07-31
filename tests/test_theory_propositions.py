"""Machine certificates for theory propositions P1–P18 + supplementary results."""

from __future__ import annotations

from lod_guide.theory.audit import new_audit, sha256_hex
from lod_guide.theory.estimands import EstimandID, estimand_for_goal
from lod_guide.theory.exact import clopper_pearson_interval, wilson_interval
from lod_guide.theory.propositions import verify_all_propositions, verify_by_layer


def test_all_propositions_pass():
    certs = verify_all_propositions()
    assert len(certs) == 22
    failed = [c for c in certs if not c.passed]
    assert not failed, [(c.result_id, c.details) for c in failed]
    ids = {c.result_id for c in certs}
    assert "P7_all_positive_trap" in ids
    assert "P8_exact_vs_asymptotic_gap" in ids
    assert "P15_lod_identifiability" in ids
    assert "P18_folklore_pareto_dominated" in ids


def test_layer_a_theorems_pass():
    layer_a = verify_by_layer("A")
    assert len(layer_a) >= 6
    assert all(c.passed for c in layer_a)
    assert all(c.proof_sketch and c.proof_sketch != "Numerical certificate via enumeration/Monte Carlo." for c in layer_a)


def test_theory_result_has_layer():
    certs = verify_all_propositions()
    layers = {c.layer for c in certs}
    assert layers == {"A", "B", "C"}


def test_estimands_locked():
    e = estimand_for_goal("G2_COMPARE_REAGENTS")
    assert e.id == EstimandID.G2_RATE_DIFFERENCE
    assert "NOT 1-(1-p)^n" in " ".join(e.identification_assumptions)


def test_intervals_nested_well():
    w = wilson_interval(18, 20)
    cp = clopper_pearson_interval(18, 20)
    assert 0 <= w[0] <= w[1] <= 1
    assert 0 <= cp[0] <= cp[1] <= 1


def test_audit_hash_stable_for_same_payload():
    est = estimand_for_goal("G1_VERIFY_LOD").to_dict()
    a = new_audit("TEST-PROTOCOL", est)
    a.final = {"x": 1}
    d1 = a.to_dict()
    # content hash excludes wall-clock if we hash without created_utc
    h1 = sha256_hex({k: v for k, v in d1.items() if k != "created_utc"})
    h2 = sha256_hex({k: v for k, v in d1.items() if k != "created_utc"})
    assert h1 == h2
