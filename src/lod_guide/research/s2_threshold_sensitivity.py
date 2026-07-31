"""
S2 diagnostic-threshold sensitivity.

Asks: if laboratories tighten or loosen DiagnosticThresholds (v0.1 defaults),
how often does parametric_candidate flip on the same blank vector?

This closes the priority-queue gap “sensitivity of diagnostic thresholds (S2)”
without changing frozen defaults used in confirmatory runs.
"""

from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

from lod_guide.data.download_real import RAW_DIR, REMOTE_DATASETS, download_dataset, parse_real_dataset
from lod_guide.data.simulate import generate_all_simulated
from lod_guide.s2_diagnostics import DEFAULT_THRESHOLDS, DiagnosticThresholds, run_diagnostics

OUT = Path(__file__).resolve().parents[3] / "data" / "research"


def _blank_from_sim(dataset_id: str) -> tuple[np.ndarray, np.ndarray | None, str]:
    sims = {d.dataset_id: d for d in generate_all_simulated()}
    ds = sims[dataset_id]
    strata = np.asarray(ds.strata) if ds.strata is not None else None
    return np.asarray(ds.values, dtype=float), strata, f"sim:{dataset_id}"


def _blank_from_real(dataset_id: str) -> tuple[np.ndarray, np.ndarray | None, str] | None:
    meta = next((d for d in REMOTE_DATASETS if d.dataset_id == dataset_id), None)
    if meta is None:
        return None
    path = RAW_DIR / meta.filename
    if not path.exists():
        try:
            path = download_dataset(meta)
        except Exception:  # noqa: BLE001
            return None
    parsed = parse_real_dataset(dataset_id, path)
    blank = np.asarray(parsed.get("blank_values") or [], dtype=float)
    blank = blank[np.isfinite(blank)]
    if blank.size < 5:
        return None
    strata = parsed.get("blank_strata")
    st = np.asarray(strata) if strata and len(strata) == blank.size else None
    return blank, st, f"real:{dataset_id}"


def _threshold_variants() -> list[tuple[str, DiagnosticThresholds]]:
    """Named perturbations around frozen defaults (multiplicative / absolute)."""
    base = DEFAULT_THRESHOLDS
    variants: list[tuple[str, DiagnosticThresholds]] = [("default_v0.1", base)]
    # Shape: stricter / looser skew+kurtosis fail cutoffs
    for label, scale in [
        ("shape_stricter_0.7x", 0.7),
        ("shape_looser_1.5x", 1.5),
        ("shape_very_loose_2x", 2.0),
    ]:
        variants.append(
            (
                label,
                replace(
                    base,
                    abs_skew_fail=base.abs_skew_fail * scale,
                    abs_excess_kurtosis_fail=base.abs_excess_kurtosis_fail * scale,
                    abs_skew_warn=base.abs_skew_warn * scale,
                    abs_excess_kurtosis_warn=base.abs_excess_kurtosis_warn * scale,
                ),
            )
        )
    # Normality α
    for label, alpha in [("norm_alpha_0.01", 0.01), ("norm_alpha_0.10", 0.10)]:
        variants.append((label, replace(base, normality_alpha=alpha)))
    # Censoring
    for label, fail, warn in [
        ("censor_stricter", 0.15, 0.05),
        ("censor_looser", 0.40, 0.20),
    ]:
        variants.append((label, replace(base, censoring_fail=fail, censoring_warn=warn)))
    # ICC / between-stratum CV
    for label, icc_f, bcv_f in [
        ("het_stricter", 0.15, 0.20),
        ("het_looser", 0.40, 0.50),
    ]:
        variants.append(
            (
                label,
                replace(
                    base,
                    icc_fail=icc_f,
                    icc_warn=min(icc_f, base.icc_warn),
                    between_stratum_cv_fail=bcv_f,
                    between_stratum_cv_warn=min(bcv_f, base.between_stratum_cv_warn),
                ),
            )
        )
    return variants


