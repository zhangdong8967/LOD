"""
Build manuscript-ready table copies (readable columns, no developer JSON noise).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from lod_guide.paper.registry import PAPER, TABLES
from lod_guide.theory.propositions import verify_all_propositions

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
    t1 = _read_csv(raw_dir / "Table01_estimands_G1_G4.csv")
    if t1:
        # map common developer columns if present
        mapped = []
        for r in t1:
            mapped.append(
                {
                    "Estimand": r.get("goal") or r.get("Estimand") or r.get("estimand"),
                    "Symbol": r.get("estimand_symbol") or r.get("Symbol"),
                    "Definition": r.get("definition") or r.get("Definition"),
                    "Sample_size_engine": r.get("sample_size_engine") or r.get("Sample_size_engine"),
                }
            )
        _write_csv(
            out_dir / "Table01_estimands_G1_G4.csv",
            mapped,
            ["Estimand", "Symbol", "Definition", "Sample_size_engine"],
        )
        written["Table1"] = str(out_dir / "Table01_estimands_G1_G4.csv")

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

    # Table 3 — exact vs asymp
    t3 = _read_csv(raw_dir / "Table03_exact_vs_asymptotic.csv")
    if t3:
        prefer = [
            "p_A",
            "p_B",
            "n",
            "power_asymptotic",
            "power_fisher_exact",
            "power_pooled_z_exact",
            "miss_beta_fisher",
        ]
        keys = [k for k in prefer if k in t3[0]] or list(t3[0].keys())
        # strip details_json-like
        keys = [k for k in keys if "json" not in k.lower()]
        _write_csv(out_dir / "Table03_exact_vs_asymptotic.csv", t3, keys)
        written["Table3"] = str(out_dir / "Table03_exact_vs_asymptotic.csv")

    # Table 4 — propositions P1–P18 (CSV filename kept for artifact compatibility)
    certs = verify_all_propositions()
    rows = [
        {
            "Proposition": c.proposition_id,
            "Statement": c.statement,
            "Passed": c.passed,
            "Key_details": json.dumps(c.details, default=str)[:200],
        }
        for c in certs
    ]
    _write_csv(
        out_dir / "Table04_propositions_P1_P8.csv",
        rows,
        ["Proposition", "Statement", "Passed", "Key_details"],
    )
    # also refresh developer table
    _write_csv(
        raw_dir / "Table04_propositions_P1_P6.csv",
        [
            {
                "proposition_id": c.proposition_id,
                "statement": c.statement,
                "passed": c.passed,
                "details_json": json.dumps(c.details, default=str),
            }
            for c in certs
        ],
        ["proposition_id", "statement", "passed", "details_json"],
    )
    written["Table4"] = str(out_dir / "Table04_propositions_P1_P8.csv")

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

    # Table 7 — already written by tierA meta; ensure copy
    t7 = raw_dir / "Table07_tierA_meta.csv"
    if t7.exists():
        rows7 = _read_csv(t7)
        if rows7:
            keys = [
                "dataset_id",
                "evidence_tier",
                "result_family",
                "parametric_candidate",
                "model_path",
                "guidance_n",
                "folklore_n",
                "n_ratio_vs_folklore",
                "loq_at_cv20",
                "allowed_claim",
            ]
            keys = [k for k in keys if k in rows7[0]]
            _write_csv(out_dir / "Table07_tierA_meta.csv", rows7, keys)
            written["Table7"] = str(out_dir / "Table07_tierA_meta.csv")

    # Table 8 — G1 coverage if present
    t8 = raw_dir / "Table08_g1_one_proportion_coverage.csv"
    if t8.exists():
        rows8 = _read_csv(t8)
        if rows8:
            _write_csv(out_dir / "Table08_g1_one_proportion_coverage.csv", rows8, list(rows8[0].keys()))
            written["Table8"] = str(out_dir / "Table08_g1_one_proportion_coverage.csv")

    return written


if __name__ == "__main__":
    print(json.dumps(build_manuscript_tables(), indent=2))
