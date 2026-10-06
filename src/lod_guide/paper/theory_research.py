"""
Unified theory research pipeline.

Chains:
  1. verify   — P1–P18 + supplementary certificates → data/audit/
  2. depth    — identification, c-optimal, minimax, Pareto, gated LoB studies
  3. table4   — manuscript Table 4 CSV/JSON + D1–D3 defect bundle
  4. review   — internal referee memo (P1–P18)
  5. bundle   — copy audit JSON into paper_artifacts/audit/
"""

from __future__ import annotations

import csv
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from lod_guide.theory.audit import sha256_hex
from lod_guide.theory.claim_types import claim_type_for
from lod_guide.theory.propositions import verify_all_propositions, verify_by_layer
from lod_guide.theory.types import TheoryResult

ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = ROOT / "data" / "audit"
RESEARCH_DIR = ROOT / "data" / "research"
PAPER = ROOT / "paper_artifacts"
PAPER_AUDIT = PAPER / "audit"
PAPER_TABLES = PAPER / "tables"
PAPER_REVIEW = PAPER / "review"

THEORY_AUDIT_JSON = AUDIT_DIR / "theory_verification_latest.json"
TABLE4_CANONICAL = "Table04_propositions_P1_P18.csv"
TABLE4_JSON = "Table04_propositions.json"
DEFECTS_JSON = "D1_D3_verification_defects.json"

# Main-text theory layer (Supplement §S2b)
VERIFICATION_DEFECTS: dict[str, dict[str, Any]] = {
    "D1": {
        "title": "Estimand conflation (E3 vs E1 vs E2)",
        "summary": (
            "E3 pass, E1 confirmation, and E2 discrimination are distinct acceptance events; "
            "filing one as evidence for another mixes estimands."
        ),
        "certificate_ids": [
            "P7_all_positive_trap",
            "T1_e3_pass_fisher_separation",
        ],
        "manuscript_tables": ["Table08_e1_one_proportion_coverage.csv", "Table09_e3_pass_rule.csv"],
    },
    "D2": {
        "title": "Small-n operating-characteristic gap (design vs confirmation)",
        "summary": (
            "Asymptotic pooled-z power can exceed exact Fisher power at folklore n; "
            "S5 design must be followed by S6 exact confirmation."
        ),
        "certificate_ids": [
            "P8_exact_vs_asymptotic_gap",
            "T2a_pooled_z_fisher_distinct",
            "T2b_berry_esseen_design_scale",
            "T4_fleiss_nstar_delta_scaling",
        ],
        "manuscript_tables": ["Table03_exact_vs_asymptotic.csv", "Table03e_p8_gap_cells.csv"],
    },
    "D3": {
        "title": "Pareto-inadmissible folklore designs (E2)",
        "summary": (
            "Folklore n=20 can be strictly Pareto-dominated on the exact Fisher (Type I, power) plane "
            "by powered n* for prespecified (p_A, p_B)."
        ),
        "certificate_ids": ["P18_folklore_pareto_dominated"],
        "manuscript_tables": ["Table03_exact_vs_asymptotic.csv", "Table03_comparison_grid_n20.csv"],
    },
}


def _now_utc() -> str:
    return datetime.now(UTC).isoformat()


def run_theory_verification(*, force: bool = False) -> dict[str, Any]:
    """Run P1–P18 verification and write canonical audit JSON."""
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    certs = verify_all_propositions(force=force)
    by_layer = {layer: verify_by_layer(layer) for layer in ("A", "B", "C")}
    failed = [c for c in certs if not c.passed]

    payload: dict[str, Any] = {
        "protocol_id": "LOD-THEORY-VERIFY-v1",
        "created_utc": _now_utc(),
        "n_total": len(certs),
        "n_failed": len(failed),
        "layers": {
            layer: {
                "count": len(rows),
                "passed": sum(1 for c in rows if c.passed),
                "results": [c.to_dict() for c in rows],
            }
            for layer, rows in by_layer.items()
        },
        "all_results": [c.to_dict() for c in certs],
    }
    payload["content_sha256"] = sha256_hex(
        {k: v for k, v in payload.items() if k != "content_sha256"}
    )

    THEORY_AUDIT_JSON.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return {
        "audit_path": str(THEORY_AUDIT_JSON),
        "n_total": len(certs),
        "n_failed": len(failed),
        "content_sha256": payload["content_sha256"],
        "failed_ids": [c.result_id for c in failed],
    }