def evaluate_blank_vector(
    values: np.ndarray,
    *,
    strata: np.ndarray | None,
    label: str,
) -> dict:
    variants = _threshold_variants()
    rows = []
    default_flag = None
    for name, thr in variants:
        flags = run_diagnostics(values, strata=strata, thresholds=thr)
        row = {
            "threshold_set": name,
            "parametric_candidate": bool(flags.parametric_candidate),
            "shape_ok": bool(flags.shape_ok),
            "censoring_ok": bool(flags.censoring_ok),
            "heterogeneity_ok": bool(flags.heterogeneity_ok),
            "skewness": flags.skewness,
            "excess_kurtosis": flags.excess_kurtosis,
            "censoring_rate": flags.censoring_rate,
            "icc": flags.icc,
            "thresholds": asdict(thr),
        }
        rows.append(row)
        if name == "default_v0.1":
            default_flag = flags.parametric_candidate

    flips = [r for r in rows if r["threshold_set"] != "default_v0.1" and r["parametric_candidate"] != default_flag]
    return {
        "label": label,
        "n": int(np.asarray(values).size),
        "default_parametric_candidate": bool(default_flag),
        "n_variants": len(rows),
        "n_flips_vs_default": len(flips),
        "flip_rate": len(flips) / max(1, len(rows) - 1),
        "flip_sets": [r["threshold_set"] for r in flips],
        "rows": rows,
    }


def run_s2_threshold_sensitivity() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    cases: list[dict] = []

    for sim_id in (
        "sim_normal_blanks",
        "sim_skewed_hetero_blanks",
        "sim_censored_floor",
        "sim_bimodal_weak_positive",
    ):
        try:
            vals, strata, label = _blank_from_sim(sim_id)
            cases.append(evaluate_blank_vector(vals, strata=strata, label=label))
        except KeyError:
            continue

    for real_id in (
        "analyseit_ep17_estradiol",
        "bioc_msstats_lobd_cptac",
        "zenodo_radioimmuno_linearity",
        "zenodo_rmn_qualification",
    ):
        got = _blank_from_real(real_id)
        if got is None:
            continue
        vals, strata, label = got
        cases.append(evaluate_blank_vector(vals, strata=strata, label=label))

    n_cases = len(cases)
    mean_flip = float(np.mean([c["flip_rate"] for c in cases])) if cases else None
    any_flip = sum(1 for c in cases if c["n_flips_vs_default"] > 0)

    # Which perturbation most often flips?
    flip_counts: dict[str, int] = {}
    for c in cases:
        for name in c["flip_sets"]:
            flip_counts[name] = flip_counts.get(name, 0) + 1

    payload = {
        "study_id": "S2-THRESHOLD-SENS-v1",
        "default_thresholds": asdict(DEFAULT_THRESHOLDS),
        "purpose": (
            "Quantify how often S2 parametric_candidate flips when DiagnosticThresholds "
            "are tightened/loosened around frozen v0.1 defaults. Defaults remain confirmatory; "
            "this study is sensitivity / education (S7-adjacent)."
        ),
        "n_cases": n_cases,
        "n_cases_with_any_flip": any_flip,
        "mean_flip_rate": mean_flip,
        "flip_count_by_threshold_set": dict(sorted(flip_counts.items(), key=lambda kv: -kv[1])),
        "cases": cases,
        "headline": {
            "n_cases": n_cases,
            "mean_flip_rate": mean_flip,
            "most_influential_sets": list(flip_counts.keys())[:5] if flip_counts else [],
            "interpretation": (
                "Non-zero flip rates mean laboratories must version and cite thresholds; "
                "frozen defaults are a convention, not a unique mathematical truth."
            ),
        },
        "claim_boundary": (
            "Does not change package defaults. Does not claim an optimal threshold set. "
            "Supports reporting threshold version in confirmatory LoD audits."
        ),
    }
    out = OUT / "s2_threshold_sensitivity.json"
    out.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    payload["path"] = str(out)
    return payload


if __name__ == "__main__":
    print(json.dumps(run_s2_threshold_sensitivity()["headline"], indent=2))
