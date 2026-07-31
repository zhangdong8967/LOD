"""Fig 1 — LoD verification planning pipeline (TikZ vector + matplotlib fallback)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

from lod_guide.paper.figure_style import (
    C_ACCENT,
    C_NEUTRAL,
    C_PRIMARY,
    C_SECONDARY,
    C_WARN,
    DOUBLE_COL_W,
    JOURNAL_PURPLE,
    apply_journal_rc,
    save_figure,
)

ROOT = Path(__file__).resolve().parents[3]
FIG_DIR = ROOT / "figures" / "methodology"
PAPER_FIG = ROOT / "paper_artifacts" / "figures"
TEX_DIR = ROOT / "manuscript" / "figures_tex"
TEX_SRC = TEX_DIR / "Fig1_pipeline.tex"
BUNDLED_TECTONIC = ROOT / ".tools" / "tectonic"


def _box(ax, cx, cy, text, *, w=0.72, h=0.38, ec=C_PRIMARY, accent=None, fs=7.5, ls="-", fc="white"):
    x, y = cx - w / 2, cy - h / 2
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.012,rounding_size=0.04",
            linewidth=1.2, edgecolor=ec, facecolor=fc, zorder=3, linestyle=ls,
        )
    )
    if accent:
        ax.add_patch(Rectangle((x, y), 0.035, h, facecolor=accent, edgecolor="none", zorder=4))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color="#222222", zorder=5, linespacing=1.05)


def _arrow(ax, x0, y0, x1, y1, *, color=C_NEUTRAL, ls="-", rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            (x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=9, linewidth=1.0,
            color=color, linestyle=ls, connectionstyle=f"arc3,rad={rad}", zorder=2,
        )
    )


def _render_matplotlib_fallback() -> Path:
    apply_journal_rc()
    fig, ax = plt.subplots(figsize=(DOUBLE_COL_W, 2.35), facecolor="white")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2.55)
    ax.axis("off")

    ax.add_patch(Rectangle((0.15, 1.88), 9.7, 0.52, facecolor="#F4F7FB", edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((0.15, 0.92), 9.7, 0.62, facecolor="#FAFAFA", edgecolor="none", zorder=0))

    gx = [2.0, 5.0, 8.0]
    for x, lab, col in zip(
        gx,
        ["G1\nVerify LoD", "G2\nCompare", "G4\nk/n rule"],
        [C_PRIMARY, C_WARN, JOURNAL_PURPLE],
    ):
        _box(ax, x, 2.14, lab, w=0.88, h=0.36, ec=col, accent=col, fs=7.2)
    ax.text(5.0, 2.48, "S0 · lock detection claim (LoD estimand)", ha="center", fontsize=7.5, color=C_NEUTRAL, fontweight="medium")

    sx = [0.7, 2.3, 4.0, 5.7, 7.4, 9.1]
    slabs = ["S0\nGoal", "S1\nHit-rate", "S5\nPlan n", "S6\nExact", "S7\nReport"]
    for x, lab in zip(sx[:5], slabs):
        _box(ax, x, 1.22, lab, w=0.72, h=0.38, ec=C_PRIMARY, fs=7)
    for i in range(4):
        _arrow(ax, sx[i] + 0.36, 1.22, sx[i + 1] - 0.36, 1.22)

    _arrow(ax, 5.0, 1.96, 5.0, 1.41, color=C_NEUTRAL, ls="--")

    _box(
        ax, 5.0, 0.55, "Optional EP17 continuous path:\nS2–S4 LoB (Supplement)",
        w=2.8, h=0.42, ec=C_NEUTRAL, fs=6.5, ls="--", fc="#F8F8F8",
    )
    _arrow(ax, 2.3, 1.03, 3.8, 0.76, color=C_NEUTRAL, ls=":", rad=0.15)

    ax.text(0.35, 1.55, "Input: protocol claim · hit data", fontsize=6.8, color=C_NEUTRAL)
    ax.text(9.65, 1.55, "Output: planned n · OC · audit JSON", fontsize=6.8, color=C_NEUTRAL, ha="right")
    ax.text(5.0, 0.08, "LoD certificates P1, P7, P8, P18 · exact Fisher/Boschloo · tier-A qPCR/probit", ha="center", fontsize=6.8, color=C_NEUTRAL)

    return save_figure(
        fig, "Fig1_decision_map", fig_dir=FIG_DIR,
        extra_stems=(),
    )


def _pdf_to_png(pdf: Path, png: Path) -> bool:
    if shutil.which("sips"):
        r = subprocess.run(["sips", "-s", "format", "png", str(pdf), "--out", str(png)], capture_output=True)
        return r.returncode == 0 and png.exists()
    if shutil.which("pdftoppm"):
        prefix = png.with_suffix("")
        r = subprocess.run(["pdftoppm", "-png", "-singlefile", str(pdf), str(prefix)], capture_output=True)
        return r.returncode == 0 and png.exists()
    return False


def _run_pdflatex(job: str) -> bool:
    """Compile TikZ job; try pdflatex, bundled tectonic, system tectonic, then Docker."""
    tex_path = Path("/Library/TeX/texbin/pdflatex")
    pdflatex = shutil.which("pdflatex") or (str(tex_path) if tex_path.is_file() else None)
    if pdflatex:
        r = subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error", f"{job}.tex"],
            cwd=TEX_DIR,
            capture_output=True,
            text=True,
        )
        return r.returncode == 0
    tectonic = str(BUNDLED_TECTONIC) if BUNDLED_TECTONIC.is_file() else shutil.which("tectonic")
    if tectonic:
        r = subprocess.run(
            [tectonic, "-X", "compile", f"{job}.tex"],
            cwd=TEX_DIR,
            capture_output=True,
            text=True,
        )
        return r.returncode == 0
    if shutil.which("docker"):
        r = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{ROOT}:/work",
                "-w", "/work/manuscript/figures_tex",
                "texlive/texlive:latest",
                "pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{job}.tex",
            ],
            capture_output=True,
            text=True,
        )
        return r.returncode == 0
    return False


def _copy_fig1_outputs(pdf: Path, png: Path) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_FIG.mkdir(parents=True, exist_ok=True)
    for stem in ("Fig1_Fig1-decision-map",):
        for src, ext in ((pdf, ".pdf"), (png, ".png")):
            for dst in (FIG_DIR / f"Fig1_decision_map{ext}", PAPER_FIG / f"{stem}{ext}"):
                if src.resolve() != dst.resolve():
                    shutil.copy2(src, dst)


def _render_tikz() -> Path | None:
    if not TEX_SRC.exists():
        return None
    if not shutil.which("pdflatex") and not BUNDLED_TECTONIC.is_file() and not shutil.which("tectonic") and not shutil.which("docker"):
        return None
    TEX_DIR.mkdir(parents=True, exist_ok=True)
    job = "Fig1_pipeline"
    for ext in (".aux", ".log"):
        (TEX_DIR / f"{job}{ext}").unlink(missing_ok=True)
    if not _run_pdflatex(job):
        return None
    pdf = TEX_DIR / f"{job}.pdf"
    if not pdf.exists():
        return None
    png = FIG_DIR / "Fig1_decision_map.png"
    if not _pdf_to_png(pdf, png):
        return None
    _copy_fig1_outputs(pdf, png)
    return png


def render_fig1_decision_map() -> Path:
    tikz = _render_tikz()
    if tikz is not None:
        return tikz
    return _render_matplotlib_fallback()
