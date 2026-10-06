"""Fig 1 — LoD verification planning pipeline (TikZ vector + matplotlib fallback)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

from lod_guide.paper.figure_style import (
    C_ACCENT,
    C_FOG,
    C_INK,
    C_MIST,
    C_NEUTRAL,
    C_PRIMARY,
    C_SAGE,
    C_SECONDARY,
    C_SLATE,
    C_WARN,
    C_WINE,
    DOUBLE_COL_W,
    JOURNAL_PURPLE,
    apply_journal_rc,
    panel_label,
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


def _port(ax, cx, cy, text, *, w=1.05, h=0.28, fs=6.2):
    x, y = cx - w / 2, cy - h / 2
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.01,rounding_size=0.03",
            linewidth=0.9, edgecolor=C_WINE, facecolor="#fef2f2", zorder=3,
        )
    )
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=C_WINE, zorder=4, linespacing=1.05)


def _arrow(ax, x0, y0, x1, y1, *, color=C_SLATE, ls="-", rad=0.0, lw=1.0):
    ax.add_patch(
        FancyArrowPatch(
            (x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=9, linewidth=lw,
            color=color, linestyle=ls, connectionstyle=f"arc3,rad={rad}", zorder=2,
        )
    )


def draw_fig1_claim_flow(
    ax,
    *,
    n_valid_cells: int,
    frac_underpowered: float,
    median_n_star: float | None = None,
    delta_bands: list[dict] | None = None,
) -> None:
    """Readable three-step banner for Fig 1A (print-scale type).

    Box 3 reports Δp-banded n*, not the lattice-wide median or the 90/80 example.
    """
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor("white")

    band_map = {str(r.get("band")): r for r in (delta_bands or [])}
    n_gt20 = band_map.get(">20", {}).get("median_n_star_ceiling")
    plan_body = r"$n^\ast$ is a function of $\Delta p$" "\n" r"$\leq$10 pp: every cell $\beta>0.8$"
    if n_gt20 is not None:
        plan_body = (
            r"$n^\ast$ follows $\Delta p$, not one $n$"
            "\n"
            r"$\leq$10 pp: all cells $\beta>0.8$"
            "\n"
            rf"$>$20 pp: median $n^\ast\approx{int(n_gt20)}$"
        )
    elif median_n_star is not None:
        plan_body = (
            r"$n^\ast$ follows $\Delta p$, not one $n$"
            "\n"
            r"$\leq$10 pp: all cells $\beta>0.8$"
            "\n"
            r"90/80 is one lattice cell"
        )

    cards = [
        (
            0.165,
            "Lock the claim",
            r"Two-arm contrast at $c^\ast$" "\n" r"$\theta_2=p_A(c^\ast)-p_B(c^\ast)$",
            C_INK,
            "#f8fafc",
        ),
        (
            0.50,
            r"Score $n=20$",
            rf"{100 * frac_underpowered:.0f}% of {n_valid_cells} lattice cells"
            "\n"
            r"have $\beta>0.8$"
            "\n"
            r"(design grid, not prevalence)",
            C_WINE,
            "#fff1f2",
        ),
        (
            0.835,
            r"Plan $n^\ast(\Delta p)$",
            plan_body,
            C_SAGE,
            "#ecfdf5",
        ),
    ]
    w, h = 0.28, 0.78
    for cx, title, body, accent, fc in cards:
        x, y = cx - w / 2, 0.08
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h,
                boxstyle="round,pad=0.012,rounding_size=0.04",
                linewidth=1.15, edgecolor=accent, facecolor=fc, zorder=2,
            )
        )
        ax.add_patch(Rectangle((x, y + h - 0.035), w, 0.035, facecolor=accent, edgecolor="none", zorder=3))
        ax.text(cx, 0.72, title, ha="center", va="center", fontsize=9.0, color=accent, fontweight="semibold", zorder=4)
        ax.text(cx, 0.38, body, ha="center", va="center", fontsize=8.0, color=C_INK, linespacing=1.25, zorder=4)

    for x0, x1 in ((0.305, 0.355), (0.645, 0.695)):
        ax.annotate(
            "",
            xy=(x1, 0.47),
            xytext=(x0, 0.47),
            arrowprops=dict(arrowstyle="-|>", color=C_SLATE, lw=1.15),
            zorder=5,
        )
    panel_label(ax, "A", inset=True)


def _theory_column(
    ax,
    *,
    stage: str,
    equation: str,
    subtitle: str,
    accent: str,
    maps_to: str = "",
    highlight: bool = False,
) -> None:
    """Single theory column aligned above panels B/C/D."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor("white")

    fc = "#f0fdf4" if highlight else "white"
    ec = accent if highlight else C_MIST
    lw = 0.95 if highlight else 0.55
    ax.add_patch(
        FancyBboxPatch(
            (0.03, 0.04), 0.94, 0.92,
            boxstyle="round,pad=0.008,rounding_size=0.04",
            linewidth=lw, edgecolor=ec, facecolor=fc, zorder=0,
        )
    )
    ax.add_patch(
        Rectangle((0.04, 0.86), 0.92, 0.11, facecolor=accent, alpha=0.18 if highlight else 0.10, edgecolor="none", zorder=1),
    )
    ax.plot([0.04, 0.96], [0.86, 0.86], color=accent, lw=2.0 if highlight else 1.6, solid_capstyle="round", zorder=2)
    ax.text(
        0.5, 0.915, stage, ha="center", va="center",
        fontsize=6.6 if highlight else 6.4, color=accent, fontweight="semibold",
    )
    ax.text(0.5, 0.55, equation, ha="center", va="center", fontsize=7.4, color=C_INK, linespacing=1.15)
    ax.text(
        0.5, 0.30, subtitle, ha="center", va="center",
        fontsize=6.4 if highlight else 6.1, color=C_INK if highlight else C_SLATE,
        fontweight="medium" if highlight else "normal", linespacing=1.1,
    )
    if maps_to:
        ax.text(0.5, 0.10, maps_to, ha="center", va="center", fontsize=5.5, color=C_SLATE, style="italic")


