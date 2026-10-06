"""Tests for theory depth modules P12–P18."""

from __future__ import annotations

from pathlib import Path

from lod_guide.research.minimax_probit_design import run_minimax_probit_design
from lod_guide.research.pareto_exact_sample_size import folklore_pareto_certificate, run_pareto_exact_sample_size
from lod_guide.research.pre_test_lob_inflation import run_pre_test_lob_inflation
from lod_guide.research.probit_design_robustness import run_probit_design_robustness
from lod_guide.research.theory_depth_studies import run_c_optimal_study, run_identification_study
from lod_guide.theory.c_optimal_lod_design import compare_to_reference_designs
from lod_guide.theory.identification import lod_identifiability_certificate
from lod_guide.theory.lod_dose_response import default_synthetic_truth


def test_all_propositions_p12_p18(theory_certs):
    certs = theory_certs
    ids = {c.result_id for c in certs}
    for pid in (
        "P12_c_optimal_efficiency",
        "P13_minimax_robust_design",
        "P14_efficiency_ratio",
        "P15_lod_identifiability",
        "P16_saturation_trap",
        "P17_gated_lob_inflation",
        "P18_folklore_pareto_dominated",
        "C_optimal_equivalence",
        "P17_selective_inflation",
        "P17_sample_split_remedy",
        "P13_minimax_formal",
    ):
        assert pid in ids
    failed = [c for c in certs if not c.passed]
    assert not failed, [(c.result_id, c.details) for c in failed]


def test_identification_good_vs_saturation():
    truth = default_synthetic_truth()
    lod = truth.lod()
    from lod_guide.research.probit_design_grid import allocate_n, make_concentration_grid

    good_conc = make_concentration_grid(lod, n_levels=5, pattern="dense_near_lod")
    good_n = allocate_n(60, 5, scheme="lod_weighted", lod=lod, concentrations=good_conc)
    assert lod_identifiability_certificate(truth, good_conc, good_n).identifiable

    import numpy as np

    sat_conc = lod * np.array([1e-4, 2e-4, 5e-4, 1e-3, 2e-3])
    sat_n = [20.0] * 5
    assert not lod_identifiability_certificate(truth, sat_conc, sat_n).identifiable


def test_c_optimal_improves_over_reference():
    cmp = compare_to_reference_designs(seed=0)
    assert cmp["efficiency_vs_reference"]["efficiency"] > 1.0


def test_theory_depth_json_deposits():
    for runner in (
        run_identification_study,
        run_c_optimal_study,
        run_minimax_probit_design,
        run_pre_test_lob_inflation,
        run_pareto_exact_sample_size,
        run_probit_design_robustness,
    ):
        out = runner()
        assert Path(out["path"]).exists()


def test_folklore_pareto_dominated():
    cert = folklore_pareto_certificate()
    assert cert["folklore_pareto_dominated"]
    assert cert["loss_ratio_folklore_over_powered"] > 1.0
