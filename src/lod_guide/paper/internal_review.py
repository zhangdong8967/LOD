"""
Internal referee-style review: P1–P18 certificates + exact vs asymptotic table.

Writes Markdown memo + CSV tables under paper_artifacts/.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from lod_guide.paper.theory_audit import load_theory_certificates, refresh_flag, theory_audit_ok
from lod_guide.paper.theory_research import VERIFICATION_DEFECTS, build_defects_bundle
from lod_guide.research.comparison_grid_export import export_comparison_grid_tables, grid_csv_rows
from lod_guide.research.exact_power_study import run_exact_power_study

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "paper_artifacts"
TABLES = PAPER / "tables"
REVIEW = PAPER / "review"
THEORY_AUDIT = ROOT / "data" / "audit" / "theory_verification_latest.json"
EXACT_JSON = ROOT / "data" / "research" / "exact_vs_asymptotic_power.json"


def _load_proposition_rows(*, force_verify: bool) -> tuple[list[dict], str]:
    certs = load_theory_certificates(force_verify=force_verify)
    source = (
        "live verify_all_propositions()"
        if force_verify or refresh_flag("LOD_REFRESH_THEORY") or not theory_audit_ok()
        else str(THEORY_AUDIT)
    )

    rows = [
        {
            "proposition_id": c.proposition_id,
            "statement": c.statement,
            "passed": c.passed,
            "details_json": json.dumps(c.details, default=str),
        }
        for c in certs
    ]
    return rows, source


def _write_propositions_csv(path: Path, *, force_verify: bool) -> list[dict]:
    rows, _ = _load_proposition_rows(force_verify=force_verify)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["proposition_id", "statement", "passed", "details_json"])
        w.writeheader()
        w.writerows(rows)
    return rows


def _load_exact_study(*, force_exact: bool) -> dict:
    if (
        not force_exact
        and not refresh_flag("LOD_REFRESH_EXACT")
        and EXACT_JSON.is_file()
    ):
        print(
            "[paper] internal review: exact power from data/research/exact_vs_asymptotic_power.json "
            "(set LOD_REFRESH_EXACT=1 to rerun)",
            flush=True,
        )
        return json.loads(EXACT_JSON.read_text(encoding="utf-8"))
    print("[paper] internal review: running run_exact_power_study()...", flush=True)
    return run_exact_power_study()


def _write_exact_csv(path: Path, study: dict) -> dict:
    rows = study["rows"]
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("label\n", encoding="utf-8")
        return study
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    return study


def write_internal_review_memo(
    *,
    force_exact: bool = False,
    force_theory_verify: bool = False,
) -> dict[str, Path]:
    TABLES.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)

    prop_csv = TABLES / "Table04_propositions_P1_P6.csv"
    exact_csv = TABLES / "Table03_exact_vs_asymptotic.csv"
    prop_rows = _write_propositions_csv(prop_csv, force_verify=force_theory_verify)
    build_defects_bundle(force_verify=force_theory_verify)
    study = _load_exact_study(force_exact=force_exact)
    _write_exact_csv(exact_csv, study)
    grid_tables = export_comparison_grid_tables(TABLES)

    # Referee memo
    fails = [r for r in prop_rows if not r["passed"]]
    memo_lines = [
        "# Internal statistical review memo",
        "",
        "**Scope.** Machine certificates **P1–P18** (plus supplementary results), "
        "verification defects **D1–D3** (Supplement §S2b), and exact vs asymptotic "
        "discrimination power (Table 3–4).",
        "",
        "## Verification defects (D1–D3)",
        "",
    ]
    for defect_id, meta in VERIFICATION_DEFECTS.items():
        memo_lines.append(f"### {defect_id} — {meta['title']}")
        memo_lines.append("")
        memo_lines.append(meta["summary"])
        memo_lines.append("")
        memo_lines.append(f"Certificates: {', '.join(meta['certificate_ids'])}")
        memo_lines.append("")
    memo_lines += [
        "## Verdict on propositions",
        "",
        f"- Certificates run: **{len(prop_rows)}**; failures: **{len(fails)}**.",
    ]
    for r in prop_rows:
        status = "PASS" if r["passed"] else "FAIL"
        memo_lines.append(f"- `{r['proposition_id']}` — **{status}**: {r['statement']}")
    memo_lines += [
        "",
        "### Referee notes (P1–P8 core)",
        "",
        "- **P1 (saturation):** Correct and central; φ_n must not be used for E2.",
        "- **P2 (binomial identity):** Algebraic; keep as sanity certificate.",
        "- **P3 (Fleiss–Chow):** Asymptotic n* calibrates pooled-z MC power near target; "
        "at folklore n=20, **exact Fisher power is materially lower** than asymptotic "
        "(see Table 3: 90 vs 80 → ~7% Fisher vs ~14% asymptotic). Do not oversell P3 as "
        "exact small-sample calibration.",
        "- **P4 (design effect):** Standard compound-symmetry DE; state ICC estimation uncertainty.",
        "- **P5 (parametric LoB mismatch):** Strong counterexample (Exp); supports S2/S3 gate.",
        "- **P6 (OVL):** Separation on a denser n-grid; not a substitute for power calculations.",
        "- **P7 (all-positive trap):** n/n does not certify high LoD claims (α^(1/n) << claim). **Headline D1.**",
        "- **P8 (exact vs asymptotic gap):** At folklore n for close alternatives, asymptotic "
        "power overstates exact Fisher power — design surface ≠ confirmation. **Headline D2.**",
        "",
        "### Referee notes (P9–P18 extensions)",
        "",
        "- **P9 (Holm FWER):** MC sketch for multi-arm gates; corroborates S4 multiplicity policy.",
        "- **P10 (weight scale):** L is homogeneous in weights — audit ledger, not utility optimum.",
        "- **P11 (Tobit):** Agreement with naive mean+z·SD when uncensored; supports parametric LoB path.",
        "- **P12–P14 (c-optimal / minimax / efficiency):** Multilevel **estimation** branch; "
        "not required for E1–E3 verification at c* but documents design dominance over equal-log folklore.",
        "- **P15–P16 (identification):** LoD identifiable on interior hit-rate grid; saturation plates break identifiability.",
        "- **P17 (gated LoB inflation):** Pre-test model selection can inflate Type I; sample-split remedy in supplementary certificate.",
        "- **P18 (folklore inadmissible):** n=20 Pareto-dominated on exact Fisher OC plane. **Headline D3.**",
        "",
        "## Exact vs asymptotic (Table 3)",
        "",
        study.get("interpretation", ""),
        "",
        "### Highlights",
        "",
    ]
    hl = study.get("highlights") or {}
    for k, v in hl.items():
        memo_lines.append(f"- **{k}:** `{json.dumps(v, default=str)}`")
    memo_lines += [
        "",
        "### Table 3 extensions (full E2 grid @ n=20)",
        "",
        f"- **reference pairs:** `{grid_tables.get('reference_pairs', '')}`",
        f"- **full grid ({len(grid_csv_rows())} cells):** `{grid_tables.get('full_grid', '')}`",
        "",
        "### Reporting policy (locked)",
        "",
    ]
    for k, v in (study.get("reporting_policy") or {}).items():
        memo_lines.append(f"- **{k}:** {v}")
    memo_lines += [
        "",
        "## Publication readiness (this memo)",
        "",
        "These tables are **submission-ready as supplementary statistical appendices** "
        "once captions are frozen. They do **not** by themselves make a full Clinical Chemistry "
        "paper complete (need narrative manuscript; LoQ engine + estradiol analysis now present as supplements).",
        "",
    ]
    memo_path = REVIEW / "INTERNAL_REVIEW_THEORY.md"
    est_csv = TABLES / "Table01_estimands_E1_E3.csv"
    with est_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["goal", "estimand_symbol", "definition", "sample_size_engine"])
        w.writerow([
            "E1",
            "p(c*) >= p0",
            "Benchmark confirmation: hit rate at c* meets IFU benchmark (typically p0=0.95); one-sided Clopper-Pearson limits",
            "one-proportion vs p0",
        ])
        w.writerow([
            "E2",
            "p_A(c*) - p_B(c*)",
            "Two-arm contrast at c*: lot/reagent discrimination theta2; exact Fisher primary (Boschloo optional confirmatory)",
            "two-proportion exact Fisher-Boschloo",
        ])
        w.writerow([
            "E3",
            "P(X>=k)",
            "Qualitative pass rule (e.g. 19/20): operating event {X>=k}; binomial pass probability distinct from E1 confirmation",
            "binomial cumulative search",
        ])

    from lod_guide.data.download_real import REMOTE_DATASETS, RAW_DIR

    ev_csv = TABLES / "Table05_evidence_ladder.csv"
    with ev_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dataset_id", "result_family", "evidence_tier", "filename", "present", "citation"])
        for d in REMOTE_DATASETS:
            present = (RAW_DIR / d.filename).exists()
            w.writerow([d.dataset_id, d.result_family, d.evidence_tier, d.filename, present, d.citation])

    # Type I calibration table (may be precomputed)
    type1_csv = TABLES / "Table06_type1_calibration.csv"
    type1_path = ROOT / "data" / "research" / "type1_calibration.json"
    if not type1_path.exists():
        from lod_guide.research.type1_calibration import run_type1_calibration_study
        run_type1_calibration_study(n_sims=2000, include_boschloo_n=-1)
    if type1_path.exists():
        t1 = json.loads(type1_path.read_text(encoding="utf-8"))
        rows = t1.get("rows") or []
        if rows:
            keys = list(rows[0].keys())
            with type1_csv.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=keys)
                w.writeheader()
                w.writerows(rows)
    memo_lines += [
        "",
        "## Type I calibration (Table 6)",
        "",
        "See `tables/Table06_type1_calibration.csv` and data/research/type1_calibration.json.",
        "",
    ]
    memo_path.write_text("\n".join(memo_lines), encoding="utf-8")
    legacy_memo = REVIEW / "INTERNAL_REVIEW_P1P6_EXACT.md"
    legacy_memo.write_text(memo_path.read_text(encoding="utf-8"), encoding="utf-8")

    return {
        "memo": memo_path,
        "propositions_csv": prop_csv,
        "exact_csv": exact_csv,
        "grid_reference_csv": Path(grid_tables.get("reference_pairs", "")),
        "grid_full_csv": Path(grid_tables.get("full_grid", "")),
        "estimands_csv": est_csv,
        "evidence_csv": ev_csv,
        "type1_csv": type1_csv,
    }
