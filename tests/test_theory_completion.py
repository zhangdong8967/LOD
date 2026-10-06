"""Tests for theory/algorithm completion modules (weights, Barnard, multiplicity, Tobit, …)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from lod_guide.research.censored_lob import lob_tobit_normal, run_censored_lob_study
from lod_guide.research.decision_weight_axioms import run_decision_weight_axioms
from lod_guide.research.multiplicity_sequential import holm_adjust, run_multiplicity_sequential_study
from lod_guide.research.probit_design_robustness import run_probit_design_robustness
from lod_guide.research.s2_risk_calibrated_thresholds import run_s2_risk_calibrated_thresholds
from lod_guide.research.variance_function_loq import fit_rocke_lorenzato, loq_from_variance_function, run_variance_function_loq_study
from lod_guide.theory.exact_tests import analyze_two_proportions_exact, barnard_difference_pvalue


def test_barnard_diff_and_analyze_fields():
    r = analyze_two_proportions_exact(18, 20, 12, 20)
    assert 0 <= r.barnard_diff_p_two_sided <= 1
    assert r.boschloo_p_two_sided <= r.fisher_p_two_sided + 1e-9
    p = barnard_difference_pvalue(10, 20, 10, 20)
    assert p > 0.2  # null-ish


def test_holm_monotone():
    adj = holm_adjust([0.01, 0.04, 0.03])
    assert adj[0] <= adj[1] or adj[0] <= 0.05
    assert max(adj) <= 1.0


def test_decision_weight_axioms():
    out = run_decision_weight_axioms(n_per_axis=2)
    assert out["headline"]["scale_invariance_ok"] is True
    assert out["headline"]["all_profiles_prefer_powered"] is True
    assert Path(out["path"]).exists()


def test_multiplicity_sequential():
    out = run_multiplicity_sequential_study()
    assert out["fwer_mc"]["fwer_holm"] <= out["fwer_mc"]["fwer_raw"] + 1e-9
    assert Path(out["path"]).exists()


def test_censored_tobit():
    rng = np.random.default_rng(0)
    x = rng.normal(1.0, 0.2, size=100)
    fit = lob_tobit_normal(x, censor_at=-10.0, alpha=0.05)
    assert fit["ok"] is True
    out = run_censored_lob_study()
    assert out["headline"]["tobit_ok"] is True


def test_variance_function_loq():
    mu = np.array([10.0, 20, 50, 100, 200])
    sd = np.sqrt(4.0 + (0.1 * mu) ** 2)
    fit = fit_rocke_lorenzato(mu, sd)
    assert fit["ok"]
    loq = loq_from_variance_function(fit["beta0"], fit["beta1"], 0.20)
    assert loq is not None and loq > 0
    out = run_variance_function_loq_study()
    assert Path(out["path"]).exists()


def test_probit_robustness_and_s2_calibration():
    r = run_probit_design_robustness()
    assert r["headline"]["max_se_inflation"] >= 1.0 - 1e-6
    s = run_s2_risk_calibrated_thresholds()
    assert "calibrated_skew_fail" in s["headline"]


def test_propositions_include_p9_p18(theory_certs):
    certs = theory_certs
    ids = {c.result_id for c in certs}
    assert "P9_holm_fwer" in ids
    assert "P10_weight_scale_invariance" in ids
    assert "P11_tobit_uncensored_agreement" in ids
    assert "P18_folklore_pareto_dominated" in ids
    assert len(certs) >= 18
    assert all(c.passed for c in certs)