def draw_fig1_panel_a_theory(
    ax,
    *,
    power_n20: float,
    n_star: int,
    frac_underpowered: float,
    median_n_star: float,
    c_lod_at_80: float,
) -> None:
    """Legacy single-axis fallback — three inset columns."""
    beta_miss = 1.0 - power_n20
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    cols = [
        ([0.0, 0.66, 1.0, 1.0], "Comparative estimand", r"$\theta_2 = p_A(c^*) - p_B(c^*)$",
         r"$H_0\!:\ \theta_2 = 0$", C_INK),
        ([0.33, 0.66, 0.34, 1.0], "OC surfaces", r"$\pi_{\mathrm{Fisher}}, n^*(p_A,p_B)$",
         rf"1225 pairs: {100*frac_underpowered:.0f}% $\beta>0.8$; median $n^*={median_n_star:.0f}$", C_SAGE),
        ([0.67, 0.66, 0.33, 1.0], "Calibration map", r"$g(p) = c/\mathrm{LoD}_{95}$",
         rf"$g(0.80) = {c_lod_at_80:.2f}$", C_INK),
    ]
    for rect, st, eq, subl, col in cols:
        sub = ax.inset_axes(rect)
        _theory_column(sub, stage=st, equation=eq, subtitle=subl, accent=col)


