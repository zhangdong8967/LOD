"""
Strict A/B/C/S stratified evidence report for the paper.

Writes:
  - data/research/EVIDENCE_STRATIFIED_REPORT.md
  - paper_artifacts/tables/Table05_evidence_ladder.csv (refreshed)
  - paper_artifacts/review/EVIDENCE_CLAIMS_BY_TIER.md
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from lod_guide.data.download_real import RAW_DIR, REMOTE_DATASETS, download_all_real, write_evidence_manifest
from lod_guide.data.simulate import generate_all_simulated

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "research"
PAPER = ROOT / "paper_artifacts"


def build_evidence_stratified_report(*, download: bool = True) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    (PAPER / "tables").mkdir(parents=True, exist_ok=True)
    (PAPER / "review").mkdir(parents=True, exist_ok=True)

    if download:
        results = download_all_real()
    else:
        results = {d.dataset_id: RAW_DIR / d.filename for d in REMOTE_DATASETS}
    write_evidence_manifest(results)

    sims = generate_all_simulated()
    tiers = {"A": [], "B": [], "C": [], "S": []}
    for d in REMOTE_DATASETS:
        path_or_err = results.get(d.dataset_id)
        present = isinstance(path_or_err, Path) and path_or_err.exists()
        if not present and isinstance(path_or_err, Path):
            present = path_or_err.exists()
        if isinstance(path_or_err, Exception):
            present = False
            err = str(path_or_err)
        else:
            err = None
        row = {
            "dataset_id": d.dataset_id,
            "result_family": d.result_family,
            "evidence_tier": d.evidence_tier,
            "filename": d.filename,
            "present": present,
            "citation": d.citation,
            "license_note": d.license_note,
            "error": err,
        }
        tiers.setdefault(d.evidence_tier, []).append(row)

    for s in sims:
        tiers["S"].append(
            {
                "dataset_id": s.dataset_id,
                "result_family": s.result_type,
                "evidence_tier": "S",
                "filename": f"{s.dataset_id}.json",
                "present": True,
                "citation": "lod_guide.data.simulate stress DGP",
                "license_note": "in silico",
                "dgp": (s.meta or {}).get("dgp"),
            }
        )

    # Table 5 CSV
    csv_path = PAPER / "tables" / "Table05_evidence_ladder.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "evidence_tier",
                "dataset_id",
                "result_family",
                "filename",
                "present",
                "may_support_empirical_claim",
                "citation",
            ]
        )
        for tier in ("A", "B", "C", "S"):
            for row in tiers.get(tier, []):
                may = "yes_primary" if tier == "A" else (
                    "corroboration_only" if tier == "B" else (
                        "demo_only" if tier == "C" else "mechanism_only"
                    )
                )
                w.writerow(
                    [
                        tier,
                        row["dataset_id"],
                        row["result_family"],
                        row["filename"],
                        row.get("present"),
                        may,
                        row.get("citation"),
                    ]
                )

    # empirical extension summary if present
    emp_path = OUT / "empirical_tierA_extension.json"
    emp = json.loads(emp_path.read_text(encoding="utf-8")) if emp_path.exists() else None

    md_lines = [
        "# Evidence stratified by tier (A/B/C/S)",
        "",
        "This report is the **claim firewall**: what each tier may support in the manuscript.",
        "",
        "## Tier meanings",
        "",
        "| Tier | Meaning | Allowed manuscript use |",
        "|------|---------|------------------------|",
        "| **A** | Public raw / replicate-level validation tables | Primary empirical illustrations |",
        "| **B** | Summaries / very small-n deposits | Diversity / external corroboration only |",
        "| **C** | Synthetic EP17 demos (match Mean/SD) | Method walk-through only — **not clinical truth** |",
        "| **S** | Simulation stress DGPs | Mechanism, coverage, power — **not** multi-assay validation |",
        "",
        f"## Counts",
        "",
        f"- Tier A: **{len(tiers['A'])}** datasets",
        f"- Tier B: **{len(tiers['B'])}**",
        f"- Tier C: **{len(tiers['C'])}**",
        f"- Tier S: **{len(tiers['S'])}** simulations",
        "",
    ]
    for tier in ("A", "B", "C", "S"):
        md_lines += [f"## Tier {tier}", ""]
        for row in tiers[tier]:
            md_lines.append(
                f"- `{row['dataset_id']}` ({row['result_family']}) — present={row.get('present')} — {row.get('citation')}"
            )
        md_lines.append("")

    md_lines += [
        "## Empirical tier-A extension (new continuous/precision deposits)",
        "",
    ]
    if emp:
        for b in emp.get("blocks") or []:
            md_lines.append(f"- `{b['dataset_id']}` tier={b.get('evidence_tier')}")
            an = b.get("analysis") or b.get("analysis_precision") or {}
            if an.get("loq_at_cv20") is not None:
                md_lines.append(f"  - LoQ@CV20≈{an.get('loq_at_cv20')} ({an.get('loq_method')})")
            ac = b.get("analysis_continuous") or {}
            if ac.get("lob_parametric") is not None:
                md_lines.append(
                    f"  - continuous gate: parametric_candidate={ac.get('parametric_candidate')}, "
                    f"path={ac.get('model_path')}"
                )
        md_lines += ["", emp.get("claim_boundary", ""), ""]
    else:
        md_lines.append("_Run `python -m lod_guide.research.empirical_tierA_extension` first._")
        md_lines.append("")

    md_lines += [
        "## Forbidden overclaims",
        "",
        "- Do not cite tier C/S as proof the algorithm is clinically validated for all chemistry panels.",
        "- Do not pool A+C+S into a single “N datasets support the algorithm” sentence without stratification.",
        "",
    ]

    report_md = OUT / "EVIDENCE_STRATIFIED_REPORT.md"
    report_md.write_text("\n".join(md_lines), encoding="utf-8")
    claims = PAPER / "review" / "EVIDENCE_CLAIMS_BY_TIER.md"
    claims.write_text("\n".join(md_lines), encoding="utf-8")

    return {
        "report": str(report_md),
        "claims": str(claims),
        "table5": str(csv_path),
        "counts": {k: len(v) for k, v in tiers.items()},
        "empirical_extension": (emp.get("path") if emp else None) or (str(emp_path) if emp_path.exists() else None),
    }


if __name__ == "__main__":
    print(json.dumps(build_evidence_stratified_report(), indent=2))
