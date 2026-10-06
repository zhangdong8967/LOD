#!/usr/bin/env python3
"""Build companion Online Supplement markdown + tables, then PDF via pandoc."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lod_guide.research.comparison_grid_export import (  # noqa: E402
    FOLKLORE_N,
    PA_GRID,
    PB_GRID,
    MIN_DELTA,
)
from lod_guide.research.e3_operating_characteristics import (  # noqa: E402
    e3_reliability_summary_rows,
    e3_vs_e2_confusion_rows,
    pass_probability,
)
from lod_guide.research.tierA_protocol_audit import (  # noqa: E402
    build_protocol_audit_rows,
    build_protocol_audit_summary_rows,
)
from lod_guide.s5_sample_size import power_two_proportions, sample_size_two_proportions  # noqa: E402
from lod_guide.theory.exact_tests import exact_power_two_proportions  # noqa: E402
from lod_guide.research.one_proportion_coverage import claim_pass_probability  # noqa: E402
from lod_guide.theory.exact import clopper_pearson_interval  # noqa: E402

OUT_TABLES = ROOT / "submission" / "supplement_tables"
SUPP_MD = ROOT / "submission" / "SUPPLEMENT.md"
MANUSCRIPT_DIR = ROOT / "manuscript"
TITLE = (
    "Claim-specific sample-size planning for binary hit-rate verification of detection capability"
)


def _write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def lattice_rows() -> tuple[list[dict], dict]:
    rows: list[dict] = []
    n_gap = 0
    n_sign = 0
    for pa in PA_GRID:
        for pb in PB_GRID:
            if not (pa > pb + MIN_DELTA):
                continue
            pw_f = float(exact_power_two_proportions(float(pa), float(pb), FOLKLORE_N, test="fisher"))
            pw_z = float(power_two_proportions(float(pa), float(pb), FOLKLORE_N, 0.05))
            ns = float(sample_size_two_proportions(float(pa), float(pb)))
            dpp = int(round((pa - pb) * 100))
            gap = pw_z - pw_f
            if abs(gap) > 1e-12:
                n_sign += 1
            if gap > 0.05:
                n_gap += 1
            rows.append(
                {
                    "p_a": round(float(pa), 2),
                    "p_b": round(float(pb), 2),
                    "delta_pp": dpp,
                    "power_exact_fisher_n20": round(pw_f, 6),
                    "power_asymptotic_n20": round(pw_z, 6),
                    "gap_asymp_minus_exact": round(gap, 6),
                    "n_star_asymptotic": round(ns, 4),
                    "beta_gt_0.8": int(pw_f < 0.2),
                }
            )
    summary = {
        "n_cells": len(rows),
        "n_any_difference": n_sign,
        "n_gap_gt_0.05": n_gap,
        "frac_beta_gt_0.8": sum(r["beta_gt_0.8"] for r in rows) / len(rows),
    }
    return rows, summary


def delta_band_rows(cell_rows: list[dict]) -> list[dict]:
    bands = [(1, 5, "1–5"), (6, 10, "6–10"), (11, 20, "11–20"), (21, 49, ">20")]
    out = []
    for lo, hi, lab in bands:
        sub = [r for r in cell_rows if lo <= r["delta_pp"] <= hi]
        ns = np.array([r["n_star_asymptotic"] for r in sub])
        pw = np.array([r["power_exact_fisher_n20"] for r in sub])
        out.append(
            {
                "delta_pp_band": lab,
                "n_cells": len(sub),
                "frac_beta_gt_0.8": round(float((pw < 0.2).mean()), 4),
                "median_power_n20": round(float(np.median(pw)), 4),
                "median_n_star_asymptotic": round(float(np.median(ns)), 1),
                "min_n_star": round(float(ns.min()), 1),
                "max_n_star": round(float(ns.max()), 1),
            }
        )
    return out


def table8_rows() -> list[dict]:
    rows = []
    for n in (20, 53, 60):
        for p in (0.90, 0.95, 0.99):
            lo20 = clopper_pearson_interval(n, n, alpha=0.05)[0] if n else None
            rows.append(
                {
                    "n": n,
                    "p_true": p,
                    "P_CP_lower_ge_0.95": round(
                        claim_pass_probability(p_true=p, n=n, claim=0.95, method="clopper"),
                        6,
                    ),
                    "CP_lower_after_n_of_n": round(clopper_pearson_interval(n, n, alpha=0.05)[0], 4),
                }
            )
    return rows


def csv_to_md(path: Path, max_rows: int | None = None) -> str:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        return ""
    header, *body = rows
    if max_rows is not None:
        extra = max(0, len(body) - max_rows)
        body = body[:max_rows]
    else:
        extra = 0
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    if extra:
        lines.append(f"\n*{extra} additional rows in `{path.name}`.*\n")
    return "\n".join(lines) + "\n"


def write_supplement_md(table_dir: Path, lattice_summary: dict) -> None:
    t3e = table_dir / "Table03e_asymptotic_vs_exact_n20.csv"
    t3f = table_dir / "Table03f_marginal_by_delta.csv"
    t7s = table_dir / "Table07b_protocol_audit_summary.csv"
    t7b = table_dir / "Table07b_protocol_audit.csv"
    t8 = table_dir / "Table08_e1_confirmation.csv"
    t9b = table_dir / "Table09b_e3_reliability_min_n.csv"
    t9c = table_dir / "Table09c_e3_vs_e2_confusion_n20.csv"
    md = f"""# Online Supplement

