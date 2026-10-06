"""
Publication figure theme — unified theory-monograph palette.

Captions live in the manuscript; in-figure text limited to panel letters A/B/C.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.transforms import Bbox

# Cohesive palette: ink + slate + sage + wine (colorblind-safe, print-friendly).
C_INK = "#1e293b"
C_SLATE = "#64748b"
C_SAGE = "#0f766e"
C_WINE = "#be123c"
C_MIST = "#e2e8f0"
C_FOG = "#f8fafc"
C_INK_LIGHT = "#334155"

# Semantic aliases (used across paper modules)
C_PRIMARY = C_INK
C_ACCENT = C_SAGE
C_WARN = C_WINE
C_SECONDARY = C_WINE
C_NEUTRAL = C_SLATE
C_LIGHT = C_MIST
C_GOLD = C_WINE

# Legacy journal names
JOURNAL_BLUE = C_INK
JOURNAL_ORANGE = C_WINE
JOURNAL_GREEN = C_SAGE
JOURNAL_YELLOW = C_WINE
JOURNAL_PURPLE = "#5b21b6"
JOURNAL_GRAY = C_SLATE
JOURNAL_LIGHT_GRAY = C_MIST
JOURNAL_SKY = "#94a3b8"
JOURNAL_RED = C_WINE
GRID_COLOR = C_MIST

DOUBLE_COL_W = 7.2
TRIPANEL_H = 3.05
TWOPANEL_H = 2.85
THEORY_FIG_H = 5.35
MONOGRAPH_H = 9.2
FOCUS_FIG_H = 4.0
PROTOCOL_FIG_H = 3.65


def create_single_panel_figure(*, height: float = FOCUS_FIG_H) -> tuple[Figure, Axes]:
    """One full-width panel — high-resolution journal figure."""
    fig, ax = plt.subplots(figsize=(DOUBLE_COL_W, height), facecolor="white")
    ax._panel_offset = False  # type: ignore[attr-defined]
    return fig, ax


def create_monograph_figure() -> tuple[Figure, dict[str, Axes]]:
    """3×3 theory grid: row0 pipeline; row1 failure mechanisms; row2 OC geometry."""
    fig = plt.figure(figsize=(DOUBLE_COL_W, MONOGRAPH_H), facecolor="white")
    gs = GridSpec(
        3,
        3,
        figure=fig,
        height_ratios=[0.95, 1.0, 1.05],
        hspace=0.48,
        wspace=0.34,
        left=0.07,
        right=0.98,
        top=0.97,
        bottom=0.05,
    )
    axes = {
        "A": fig.add_subplot(gs[0, :]),
        "B": fig.add_subplot(gs[1, 0]),
        "C": fig.add_subplot(gs[1, 1]),
        "D": fig.add_subplot(gs[1, 2]),
        "E": fig.add_subplot(gs[2, 0]),
        "F": fig.add_subplot(gs[2, 1]),
        "G": fig.add_subplot(gs[2, 2]),
    }
    for ax in axes.values():
        ax._panel_offset = True  # type: ignore[attr-defined]
    return fig, axes


def create_empirical_figure() -> tuple[Figure, dict[str, Axes]]:
    """Empirical row: qPCR curve · tier-A n ratios · decision-risk bars."""
    fig = plt.figure(figsize=(DOUBLE_COL_W, 4.05), facecolor="white")
    gs = GridSpec(1, 3, figure=fig, wspace=0.36, left=0.07, right=0.98, top=0.92, bottom=0.10)
    axes = {
        "H": fig.add_subplot(gs[0, 0]),
        "I": fig.add_subplot(gs[0, 1]),
        "J": fig.add_subplot(gs[0, 2]),
    }
    for ax in axes.values():
        ax._panel_offset = True  # type: ignore[attr-defined]
    return fig, axes


def apply_journal_rc() -> None:
    """Seaborn ticks theme + matplotlib fine-tuning for print."""
    sns.set_theme(
        style="white",
        context="paper",
        font="sans-serif",
        font_scale=1.05,
        rc={
            "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
            "axes.linewidth": 0.85,
            "axes.edgecolor": C_INK_LIGHT,
            "axes.labelsize": 9,
            "axes.labelweight": "medium",
            "axes.facecolor": C_FOG,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7.5,
            "legend.frameon": True,
            "legend.framealpha": 0.98,
            "legend.edgecolor": C_MIST,
            "legend.borderpad": 0.35,
            "lines.linewidth": 2.0,
            "lines.markersize": 5.5,
            "savefig.dpi": 400,
            "savefig.facecolor": "white",
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.05,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "figure.facecolor": "white",
        },
    )


def panel_label(ax: Axes, letter: str, *, inset: bool = False) -> None:
    """Bold panel letter — badge above axes, or inset chip inside top-left."""
    if inset:
        ax.text(
            0.02,
            0.98,
            letter,
            transform=ax.transAxes,
            fontsize=9.5,
            fontweight="bold",
            va="top",
            ha="left",
            color="white",
            clip_on=False,
            bbox=dict(
                boxstyle="circle,pad=0.24",
                facecolor=C_INK,
                edgecolor="none",
                alpha=0.96,
            ),
            zorder=10,
        )
        return
    x = -0.11 if getattr(ax, "_panel_offset", False) else 0.015
    ax.text(
        x,
        1.06,
        letter,
        transform=ax.transAxes,
        fontsize=10.5,
        fontweight="bold",
        va="bottom",
        ha="center",
        color="white",
        clip_on=False,
        bbox=dict(
            boxstyle="circle,pad=0.28",
            facecolor=C_INK,
            edgecolor="none",
            alpha=0.96,
        ),
        zorder=10,
    )


def subtitle_chip(
    ax: Axes,
    text: str,
    *,
    color: str = C_INK,
    y: float = 1.02,
    x: float = 0.02,
    fontsize: float = 6.8,
    facecolor: str = "#ffffff",
    edgecolor: str = C_MIST,
) -> None:
    ax.text(
        x,
        y,
        text,
        transform=ax.transAxes,
        fontsize=fontsize,
        color=color,
        fontweight="medium",
        va="bottom",
        ha="left",
        bbox=dict(
            boxstyle="round,pad=0.35,rounding_size=0.12",
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidth=0.6,
            alpha=0.97,
        ),
        clip_on=False,
        zorder=9,
    )


def style_colorbar(
    cbar,
    *,
    label: str,
    fontsize: float = 7.5,
    ticks: list[float] | None = None,
    highlight: float | None = None,
    orientation: str = "vertical",
) -> None:
    cbar.ax.tick_params(labelsize=6.8, length=2.5, width=0.5, color=C_SLATE)
    cbar.outline.set_linewidth(0.5)
    cbar.outline.set_edgecolor(C_MIST)
    pad = 4 if orientation == "horizontal" else 6
    cbar.set_label(label, fontsize=fontsize, labelpad=pad, color=C_INK)
    if ticks is not None:
        cbar.set_ticks(ticks)
        cbar.set_ticklabels([f"{t:g}" for t in ticks])
    if highlight is not None:
        tick_labels = cbar.ax.get_xticklabels() if orientation == "horizontal" else cbar.ax.get_yticklabels()
        for lbl in tick_labels:
            try:
                if abs(float(lbl.get_text()) - highlight) < 1e-6:
                    lbl.set_color(C_WINE)
                    lbl.set_fontweight("bold")
            except ValueError:
                pass


def frame_panel(ax: Axes, *, facecolor: str = "white", edgecolor: str = C_MIST, linewidth: float = 0.75) -> None:
    ax.set_facecolor(facecolor)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(linewidth)
        spine.set_edgecolor(edgecolor)


def finish_axis(ax: Axes, *, grid: str = "y") -> None:
    sns.despine(ax=ax, offset=2, trim=False)
    if grid:
        ax.grid(True, axis=grid, color=GRID_COLOR, linewidth=0.65, alpha=1.0, zorder=0)
        ax.set_axisbelow(True)


def create_triptych() -> tuple[Figure, list[Axes]]:
    fig = plt.figure(figsize=(DOUBLE_COL_W, TRIPANEL_H), facecolor="white")
    gs = GridSpec(1, 3, figure=fig, wspace=0.42, left=0.09, right=0.98, top=0.90, bottom=0.20)
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    for ax in axes:
        ax._panel_offset = True  # type: ignore[attr-defined]
    return fig, axes


def create_grid(nrows: int, ncols: int, *, height: float | None = None) -> tuple[Figure, np.ndarray]:
    h = height or (2.45 * nrows + 0.3)
    fig = plt.figure(figsize=(DOUBLE_COL_W, h), facecolor="white")
    gs = GridSpec(nrows, ncols, figure=fig, wspace=0.34, hspace=0.38, left=0.08, right=0.98, top=0.94, bottom=0.08)
    axes = np.array([[fig.add_subplot(gs[i, j]) for j in range(ncols)] for i in range(nrows)])
    return fig, axes


def create_diptych() -> tuple[Figure, list[Axes]]:
    fig = plt.figure(figsize=(DOUBLE_COL_W, TWOPANEL_H), facecolor="white")
    gs = GridSpec(1, 2, figure=fig, wspace=0.38, left=0.08, right=0.98, top=0.90, bottom=0.18)
    axes = [fig.add_subplot(gs[0, i]) for i in range(2)]
    for ax in axes:
        ax._panel_offset = True  # type: ignore[attr-defined]
    return fig, axes


def create_theory_figure() -> tuple[Figure, Axes, Axes, Axes]:
    """Top schematic + bottom OC plane + power curve (with inset room)."""
    fig = plt.figure(figsize=(DOUBLE_COL_W, THEORY_FIG_H), facecolor="white")
    gs = GridSpec(
        2,
        2,
        figure=fig,
        height_ratios=[1.05, 1.35],
        hspace=0.42,
        wspace=0.32,
        left=0.08,
        right=0.97,
        top=0.96,
        bottom=0.09,
    )
    ax_top = fig.add_subplot(gs[0, :])
    ax_oc = fig.add_subplot(gs[1, 0])
    ax_pw = fig.add_subplot(gs[1, 1])
    for ax in (ax_oc, ax_pw):
        ax._panel_offset = True  # type: ignore[attr-defined]
    ax_top._panel_offset = True  # type: ignore[attr-defined]
    return fig, ax_top, ax_oc, ax_pw


def create_panel_figure(n_panels: int, *, height: float | None = None) -> tuple[Figure, list[Axes]]:
    if n_panels == 3:
        fig, axes = create_triptych()
        if height is not None:
            fig.set_size_inches(DOUBLE_COL_W, height)
        return fig, axes
    if n_panels == 2:
        fig, axes = create_diptych()
        if height is not None:
            fig.set_size_inches(DOUBLE_COL_W, height)
        return fig, axes
    raise ValueError(f"Unsupported panel count: {n_panels}")


def style_data_axis(ax: Axes, *, grid: str = "y", y_grid: bool = True, x_grid: bool = False) -> None:
    g = grid
    if y_grid and x_grid:
        g = "both"
    elif not y_grid and x_grid:
        g = "x"
    finish_axis(ax, grid=g if grid else "")


def reference_line(
    ax: Axes,
    value: float,
    *,
    axis: str = "y",
    color: str = C_SLATE,
    label: str | None = None,
    ls=(0, (4, 3)),
    lw: float = 0.9,
    alpha: float = 1.0,
) -> None:
    fn = ax.axhline if axis == "y" else ax.axvline
    fn(value, color=color, ls=ls, lw=lw, alpha=alpha, label=label, zorder=2)


def shade_between(ax: Axes, x, y1, y2, *, color: str = C_SAGE, alpha: float = 0.10) -> None:
    ax.fill_between(x, y1, y2, color=color, alpha=alpha, linewidth=0, zorder=1)


def styled_bar(ax, x, height, *, colors, width=0.62, yerr=None, labels=None):
    return ax.bar(
        x,
        height,
        width=width,
        color=colors,
        edgecolor="white",
        linewidth=0.9,
        yerr=yerr,
        capsize=2.5,
        zorder=3,
    )


def save_figure(
    fig: Figure,
    stem: str,
    *,
    fig_dir: Path,
    extra_stems: tuple[str, ...] = (),
    dpi: int | None = None,
    bbox_inches: str | None = "tight",
) -> Path:
    fig_dir.mkdir(parents=True, exist_ok=True)
    primary = fig_dir / f"{stem}.png"
    # Passing bbox_inches=None still falls back to rcParams['savefig.bbox'] ('tight').
    if bbox_inches is None:
        w_in, h_in = fig.get_size_inches()
        bbox: str | Bbox = Bbox.from_bounds(0, 0, float(w_in), float(h_in))
    else:
        bbox = bbox_inches
    save_kw = dict(facecolor="white", edgecolor="none", bbox_inches=bbox)
    if dpi is not None:
        save_kw["dpi"] = dpi
    for name in {stem, *extra_stems}:
        for ext in (".png", ".pdf"):
            fig.savefig(fig_dir / f"{name}{ext}", **save_kw)
        if dpi is not None:
            fig.savefig(
                fig_dir / f"{name}.tif",
                format="tiff",
                pil_kwargs={"compression": "tiff_lzw"},
                **save_kw,
            )
    plt.close(fig)
    return primary


def binomial_se(p: float, n: int) -> float:
    p = float(np.clip(p, 0.0, 1.0))
    return float(np.sqrt(max(p * (1.0 - p) / max(n, 1), 0.0)))
