#!/usr/bin/env python3
"""One-time migration: G1/G2/G4 → E1/E2/E3; G3 → LOQ (LoQ branch)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
}
SKIP_PATH_PARTS = (
    "literature/endnote",
    "literature/software",
)
SKIP_SUFFIXES = {".nbib", ".enw", ".pyc", ".png", ".pdf", ".docx", ".log", ".aux"}

# Longest-first token replacements (code + prose)
REPLACEMENTS: list[tuple[str, str]] = [
    # Files / module paths
    ("Table01_estimands_G1_G4", "Table01_estimands_E1_E3"),
    ("Table08b_g1_claim_pass", "Table08b_e1_claim_pass"),
    ("Table08_g1_one_proportion_coverage", "Table08_e1_one_proportion_coverage"),
    ("Table09c_g4_vs_g2_confusion", "Table09c_e3_vs_e2_confusion"),
    ("Table09b_g4_reliability_min_n", "Table09b_e3_reliability_min_n"),
    ("Table09_g4_operating_characteristics", "Table09_e3_operating_characteristics"),
    ("g4_operating_characteristics.json", "e3_operating_characteristics.json"),
    ("g4_operating_characteristics", "e3_operating_characteristics"),
    ("run_g4_operating_characteristics_study", "run_e3_operating_characteristics_study"),
    ("T9_g4_operating", "T9_e3_operating"),
    ("T8_g1_coverage", "T8_e1_coverage"),
    ("T2_loq_precision", "T2_loq_precision"),  # noop anchor
    # Enum / IDs
    ("G4_QUALITATIVE_KN", "E3_QUALITATIVE_KN"),
    ("G4_KN_PROBABILITY", "E3_KN_PROBABILITY"),
    ("G4-OPERATING-CHARACTERISTICS", "E3-OPERATING-CHARACTERISTICS"),
    ("G4_N_VALUES", "E3_N_VALUES"),
    ("G4_P_PCT", "E3_P_PCT"),
    ("G1-ONE-PROPORTION-COVERAGE", "E1-ONE-PROPORTION-COVERAGE"),
    ("G1_VERIFY_LOD", "E1_VERIFY_LOD"),
    ("G1_DETECTION_PROBABILITY", "E1_DETECTION_PROBABILITY"),
    ("G1_LOD_CONCENTRATION", "E1_LOD_CONCENTRATION"),
    ("G2_COMPARE_REAGENTS", "E2_COMPARE_REAGENTS"),
    ("G2_RATE_DIFFERENCE", "E2_RATE_DIFFERENCE"),
    ("G3_LOQ_PRECISION", "LOQ_PRECISION"),
    ("G3_CV_AT_CONCENTRATION", "LOQ_CV_AT_CONCENTRATION"),
    # Scenario / JSON keys
    ("G2_folklore_n20_", "E2_folklore_n20_"),
    ("G2_powered_nstar_", "E2_powered_nstar_"),
    ("G2_median_folklore_over_powered", "E2_median_folklore_over_powered"),
    ("G2_loss_ratio_folklore_over_powered", "E2_loss_ratio_folklore_over_powered"),
    ("G2_loss_ratio_by_pair", "E2_loss_ratio_by_pair"),
    ("G2_ratio_folklore_over_powered", "E2_ratio_folklore_over_powered"),
    ("G1_loss_ratio_parametric_over_nonparametric", "E1_loss_ratio_parametric_over_nonparametric"),
    ("G1_ratio_para_over_nonpar", "E1_ratio_para_over_nonpar"),
    ("G2_ignored_ICC_DE", "E2_ignored_ICC_DE"),
    ("G1_parametric_LoB_on_Exp", "E1_parametric_LoB_on_Exp"),
    ("G1_nonparametric_LoB_on_Exp", "E1_nonparametric_LoB_on_Exp"),
    ("g4_vs_g2_confusion", "e3_vs_e2_confusion"),
    ("g4_grid_rows", "e3_grid_rows"),
    ("g4_reliability_summary_rows", "e3_reliability_summary_rows"),
    ("g4_vs_g2_confusion_rows", "e3_vs_e2_confusion_rows"),
    # Prose combos (before single tokens)
    ("G1–G4", "E1–E3"),
    ("G1-G4", "E1-E3"),
    ("G1, G2, or G4", "E1, E2, or E3"),
    ("G1, G2, or G4", "E1, E2, or E3"),
    ("G1, G2, and G4", "E1, E2, and E3"),
    ("G1/G2/G4", "E1/E2/E3"),
    ("G1/G2/G4", "E1/E2/E3"),
    ("G1 and G2", "E1 and E2"),
    ("G4 and G1", "E3 and E1"),
    ("G4 or G1", "E3 or E1"),
    ("G4 vs G2", "E3 vs E2"),
    ("G4-vs-G2", "E3-vs-E2"),
    ("G4-type", "E3-type"),
    ("G4 pass", "E3 pass"),
    ("G4 rule", "E3 rule"),
    ("G4 and G1", "E3 and E1"),
    ("G4/G1", "E3/E1"),
    ("for G4/G1", "for E3/E1"),
    ("G2 decision", "E2 decision"),
    ("G2 estimand", "E2 estimand"),
    ("G2 planning", "E2 planning"),
    ("G2 sample", "E2 sample"),
    ("G2 (main", "E2 (main"),
    ("G2 (90", "E2 (90"),
    ("G2 (two", "E2 (two"),
    ("G2 at", "E2 at"),
    ("G2.", "E2."),
    ("G2,", "E2,"),
    ("G2 ", "E2 "),
    ("G2)", "E2)"),
    ("G2:", "E2:"),
    ("G2;", "E2;"),
    ("G1 (benchmark", "E1 (benchmark"),
    ("G1 (confirmatory", "E1 (confirmatory"),
    ("G1 (single", "E1 (single"),
    ("G1 at", "E1 at"),
    ("G1.", "E1."),
    ("G1,", "E1,"),
    ("G1 ", "E1 "),
    ("G1)", "E1)"),
    ("G1:", "E1:"),
    ("G4 (rule", "E3 (rule"),
    ("G4 (19", "E3 (19"),
    ("G4.", "E3."),
    ("G4,", "E3,"),
    ("G4 ", "E3 "),
    ("G4)", "E3)"),
    ("G4:", "E3:"),
    ("**G4**", "**E3**"),
    ("**G2**", "**E2**"),
    ("**G1**", "**E1**"),
    ("(G4)", "(E3)"),
    ("(G2)", "(E2)"),
    ("(G1)", "(E1)"),
    ("estimand G4", "estimand E3"),
    ("estimand G2", "estimand E2"),
    ("estimand G1", "estimand E1"),
    ("estimands G1", "estimands E1"),
    ("Primary LoD estimands G1, G2, G4", "Primary LoD verification estimands E1, E2, E3"),
    ("G1, G2, G4", "E1, E2, E3"),
    ("G1/G2/G4", "E1/E2/E3"),
    ("G3 LoQ", "LoQ branch"),
    ("(G3 LoQ", "(LoQ branch"),
    ("G3 (LoQ", "LoQ branch ("),
    ("**G3**", "**LoQ branch**"),
    ("G3)", "LoQ)"),
    ("G3 ", "LoQ "),
    ("G3.", "LoQ."),
    ("G3,", "LoQ,"),
    ("(G3)", "(LoQ)"),
    ("Goal.G4", "Goal.E3_QUALITATIVE_KN"),
    ("Goal.G3", "Goal.LOQ_PRECISION"),
    ("Goal.G2", "Goal.E2_COMPARE_REAGENTS"),
    ("Goal.G1", "Goal.E1_VERIFY_LOD"),
    # Table row IDs
    ('["G4",', '["E3",'),
    ('["G2",', '["E2",'),
    ('["G1",', '["E1",'),
    ('| **G4** |', '| **E3** |'),
    ('| **G2** |', '| **E2** |'),
    ('| **G1** |', '| **E1** |'),
    # Figure labels
    ('"G1 verify"', '"E1 verify"'),
    ('"G2 compare"', '"E2 compare"'),
    ('"G4 $k/n$"', '"E3 $k/n$"'),
    ("G1\\nVerify", "E1\\nVerify"),
    ("G2\\nCompare", "E2\\nCompare"),
    ("G4\\nk/n", "E3\\nk/n"),
    ("G2 · lot", "E2 · lot"),
    ("G2 prospective", "E2 prospective"),
    ("G2 $\\beta$", "E2 $\\beta$"),
    ("8×G2 + G1", "8×E2 + E1"),
    ("G2 $\\beta$ grid", "E2 $\\beta$ grid"),
    ("G1 risk ledger", "E1 risk ledger"),
    ("G1 Wilson", "E1 Wilson"),
    ("G1 interval", "E1 interval"),
    ("G1 confirmatory", "E1 confirmatory"),
    ("G1 coverage", "E1 coverage"),
    ("G4 pass-rule", "E3 pass-rule"),
    ("G4-vs-G2 confusion", "E3-vs-E2 confusion"),
    ("G4 pass probability", "E3 pass probability"),
    ("G4 operating", "E3 operating"),
    ("for G1", "for E1"),
    ("for G2", "for E2"),
    ("for G4", "for E3"),
    ("P7 (G1)", "P7 (E1)"),
    ("P18 (G2)", "P18 (E2)"),
    ("S0 lock G1", "S0 lock E1"),
    ("S0 — Goals (frozen estimands G1–G4)", "S0 — Goals (frozen estimands E1–E3; LoQ branch separate)"),
    ("S0 — Goals (frozen estimands G1–G4)", "S0 — Goals (frozen estimands E1–E3; LoQ branch separate)"),
    ("estimands G1–G4", "estimands E1–E3"),
    ("G1–G4 are", "E1–E3 are"),
    ("orchestrates G1–G4", "orchestrates E1–E3"),
    ("lock G1/G2/G4", "lock E1/E2/E3"),
    ("lock G1, G2, or G4", "lock E1, E2, or E3"),
    ("lock estimand G1", "lock estimand E1"),
    ("G1/G4", "E1/E3"),
    ("G4/G1", "E3/E1"),
    ("n per arm (G2)", "n per arm (E2)"),
    ("total trials (G1/G4)", "total trials (E1/E3)"),
    ("For G2,", "For E2,"),
    ("For G1,", "For E1,"),
    ("rule **G4**", "rule **E3**"),
    ("qualitative rule **G4**", "qualitative rule **E3**"),
    ("Fig. 1A — G2", "Fig. 1A — E2"),
    ("Box 1 (G4 and G1", "Box 1 (E3 and E1"),
    ("Box 2 (G2 at", "Box 2 (E2 at"),
    ("requires p_a and p_b", "requires p_a and p_b"),  # noop
    ('"G2"', '"E2"'),
    ('"G1"', '"E1"'),
    ('"G4"', '"E3"'),
    ("G2 uses", "E2 uses"),
    ("G1 uses", "E1 uses"),
    ("G4 search", "E3 search"),
    ("G3 requires", "LoQ requires"),
    ("G2 requires", "E2 requires"),
    ("G1 Wilson vs", "E1 Wilson vs"),
    ("Supports confirmatory G1", "Supports confirmatory E1"),
    ("G4 pass rules", "E3 pass rules"),
    ("for G2 two-proportion", "for E2 two-proportion"),
    ("does not substitute for G2", "does not substitute for E2"),
    ("G4-vs-G2", "E3-vs-E2"),
    ("G4 vs G1", "E3 vs E1"),
    ("G4 pass as evidence for G1 or G2", "E3 pass as evidence for E1 or E2"),
    ("Recording a G4 pass", "Recording an E3 pass"),
    ("quantified **G4**", "quantified **E3**"),
    ("planning for **G2**", "planning for **E2**"),
    ("powered $n$ for G1 or G2", "powered $n$ for E1 or E2"),
    ("G1 param.", "E1 param."),
    ("G1 nonpar.", "E1 nonpar."),
    ("label=rf\"G2 folklore", "label=rf\"E2 folklore"),
    ("label=r\"G2 powered", "label=r\"E2 powered"),
    ("g1_labels = [\"G1 param.\", \"G1 nonpar.\"]", "e1_labels = [\"E1 param.\", \"E1 nonpar.\"]"),
    ("g1 = [", "e1 = ["),
    ("g1_labels", "e1_labels"),
    ("startswith(\"G1_\")", "startswith(\"E1_\")"),
    ("startswith(\"G2_folklore", "startswith(\"E2_folklore"),
    ("startswith(\"G2_powered", "startswith(\"E2_powered"),
    ("replace(\"G2_folklore_n20_\"", "replace(\"E2_folklore_n20_\""),
    ("replace(\"G2_powered_nstar_\"", "replace(\"E2_powered_nstar_\""),
    ("θ₄ = P(S_n ≥ k)", "θ₃ = P(S_n ≥ k)"),
    ("θ₄ = P(S_n", "θ₃ = P(S_n"),
    ("θ₃ = CV(c)", "CV(c)"),
    ("symbol=\"θ₃ = CV(c)\"", "symbol=\"CV(c)\""),
    ("G1/G2/G4 only", "E1/E2/E3 only"),
    ("G1/G2/G4 planned", "E1/E2/E3 planned"),
    ("estimand 仅 G1/G2/G4", "estimand 仅 E1/E2/E3"),
    ("锁定 G1/G2/G4", "锁定 E1/E2/E3"),
    ("锁定 G1、G2 或 G4", "锁定 E1、E2 或 E3"),
    ("G1–G4", "E1–E3"),
    ("G1/G2/G4", "E1/E2/E3"),
    ("G4 型", "E3 型"),
    ("G4 通过", "E3 通过"),
    ("G4 规则", "E3 规则"),
    ("G2 情形", "E2 情形"),
    ("G2 样本", "E2 样本"),
    ("G2 规划", "E2 规划"),
    ("G2 方案", "E2 方案"),
    ("G2 两臂", "E2 两臂"),
    ("G2 比对", "E2 比对"),
    ("G1 用", "E1 用"),
    ("G1（", "E1（"),
    ("G2（", "E2（"),
    ("G4（", "E3（"),
    ("**G1（", "**E1（"),
    ("**G2（", "**E2（"),
    ("**G4（", "**E3（"),
    ("G3（", "LoQ branch（"),
    ("G3 ", "LoQ "),
    ("G4 ", "E3 "),
    ("G2 ", "E2 "),
    ("G1 ", "E1 "),
]

# Fix double replacements from Goal chain
FIXUPS = [
    ("Goal.E3_QUALITATIVE_KN_QUALITATIVE_KN", "Goal.E3_QUALITATIVE_KN"),
    ("Goal.E2_COMPARE_REAGENTS_COMPARE_REAGENTS", "Goal.E2_COMPARE_REAGENTS"),
    ("Goal.E1_VERIFY_LOD_VERIFY_LOD", "Goal.E1_VERIFY_LOD"),
    ("Goal.LOQ_PRECISION_LOQ_PRECISION", "Goal.LOQ_PRECISION"),
    ("LoQ branch ( / precision", "LoQ / precision"),
    ("LoQ branch (LoQ", "LoQ"),
    ("E1/E2/E3/E2/E3", "E1/E2/E3"),
    ("E1/E2/E3/E1/E3", "E1/E2/E3"),
]


def should_skip(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return True
    rel = path.relative_to(ROOT).as_posix()
    if any(rel.startswith(p) for p in SKIP_PATH_PARTS):
        return True
    if path.suffix in SKIP_SUFFIXES:
        return True
    if rel.startswith("paper_artifacts/manuscript/"):
        return True  # regenerated
    if rel == "paper_artifacts/MANIFEST.json":
        return True  # regenerated
    if rel.startswith("data/research/") and path.suffix == ".json":
        return True  # regenerated
    if rel == "scripts/migrate_g_to_e_estimands.py":
        return True
    return False


def migrate_text(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    for old, new in FIXUPS:
        text = text.replace(old, new)
    # Residual standalone tokens in code/comments (word boundaries)
    text = re.sub(r"\bG4\b", "E3", text)
    text = re.sub(r"\bG3\b", "LoQ", text)
    text = re.sub(r"\bG2\b", "E2", text)
    text = re.sub(r"\bG1\b", "E1", text)
    for old, new in FIXUPS:
        text = text.replace(old, new)
    return text


def main() -> None:
    changed: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        updated = migrate_text(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(path)
    print(f"Updated {len(changed)} files")
    for p in sorted(changed)[:60]:
        print(f"  {p.relative_to(ROOT)}")
    if len(changed) > 60:
        print(f"  ... and {len(changed) - 60} more")


if __name__ == "__main__":
    main()