**Title:** {TITLE}

**Companion:** Main manuscript (clinical planning in the main text; mapping rules, lattice margins, audit ledger, and operating-characteristic tables here).

**Main manuscript figures/tables:** Fig. 1 (A–D), Fig. 2 (A–C); Tables 1–3.

**Scope.** Binary hit-rate claims only (each replicate scored detected or not). Blank-SD LoB/LoD, probit/logit concentration estimation, and EP26 quantitative lot tests are out of scope.

**Numbering.** Main-text tables are Tables 1–3. Supplement tables keep the labels cited in the main text (3e, 3f, 7b, 8, 9b, 9c) and are independent of that sequence. Supplement Table 7b is not main-text Table 3.

**Rebuild.** `python3 scripts/build_online_supplement.py`

---

## S1. Claim-mapping rules (audit)

Four phrase rules were applied to 16 publicly accessible rows (Supplementary Table 7b).

1. A stated k-of-n or 19-of-20 pass rule → qualitative pass criteria.
2. A two-lot, two-material, or two-target contrast at the LoD, or a multi-lot detect grid → two-arm comparison. “Equivalent” without a numeric margin was treated as discrimination, not TOST.
3. A single-method 95% detection claim, LoD confirmation sentence, or low-level series without a pass rule or two-arm contrast → benchmark confirmation.
4. Hospital and published x/n tables without a two-arm sentence → benchmark confirmation.

Defaults when rates were unwritten: p0 = 0.95 for benchmark confirmation; (pA, pB) = (0.90, 0.80) for two-arm records (the Introduction planning pair, not a measured hit rate in those files). Replicate counts were not imputed. None of the 16 source texts stated an 80% power target.

## S2. Lattice operating characteristics

The two-arm lattice is 1,225 equally spaced pairs with pA > pB on the integer 50–99% grid, scored with exact two-sided Fisher tests at n = 20 per arm (α = 0.05).

- Cells: {lattice_summary['n_cells']}
- Fraction with exact Fisher β > 0.80: {lattice_summary['frac_beta_gt_0.8']:.3f}
- Cells in which asymptotic pooled-z power exceeded exact Fisher by more than 0.05: {lattice_summary['n_gap_gt_0.05']} (this is the 778-cell count cited in the main text).

Fig. 1C displays n* on a 20–435 scale; that range is a plot scale (95%/90% ≈ 435) and does not cap 1-percentage-point cells.

### Supplementary Table 3f. Exact Fisher underpowering and asymptotic n* by Δp band

{csv_to_md(t3f)}

### Supplementary Table 3e. Asymptotic versus exact Fisher power at n = 20 (first 25 cells)

{csv_to_md(t3e, max_rows=25)}

## S3. Benchmark confirmation (Supplementary Table 8)

The study confirmation rule is that the lower Clopper–Pearson 95% limit for p is at least 0.95. After 20/20 positives that limit remains below 0.95. Table 8 gives the exact probability of meeting the rule when the true detection probability is 0.90, 0.95, or 0.99.

{csv_to_md(t8)}

## S4. Qualitative pass rules (Supplementary Tables 9b and 9c)

Table 9b: smallest n such that P(X ≥ k | p) ≥ 0.95 for k ∈ {{19, 18, 17}}. Table 9c: pairs in which both arms can pass 19/20 while exact Fisher power remains low.

{csv_to_md(t9b)}

{csv_to_md(t9c)}

At p = 0.95, P(X ≥ 19 | n = 20) = {pass_probability(p=0.95, n=20, k=19):.4f}.

## S5. Protocol audit ledger (Supplementary Table 7b)

Convenience sample, not a prevalence survey. Mapped claims in the ledger still use internal labels E1/E2/E3 (benchmark confirmation / two-arm / qualitative pass). Main text uses the descriptive names.

### Compact summary

{csv_to_md(t7s)}

### Verbatim quotes (truncated display; full CSV in the table folder)

{csv_to_md(t7b, max_rows=16)}

## S6. Worked example

Archived EP17 Section 7.3 language (Analyse-it estradiol workbook annotation): a minimum of 20 replicates at the LoD concentration, and for a 95% detection claim at least 19 of 20 should be detected.

| Locked claim | n at conventional 20 | n* under Table 1 targets |
| --- | --- | --- |
| Qualitative pass, k held at 19, p = 0.95 | P(pass) = 0.736 | 21 |
| Benchmark confirmation, p = 0.95 | CP lower limit after 20/20 < 0.95; P(confirm) = 0 | 53 |
| Two-arm 90%/80% | exact Fisher power ≈ 0.07 | 199 |

