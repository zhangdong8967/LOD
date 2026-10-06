"""
Build manuscript-ready table copies (readable columns, no developer JSON noise).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from lod_guide.paper.registry import PAPER, TABLES
from lod_guide.paper.theory_research import build_table4
from lod_guide.research.s2_threshold_table import TABLE_NAME, export_s2_threshold_table, s2_threshold_rows

ROOT = Path(__file__).resolve().parents[3]


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})


def build_manuscript_tables() -> dict[str, str]:
    out_dir = PAPER / "tables" / "manuscript"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = PAPER / "tables"
    written: dict[str, str] = {}

    # Table 1 — estimands
    t1 = _read_csv(raw_dir / "Table01_estimands_E1_E3.csv")
    if t1:
        # map common developer columns if present
        mapped = []
        for r in t1:
            mapped.append(
                {
                    "Goal": r.get("goal") or r.get("Estimand") or r.get("estimand"),
                    "Estimand": r.get("estimand_symbol") or r.get("Symbol"),
                    "Definition": r.get("definition") or r.get("Definition"),
                    "Sample_size_method": r.get("sample_size_engine") or r.get("Sample_size_engine"),
                }
            )
        _write_csv(
            out_dir / "Table01_estimands_E1_E3.csv",
            mapped,
            ["Goal", "Estimand", "Definition", "Sample_size_method"],
        )
        written["Table1"] = str(out_dir / "Table01_estimands_E1_E3.csv")

    # Table 2 — LoQ
    t2 = _read_csv(raw_dir / "Table02_loq_precision_main.csv")
    if t2:
        mapped = []
        for r in t2:
            mapped.append(
                {
                    "Quantity": r.get("quantity") or r.get("Quantity") or r.get("metric"),
                    "Value": r.get("value") or r.get("Value") or r.get("result"),
                    "Unit_or_note": r.get("unit") or r.get("note") or r.get("Unit_or_note") or "",
                }
            )
        # if columns already readable, pass through selected keys
        if not mapped[0]["Quantity"]:
            keys = list(t2[0].keys())
            _write_csv(out_dir / "Table02_loq_precision_main.csv", t2, keys)
        else:
            _write_csv(
                out_dir / "Table02_loq_precision_main.csv",
                mapped,
                ["Quantity", "Value", "Unit_or_note"],
            )
        written["Table2"] = str(out_dir / "Table02_loq_precision_main.csv")

    # Table 2a — frozen S2 diagnostic thresholds (supplement only)
    export_s2_threshold_table(raw_dir)
    t2a = s2_threshold_rows()
    if t2a:
        keys = list(t2a[0].keys())
        _write_csv(out_dir / TABLE_NAME, t2a, keys)
        written["Table2a"] = str(out_dir / TABLE_NAME)

    # Table 3 — exact vs asymp + grid extensions
    t3 = _read_csv(raw_dir / "Table03_exact_vs_asymptotic.csv")
    if t3:
        prefer = [
            "p_a",
            "p_b",
            "n",
            "power_asymptotic_pooled_z",
            "power_exact_fisher",
            "power_exact_pooled_z_enum",
            "miss_beta_exact_fisher",
        ]
        keys = [k for k in prefer if k in t3[0]] or list(t3[0].keys())
        keys = [k for k in keys if "json" not in k.lower()]
        _write_csv(out_dir / "Table03_exact_vs_asymptotic.csv", t3, keys)
        written["Table3"] = str(out_dir / "Table03_exact_vs_asymptotic.csv")

    # Table 3 — reference pairs (manuscript slim)
    t3ref = raw_dir / "Table03_reference_pairs_n20.csv"
    if t3ref.exists():
        rows = _read_csv(t3ref)
        if rows:
            slim = []
            for r in rows:
                slim.append(
                    {
                        "pair": r.get("pair"),
                        "delta_p": f"{float(r['delta_p']):.2f}" if r.get("delta_p") else "",
                        "n": r.get("n"),
                        "power_exact_fisher": f"{float(r['power_exact_fisher']):.3f}"
                        if r.get("power_exact_fisher")
                        else "",
                        "miss_beta": f"{float(r['miss_beta_exact_fisher']):.3f}"
                        if r.get("miss_beta_exact_fisher")
                        else "",
                        "n_star_ceiling": r.get("n_star_ceiling"),
                    }
                )
            _write_csv(
                out_dir / "Table03_reference_pairs_n20.csv",
                slim,
                ["pair", "delta_p", "n", "power_exact_fisher", "miss_beta", "n_star_ceiling"],
            )
            written["Table3_reference"] = str(out_dir / "Table03_reference_pairs_n20.csv")

    ext_grid = raw_dir / "Table03_comparison_grid_n20.csv"
    if ext_grid.exists():
        rows = _read_csv(ext_grid)
        if rows:
            _write_csv(out_dir / "Table03_comparison_grid_n20.csv", rows, list(rows[0].keys()))
            written["Table03_comparison_grid_n20.csv"] = str(out_dir / "Table03_comparison_grid_n20.csv")

    # Table 4 — propositions P1–P18 (canonical + legacy aliases)
    t4 = build_table4(force_verify=False, tables_root=PAPER / "tables")
    written["Table4"] = t4["Table4_csv"]
    written["Table4_json"] = t4["Table4_json"]

    # Table 5 — evidence ladder
    t5 = _read_csv(raw_dir / "Table05_evidence_ladder.csv")
    if t5:
        mapped = [
            {
                "Evidence_tier": r.get("evidence_tier"),
                "Dataset_ID": r.get("dataset_id"),
                "Result_family": r.get("result_family"),
                "Present": r.get("present"),
                "May_support_empirical_claim": r.get("may_support_empirical_claim"),
                "Citation": (r.get("citation") or "")[:120],
            }
            for r in t5
        ]
        _write_csv(
            out_dir / "Table05_evidence_ladder.csv",
            mapped,
            [
                "Evidence_tier",
                "Dataset_ID",
                "Result_family",
                "Present",
                "May_support_empirical_claim",
                "Citation",
            ],
        )
        written["Table5"] = str(out_dir / "Table05_evidence_ladder.csv")

    # Table 6 — type I
    t6 = _read_csv(raw_dir / "Table06_type1_calibration.csv")
    if t6:
        keys = [k for k in t6[0].keys() if "json" not in k.lower()]
        _write_csv(out_dir / "Table06_type1_calibration.csv", t6, keys)
        written["Table6"] = str(out_dir / "Table06_type1_calibration.csv")

    # Table 7 — tier A meta with abbreviated citations
    TIER_A_CITATIONS = {
        "zenodo_mus_wt_qpcr": "Piaggio et al. (2024)",
        "zenodo_mus_multiplex_qpcr": "Piaggio et al. (2024)",
        "analyseit_ep17_estradiol": "Analyse-it EP17 workbook",
        "analyseit_ep17_probit": "Analyse-it EP17 workbook",
        "mendeley_carobene_lombardy_eqa": "Carobene et al. (2026)",
        "bioc_msstats_lobd_cptac": "MSstatsLOBD / CPTAC",
        "zenodo_radioimmuno_precision": "Malkamäki et al. (2024)",
        "zenodo_radioimmuno_linearity": "Malkamäki et al. (2024)",
        "zenodo_rmn_qualification": "Sawant et al. (2025)",
    }
    t7 = raw_dir / "Table07_tierA_meta.csv"
    if t7.exists():
        rows7 = _read_csv(t7)
        if rows7:
            mapped7 = []
            for i, r in enumerate(rows7, start=1):
                ratio = r.get("n_ratio_vs_folklore") or ""
                mapped7.append(
                    {
                        "No": str(i),
                        "Citation": TIER_A_CITATIONS.get(r.get("dataset_id", ""), r.get("dataset_id", "")),
                        "result_family": r.get("result_family"),
                        "model_path": r.get("model_path"),
                        "guidance_n": r.get("guidance_n"),
                        "folklore_n": r.get("folklore_n"),
                        "n_star_over_n20": ratio,
                    }
                )
            _write_csv(
                out_dir / "Table07_tierA_meta.csv",
                mapped7,
                [
                    "No",
                    "Citation",
                    "result_family",
                    "model_path",
                    "guidance_n",
                    "folklore_n",
                    "n_star_over_n20",
                ],
            )
            written["Table7"] = str(out_dir / "Table07_tierA_meta.csv")

    # Table 7b — protocol-file audit matrix (Supplement)
    t7b = raw_dir / "Table07b_protocol_audit.csv"
    if t7b.exists():
        rows7b = _read_csv(t7b)
        if rows7b:
            mapped7b = []
            for i, r in enumerate(rows7b, start=1):
                mapped7b.append(
                    {
                        "No": str(i),
                        "Audit_ID": r.get("audit_id"),
                        "Tier": r.get("evidence_tier"),
                        "Mapped_claim": r.get("mapped_claim"),
                        "Archived_n": r.get("archived_n"),
                        "Guidance_n_star": r.get("guidance_n_star"),
                        "n_star_over_n20": r.get("n_ratio_vs_20"),
                        "OC_metric": r.get("oc_metric"),
                        "OC_at_archived_n": r.get("oc_value_at_archived_n"),
                        "Protocol_quote": (r.get("protocol_quote") or "")[:200],
                        "Quote_source": (r.get("quote_source") or "")[:120],
                    }
                )
            _write_csv(
                out_dir / "Table07b_protocol_audit.csv",
                mapped7b,
                [
                    "No",
                    "Audit_ID",
                    "Tier",
                    "Mapped_claim",
                    "Archived_n",
                    "Guidance_n_star",
                    "n_star_over_n20",
                    "OC_metric",
                    "OC_at_archived_n",
                    "Protocol_quote",
                    "Quote_source",
                ],
            )
            written["Table7b"] = str(out_dir / "Table07b_protocol_audit.csv")

    # Table 7b-S — compact protocol audit summary (Supplement)
    t7bs = raw_dir / "Table07b_protocol_audit_summary.csv"
    if t7bs.exists():
        rows7bs = _read_csv(t7bs)
        if rows7bs:
            mapped7bs = []
            for i, r in enumerate(rows7bs, start=1):
                mapped7bs.append(
                    {
                        "No": str(i),
                        "Audit_ID": r.get("audit_id"),
                        "Tier": r.get("evidence_tier"),
                        "Mapped_claim": r.get("mapped_claim"),
                        "Archived_n": r.get("archived_n"),
                        "Guidance_n_star": r.get("guidance_n_star"),
                        "n_star_over_n20": r.get("n_ratio_vs_20"),
                        "OC_metric": r.get("oc_metric"),
                        "OC_at_archived_n": r.get("oc_value_at_archived_n"),
                        "Empirical_rate": r.get("empirical_rate_at_archived_n"),
                        "OC_below_target": r.get("oc_below_mapped_target"),
                    }
                )
            _write_csv(
                out_dir / "Table07b_protocol_audit_summary.csv",
                mapped7bs,
                [
                    "No",
                    "Audit_ID",
                    "Tier",
                    "Mapped_claim",
                    "Archived_n",
                    "Guidance_n_star",
                    "n_star_over_n20",
                    "OC_metric",
                    "OC_at_archived_n",
                    "Empirical_rate",
                    "OC_below_target",
                ],
            )
            written["Table7bS"] = str(out_dir / "Table07b_protocol_audit_summary.csv")

    # Table 8 — E1 coverage if present
    t8 = raw_dir / "Table08_e1_one_proportion_coverage.csv"
    if t8.exists():
        rows8 = _read_csv(t8)
        if rows8:
            _write_csv(out_dir / "Table08_e1_one_proportion_coverage.csv", rows8, list(rows8[0].keys()))
            written["Table8"] = str(out_dir / "Table08_e1_one_proportion_coverage.csv")

    return written


if __name__ == "__main__":
    print(json.dumps(build_manuscript_tables(), indent=2))
