"""
Publication figure theme — Nature/Cell-style matplotlib + optional seaborn base.

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

# Muted professional palette (colorblind-safe, print-friendly).
C_PRIMARY = "#2166AC"
C_SECONDARY = "#B2182B"
C_ACCENT = "#1B7837"
C_WARN = "#D95F02"
C_NEUTRAL = "#636363"
C_LIGHT = "#D9D9D9"
C_GOLD = "#E6AB02"

# Legacy aliases
JOURNAL_BLUE = C_PRIMARY
JOURNAL_ORANGE = C_WARN
JOURNAL_GREEN = C_ACCENT
JOURNAL_YELLOW = C_GOLD
JOURNAL_PURPLE = "#762A83"
JOURNAL_GRAY = C_NEUTRAL
JOURNAL_LIGHT_GRAY = C_LIGHT
JOURNAL_SKY = "#92C5DE"
JOURNAL_RED = C_SECONDARY
GRID_COLOR = "#EBEBEB"

DOUBLE_COL_W = 7.2
TRIPANEL_H = 3.05
TWOPANEL_H = 2.85


def apply_journal_rc() -> None:
    """Seaborn ticks theme + matplotlib fine-tuning for print."""
    sns.set_theme(
        style="ticks",
        context="paper",
        font="sans-serif",
        font_scale=1.05,
        rc={
            "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
            "axes.linewidth": 0.9,
            "axes.edgecolor": "#333333",
            "axes.labelsize": 9,
            "axes.labelweight": "medium",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7.5,
            "legend.frameon": True,
            "legend.framealpha": 1.0,
            "legend.edgecolor": GRID_COLOR,
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


def finish_axis(ax: Axes, *, grid: str = "y") -> None:
    """Despine + light grid."""
    sns.despine(ax=ax, offset=2, trim=False)
    if grid:
        ax.grid(True, axis=grid, color=GRID_COLOR, linewidth=0.7, alpha=1.0, zorder=0)
        ax.set_axisbelow(True)


def panel_label(ax: Axes, letter: str) -> None:
    ax.text(
        -0.11 if hasattr(ax, "_panel_offset") else 0.02,
        1.06,
        letter,
        transform=ax.transAxes,
        fontsize=12,
        fontweight="bold",
        va="bottom",
        ha="left",
        clip_on=False,
    )


def create_triptych() -> tuple[Figure, list[Axes]]:
    fig = plt.figure(figsize=(DOUBLE_COL_W, TRIPANEL_H), facecolor="white")
    gs = GridSpec(1, 3, figure=fig, wspace=0.42, left=0.09, right=0.98, top=0.90, bottom=0.20)
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    for ax in axes:
        ax._panel_offset = True  # type: ignore[attr-defined]
    return fig, axes


def create_grid(nrows: int, ncols: int, *, height: float | None = None) -> tuple[Figure, np.ndarray]:
    """2×2 (or general) panel grid with publication margins."""
    h = height or (2.45 * nrows + 0.3)
    fig = plt.figure(figsize=(DOUBLE_COL_W, h), facecolor="white")
    gs = GridSpec(nrows, ncols, figure=fig, wspace=0.34, hspace=0.38, left=0.08, right=0.98, top=0.94, bottom=0.08)
    axes = np.array([[fig.add_subplot(gs[i, j]) for j in range(ncols)] for i in range(nrows)])
    return fig, axes


def create_diptych() -> tuple[Figure, list[Axes]]:
    fig = plt.figure(figsize=(DOUBLE_COL_W, TWOPANEL_H), facecolor="white")
    gs = GridSpec(1, 2, figure=fig, wspace=0.38, left=0.08, right=0.98, top=0.90, bottom=0.18)
    return fig, [fig.add_subplot(gs[0, i]) for i in range(2)]


def create_panel_figure(n_panels: int, *, height: float | None = None) -> tuple[Figure, list[Axes]]:
    """Backward-compatible panel factory."""
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


def reference_line(ax: Axes, value: float, *, axis: str = "y", color: str = C_NEUTRAL, label: str | None = None, ls=(0, (4, 3)), lw: float = 1.0, alpha: float = 1.0) -> None:
    fn = ax.axhline if axis == "y" else ax.axvline
    fn(value, color=color, ls=ls, lw=lw, alpha=alpha, label=label, zorder=2)


def shade_between(ax: Axes, x, y1, y2, *, color: str = C_PRIMARY, alpha: float = 0.12) -> None:
    ax.fill_between(x, y1, y2, color=color, alpha=alpha, linewidth=0, zorder=1)


def styled_bar(ax, x, height, *, colors, width=0.62, yerr=None, labels=None):
    return ax.bar(x, height, width=width, color=colors, edgecolor="white", linewidth=0.9, yerr=yerr, capsize=2.5, zorder=3)


def save_figure(
    fig: Figure,
    stem: str,
    *,
    fig_dir: Path,
    extra_stems: tuple[str, ...] = (),
) -> Path:
    """Save PNG/PDF under fig_dir only; manuscript copies via build_artifacts._copy_figures."""
    fig_dir.mkdir(parents=True, exist_ok=True)
    primary = fig_dir / f"{stem}.png"
    for name in {stem, *extra_stems}:
        for ext in (".png", ".pdf"):
            fig.savefig(fig_dir / f"{name}{ext}", facecolor="white", edgecolor="none")
    return primary


def binomial_se(p: float, n: int) -> float:
    p = float(np.clip(p, 0.0, 1.0))
    return float(np.sqrt(max(p * (1.0 - p) / max(n, 1), 0.0)))
