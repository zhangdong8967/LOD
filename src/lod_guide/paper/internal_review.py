"""
Internal referee-style review: P1–P6 certificates + exact vs asymptotic table.

Writes Markdown memo + CSV tables under paper_artifacts/.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from lod_guide.research.exact_power_study import run_exact_power_study
from lod_guide.theory.propositions import verify_all_propositions

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "paper_artifacts"
TABLES = PAPER / "tables"
REVIEW = PAPER / "review"


def _write_propositions_csv(path: Path) -> list[dict]:
    certs = verify_all_propositions()
    rows = []
    for c in certs:
        rows.append(
            {
                "proposition_id": c.proposition_id,
                "statement": c.statement,
                "passed": c.passed,
                "details_json": json.dumps(c.details, default=str),
            }
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["proposition_id", "statement", "passed", "details_json"])
        w.writeheader()
        w.writerows(rows)
    return rows


def _write_exact_csv(path: Path) -> dict:
    study = run_exact_power_study()
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


def write_internal_review_memo(*, force_exact: bool = True) -> dict[str, Path]:
    TABLES.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)

    prop_csv = TABLES / "Table04_propositions_P1_P6.csv"
    exact_csv = TABLES / "Table03_exact_vs_asymptotic.csv"
    prop_rows = _write_propositions_csv(prop_csv)
    study = _write_exact_csv(exact_csv) if force_exact else json.loads(
        (ROOT / "data" / "research" / "exact_vs_asymptotic_power.json").read_text()
    )

    # Referee memo
    fails = [r for r in prop_rows if not r["passed"]]
    memo_lines = [
        "# Internal statistical review memo",
        "",
        "**Scope.** Machine certificates P1–P8 and exact vs asymptotic discrimination power (Table 3–4).",
        "",
        "## Verdict on propositions",
        "",
        f"- Certificates run: **{len(prop_rows)}**; failures: **{len(fails)}**.",
    ]
    for r in prop_rows:
        status = "PASS" if r["passed"] else "FAIL"
        memo_lines.append(f"- `{r['proposition_id']}` — **{status}**: {r['statement']}")
    memo_lines += [
        "",
        "### Referee notes (P1–P8)",
        "",
        "- **P1 (saturation):** Correct and central; φ_n must not be used for G2.",
        "- **P2 (binomial identity):** Algebraic; keep as sanity certificate.",
        "- **P3 (Fleiss–Chow):** Asymptotic n* calibrates pooled-z MC power near target; "
        "at folklore n=20, **exact Fisher power is materially lower** than asymptotic "
        "(see Table 3: 90 vs 80 → ~7% Fisher vs ~14% asymptotic). Do not oversell P3 as "
        "exact small-sample calibration.",
        "- **P4 (design effect):** Standard compound-symmetry DE; state ICC estimation uncertainty.",
        "- **P5 (parametric LoB mismatch):** Strong counterexample (Exp); supports S2/S3 gate.",
        "- **P6 (OVL):** Separation on a denser n-grid; not a substitute for power calculations.",
        "- **P7 (all-positive trap):** n/n does not certify high LoD claims (α^(1/n) << claim).",
        "- **P8 (exact vs asymptotic gap):** At folklore n for close alternatives, asymptotic "
        "power overstates exact Fisher power — design surface ≠ confirmation.",
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
    memo_path = REVIEW / "INTERNAL_REVIEW_P1P6_EXACT.md"
    memo_path.write_text("\n".join(memo_lines), encoding="utf-8")

    # also write estimands + evidence quick tables
    est_csv = TABLES / "Table01_estimands_G1_G4.csv"
    with est_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["goal", "estimand_symbol", "definition", "sample_size_engine"])
        w.writerow(["G1", "p(c*) or LoD claim", "Single-method LoD verification", "one-proportion vs p0"])
        w.writerow(["G2", "p_A-p_B at c*", "Compare reagents/lots at LoD concentration", "two-proportion / exact Fisher-Boschloo"])
        w.writerow(["G4", "P(X>=k)", "Qualitative k/n at detection limit", "binomial cumulative search"])

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

    return {
        "memo": memo_path,
        "propositions_csv": prop_csv,
        "exact_csv": exact_csv,
        "estimands_csv": est_csv,
        "evidence_csv": ev_csv,
        "type1_csv": type1_csv,
    }