def draw_fig1_panel_a_columns(
    fig,
    axes: tuple,
    *,
    n_valid_cells: int,
    frac_underpowered: float,
    median_n_star: float,
    c_lod_at_80: float,
    power_n20: float | None = None,
    n_star: int | None = None,
) -> None:
    """
    Fig 1 panel A — three columns aligned with B/C/D below.

    Lattice-first: surfaces over all integer (p_A, p_B) pairs; optional illustrative pair for legacy callers.
    """
    ax1, ax2, ax3 = axes

    pos = ax1.get_position()
    fig.text(
        0.5, pos.y1 + 0.028,
        r"LoD$_{95}$ analytical layer: $\Pr(\mathrm{miss}\mid c^*)=1-p_0=0.05$"
        r" $\rightarrow$ inferential layer: finite-$n$ OC ($\alpha$, $\beta$) — not $n\to\infty$",
        ha="center", va="bottom", fontsize=6.2, color=C_WINE, fontweight="medium",
    )
    fig.text(
        0.5, pos.y1 + 0.012,
        r"E2 surfaces $\pi_{\mathrm{Fisher}}(p_A,p_B;n)$ and $n^*(p_A,p_B)$ on 1225-cell integer lattice (50--99%)",
        ha="center", va="bottom", fontsize=6.7, color=C_INK, fontweight="medium",
    )

    _theory_column(
        ax1,
        stage="Comparative estimand",
        equation=r"$\theta_2 = p_A(c^*) - p_B(c^*)$",
        subtitle=r"$H_0\!:\ \theta_2 = 0$  ·  $\hat p$ not $1-(1-p)^n$",
        accent=C_INK,
        maps_to=r"analytical: $p_0{=}0.95 \Rightarrow \Pr(\mathrm{miss}){=}0.05$",
    )
    oc_sub = (
        rf"{n_valid_cells} pairs @ $n=20$: "
        rf"{100 * frac_underpowered:.0f}% $\beta>0.8$  ·  median $n^*={median_n_star:.0f}$"
    )
    _theory_column(
        ax2,
        stage="OC surfaces",
        equation=r"$\pi_{\mathrm{Fisher}}(p_A,p_B;n),\; n^*(p_A,p_B)$",
        subtitle=oc_sub,
        accent=C_SAGE,
        highlight=True,
        maps_to=r"Eq. (2); exact Fisher @ folklore $n$",
    )
    _theory_column(
        ax3,
        stage="Calibration map",
        equation=r"$g(p) = c/\mathrm{LoD}_{95}$",
        subtitle=rf"$g(0.80)={c_lod_at_80:.2f}$ example  ·  logistic $\Lambda$, $p$ 50–99%",
        accent=C_INK,
    )

    p1, p2, p3 = ax1.get_position(), ax2.get_position(), ax3.get_position()
    mid12 = (p1.x1 + p2.x0) / 2
    mid23 = (p2.x1 + p3.x0) / 2
    y_arr = p1.y0 + (p1.y1 - p1.y0) * 0.52
    fig.add_artist(
        FancyArrowPatch(
            (mid12 - 0.012, y_arr), (mid12 + 0.012, y_arr),
            transform=fig.transFigure, arrowstyle="-|>", mutation_scale=7,
            linewidth=0.85, color=C_SLATE, zorder=10,
        )
    )
    fig.add_artist(
        FancyArrowPatch(
            (mid23 - 0.012, y_arr), (mid23 + 0.012, y_arr),
            transform=fig.transFigure, arrowstyle="-|>", mutation_scale=7,
            linewidth=0.85, color=C_SLATE, zorder=10,
        )
    )

    panel_label(ax1, "A", inset=True)


def draw_fig1_panel_a_story(
    ax,
    *,
    power_n20: float,
    n_star: int,
    frac_underpowered: float,
    median_n_star: float,
    c_lod_at_80: float,
) -> None:
    """Alias — integrated Fig 1 uses the theory panel."""
    draw_fig1_panel_a_theory(
        ax,
        power_n20=power_n20,
        n_star=n_star,
        frac_underpowered=frac_underpowered,
        median_n_star=median_n_star,
        c_lod_at_80=c_lod_at_80,
    )


def draw_pipeline_schematic_compact(ax) -> None:
    """Legacy fallback with headline defaults."""
    draw_fig1_panel_a_theory(
        ax,
        power_n20=0.07,
        n_star=199,
        frac_underpowered=0.61,
        median_n_star=116.0,
        c_lod_at_80=0.17,
    )


def _draw_pipeline_schematic_compact_s07(ax) -> None:
    """Deprecated S0–S7 strip (supplement / standalone only)."""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1.0)
    ax.axis("off")

    ax.add_patch(Rectangle((0.05, 0.78), 9.9, 0.18, facecolor=C_MIST, edgecolor="none", zorder=0))
    ax.text(
        5.0, 0.87,
        r"Prospective claim $\rightarrow$ lock estimand (E1 / E2 / E3) $\rightarrow$ plan $n$ $\rightarrow$ exact confirm",
        ha="center", va="center", fontsize=7.0, color=C_INK,
    )

    for x, lab, col in zip([1.5, 5.0, 8.5], ["E1 verify", "E2 compare", "E3 $k/n$"], [C_INK, C_WINE, JOURNAL_PURPLE]):
        ax.text(x, 0.66, lab, ha="center", va="center", fontsize=6.2, color=col, fontweight="semibold")

    sx = [0.7, 2.4, 4.1, 5.8, 7.5, 9.2]
    sy = 0.46
    for x, lab in zip(sx[:5], ["S0", "S1", "S5", "S6", "S7"]):
        ec = C_SAGE if lab in {"S5", "S6"} else C_INK
        _box(ax, x, sy, lab, w=0.58, h=0.22, ec=ec, fs=6.5)
    for i in range(4):
        _arrow(ax, sx[i] + 0.29, sy, sx[i + 1] - 0.29, sy, color=C_SLATE, lw=0.9)

    ax.text(
        5.0, 0.22,
        r"Folklore bypass: $n{=}20$, skip S5 (S1$\rightarrow$S6)   ·   "
        r"P7 $n/n$ trap   ·   P18 $\beta{\approx}0.93$   ·   P8 exact$\neq$asymp.",
        ha="center", va="center", fontsize=6.0, color=C_SLATE,
    )


