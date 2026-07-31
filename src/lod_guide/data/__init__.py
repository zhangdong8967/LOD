"""
Unified catalogue of real + simulated LoD datasets for diverse benchmarking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from lod_guide.data.download_real import (
    RAW_DIR,
    REMOTE_DATASETS,
    download_all_real,
    load_zenodo_qpcr_cq,
    parse_real_dataset,
)
from lod_guide.data.simulate import SimulatedDataset, generate_all_simulated
from lod_guide.s0_goal import Goal


@dataclass
class CatalogueEntry:
    dataset_id: str
    source: str  # real | simulated
    result_type: str
    description: str
    challenge_tags: list[str]
    citation: str = ""
    path: str | None = None
    evidence_tier: str = ""
    guidance: dict[str, Any] = field(default_factory=dict)


def build_catalogue(*, download: bool = True, regenerate_sim: bool = True) -> list[CatalogueEntry]:
    entries: list[CatalogueEntry] = []

    sims = generate_all_simulated()
    for ds in sims:
        entries.append(
            CatalogueEntry(
                dataset_id=ds.dataset_id,
                source="simulated",
                result_type=ds.result_type,
                description=ds.description,
                challenge_tags=ds.challenge_tags,
                citation="lod_guide.data.simulate (in silico stress DGP)",
                path=str(Path(ds.to_disk())),
                evidence_tier="S",
            )
        )

    if download:
        results = download_all_real()
    else:
        results = {ds.dataset_id: RAW_DIR / ds.filename for ds in REMOTE_DATASETS}

    meta_by_id = {d.dataset_id: d for d in REMOTE_DATASETS}
    for did, path_or_err in results.items():
        meta = meta_by_id[did]
        if isinstance(path_or_err, Exception) or not Path(str(path_or_err)).exists():
            entries.append(
                CatalogueEntry(
                    dataset_id=did,
                    source="real",
                    result_type=meta.result_family,
                    description=f"FAILED download: {path_or_err}",
                    challenge_tags=["download_failed"],
                    citation=meta.citation,
                    evidence_tier=meta.evidence_tier,
                )
            )
            continue
        path = Path(path_or_err)
        entries.append(
            CatalogueEntry(
                dataset_id=did,
                source="real",
                result_type=meta.result_family,
                description=meta.citation,
                challenge_tags=["real_public", meta.result_family, f"tier_{meta.evidence_tier}"],
                citation=meta.citation,
                path=str(path),
                evidence_tier=meta.evidence_tier,
            )
        )
    return entries


def run_guidance_on_entry(entry: CatalogueEntry) -> dict[str, Any]:
    """Map each catalogue entry to an appropriate guidance goal and run S0–S7."""
    from lod_guide.pipeline import run_guidance

    if entry.source == "simulated":
        from lod_guide.data.simulate import SIM_DIR
        import json

        payload = json.loads((SIM_DIR / f"{entry.dataset_id}.json").read_text(encoding="utf-8"))
        meta = payload.get("meta") or {}
        values = np.array(payload["values"], dtype=float) if payload.get("values") else None
        strata = np.array(payload["strata"]) if payload.get("strata") else None
        low = np.array(payload["low_level"], dtype=float) if payload.get("low_level") else None
        rt = payload["result_type"]

        if entry.dataset_id == "sim_binary_reagents_90_vs_80":
            res = run_guidance(
                goal=Goal.G2_COMPARE_REAGENTS,
                result_type="binary",
                use_case="kit_a_vs_kit_b_near_lod",
                p_a=meta["p_a"],
                p_b=meta["p_b"],
                run_sensitivity=False,
            )
        elif entry.dataset_id == "sim_binary_low_p_lod":
            res = run_guidance(
                goal=Goal.G1_VERIFY_LOD,
                result_type="binary",
                use_case="ldt_lod_establishment",
                p=meta["p"],
                p0=meta["p0_claim"],
                run_sensitivity=False,
            )
        elif entry.dataset_id == "sim_multiclass_blood_type":
            res = run_guidance(
                goal=Goal.G4_QUALITATIVE_KN,
                result_type="multiclass",
                n_classes=meta["n_classes"],
                success_definition=meta["success_definition"],
                p=meta["p_success"],
                k=1,
                power=0.95,
                run_sensitivity=False,
            )
        elif rt == "count":
            res = run_guidance(
                goal=Goal.G1_VERIFY_LOD,
                result_type="count",
                values=values,
                strata=strata,
                use_case="ldt_lod_establishment",
                p=0.8,
                p0=0.95,
                cluster_size=40,
                run_sensitivity=False,
            )
        else:
            res = run_guidance(
                goal=Goal.G1_VERIFY_LOD,
                result_type="continuous",
                values=values,
                strata=strata,
                low_level=low,
                use_case="ldt_lod_establishment",
                p0=0.95,
                cluster_size=20,
                run_sensitivity=False,
            )
        return {
            "dataset_id": entry.dataset_id,
            "evidence_tier": entry.evidence_tier,
            "goal": res.goal.goal.value,
            "model_path": res.model_path.value,
            "parametric_ok": res.report.parametric_ok,
            "n_per_arm": res.sample_size.n_per_arm,
            "correction": res.report.correction_method,
            "warnings_n": len(res.report.warnings),
            "challenges_folklore_n20": any("n=20" in w for w in res.report.warnings),
            "dgp": meta.get("dgp"),
        }

    if entry.path and Path(entry.path).exists():
        parsed = parse_real_dataset(entry.dataset_id, Path(entry.path))
        values = np.asarray(parsed.get("blank_values") or [0.0], dtype=float)
        strata_raw = parsed.get("blank_strata")
        strata = np.asarray(strata_raw) if strata_raw is not None and len(strata_raw) == len(values) else None
        low_list = parsed.get("low_level_values") or []
        low = np.asarray(low_list, dtype=float) if low_list else None

        # Probit / hit-rate family: G2 from two concentration tiers if available
        hit_summary = parsed.get("hit_summary") or {}
        if hit_summary:
            rates = [(sq, info["rate"], info["n"]) for sq, info in hit_summary.items() if float(sq) >= 0]
            rates = sorted(rates, key=lambda t: t[0])
            out: dict[str, Any] = {
                "dataset_id": entry.dataset_id,
                "evidence_tier": entry.evidence_tier,
                "assay_family": parsed.get("assay_family"),
                "n_rows": parsed.get("n_rows"),
                "hit_summary_head": rates[:6],
            }
            # still run continuous blank guidance if blanks exist and non-trivial
            if values.size >= 5 and float(np.nanstd(values)) > 0:
                res = run_guidance(
                    goal=Goal.G1_VERIFY_LOD,
                    result_type="continuous",
                    values=values,
                    strata=strata,
                    low_level=low,
                    use_case="ldt_lod_establishment",
                    p0=0.95,
                    cluster_size=8,
                    run_sensitivity=False,
                )
                out.update(
                    {
                        "goal": res.goal.goal.value,
                        "model_path": res.model_path.value,
                        "parametric_ok": res.report.parametric_ok,
                        "n_per_arm": res.sample_size.n_per_arm,
                    }
                )
            if len(rates) >= 2:
                p_hi = rates[-1][1]
                p_lo = rates[0][1]
                if abs(p_hi - p_lo) > 0.02:
                    cmp = run_guidance(
                        goal=Goal.G2_COMPARE_REAGENTS,
                        result_type="binary",
                        use_case="kit_a_vs_kit_b_near_lod",
                        p_a=max(p_hi, p_lo),
                        p_b=min(p_hi, p_lo),
                        run_sensitivity=False,
                    )
                    out["g2_from_hit_rates"] = {
                        "p_a": max(p_hi, p_lo),
                        "p_b": min(p_hi, p_lo),
                        "n_per_arm": cmp.sample_size.n_per_arm,
                    }
            return out

        res = run_guidance(
            goal=Goal.G1_VERIFY_LOD,
            result_type="continuous",
            values=values if values.size else np.array([0.0]),
            strata=strata,
            low_level=low,
            use_case="ldt_lod_establishment",
            p0=0.95,
            cluster_size=8,
            run_sensitivity=False,
        )
        return {
            "dataset_id": entry.dataset_id,
            "evidence_tier": entry.evidence_tier,
            "assay_family": parsed.get("assay_family"),
            "goal": res.goal.goal.value,
            "model_path": res.model_path.value,
            "parametric_ok": res.report.parametric_ok,
            "n_per_arm": res.sample_size.n_per_arm,
            "correction": res.report.correction_method,
            "warnings_n": len(res.report.warnings),
            "n_blank": int(values.size),
            "evidence_note": parsed.get("evidence_note"),
        }

    return {"dataset_id": entry.dataset_id, "error": "missing path"}


def run_diverse_benchmark(*, download: bool = True) -> list[dict[str, Any]]:
    cat = build_catalogue(download=download)
    return [run_guidance_on_entry(e) for e in cat if "download_failed" not in e.challenge_tags]
