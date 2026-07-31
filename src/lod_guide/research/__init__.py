"""Research analyses: deep qPCR, OC Monte Carlo, LoB coverage."""

from lod_guide.research.all_positive_trap import run_all_positive_trap_study
from lod_guide.research.bootstrap_ci import bootstrap_quantile_lob, bootstrap_parametric_lob
from lod_guide.research.concentration_relative import run_concentration_relative_study
from lod_guide.research.continuous_models import (
    build_all_continuous_models,
    query_all_positive,
    query_discrimination,
)
from lod_guide.research.deep_qpcr import run_deep_qpcr_research
from lod_guide.research.lob_coverage import run_lob_coverage
from lod_guide.research.operating_characteristics import run_operating_characteristics
from lod_guide.research.reagent_discrimination import (
    run_reagent_discrimination_study,
    run_continuous_discrimination_study,
)
from lod_guide.research.exact_power_study import run_exact_power_study
from lod_guide.research.precision_profile import run_precision_profile_study
from lod_guide.research.ep17_estradiol import run_ep17_estradiol_study
from lod_guide.research.msstats_lob_study import run_msstats_lob_study
from lod_guide.research.type1_calibration import run_type1_calibration_study
from lod_guide.research.reproducibility_deposit import build_reproducibility_deposit
from lod_guide.research.empirical_tierA_extension import run_empirical_tierA_extension
from lod_guide.research.evidence_stratified_report import build_evidence_stratified_report
from lod_guide.research.decision_risk import evaluate_standard_scenarios
from lod_guide.research.tierA_meta_analysis import run_tierA_meta_analysis
from lod_guide.research.one_proportion_coverage import run_one_proportion_coverage_study
from lod_guide.research.s2_threshold_sensitivity import run_s2_threshold_sensitivity
from lod_guide.research.probit_design_grid import run_probit_design_grid
from lod_guide.research.decision_weight_axioms import run_decision_weight_axioms
from lod_guide.research.multiplicity_sequential import run_multiplicity_sequential_study
from lod_guide.research.censored_lob import run_censored_lob_study
from lod_guide.research.variance_function_loq import run_variance_function_loq_study
from lod_guide.research.probit_design_robustness import run_probit_design_robustness
from lod_guide.research.s2_risk_calibrated_thresholds import run_s2_risk_calibrated_thresholds
from lod_guide.research.minimax_probit_design import run_minimax_probit_design
from lod_guide.research.pre_test_lob_inflation import run_pre_test_lob_inflation
from lod_guide.research.pareto_exact_sample_size import run_pareto_exact_sample_size
from lod_guide.research.theory_depth_studies import run_c_optimal_study, run_identification_study

__all__ = [
    "run_deep_qpcr_research",
    "run_operating_characteristics",
    "run_lob_coverage",
    "bootstrap_quantile_lob",
    "bootstrap_parametric_lob",
    "run_all_positive_trap_study",
    "run_reagent_discrimination_study",
    "run_continuous_discrimination_study",
    "run_concentration_relative_study",
    "build_all_continuous_models",
    "query_all_positive",
    "query_discrimination",
    "run_exact_power_study",
    "run_precision_profile_study",
    "run_ep17_estradiol_study",
    "run_msstats_lob_study",
    "run_type1_calibration_study",
    "build_reproducibility_deposit",
    "run_empirical_tierA_extension",
    "build_evidence_stratified_report",
    "evaluate_standard_scenarios",
    "run_tierA_meta_analysis",
    "run_one_proportion_coverage_study",
    "run_s2_threshold_sensitivity",
    "run_probit_design_grid",
    "run_decision_weight_axioms",
    "run_multiplicity_sequential_study",
    "run_censored_lob_study",
    "run_variance_function_loq_study",
    "run_probit_design_robustness",
    "run_s2_risk_calibrated_thresholds",
    "run_minimax_probit_design",
    "run_pre_test_lob_inflation",
    "run_pareto_exact_sample_size",
    "run_identification_study",
    "run_c_optimal_study",
]