def draw_pipeline_schematic(ax, *, standalone: bool = False) -> None:
    """S0–S7 planning map. Use standalone=True for full-width Fig 1 (larger type)."""
    fs = 1.28 if standalone else 1.0
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.05)
    ax.axis("off")

    ax.add_patch(Rectangle((0.15, 2.52), 9.7, 0.28, facecolor=C_MIST, edgecolor="none", zorder=0))
    ax.text(
        5.0, 2.66,
        r"Minimize $L = w_I\,\mathrm{TypeI} + w_{II}\,\beta + w_M\,\mathbf{1}\{\mathrm{mismatch}\} + w_C(\mathrm{DE}-1)$",
        ha="center", fontsize=7.2 * fs, color=C_INK,
    )

    gx = [2.0, 5.0, 8.0]
    for x, lab, col in zip(
        gx,
        ["E1\nVerify LoD", "E2\nCompare", "E3\nk/n rule"],
        [C_INK, C_WINE, JOURNAL_PURPLE],
    ):
        _box(ax, x, 2.18, lab, w=0.88, h=0.36, ec=col, accent=col, fs=7.0 * fs)
    ax.text(5.0, 2.50, "S0 · lock one detection estimand", ha="center", fontsize=6.5 * fs, color=C_SLATE)

    sx = [0.7, 2.3, 4.0, 5.7, 7.4, 9.1]
    slabs = ["S0\nGoal", "S1\nHit-rate", "S5\nPlan n", "S6\nExact", "S7\nReport"]
    stage_cols = [C_INK, C_INK, C_SAGE, C_SAGE, C_INK]
    for x, lab, col in zip(sx[:5], slabs, stage_cols):
        _box(ax, x, 1.48, lab, w=0.72, h=0.38, ec=col, fs=7 * fs)
    for i in range(4):
        _arrow(ax, sx[i] + 0.36, 1.48, sx[i + 1] - 0.36, 1.48, color=C_SLATE)
    _arrow(ax, 5.0, 1.97, 5.0, 1.67, color=C_SLATE, ls="--")

    _box(
        ax, 6.8, 1.98, "Folklore bypass:\nskip S5, $n=20$",
        w=1.35, h=0.32, ec=C_WINE, fs=6.5 * fs, ls="--", fc="#fff1f2",
    )
    _arrow(ax, 2.3, 1.67, 6.1, 1.98, color=C_WINE, ls="--", rad=-0.25, lw=1.0)
    _arrow(ax, 6.8, 1.82, 7.4, 1.67, color=C_WINE, ls="--", lw=1.0)

    _port(ax, 2.0, 1.70, "P7 · $n/n$ trap", fs=6.2 * fs if standalone else 6.2)
    _port(ax, 4.0, 1.02, r"P18 · $\beta \approx 0.93$", fs=6.2 * fs if standalone else 6.2)
    _port(ax, 8.35, 1.98, r"P8 · exact $\neq$ asymp.", fs=6.2 * fs if standalone else 6.2)

    ax.text(0.35, 1.18, "Claim to data", fontsize=6.5 * fs, color=C_SLATE)
    ax.text(9.65, 1.18, "OC · audit", fontsize=6.5 * fs, color=C_SLATE, ha="right")


def _render_matplotlib_fallback() -> Path:
    apply_journal_rc()
    fig, ax = plt.subplots(figsize=(DOUBLE_COL_W, 3.05), facecolor="white")
    draw_pipeline_schematic(ax)
    return save_figure(fig, "Fig1_decision_map", fig_dir=FIG_DIR, extra_stems=())


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