def run_theory_depth(
    *,
    studies: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Run theory-depth research deposits (identification, design, Pareto, gated LoB)."""
    from lod_guide.research.minimax_probit_design import run_minimax_probit_design
    from lod_guide.research.pareto_exact_sample_size import run_pareto_exact_sample_size
    from lod_guide.research.pre_test_lob_inflation import run_pre_test_lob_inflation
    from lod_guide.research.probit_design_robustness import run_probit_design_robustness
    from lod_guide.research.theory_depth_studies import run_c_optimal_study, run_identification_study

    from lod_guide.research.reliability_summaries import run_reliability_summaries
    from lod_guide.research.tost_equivalence_branch import run_tost_equivalence_branch

    runners: dict[str, Callable[[], dict]] = {
        "identification": run_identification_study,
        "c_optimal": run_c_optimal_study,
        "minimax_probit": run_minimax_probit_design,
        "probit_robustness": run_probit_design_robustness,
        "pre_test_lob": run_pre_test_lob_inflation,
        "pareto_exact_n": run_pareto_exact_sample_size,
        "reliability_summary": run_reliability_summaries,
        "tost_equivalence": run_tost_equivalence_branch,
    }
    selected = studies or tuple(runners.keys())
    outputs: dict[str, Any] = {}
    for name in selected:
        if name not in runners:
            raise ValueError(f"Unknown theory-depth study: {name!r}")
        out = runners[name]()
        outputs[name] = {
            "path": out.get("path"),
            "study_id": out.get("study_id"),
            "headline": out.get("headline"),
        }
    return {"studies": outputs, "n_studies": len(outputs)}


def _certs_for_table4(*, force_verify: bool) -> tuple[list[TheoryResult], str]:
    from lod_guide.paper.theory_audit import (
        certs_from_audit,
        load_theory_certificates,
        theory_audit_ok,
    )

    if force_verify:
        certs = verify_all_propositions(force=True)
        source = "live verify_all_propositions(force=True)"
    else:
        certs = load_theory_certificates(force_verify=False)
        source = (
            str(THEORY_AUDIT_JSON)
            if theory_audit_ok() and THEORY_AUDIT_JSON.is_file()
            else "live verify_all_propositions()"
        )
    return certs, source


HEADLINE_PROPOSITIONS = frozenset(
    {"P7_all_positive_trap", "P8_exact_vs_asymptotic_gap", "P18_folklore_pareto_dominated"}
)
HEADLINE_EXTENSION_THEOREMS = frozenset(
    {
        "T1_e3_pass_fisher_separation",
        "T2a_pooled_z_fisher_distinct",
        "T2b_berry_esseen_design_scale",
        "T4_fleiss_nstar_delta_scaling",
        "T5_tost_vs_e2_non_nested",
    }
)
EXTENSION_PREFIXES = ("P12_", "P13_", "P14_", "P15_", "P16_", "P17_", "C_optimal_")


def proposition_role(result_id: str) -> str:
    """Classify certificates for Table 4 (headline / headline extension / core / extension / supplementary)."""
    if result_id in HEADLINE_PROPOSITIONS:
        return "headline"
    if result_id in HEADLINE_EXTENSION_THEOREMS:
        return "headline extension"
    if result_id.startswith(EXTENSION_PREFIXES):
        return "extension"
    if result_id in {
        "P1_saturation",
        "P2_binomial_reliability",
        "P3_two_proportion_power",
        "P4_design_effect",
        "P5_parametric_lob_inconsistency",
        "P6_ovl_separation",
        "P9_holm_fwer",
        "P10_weight_scale_invariance",
        "P11_tobit_uncensored_agreement",
    }:
        return "core"
    return "supplementary"


def build_table4(*, force_verify: bool = False, tables_root: Path | None = None) -> dict[str, str]:
    """Build Table 4 CSV/JSON and legacy filename aliases."""
    certs, source = _certs_for_table4(force_verify=force_verify)
    root = tables_root or PAPER_TABLES
    out_dir = root / "manuscript"
    raw_dir = root
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    csv_rows = [
        {
            "Proposition": c.result_id,
            "Role": proposition_role(c.result_id),
            "Claim_type": claim_type_for(c.result_id),
            "Layer": c.layer,
            "Statement": c.statement,
            "Passed": c.passed,
            "Key_details": json.dumps(c.details, default=str)[:200],
        }
        for c in certs
    ]
    csv_fields = ["Proposition", "Role", "Claim_type", "Layer", "Statement", "Passed", "Key_details"]
    canonical = out_dir / TABLE4_CANONICAL
    _write_csv(canonical, csv_rows, csv_fields)

    dev_rows = [
        {
            "proposition_id": c.result_id,
            "role": proposition_role(c.result_id),
            "claim_type": claim_type_for(c.result_id),
            "layer": c.layer,
            "statement": c.statement,
            "passed": c.passed,
            "details_json": json.dumps(c.details, default=str),
        }
        for c in certs
    ]
    dev_path = raw_dir / "Table04_propositions_P1_P6.csv"
    _write_csv(
        dev_path,
        dev_rows,
        ["proposition_id", "role", "claim_type", "layer", "statement", "passed", "details_json"],
    )

    # Legacy aliases (same content as canonical manuscript table)
    for alias in ("Table04_propositions_P1_P8.csv",):
        shutil.copy2(canonical, out_dir / alias)

    audit_sha = ""
    if THEORY_AUDIT_JSON.is_file():
        try:
            audit_sha = json.loads(THEORY_AUDIT_JSON.read_text(encoding="utf-8")).get(
                "content_sha256", ""
            )
        except (json.JSONDecodeError, OSError):
            audit_sha = ""

    json_payload = {
        "protocol_id": "LOD-THEORY-TABLE4-v1",
        "created_utc": _now_utc(),
        "certificate_source": source,
        "theory_audit_sha256": audit_sha,
        "n_total": len(certs),
        "n_failed": sum(1 for c in certs if not c.passed),
        "propositions": [
            {
                "proposition_id": c.result_id,
                "role": proposition_role(c.result_id),
            "claim_type": claim_type_for(c.result_id),
                "layer": c.layer,
                "statement": c.statement,
                "passed": c.passed,
                "proof_sketch": c.proof_sketch[:500] if c.proof_sketch else "",
                "details": c.details,
            }
            for c in certs
        ],
    }
    json_payload["content_sha256"] = sha256_hex(
        {k: v for k, v in json_payload.items() if k != "content_sha256"}
    )
    json_path = out_dir / TABLE4_JSON
    json_path.write_text(json.dumps(json_payload, indent=2, default=str), encoding="utf-8")

    return {
        "Table4_csv": str(canonical),
        "Table4_json": str(json_path),
        "Table4_dev_csv": str(dev_path),
        "certificate_source": source,
        "content_sha256": json_payload["content_sha256"],
    }


def build_defects_bundle(
    *, force_verify: bool = False, audit_root: Path | None = None
) -> dict[str, str]:
    """Map main-text defects D1–D3 to certificate rows (Supplement §S2b)."""
    certs, _ = _certs_for_table4(force_verify=force_verify)
    by_id = {c.result_id: c for c in certs}
    audit_dir = audit_root or PAPER_AUDIT
    audit_dir.mkdir(parents=True, exist_ok=True)

    defects: dict[str, Any] = {}
    for defect_id, meta in VERIFICATION_DEFECTS.items():
        linked = []
        for cid in meta["certificate_ids"]:
            cert = by_id.get(cid)
            if cert is None:
                linked.append({"certificate_id": cid, "found": False})
            else:
                linked.append(
                    {
                        "certificate_id": cid,
                        "found": True,
                        "layer": cert.layer,
                        "passed": cert.passed,
                        "statement": cert.statement,
                        "headline_details": _headline_details(cert),
                    }
                )
        defects[defect_id] = {**meta, "certificates": linked}

    payload = {
        "protocol_id": "LOD-THEORY-DEFECTS-v1",
        "created_utc": _now_utc(),
        "defects": defects,
        "scope": {
            "closed": [
                "Estimand lock → OC design → exact confirmation → tiered report (S0–S7)",
                "Binomial / Fisher / Clopper–Pearson engines at c*",
                "Decision-risk audit ledger L (equal default weights)",
            ],
            "extension_branches": [
                "Multilevel LoD estimation (P12–P16)",
                "TOST / formal equivalence on theta_2",
                "Clinical utility–optimal L weights",
                "PCR Poisson-binomial (Vaks et al.)",
            ],
        },
    }
    if THEORY_AUDIT_JSON.is_file():
        try:
            payload["theory_audit_sha256"] = json.loads(
                THEORY_AUDIT_JSON.read_text(encoding="utf-8")
            ).get("content_sha256", "")
        except (json.JSONDecodeError, OSError):
            pass
    payload["content_sha256"] = sha256_hex(
        {k: v for k, v in payload.items() if k != "content_sha256"}
    )

    path = audit_dir / DEFECTS_JSON
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return {"defects_json": str(path), "content_sha256": payload["content_sha256"]}


def copy_audit_bundle() -> dict[str, str]:
    """Mirror theory audit JSON into paper_artifacts/audit/."""
    PAPER_AUDIT.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    if THEORY_AUDIT_JSON.is_file():
        dest = PAPER_AUDIT / THEORY_AUDIT_JSON.name
        shutil.copy2(THEORY_AUDIT_JSON, dest)
        written["theory_verification"] = str(dest)
    return written


def write_theory_summary(*, force_verify: bool = False) -> Path:
    """Human-readable theory research summary for co-authors."""
    certs, source = _certs_for_table4(force_verify=force_verify)
    by_layer = {layer: [c for c in certs if c.layer == layer] for layer in ("A", "B", "C")}
    PAPER_REVIEW.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Theory research summary",
        "",
        f"**Generated:** {_now_utc()}",
        f"**Certificate source:** `{source}`",
        "",
        "## Layer counts",
        "",
    ]
    for layer in ("A", "B", "C"):
        rows = by_layer[layer]
        n_pass = sum(1 for c in rows if c.passed)
        lines.append(f"- **Layer {layer}:** {n_pass}/{len(rows)} passed")
    lines += [
        "",
        "## Verification defects (main text D1–D3)",
        "",
    ]
    for defect_id, meta in VERIFICATION_DEFECTS.items():
        lines.append(f"### {defect_id} — {meta['title']}")
        lines.append("")
        lines.append(meta["summary"])
        lines.append("")
        lines.append(f"Certificates: {', '.join(meta['certificate_ids'])}")
        lines.append("")

    lines += ["## All certificates", ""]
    for c in certs:
        mark = "PASS" if c.passed else "FAIL"
        lines.append(f"- `[{mark}]` **{c.result_id}** (layer {c.layer}): {c.statement}")

    path = PAPER_REVIEW / "THEORY_RESEARCH_SUMMARY.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def audit_check(*, min_total: int = 27) -> dict[str, Any]:
    """Check canonical theory audit JSON without rerunning certificates."""
    from lod_guide.paper.theory_audit import theory_audit_ok, theory_bundle_ok

    ok = theory_audit_ok(min_total=min_total)
    bundle_ok = theory_bundle_ok()
    payload: dict[str, Any] = {
        "ok": ok and bundle_ok,
        "audit_ok": ok,
        "bundle_ok": bundle_ok,
        "audit_path": str(THEORY_AUDIT_JSON),
        "exists": THEORY_AUDIT_JSON.is_file(),
    }
    if THEORY_AUDIT_JSON.is_file():
        try:
            data = json.loads(THEORY_AUDIT_JSON.read_text(encoding="utf-8"))
            payload.update(
                {
                    "n_total": data.get("n_total"),
                    "n_failed": data.get("n_failed"),
                    "content_sha256": data.get("content_sha256"),
                    "created_utc": data.get("created_utc"),
                }
            )
        except (json.JSONDecodeError, OSError) as exc:
            payload["ok"] = False
            payload["error"] = str(exc)
    else:
        payload["ok"] = False
    return payload


def ensure_theory_research(*, force: bool = False, depth: bool = True) -> dict[str, Any]:
    """
    Ensure theory audit + paper bundle are current.

    - ``force=True`` or ``LOD_REFRESH_THEORY=1``: full verify + depth + Table 4.
    - Audit OK but bundle stale: rebuild Table 4 / defects / audit mirror (skip verify).
    - Audit stale: run verify then rebuild bundle.
    """
    from lod_guide.paper.theory_audit import refresh_flag, theory_audit_ok, theory_bundle_ok

    force = force or refresh_flag("LOD_REFRESH_THEORY")
    if not force and theory_bundle_ok():
        return {
            "status": "ok",
            "skipped": True,
            "reason": "theory audit and paper_artifacts bundle in sync",
        }

    need_verify = force or not theory_audit_ok()
    print(
        "[theory] "
        + (
            "running full theory pipeline (verify + depth + Table 4)…"
            if need_verify
            else "rebuilding paper theory bundle from existing audit…"
        ),
        flush=True,
    )
    result = run_theory_pipeline(
        verify=need_verify,
        depth=depth,
        table4=True,
        internal_review=False,
        summary=True,
        copy_audit=True,
        force_verify=force,
    )
    result["status"] = "refreshed"
    result["skipped"] = False
    return result


def run_theory_pipeline(
    *,
    verify: bool = True,
    depth: bool = True,
    table4: bool = True,
    internal_review: bool = False,
    summary: bool = True,
    copy_audit: bool = True,
    force_verify: bool = False,
    depth_studies: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """One-click complete theory research pipeline."""
    result: dict[str, Any] = {"steps": {}}

    if verify or force_verify:
        vr = run_theory_verification(force=force_verify)
        result["steps"]["verify"] = vr
        if vr["n_failed"]:
            raise SystemExit(f"Theory verification failed: {vr['failed_ids']}")

    if depth:
        result["steps"]["depth"] = run_theory_depth(studies=depth_studies)

    if table4:
        result["steps"]["table4"] = build_table4(force_verify=force_verify)
        result["steps"]["defects"] = build_defects_bundle(force_verify=force_verify)

    if copy_audit:
        result["steps"]["audit_bundle"] = copy_audit_bundle()

    if summary:
        result["steps"]["summary"] = {"path": str(write_theory_summary(force_verify=force_verify))}

    if internal_review:
        from lod_guide.paper.internal_review import write_internal_review_memo

        paths = write_internal_review_memo(force_theory_verify=force_verify)
        result["steps"]["internal_review"] = {k: str(v) for k, v in paths.items()}

    check = audit_check()
    result["audit_check"] = check
    if not check.get("ok"):
        raise SystemExit("Theory audit check failed after pipeline run.")
    return result


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k) for k in fieldnames})


def _headline_details(cert: TheoryResult) -> dict[str, Any]:
    d = cert.details
    if cert.result_id == "P7_all_positive_trap":
        return {k: d.get(k) for k in ("n", "P_all_positive", "CP_onesided_lower", "claim") if k in d}
    if cert.result_id == "P8_exact_vs_asymptotic_gap":
        return {
            k: d.get(k)
            for k in ("p_a", "p_b", "n", "power_asymptotic", "power_fisher_exact", "gap")
            if k in d
        }
    if cert.result_id == "P18_folklore_pareto_dominated":
        return {
            k: d.get(k)
            for k in ("folklore_n", "powered_n_star", "loss_ratio", "n_dominators")
            if k in d
        }
    return {k: d[k] for k in list(d.keys())[:6]}