The audit used the qualitative-pass mapping for that sentence.

## S7. Reproducibility

Python 3.10; lod_guide v0.5.0. Tables in this file were regenerated by `scripts/build_online_supplement.py`. Main-text figures remain those in `manuscript/figures/`.
"""
    SUPP_MD.write_text(md, encoding="utf-8")


def pandoc_pdf(md_path: Path, pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    docx_path = pdf_path.with_suffix(".docx")
    subprocess.run(["pandoc", str(md_path), "-o", str(docx_path)], check=True)
    env_path = "/Library/TeX/texbin:/opt/homebrew/bin:/usr/local/bin"
    import os

    os.environ["PATH"] = env_path + ":" + os.environ.get("PATH", "")
    last_err = ""
    for engine in ("xelatex", "pdflatex", "lualatex"):
        log = pdf_path.with_suffix(f".{engine}.log")
        r = subprocess.run(
            [
                "pandoc",
                str(md_path),
                "-o",
                str(pdf_path),
                f"--pdf-engine={engine}",
                "-V",
                "geometry:margin=1in",
                "-V",
                "fontsize=11pt",
            ],
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            return
        last_err = (r.stderr or r.stdout)[-800:]
        log.write_text(last_err, encoding="utf-8")
    raise SystemExit(f"pandoc PDF failed:\n{last_err}")


def main() -> None:
    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    cells, summary = lattice_rows()
    _write_csv(
        OUT_TABLES / "Table03e_asymptotic_vs_exact_n20.csv",
        cells,
        [
            "p_a",
            "p_b",
            "delta_pp",
            "power_exact_fisher_n20",
            "power_asymptotic_n20",
            "gap_asymp_minus_exact",
            "n_star_asymptotic",
            "beta_gt_0.8",
        ],
    )
    _write_csv(
        OUT_TABLES / "Table03f_marginal_by_delta.csv",
        delta_band_rows(cells),
        [
            "delta_pp_band",
            "n_cells",
            "frac_beta_gt_0.8",
            "median_power_n20",
            "median_n_star_asymptotic",
            "min_n_star",
            "max_n_star",
        ],
    )
    audit = build_protocol_audit_rows()
    summary_rows = build_protocol_audit_summary_rows(audit)
    claim_map = {
        "E1": "benchmark confirmation",
        "E2": "two-arm",
        "E3": "qualitative pass",
    }
    for r in audit:
        r["mapped_claim"] = claim_map.get(str(r.get("mapped_claim")), r.get("mapped_claim"))
    for r in summary_rows:
        r["mapped_claim"] = claim_map.get(str(r.get("mapped_claim")), r.get("mapped_claim"))
    fields = [
        "audit_id",
        "evidence_tier",
        "mapped_claim",
        "archived_n",
        "guidance_n_star",
        "n_ratio_vs_20",
        "oc_metric",
        "oc_value_at_archived_n",
        "target_rates",
        "quote_source",
        "protocol_quote",
    ]
    _write_csv(OUT_TABLES / "Table07b_protocol_audit.csv", audit, fields)
    _write_csv(
        OUT_TABLES / "Table07b_protocol_audit_summary.csv",
        summary_rows,
        [
            "no",
            "audit_id",
            "evidence_tier",
            "mapped_claim",
            "archived_n",
            "guidance_n_star",
            "n_ratio_vs_20",
            "oc_metric",
            "oc_value_at_archived_n",
        ],
    )
    _write_csv(
        OUT_TABLES / "Table08_e1_confirmation.csv",
        table8_rows(),
        ["n", "p_true", "P_CP_lower_ge_0.95", "CP_lower_after_n_of_n"],
    )
    _write_csv(
        OUT_TABLES / "Table09b_e3_reliability_min_n.csv",
        e3_reliability_summary_rows(),
        ["k", "p_pct", "target_P_pass", "min_n", "pass_rule_at_min_n", "P_pass_at_min_n"],
    )
    _write_csv(
        OUT_TABLES / "Table09c_e3_vs_e2_confusion_n20.csv",
        e3_vs_e2_confusion_rows(),
        [
            "pair",
            "n_per_arm",
            "pass_rule",
            "P_pass_arm_a",
            "P_pass_arm_b",
            "P_both_arms_pass",
            "exact_fisher_power",
            "miss_beta_fisher",
        ],
    )
    write_supplement_md(OUT_TABLES, summary)
    print(f"Wrote {SUPP_MD}")
    print("lattice", summary)
    pdf = MANUSCRIPT_DIR / "Online_Supplement.pdf"
    pandoc_pdf(SUPP_MD, pdf)
    dest = ROOT / "submission" / "Online_Supplement.pdf"
    dest.write_bytes(pdf.read_bytes())
    print(f"Wrote {pdf} and {dest}")


if __name__ == "__main__":
    main()
