#!/usr/bin/env python3
"""Run theory-depth studies (identification, c-optimal, minimax, gated LoB, Pareto exact n)."""

from __future__ import annotations

import json

from lod_guide.research.minimax_probit_design import run_minimax_probit_design
from lod_guide.research.pareto_exact_sample_size import run_pareto_exact_sample_size
from lod_guide.research.pre_test_lob_inflation import run_pre_test_lob_inflation
from lod_guide.research.probit_design_robustness import run_probit_design_robustness
from lod_guide.research.theory_depth_studies import run_c_optimal_study, run_identification_study
from lod_guide.theory.propositions import verify_all_propositions


def main() -> None:
    runners = [
        ("identification", run_identification_study),
        ("c_optimal", run_c_optimal_study),
        ("minimax_probit", run_minimax_probit_design),
        ("probit_robustness", run_probit_design_robustness),
        ("pre_test_lob", run_pre_test_lob_inflation),
        ("pareto_exact_n", run_pareto_exact_sample_size),
    ]
    for name, fn in runners:
        out = fn()
        print(f"[{name}] {out.get('path', out.get('study_id'))}")
        if "headline" in out:
            print(json.dumps(out["headline"], indent=2))

    certs = verify_all_propositions()
    failed = [c.result_id for c in certs if not c.passed]
    print(f"Theory results: {len(certs)} total, {len(failed)} failed")
    if failed:
        raise SystemExit(f"Failed: {failed}")


if __name__ == "__main__":
    main()
