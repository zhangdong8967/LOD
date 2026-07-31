"""
Deposit studies for identification and c-optimal LoD design theory.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from lod_guide.research.probit_design_grid import allocate_n, make_concentration_grid
from lod_guide.theory.c_optimal_lod_design import compare_to_reference_designs
from lod_guide.theory.identification import lod_identifiability_certificate, saturation_certificate
from lod_guide.theory.lod_dose_response import default_synthetic_truth

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def run_identification_study() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    truth = default_synthetic_truth()
    lod = truth.lod()

    good_conc = make_concentration_grid(lod, n_levels=5, pattern="dense_near_lod")
    good_n = allocate_n(60, 5, scheme="lod_weighted", lod=lod, concentrations=good_conc)
    good = lod_identifiability_certificate(truth, good_conc, good_n)

    # Saturation plate: all concentrations far below LoD → p ≈ 0
    sat_conc = lod * np.array([1e-4, 2e-4, 5e-4, 1e-3, 2e-3])
    sat_n = np.full(5, 12.0)
    bad = lod_identifiability_certificate(truth, sat_conc, sat_n)
    sat = saturation_certificate(truth, sat_conc, sat_n)

    payload = {
        "study_id": "LOD-IDENTIFICATION-v1",
        "good_design": good.to_dict(),
        "saturation_design": bad.to_dict(),
        "saturation_trap": sat,
        "headline": {
            "good_identifiable": good.identifiable,
            "saturation_identifiable": bad.identifiable,
            "saturation_trap": sat["saturation_trap"],
        },
    }
    path = OUT / "identification_study.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload


def run_c_optimal_study() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    cmp = compare_to_reference_designs(seed=0)
    payload = {
        "study_id": "C-OPTIMAL-LOD-DESIGN-v1",
        **cmp,
        "headline": {
            "c_optimal_se": cmp["c_optimal"]["se_log10_lod"],
            "reference_se": cmp["reference_equal_log_equal_n"]["se_log10_lod"],
            "efficiency": cmp["efficiency_vs_reference"]["efficiency"],
        },
    }
    path = OUT / "c_optimal_lod_design.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(path)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_identification_study()["headline"], indent=2))
    print(json.dumps(run_c_optimal_study()["headline"], indent=2))
