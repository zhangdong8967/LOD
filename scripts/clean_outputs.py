#!/usr/bin/env python3
"""
Remove stale figure aliases and LaTeX build noise from the LOD repo.

Keeps:
  - figures/methodology/{registry source_png + research module stems}
  - paper_artifacts/figures/{FigN_developer-id.*} per registry

Run from repo root:
  python scripts/clean_outputs.py          # dry-run
  python scripts/clean_outputs.py --apply  # delete files
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from lod_guide.paper.registry import FIGURES, FIG_SRC, PAPER

ROOT = Path(__file__).resolve().parents[1]
METHODOLOGY = FIG_SRC
PAPER_FIG = PAPER / "figures"
MANUSCRIPT = ROOT / "manuscript"

# Legacy alias stems written by save_figure(extra_stems=...) — safe to drop after rebuild.
METHODOLOGY_ALIAS_STEMS = frozenset(
    {
        "Fig1_FigM1",
        "Fig1_Fig1-decision-map",
        "Fig2_Fig2",
        "Fig3_Fig3",
        "Fig4_Fig4",
        "Fig4_Fig4-remedy",
        "Fig4_FigT1-T2",
        "Fig5_Fig5",
        "Fig5_tierA_grid",
        "Fig5_tierA_loq",
        "Fig8_loq_radioimmuno_tierA",
    }
)

# Pre–5-figure main-text numbering in paper_artifacts/figures/.
LEGACY_PAPER_PREFIXES = re.compile(r"^Fig[56789]_")

LATEX_NOISE = ("*.aux", "*.log", "*.out", "missfont.log")


def _registry_methodology_stems() -> set[str]:
    stems: set[str] = set()
    for spec in FIGURES:
        base = Path(spec.source_png).stem
        stems.add(base)
    # Supplement-only single panel not in FIGURES tuple
    stems.add("FigL_radioimmuno_loq_profile")
    return stems


def _registry_paper_dests() -> set[str]:
    names: set[str] = set()
    for spec in FIGURES:
        safe = spec.manuscript_id.replace(" ", "")
        for ext in (".png", ".pdf"):
            names.add(f"{safe}_{spec.developer_id}{ext}")
    return names


def _research_module_stem_pattern(name: str) -> bool:
    """Stems produced by research figure generators (not manuscript aliases)."""
    return bool(
        re.match(
            r"^Fig(?:M[0-9]|D[0-9]|T[0-9]|C[0-9]|R[0-9]|L[0-9]|9_|S_)[\w\-]*",
            Path(name).stem,
        )
    )


def collect_removable_methodology(stems_keep: set[str]) -> list[Path]:
    removable: list[Path] = []
    if not METHODOLOGY.is_dir():
        return removable
    for path in METHODOLOGY.iterdir():
        if path.suffix not in {".png", ".pdf"}:
            continue
        stem = path.stem
        if stem in METHODOLOGY_ALIAS_STEMS:
            removable.append(path)
            continue
        if stem in stems_keep:
            continue
        if _research_module_stem_pattern(path.name):
            continue
        removable.append(path)
    return sorted(removable)


def collect_removable_paper_figures(keep: set[str]) -> list[Path]:
    removable: list[Path] = []
    if not PAPER_FIG.is_dir():
        return removable
    for path in PAPER_FIG.iterdir():
        if path.suffix not in {".png", ".pdf"}:
            continue
        if path.name in keep:
            continue
        removable.append(path)
    return sorted(removable)


def collect_latex_noise() -> list[Path]:
    out: list[Path] = []
    for pattern in LATEX_NOISE:
        out.extend(MANUSCRIPT.rglob(pattern))
        out.extend((MANUSCRIPT / "figures_tex").rglob(pattern))
    return sorted({p for p in out if p.is_file()})


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean stale LOD figure and LaTeX outputs")
    parser.add_argument("--apply", action="store_true", help="Actually delete files (default: dry-run)")
    args = parser.parse_args()

    reg_stems = _registry_methodology_stems()
    paper_keep = _registry_paper_dests()

    to_remove: list[Path] = []
    to_remove.extend(collect_removable_methodology(reg_stems))
    to_remove.extend(collect_removable_paper_figures(paper_keep))
    to_remove.extend(collect_latex_noise())

    # Deduplicate
    seen: set[Path] = set()
    unique: list[Path] = []
    for p in to_remove:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            unique.append(p)

    print(f"{'APPLY' if args.apply else 'DRY-RUN'}: {len(unique)} files marked for removal")
    for p in unique:
        rel = p.relative_to(ROOT) if p.is_relative_to(ROOT) else p
        print(f"  {rel}")

    if args.apply and unique:
        for p in unique:
            p.unlink(missing_ok=True)
        print(f"Deleted {len(unique)} files.")
        print("Next: make fig1-tikz && python -m lod_guide.paper.main_figures && make paper-artifacts")


if __name__ == "__main__":
    main()
