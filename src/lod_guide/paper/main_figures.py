"""
Main-text figures — v7 story-first layout.

Fig 1: integrated protocol + E2 planning (panels A–D) — single manuscript figure.
Supplement: tables/CSVs only (grid in Table 3 extensions).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap, ListedColormap, LogNorm

from lod_guide.paper.figure_style import (
    C_FOG,
    C_INK,
    C_MIST,
    C_NEUTRAL,
    C_PRIMARY,
    C_SAGE,
    C_SLATE,
    C_WINE,
    DOUBLE_COL_W,
    FOCUS_FIG_H,
    PROTOCOL_FIG_H,
    apply_journal_rc,
    binomial_se,
    create_diptych,
    create_monograph_figure,
    create_single_panel_figure,
    create_triptych,
    finish_axis,
    panel_label,
    save_figure,
    style_colorbar,
    subtitle_chip,
    frame_panel,
)
from lod_guide.paper.flowchart_fig1 import draw_fig1_claim_flow, draw_fig1_panel_a_columns, draw_pipeline_schematic
from lod_guide.paper.flowchart_fig1 import render_fig1_decision_map as _legacy_fig1_map
from lod_guide.research.all_positive_trap import exact_lower_bound_after_all_success
from lod_guide.research.reagent_discrimination import LogisticLoDCurve, evaluate_relative_lod_continuum
from lod_guide.s5_sample_size import power_two_proportions, sample_size_two_proportions
from lod_guide.theory.exact_tests import exact_power_two_proportions
from lod_guide.theory.selective.sample_split import monte_carlo_compare_split_vs_unsplit

from lod_guide.research.e2_planning_constants import (
    ILLUSTRATIVE_PAIR,
    P_A_ILLUSTRATIVE,
    P_B_ILLUSTRATIVE,
)

ROOT = Path(__file__).resolve().parents[3]
FIG_DIR = ROOT / "figures" / "methodology"
DATA = ROOT / "data" / "research"

P_A, P_B = P_A_ILLUSTRATIVE, P_B_ILLUSTRATIVE

_HEAT_CMAP = LinearSegmentedColormap.from_list(
    "lod_ink_sage", ["#f1f5f9", "#94a3b8", "#0f766e", "#1e293b"], N=256
)


def _load_json(name: str) -> dict | None:
    p = DATA / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _power_curve_ns(n_max: int = 220) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    cache_path = DATA / "fig2_headline_power_curve.json"
    key_ns = [5, 8, 10, 12, 15, 18, 20, 25, 30, 40, 50, 60, 80, 100, 125, 150, 175, 199, n_max]
    ns = np.unique(np.array(key_ns, dtype=int))
    if cache_path.is_file():
        loaded = json.loads(cache_path.read_text(encoding="utf-8"))
        if loaded.get("ns") == ns.tolist():
            return ns, np.array(loaded["asymptotic"]), np.array(loaded["exact_fisher"])
    pw_a = np.array([power_two_proportions(P_A, P_B, int(n)) for n in ns])
    pw_f = np.array([exact_power_two_proportions(P_A, P_B, int(n), test="fisher") for n in ns])
    DATA.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps({"ns": ns.tolist(), "asymptotic": pw_a.tolist(), "exact_fisher": pw_f.tolist()}, indent=2),
        encoding="utf-8",
    )
    return ns, pw_a, pw_f


from lod_guide.research.comparison_grid_export import (
    FOLKLORE_N,
    REF_PAIRS,
    build_comparison_grid,
    export_comparison_grid_tables,
    grid_arrays,
    pareto_plane_points,
)
from lod_guide.research.comparison_grid_uq import (
    export_grid_uq_tables,
    sensitivity_contour_levels,
)
from lod_guide.research.decision_risk import evaluate_standard_scenarios
from lod_guide.research.lattice_surface_model import (
    build_lattice_surface_model,
    export_lattice_surface_tables,
)


def _plot_nstar_delta_marginal(ax, marginal_rows: list[dict]) -> None:
    """Marginal design surface median n* vs contrast Δ over the full lattice."""
    if not marginal_rows:
        ax.axis("off")
        return
    dpp = [r["delta_pp"] for r in marginal_rows]
    n_med = [r["median_n_star_asymptotic"] for r in marginal_rows]
    frame_panel(ax, facecolor="white", edgecolor=C_MIST, linewidth=0.5)
    ax.plot(dpp, n_med, color=C_SAGE, lw=1.8, zorder=3)
    ax.axhline(FOLKLORE_N, color=C_WINE, ls=(0, (4, 2)), lw=0.9, zorder=2)
    ax.set(
        xlabel=r"$\Delta=p_A-p_B$ (pp)",
        ylabel=r"median $n^*$",
        xlim=(0, 50),
        yscale="log",
        ylim=(8, 600),
    )
    ax.set_xticks([1, 10, 20, 30, 40, 49])
    ax.tick_params(labelsize=5.5, length=0, pad=2)
    ax.text(
        0.97, 0.92, r"$n=20$",
        transform=ax.transAxes, fontsize=5.2, color=C_WINE, ha="right", va="top",
    )
    ax.text(
        0.03, 0.08, r"marginal\nby $\Delta$",
        transform=ax.transAxes, fontsize=5.0, color=C_SLATE, ha="left", va="bottom",
    )
    sns.despine(ax=ax, offset=1, trim=True)


def _heatmap_ticks(values: np.ndarray, *, step: int = 4, as_pct: bool = False) -> list[str]:
    out: list[str] = []
    for k, p in enumerate(values):
        if k % step != 0:
            out.append("")
        elif as_pct:
            out.append(str(int(round(p * 100))))
        else:
            out.append(f"{p:.0%}")
    return out


_MISS_BOUNDS = [0.0, 0.2, 0.5, 0.8, 1.0]
_MISS_CMAP = ListedColormap(["#ffffff", "#f1f5f9", "#fecdd3", "#f43f5e", "#881337"])
_MISS_NORM = BoundaryNorm(_MISS_BOUNDS, _MISS_CMAP.N)
_NSTAR_CMAP = LinearSegmentedColormap.from_list(
    "lod_nstar",
    ["#ffffff", "#ecfdf5", "#99f6e4", "#2dd4bf", "#0f766e", "#134e4a"],
    N=256,
)
_NSTAR_NORM = LogNorm(vmin=10, vmax=500)
_LATTICE_TICKS = (50, 60, 70, 80, 90, 99)
_HEADLINE_PAIR = "90/80"
_LATTICE_CBAR_KW = {"fraction": 0.046, "pad": 0.02, "aspect": 22}
_FIG1_DPI = 600
_FIG2_DPI = 600

# Short y-axis labels for Fig 2B — aligned with Table 7 citation abbreviations.
TIER_A_DEPOSIT_LABELS: dict[str, str] = {
    "zenodo_mus_wt_qpcr": "Piaggio WT",
    "zenodo_mus_multiplex_qpcr": "Piaggio multiplex",
    "analyseit_ep17_estradiol": "EP17 estradiol",
    "analyseit_ep17_probit": "EP17 probit",
    "mendeley_carobene_lombardy_eqa": "Carobene EQA",
    "bioc_msstats_lobd_cptac": "MSstatsLOBD",
    "zenodo_radioimmuno_precision": "Malkamaki precision",
    "zenodo_radioimmuno_linearity": "Malkamaki linearity",
    "zenodo_rmn_qualification": "Sawant RMN",
    "plos_bzdok2024_trec_lod": "Bzdok TREC",
}


def _lattice_extent(n: int) -> tuple[float, float, float, float]:
    return (49.5, 99.5, 99.5, 49.5)


def _style_lattice_ax(ax) -> None:
    frame_panel(ax, facecolor="#fafbfc", edgecolor=C_MIST, linewidth=0.65)
    ax.tick_params(length=0, pad=5, colors=C_SLATE, labelsize=8.0)


def _lattice_mesh(pa: np.ndarray, pb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Meshgrid aligned with imshow extent (pb on x, pa on y)."""
    return np.meshgrid(pb * 100.0, pa * 100.0)


def _overlay_uq_contours(
    ax,
    pa: np.ndarray,
    pb: np.ndarray,
    *,
    panel: str,
) -> None:
    """Tier-2 sensitivity bracket contours (asymptotic α / power-target bands)."""
    spec = sensitivity_contour_levels(panel)
    x, y = _lattice_mesh(pa, pb)
    lo = spec["surfaces"]["lo"]
    hi = spec["surfaces"]["hi"]
    lab_lo, lab_hi = spec["labels"]

    if panel == "miss_beta":
        level = spec["level"]
        ax.contour(
            x, y, lo, levels=[level], colors=[C_INK], linestyles=[(0, (4, 2))],
            linewidths=1.0, alpha=0.55, zorder=5,
        )
        ax.contour(
            x, y, hi, levels=[level], colors=[C_INK], linestyles=[(0, (2, 2))],
            linewidths=1.0, alpha=0.55, zorder=5,
        )
        ax.text(
            0.03, 0.04, rf"{lab_lo} / {lab_hi} @ $\beta=0.8$",
            transform=ax.transAxes, fontsize=7.0, color=C_SLATE, ha="left", va="bottom",
            bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor=C_MIST, alpha=0.92, linewidth=0.4),
            zorder=10,
        )
        return

    valid = np.isfinite(lo) & np.isfinite(hi)
    med_lo = float(np.nanmedian(lo[valid]))
    med_hi = float(np.nanmedian(hi[valid]))
    ax.contour(
        x, y, lo, levels=[med_lo], colors=[C_SAGE], linestyles=[(0, (4, 2))],
        linewidths=1.0, alpha=0.65, zorder=5,
    )
    ax.contour(
        x, y, hi, levels=[med_hi], colors=[C_INK], linestyles=[(0, (2, 2))],
        linewidths=1.0, alpha=0.65, zorder=5,
    )
    ax.text(
        0.03, 0.04, rf"{lab_lo}: $n^*\approx{med_lo:.0f}$  ·  {lab_hi}: $n^*\approx{med_hi:.0f}$",
        transform=ax.transAxes, fontsize=7.0, color=C_SLATE, ha="left", va="bottom",
        bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor=C_MIST, alpha=0.92, linewidth=0.4),
        zorder=10,
    )


def _plot_lattice_heatmap(
    ax,
    data: np.ndarray,
    pa: np.ndarray,
    pb: np.ndarray,
    *,
    cmap,
    cbar_label: str,
    norm=None,
    vmin: float | None = None,
    vmax: float | None = None,
    cbar_ticks: list[float] | None = None,
    cbar_highlight: float | None = None,
    cax=None,
    show_ylabel: bool = True,
    cbar_orientation: str = "vertical",
) -> None:
    masked = np.ma.masked_invalid(data.astype(float))
    cmap_use = cmap.copy() if hasattr(cmap, "copy") else cmap
    if hasattr(cmap_use, "set_bad"):
        cmap_use.set_bad("#eef2f7")

    imshow_kw: dict = dict(
        origin="upper",
        aspect="equal",
        cmap=cmap_use,
        extent=_lattice_extent(len(pa)),
        interpolation="nearest",
        rasterized=True,
    )
    if norm is not None:
        imshow_kw["norm"] = norm
    else:
        imshow_kw["vmin"] = vmin
        imshow_kw["vmax"] = vmax
    im = ax.imshow(masked, **imshow_kw)
    _style_lattice_ax(ax)
    ax.set_xticks(list(_LATTICE_TICKS))
    ax.set_yticks(list(_LATTICE_TICKS))
    ax.set_xlabel(r"Competitor hit rate $p_B$ (%)", fontsize=8.0, labelpad=5, color=C_INK)
    if show_ylabel:
        ax.set_ylabel(r"Reference hit rate $p_A$ (%)", fontsize=8.0, labelpad=8, color=C_INK)
    else:
        ax.set_ylabel("")
    ax.plot([49.5, 99.5], [99.5, 49.5], color="#cbd5e1", lw=1.1, solid_capstyle="round", zorder=4)

    if cax is not None:
        cbar = ax.figure.colorbar(im, cax=cax, orientation=cbar_orientation)
    else:
        cbar = ax.figure.colorbar(im, ax=ax, **_LATTICE_CBAR_KW)
    style_colorbar(
        cbar,
        label=cbar_label,
        ticks=cbar_ticks,
        highlight=cbar_highlight,
        fontsize=7.5 if cax is not None else 8.0,
        orientation=cbar_orientation,
    )


def _annotate_headline_pair(
    ax,
    pa: np.ndarray,
    pb: np.ndarray,
    z: np.ndarray,
    *,
    value_is_nstar: bool = False,
    callout_xy: tuple[float, float] = (68, 78),
    compact: bool = False,
    legend_inset: bool = False,
) -> None:
    """Single 90/80 callout — main-text figure only."""
    pa_v, pb_v = 0.90, 0.80
    ia = int(np.argmin(np.abs(pa - pa_v)))
    ib = int(np.argmin(np.abs(pb - pb_v)))
    if np.isnan(z[ia, ib]):
        return
    x, y = pb_v * 100, pa_v * 100
    val = float(z[ia, ib])
    note = rf"$n^*={val:.0f}$" if value_is_nstar else rf"$\beta={val:.2f}$"
    label = rf"ex. 90/80: {note}" if compact else rf"Example 90/80  {note}"

    ax.scatter([x], [y], s=110 if compact else 150, facecolors="none", edgecolors=C_INK, linewidths=2.0, zorder=7)
    ax.scatter([x], [y], s=32 if compact else 40, c=C_WINE, edgecolors="white", linewidths=1.0, zorder=8)

    if legend_inset:
        ax.text(
            0.97, 0.97, label,
            transform=ax.transAxes,
            fontsize=8.0,
            color=C_INK,
            fontweight="semibold",
            ha="right",
            va="top",
            bbox=dict(
                boxstyle="round,pad=0.28,rounding_size=0.10",
                facecolor="white",
                edgecolor=C_WINE,
                linewidth=0.8,
                alpha=0.97,
            ),
            zorder=9,
        )
        return

    ax.annotate(
        label,
        xy=(x, y),
        xytext=callout_xy,
        fontsize=8.0 if compact else 8.5,
        color=C_INK,
        fontweight="semibold",
        ha="center",
        va="center",
        bbox=dict(
            boxstyle="round,pad=0.30,rounding_size=0.12",
            facecolor="white",
            edgecolor=C_WINE,
            linewidth=0.85,
            alpha=0.98,
        ),
        arrowprops=dict(
            arrowstyle="-|>", color=C_WINE, lw=0.9,
            connectionstyle="arc3,rad=0.22" if compact else "arc3,rad=0.12",
            shrinkA=5, shrinkB=4,
        ),
        zorder=9,
    )


def _annotate_ref_pairs(
    ax,
    pa: np.ndarray,
    pb: np.ndarray,
    z: np.ndarray,
    *,
    headline_only_label: bool = True,
    value_is_nstar: bool = False,
    headline_only: bool = False,
    callout_xy: tuple[float, float] = (68, 78),
    compact: bool = False,
    legend_inset: bool = False,
) -> None:
    if headline_only:
        _annotate_headline_pair(
            ax, pa, pb, z, value_is_nstar=value_is_nstar,
            callout_xy=callout_xy, compact=compact, legend_inset=legend_inset,
        )
        return
    for pa_v, pb_v, lab in REF_PAIRS:
        ia = int(np.argmin(np.abs(pa - pa_v)))
        ib = int(np.argmin(np.abs(pb - pb_v)))
        if np.isnan(z[ia, ib]):
            continue
        x, y = pb_v * 100, pa_v * 100
        is_headline = lab == _HEADLINE_PAIR
        if is_headline:
            _annotate_headline_pair(
                ax, pa, pb, z,
                value_is_nstar=value_is_nstar,
                compact=compact,
                legend_inset=legend_inset,
            )
        elif not headline_only_label:
            ax.scatter(
                [x], [y], s=42, facecolors="none", edgecolors=C_INK,
                linewidths=0.7, alpha=0.55, zorder=6,
            )
            ax.text(x + 1.2, y - 1.0, lab, fontsize=5.0, color=C_SLATE, alpha=0.85, zorder=6)


def _plot_lod_continuum_panel(ax, *, embedded: bool = False) -> None:
    xp_base = np.arange(50, 100, dtype=float)
    slope_curves: dict[float, np.ndarray] = {}
    for slope in (1.5, 2.0, 2.5):
        curve = LogisticLoDCurve(slope=slope)
        rel = evaluate_relative_lod_continuum(p_max_pct=99, p_min_pct=50, step_pct=1, curve=curve)
        xp = np.array([r["p_pct"] for r in rel], dtype=float)
        yp = np.array([r["relative_c_lod95"] for r in rel], dtype=float)
        slope_curves[slope] = yp
        if slope == 2.0:
            xp_base = xp

    y_lo = np.minimum.reduce(list(slope_curves.values()))
    y_hi = np.maximum.reduce(list(slope_curves.values()))

    frame_panel(ax, facecolor="white")
    ax.fill_between(xp_base, y_lo, y_hi, color=C_SAGE, alpha=0.14, zorder=1)
    for slope, yp in slope_curves.items():
        ax.plot(
            xp_base, yp,
            color=C_INK if slope == 2.0 else C_SLATE,
            lw=2.6 if slope == 2.0 else 1.0,
            ls="-" if slope == 2.0 else (0, (4, 2)),
            alpha=1.0 if slope == 2.0 else 0.65,
            zorder=3 if slope == 2.0 else 2,
        )

    ax.axhline(1.0, color=C_SLATE, ls=(0, (5, 3)), lw=0.8, zorder=2)
    ax.axvline(95, color=C_SLATE, ls=(0, (3, 3)), lw=0.65, alpha=0.55, zorder=2)
    ax.axvline(80, color=C_WINE, ls=(0, (3, 3)), lw=0.65, alpha=0.35, zorder=2)

    y80 = float(slope_curves[2.0][int(np.where(xp_base == 80)[0][0])])
    y95 = float(slope_curves[2.0][int(np.where(xp_base == 95)[0][0])])

    ax.scatter([95], [y95], s=72, c=C_INK, marker="D", edgecolors="white", linewidths=0.9, zorder=5)
    ax.scatter([80], [y80], s=88, c=C_WINE, edgecolors="white", linewidths=1.0, zorder=6)

    ax.annotate(
        rf"LoD$_{{95}}$",
        xy=(95, y95), xytext=(86.5, 0.92),
        fontsize=8.0, color=C_INK, ha="right", va="bottom",
        arrowprops=dict(arrowstyle="-", color=C_SLATE, lw=0.65),
        zorder=7,
    )
    if embedded:
        ax.text(
            0.04, 0.30,
            rf"$p=80\% \Rightarrow c/\mathrm{{LoD}}_{{95}}={y80:.2f}$",
            transform=ax.transAxes,
            fontsize=8.0, color=C_WINE, fontweight="semibold", ha="left", va="center",
            bbox=dict(boxstyle="round,pad=0.22", facecolor="#fff1f2", edgecolor=C_WINE, linewidth=0.55, alpha=0.95),
            zorder=7,
        )
    else:
        ax.annotate(
            rf"$p=80\% \Rightarrow c/\mathrm{{LoD}}_{{95}}={y80:.2f}$",
            xy=(80, y80), xytext=(62, 0.38),
            fontsize=6.5, color=C_WINE, fontweight="semibold", ha="center",
            arrowprops=dict(arrowstyle="-|>", color=C_WINE, lw=0.85, connectionstyle="arc3,rad=-0.08"),
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#fff1f2", edgecolor=C_WINE, linewidth=0.55, alpha=0.95),
            zorder=7,
        )

    ax.set(
        xlabel=r"Single-trial hit rate $p$ (%)",
        ylabel=r"$c/\mathrm{LoD}_{95}$" if embedded else r"$c/\mathrm{LoD}_{95}$  (linear scale)",
        xlim=(49, 99.5),
        ylim=(0.0, 1.05),
    )
    if embedded:
        ax.yaxis.set_label_coords(-0.12, 0.5)
        ax.set_xticks([50, 60, 70, 80, 90, 99])
    else:
        ax.set_xticks([50, 60, 70, 80, 90, 95, 99])
    ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.grid(True, axis="both", color=C_MIST, linewidth=0.45, alpha=0.85, zorder=0)
    ax.set_axisbelow(True)
    sns.despine(ax=ax, offset=2, trim=False)
    if not embedded:
        subtitle_chip(ax, "Logistic map + slope sensitivity (1.5–2.5)", color=C_INK, y=1.01)


def _panel_title(fig, ax, text: str, *, color: str = C_INK) -> None:
    """Centered short title above one subplot column (avoids cross-panel overlap)."""
    pos = ax.get_position()
    fig.text(
        (pos.x0 + pos.x1) / 2,
        pos.y1 + 0.012,
        text,
        ha="center",
        va="bottom",
        fontsize=6.3,
        color=color,
        fontweight="medium",
    )


def _fisher_power_grid_n20() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    grid = build_comparison_grid()
    pa, pb, power, _, _ = grid_arrays(grid)
    return pa, pb, power


def _plot_g1_all_positive(ax) -> None:
    ns = np.arange(1, 41)
    claim_p = 0.95
    for p, col, lw in [(0.95, C_INK, 2.2), (0.90, C_SLATE, 1.4), (0.80, C_WINE, 1.5), (0.50, C_MIST, 1.0)]:
        y = p**ns
        ax.plot(ns, y, color=col, lw=lw, label=rf"$p={p:.2f}$", zorder=3)
    ax.axhline(claim_p, color=C_SLATE, ls=(0, (4, 3)), lw=0.8, label=rf"claim={claim_p:.0%}")
    ax.axvline(20, color=C_WINE, ls=(0, (5, 2)), lw=1.0)
    lb20 = exact_lower_bound_after_all_success(20, 0.05, two_sided=False)
    for p, col in ((0.95, C_INK), (0.90, C_SLATE), (0.80, C_WINE)):
        ax.scatter([20], [p**20], s=28, c=col, edgecolors="white", linewidths=0.6, zorder=5)
    ax.hlines(lb20, 18.5, 21.5, colors=C_SAGE, linewidth=1.2, zorder=4)
    ax.text(22, lb20, rf"CP LB={lb20:.2f}", fontsize=6, color=C_SAGE, va="center")
    ax.text(22, 0.95**20, rf"$0.95^{{20}}={0.95**20:.2f}$", fontsize=6, color=C_INK, va="center")
    ax.set(xlabel=r"$n$ replicates", ylabel=r"$\Pr(X{=}n\mid p)=p^n$", xlim=(0, 40), ylim=(0, 1.02))
    ax.legend(loc="upper right", fontsize=5.5, ncol=2, framealpha=0.98)
    finish_axis(ax)


def _plot_g2_miss_heatmap(
    ax,
    *,
    pct_step: int = 5,
    headline_only: bool = False,
    embedded: bool = False,
    cax=None,
    show_ylabel: bool = True,
    cbar_orientation: str = "vertical",
) -> None:
    """Full (p_A, p_B) integer grid 50–99%: miss β at folklore n=20."""
    grid = build_comparison_grid()
    pa, pb, _, miss, _ = grid_arrays(grid)
    _plot_lattice_heatmap(
        ax, miss, pa, pb,
        cmap=_MISS_CMAP,
        norm=_MISS_NORM,
        cbar_label=r"Miss $\beta$",
        cbar_ticks=[0.0, 0.2, 0.5, 0.8, 1.0],
        cbar_highlight=0.8,
        cax=cax,
        show_ylabel=show_ylabel,
        cbar_orientation=cbar_orientation,
    )
    _annotate_ref_pairs(
        ax, pa, pb, miss, headline_only=headline_only,
        compact=embedded, legend_inset=embedded,
    )
    if embedded:
        _overlay_uq_contours(ax, pa, pb, panel="miss_beta")
    sm = grid.get("summary") or {}
    frac = sm.get("frac_miss_gt_0.8")
    n_valid = sm.get("n_valid_cells")
    if frac is not None and n_valid is not None and not embedded:
        subtitle_chip(
            ax,
            rf"Underpowered: {100 * frac:.0f}% pairs with $\beta>0.8$ at $n=20$  ·  {int(n_valid)} cells",
            color=C_WINE,
            y=1.01,
        )


def _plot_g2_miss_scenarios(ax) -> None:
    """Legacy 3-bar panel (supplement)."""
    _plot_g2_miss_heatmap(ax)


def _plot_p16_saturation(ax) -> None:
    ident = _load_json("identification_study.json")
    if not ident:
        ax.axis("off")
        return
    cats = ["Interior\nlevels\n(P15 ok)", "Saturation\nplateau\n(P16)"]
    vals = [float(ident["good_design"]["se_log10_lod"]), float(ident["saturation_design"]["se_log10_lod"])]
    x = np.arange(2)
    ax.bar(x, vals, color=[C_SAGE, C_WINE], width=0.52, edgecolor="white", linewidth=0.9, zorder=3)
    ax.set_yscale("log")
    ax.set_xticks(x, cats, fontsize=6.5)
    ax.set_ylabel(r"SE$(\log_{10}\mathrm{LoD}_{95})$")
    ax.text(1, vals[1] * 1.15, "non-identifiable", ha="center", fontsize=6.5, color=C_WINE)
    finish_axis(ax)


def _plot_pareto_plane(ax) -> None:
    pareto = _load_json("pareto_exact_sample_size.json")
    if not pareto:
        ax.axis("off")
        return
    cert = pareto["certificate"]
    ref_pts = pareto_plane_points()

    ax.fill_between([0, 0.07], [0.80, 0.80], [0.95, 0.95], color=C_SAGE, alpha=0.14, zorder=0)
    ax.fill_between([0, 0.07], [0, 0], [0.80, 0.80], color=C_WINE, alpha=0.08, zorder=0)
    ax.axhline(0.80, color=C_SLATE, ls=(0, (4, 3)), lw=0.85)
    ax.axvline(0.05, color=C_SLATE, ls=(0, (4, 3)), lw=0.85)

    # All reference pairs @ folklore n=20 (small) and powered n* (small diamonds).
    for pt in ref_pts:
        folk, pow_ = pt["folklore"], pt["powered"]
        is_headline = pt["pair"] == "90/80"
        ax.scatter(
            folk["type_i_fisher"], folk["power_fisher"],
            s=90 if is_headline else 32, c=C_WINE, marker="o",
            edgecolors="white", linewidths=0.9 if is_headline else 0.5,
            alpha=1.0 if is_headline else 0.72, zorder=4 if is_headline else 3,
        )
        ax.scatter(
            pow_["type_i_fisher"], pow_["power_fisher"],
            s=95 if is_headline else 28, c=C_SAGE, marker="D",
            edgecolors="white", linewidths=0.9 if is_headline else 0.5,
            alpha=1.0 if is_headline else 0.65, zorder=4 if is_headline else 3,
        )
        if not is_headline and folk["power_fisher"] < 0.25:
            ax.annotate(
                pt["pair"], xy=(folk["type_i_fisher"], folk["power_fisher"]),
                xytext=(3, 3), textcoords="offset points", fontsize=4.5, color=C_WINE, alpha=0.85,
            )

    f, p = cert["folklore"], cert["powered"]
    ax.annotate(
        "P18",
        xy=(f["type_i_fisher"], f["power_fisher"]),
        xytext=(0.024, 0.38),
        fontsize=7, color=C_WINE, ha="center",
        arrowprops=dict(arrowstyle="-|>", color=C_WINE, lw=0.85),
    )
    ax.annotate("", xy=(p["type_i_fisher"], p["power_fisher"]), xytext=(f["type_i_fisher"], f["power_fisher"]),
                arrowprops=dict(arrowstyle="-|>", color=C_SAGE, lw=1.0, ls="--"))
    ax.scatter([], [], s=32, c=C_WINE, marker="o", label=r"Folklore $n" + r"{=}20$ (8 pairs)")
    ax.scatter([], [], s=28, c=C_SAGE, marker="D", label=r"Powered $n^*$ (8 pairs)")
    ax.text(0.97, 0.08, r"$L_\mathrm{folk}/L_\mathrm{pow}\approx 3.9$ (8 pairs)",
            transform=ax.transAxes, ha="right", fontsize=6.5, color=C_INK)
    ax.set(xlabel=r"Type I ($\alpha$)", ylabel="Power", xlim=(0, 0.07), ylim=(0, 0.88))
    ax.legend(loc="lower right", fontsize=5.5, framealpha=0.98)
    finish_axis(ax, grid="both")


def _plot_headline_power_focused(ax) -> None:
    """Box 1 centerpiece: exact Fisher power for 90% vs 80% only (large type)."""
    ns, _, _ = _power_curve_ns(n_max=220)
    pa_v, pb_v = P_A, P_B
    pw_f = np.array([exact_power_two_proportions(pa_v, pb_v, int(n), test="fisher") for n in ns])
    n20_pw = exact_power_two_proportions(pa_v, pb_v, 20, test="fisher")
    nstar = int(np.ceil(sample_size_two_proportions(pa_v, pb_v)))
    nstar_pw = exact_power_two_proportions(pa_v, pb_v, nstar, test="fisher")

    ax.fill_between(ns, 0, pw_f, color=C_SAGE, alpha=0.08, zorder=1)
    ax.fill_between(ns, 0, pw_f, where=pw_f < 0.80, color=C_WINE, alpha=0.10, zorder=1)
    ax.plot(ns, pw_f, color=C_INK, lw=2.8, zorder=3, label=r"Exact Fisher: 90% vs 80% hit rate")

    ax.axhline(0.80, color=C_SAGE, ls=(0, (4, 3)), lw=1.1, label="80% power target")
    ax.axvline(20, color=C_WINE, ls=(0, (5, 2)), lw=1.2, alpha=0.85, label=rf"Folklore $n={20}$/arm")

    ax.scatter([20], [n20_pw], s=120, c=C_WINE, edgecolors="white", linewidths=1.2, zorder=5)
    ax.scatter([nstar], [nstar_pw], s=140, c=C_SAGE, marker="D", edgecolors="white", linewidths=1.2, zorder=5)

    ax.annotate(
        rf"Power $={n20_pw:.2f}$" + "\n" + rf"miss $\beta={1-n20_pw:.2f}$",
        xy=(20, n20_pw), xytext=(28, 0.22),
        fontsize=9, color=C_WINE, ha="left",
        arrowprops=dict(arrowstyle="-|>", color=C_WINE, lw=1.0),
    )
    ax.annotate(
        rf"$n^*={nstar}$/arm" + "\n" + rf"power $={nstar_pw:.2f}$",
        xy=(nstar, nstar_pw), xytext=(nstar * 0.42, 0.62),
        fontsize=9, color=C_SAGE, ha="center",
        arrowprops=dict(arrowstyle="-|>", color=C_SAGE, lw=1.0),
    )
    ax.text(
        0.03, 0.97,
        "E2 · lot equivalence at LoD concentration\n(detection claim lock before bench work)",
        transform=ax.transAxes, fontsize=9, color=C_INK, va="top", fontweight="bold",
    )
    ax.set(xscale="log", xlabel=r"Replicates per arm ($n$)", ylabel="Exact Fisher power",
           xlim=(4, 250), ylim=(0, 0.98))
    ax.legend(loc="lower right", fontsize=8, framealpha=0.98)
    finish_axis(ax)


def _plot_headline_power(ax) -> None:
    ns, _, _ = _power_curve_ns()
    curves = [
        (0.90, 0.80, C_INK, 2.2, "90 vs 80"),
        (0.90, 0.70, C_WINE, 1.5, "90 vs 70"),
        (0.95, 0.85, C_SLATE, 1.3, "95 vs 85"),
        (0.90, 0.50, C_SAGE, 1.2, "90 vs 50"),
    ]
    for pa_v, pb_v, col, lw, lab in curves:
        pw_f = np.array([exact_power_two_proportions(pa_v, pb_v, int(n), test="fisher") for n in ns])
        ax.plot(ns, pw_f, color=col, lw=lw, label=lab, zorder=3)
        n20_pw = exact_power_two_proportions(pa_v, pb_v, 20, test="fisher")
        nstar = int(np.ceil(sample_size_two_proportions(pa_v, pb_v)))
        ax.scatter([20], [n20_pw], s=22, c=col, edgecolors="white", linewidths=0.5, zorder=5)
        if pa_v == 0.90 and pb_v == 0.80:
            ax.scatter([nstar], [exact_power_two_proportions(pa_v, pb_v, nstar, test="fisher")],
                       s=32, c=col, marker="D", edgecolors="white", linewidths=0.6, zorder=5)
            ax.annotate(rf"$n^*\!={nstar}$", xy=(nstar, 0.55), xytext=(nstar * 0.55, 0.72),
                        fontsize=6, color=col, arrowprops=dict(arrowstyle="-", color=col, lw=0.6))
    ax.axhline(0.80, color=C_SAGE, ls=(0, (4, 3)), lw=0.85)
    ax.axvline(20, color=C_WINE, ls=(0, (5, 2)), lw=0.9, alpha=0.7)
    ax.set(xscale="log", xlabel=r"$n$ per arm", ylabel="Exact Fisher power", xlim=(4, 250), ylim=(0, 0.95))
    ax.legend(loc="lower right", fontsize=5.5, ncol=2, framealpha=0.98)
    finish_axis(ax)


def _plot_fisher_heatmap(ax) -> None:
    """Exact Fisher power at n=20 over full (p_A, p_B) grid."""
    pa, pb, power = _fisher_power_grid_n20()
    _plot_lattice_heatmap(
        ax, power, pa, pb,
        cmap=_HEAT_CMAP, vmin=0.0, vmax=0.85,
        cbar_label="Power",
    )
    _annotate_ref_pairs(ax, pa, pb, power)
    subtitle_chip(ax, r"Exact Fisher @ $n=20$", color=C_INK, y=1.01)


def _plot_nstar_heatmap(
    ax,
    *,
    pct_step: int = 5,
    headline_only: bool = False,
    embedded: bool = False,
    cax=None,
    show_ylabel: bool = True,
    cbar_orientation: str = "vertical",
) -> None:
    """Asymptotic n* (80% power) over integer 50–99% (p_A, p_B) grid."""
    grid = build_comparison_grid()
    pa, pb, _, _, nstar = grid_arrays(grid)
    nstar_plot = np.clip(nstar, 10, 500)
    _plot_lattice_heatmap(
        ax,
        nstar_plot,
        pa,
        pb,
        cmap=_NSTAR_CMAP,
        norm=_NSTAR_NORM,
        cbar_label=r"Required $n^*$ per arm",
        cbar_ticks=[20, 50, 100, 199, 500],
        cbar_highlight=199,
        cax=cax,
        show_ylabel=show_ylabel,
        cbar_orientation=cbar_orientation,
    )
    _annotate_ref_pairs(
        ax, pa, pb, nstar, value_is_nstar=True, headline_only=headline_only,
        compact=embedded, legend_inset=embedded,
    )
    if embedded:
        _overlay_uq_contours(ax, pa, pb, panel="n_star")
    sm = grid.get("summary") or {}
    n_capped = int(np.nansum(nstar > 500))
    cap_note = f"  ·  {n_capped} pairs $>500$" if n_capped else ""
    if not embedded:
        subtitle_chip(
            ax,
            rf"Median $n^*\!=\!{sm.get('median_n_star', 0):.0f}$ for 80% power{cap_note}",
            color=C_SAGE,
            y=1.01,
        )


def _plot_qpcr_hit_rate(ax) -> None:
    from lod_guide.data.download_real import RAW_DIR, parse_real_dataset

    path = RAW_DIR / "zenodo_mus_wt_lod_loq.csv"
    if not path.exists():
        ax.text(0.5, 0.5, "Missing qPCR data", ha="center", va="center", transform=ax.transAxes)
        ax.axis("off")
        return
    parsed = parse_real_dataset("zenodo_mus_wt_qpcr", path)
    hit_summary = parsed.get("hit_summary") or {}
    positive = sorted((sq, v) for sq, v in hit_summary.items() if sq and sq > 0)
    if not positive:
        ax.axis("off")
        return
    xs = np.array([p[0] for p in positive], float)
    ys = np.array([p[1]["rate"] for p in positive], float)
    ns = np.array([p[1]["n"] for p in positive], int)
    yerr = np.sqrt(np.clip(ys * (1 - ys) / np.maximum(ns, 1), 0, 1))
    ax.errorbar(xs, ys, yerr=yerr, fmt="none", ecolor=C_SLATE, elinewidth=0.7, capsize=2, alpha=0.55, zorder=2)
    ax.scatter(xs, ys, s=40 + 2 * ns, c=C_INK, edgecolors="white", linewidths=0.7, zorder=4)
    ax.axhline(0.95, color=C_SLATE, ls=(0, (4, 3)), lw=0.85)
    ax.set_xscale("log")
    ax.set(xlabel="SQ (copies/rxn)", ylabel="Hit rate", ylim=(-0.05, 1.05))
    ax.yaxis.set_label_coords(-0.18, 0.5)
    finish_axis(ax)


def _plot_tierA_n_ratios(ax) -> None:
    meta = _load_json("tierA_meta_analysis.json") or {}
    all_rows = meta.get("rows", [])
    with_ratio = [
        r for r in all_rows
        if r.get("guidance_n") and r.get("n_ratio_vs_folklore") and not r.get("error")
    ]
    without_ratio = [
        r for r in all_rows
        if r.get("guidance_n") and not r.get("n_ratio_vs_folklore") and not r.get("error")
    ]
    rows = sorted(with_ratio, key=lambda r: float(r["n_ratio_vs_folklore"]), reverse=True)
    rows.extend(sorted(without_ratio, key=lambda r: r.get("dataset_id", "")))
    if not rows:
        ax.axis("off")
        return

    def _label(r: dict) -> str:
        did = r.get("dataset_id", "")
        if did in TIER_A_DEPOSIT_LABELS:
            return TIER_A_DEPOSIT_LABELS[did]
        return did.replace("zenodo_", "").replace("analyseit_", "EP17 ").replace("_", " ")

    y = np.arange(len(rows))
    ratios: list[float | None] = []
    colors: list[str] = []
    for r in rows:
        ratio = r.get("n_ratio_vs_folklore")
        if ratio is not None:
            ratios.append(float(ratio))
            colors.append(C_SAGE if float(ratio) >= 1.0 else C_WINE)
        else:
            ratios.append(np.nan)
            colors.append(C_SLATE)

    xpos = [r if r is not None and np.isfinite(r) else 0.0 for r in ratios]
    ax.barh(y, xpos, height=0.52, color=colors, alpha=0.85, edgecolor="white", linewidth=0.8, zorder=3)
    ax.axvline(1.0, color=C_WINE, ls=(0, (5, 2)), lw=1.15, label=r"$n=20$")
    xmax = max((r for r in ratios if r is not None and np.isfinite(r)), default=1.0)
    for yi, r, row in zip(y, ratios, rows):
        if r is not None and np.isfinite(r):
            ax.text(r + 0.04, yi, f"{r:.1f}×", va="center", ha="left", fontsize=8.0, color=C_INK)
        else:
            gn = row.get("guidance_n")
            ax.text(0.05, yi, f"n={gn}, ratio N/A", va="center", ha="left", fontsize=7.5, color=C_SLATE)
    ax.set(yticks=y, yticklabels=[_label(r) for r in rows], xlabel=r"$n_\mathrm{guidance} / n_{20}$",
           xlim=(0, max(xmax, 1.0) * 1.32))
    ax.text(0.02, 1.02, f"Tier A: {len(rows)}/{len(all_rows)} deposits", transform=ax.transAxes,
            fontsize=8.0, color=C_INK, fontweight="bold", va="bottom")
    ax.invert_yaxis()
    ax.legend(loc="lower left", fontsize=7.5)
    finish_axis(ax, grid="x")


def _plot_decision_risk_ledger(ax) -> None:
    risk = _load_json("decision_risk.json") or {}
    scenarios = risk.get("scenarios") or []
    g2_folk = sorted(
        [s for s in scenarios if str(s.get("scenario_id", "")).startswith("E2_folklore_n20_")],
        key=lambda s: float(s["loss"]),
        reverse=True,
    )
    g2_pow = {
        str(s["scenario_id"]).replace("E2_powered_nstar_", ""): s
        for s in scenarios
        if str(s.get("scenario_id", "")).startswith("E2_powered_nstar_")
    }
    e1 = [s for s in scenarios if str(s.get("scenario_id", "")).startswith("E1_")]
    if not g2_folk:
        ax.axis("off")
        return

    def _pair_label(sid: str) -> str:
        return sid.replace("E2_folklore_n20_", "").replace("_vs_", "/")

    n_g2 = len(g2_folk)
    n_e1 = len(e1)
    y_g2 = np.arange(n_g2)
    y_e1 = np.arange(n_g2 + 0.6, n_g2 + 0.6 + n_e1) if n_e1 else np.array([])

    folk_loss = [float(s["loss"]) for s in g2_folk]
    ax.barh(y_g2, folk_loss, height=0.48, color=C_WINE, alpha=0.88, edgecolor="white", linewidth=0.7,
            label=r"$n{=}20$", zorder=3)
    pow_x, pow_y = [], []
    for s, yi in zip(g2_folk, y_g2):
        slug = str(s["scenario_id"]).replace("E2_folklore_n20_", "")
        pow_s = g2_pow.get(slug)
        if pow_s:
            pow_x.append(float(pow_s["loss"]))
            pow_y.append(yi)
    if pow_x:
        ax.scatter(pow_x, pow_y, s=36, c=C_SAGE, marker="D", edgecolors="white", linewidths=0.6,
                   label=r"powered $n^*$", zorder=5)

    if n_e1:
        ax.axhline(n_g2 - 0.35, color=C_MIST, lw=0.8, zorder=1)
        e1_labels = ["Parametric", "Nonparametric"]
        e1_colors = [C_WINE, C_SAGE]
        for i, (s, yi) in enumerate(zip(e1, y_e1)):
            col = e1_colors[i] if i < len(e1_colors) else C_SLATE
            ax.barh([yi], [float(s["loss"])], height=0.38, color=col, alpha=0.75,
                    edgecolor="white", linewidth=0.6, zorder=3)

    yticks = list(y_g2) + list(y_e1)
    ylabels = [_pair_label(str(s["scenario_id"])) for s in g2_folk]
    if n_e1:
        ylabels += e1_labels[:n_e1]
    ax.set(yticks=yticks, yticklabels=ylabels, xlabel=r"Decision risk $L$",
           xlim=(0, max(folk_loss + [float(s["loss"]) for s in e1] + pow_x) * 1.12))
    ax.invert_yaxis()
    comp = risk.get("comparisons") or {}
    med = comp.get("E2_median_folklore_over_powered")
    note = rf"median $L_{{n=20}}/L_{{n^\ast}}\approx{med:.1f}$" if med else ""
    ratio90 = comp.get("E2_loss_ratio_folklore_over_powered")
    if ratio90 and med:
        note = rf"median $L_{{n=20}}/L_{{n^\ast}}\approx{med:.1f}$ (8 pairs)"
    if note:
        ax.set_title(note, fontsize=7.5, color=C_INK, loc="center", pad=4)
    ax.legend(loc="lower right", fontsize=7.0, framealpha=0.96)
    finish_axis(ax, grid="x")


def fig1_lod_replicate_planning(out: Path | None = None) -> Path:
    """
    Main Fig 1 — single integrated figure (protocol + E2 planning lattice).

    A: decision-theoretic E2 framework (estimand θ₂ → OC design n* → concentration map g(p)).
    B: exact Fisher miss β @ n=20 for all valid (p_A, p_B) pairs.
    C: required n* for 80% power on the same lattice.
    D: logistic map c/LoD95 vs hit rate p for every integer 50%–99%.
    """
    apply_journal_rc()
    grid = build_comparison_grid()
    sm = grid.get("summary") or {}
    lattice_model = build_lattice_surface_model()
    frac = sm.get("frac_miss_gt_0.8")
    n_valid = sm.get("n_valid_cells")
    median_n = sm.get("median_n_star", 0)
    rel80 = evaluate_relative_lod_continuum(p_max_pct=99, p_min_pct=50, step_pct=1, curve=LogisticLoDCurve(slope=2.0))
    c_lod_80 = float(next(r["relative_c_lod95"] for r in rel80 if r["p_pct"] == 80))

    fig = plt.figure(figsize=(DOUBLE_COL_W, 8.35), facecolor="white")
    gs = fig.add_gridspec(
        3, 3,
        height_ratios=[0.42, 1.0, 0.085],
        width_ratios=[1.05, 1.05, 0.95],
        hspace=0.38,
        wspace=0.34,
        left=0.09,
        right=0.97,
        top=0.97,
        bottom=0.08,
    )

    ax_a = fig.add_subplot(gs[0, :])
    draw_fig1_claim_flow(
        ax_a,
        n_valid_cells=int(n_valid or lattice_model["lattice"]["n_valid_cells"]),
        frac_underpowered=float(frac or 0.0),
        median_n_star=float(median_n),
        delta_bands=list(lattice_model.get("delta_bands") or []),
    )

    ax_b = fig.add_subplot(gs[1, 0])
    ax_c = fig.add_subplot(gs[1, 1], sharey=ax_b)
    ax_d = fig.add_subplot(gs[1, 2])
    cax_b = fig.add_subplot(gs[2, 0])
    cax_c = fig.add_subplot(gs[2, 1])

    _plot_g2_miss_heatmap(
        ax_b, headline_only=False, embedded=True,
        cax=cax_b, show_ylabel=True, cbar_orientation="horizontal",
    )
    panel_label(ax_b, "B", inset=True)
    if frac is not None:
        ax_b.set_title(
            rf"Miss $\beta$ at $n=20$ ({100 * float(frac):.0f}% of cells $\beta>0.8$)",
            fontsize=8.0, color=C_INK, loc="center", pad=5, fontweight="medium",
        )

    _plot_nstar_heatmap(
        ax_c, headline_only=False, embedded=True,
        cax=cax_c, show_ylabel=False, cbar_orientation="horizontal",
    )
    panel_label(ax_c, "C", inset=True)
    ax_c.tick_params(labelleft=False)
    ax_c.set_title(
        r"Required $n^\ast(\Delta p)$ at 80% power",
        fontsize=8.0, color=C_INK, loc="center", pad=5, fontweight="medium",
    )

    _plot_lod_continuum_panel(ax_d, embedded=True)
    panel_label(ax_d, "D", inset=True)
    ax_d.set_title(
        r"$c/\mathrm{LoD}_{95}$ vs hit rate $p$",
        fontsize=8.0, color=C_INK, loc="center", pad=5, fontweight="medium",
    )
    return save_figure(
        fig,
        "Fig1_lod_replicate_planning",
        fig_dir=FIG_DIR,
        dpi=_FIG1_DPI,
        bbox_inches=None,
    )


def fig1_design_protocol(out: Path | None = None) -> Path:
    """Main Fig 1 — prospective protocol (Methods anchor)."""
    apply_journal_rc()
    fig, ax = create_single_panel_figure(height=PROTOCOL_FIG_H)
    draw_pipeline_schematic(ax, standalone=True)
    fig.tight_layout(pad=0.4)
    return save_figure(fig, "Fig1_design_protocol", fig_dir=FIG_DIR, extra_stems=("Fig1_decision_monograph",))


def fig2_g2_headline(out: Path | None = None) -> Path:
    """Main Fig 2 — E2 Box 1 operating curve (Results anchor)."""
    apply_journal_rc()
    fig, ax = create_single_panel_figure(height=FOCUS_FIG_H)
    _plot_headline_power_focused(ax)
    fig.tight_layout(pad=0.5)
    return save_figure(fig, "Fig2_g2_headline", fig_dir=FIG_DIR, extra_stems=("Fig2_empirical_calibration",))


def fig1_decision_monograph(out: Path | None = None) -> Path:
    """Supplement — legacy v5 seven-panel theory grid."""
    apply_journal_rc()
    fig, axes = create_monograph_figure()
    draw_pipeline_schematic(axes["A"])
    panel_label(axes["A"], "A")
    _plot_g1_all_positive(axes["B"])
    panel_label(axes["B"], "B")
    _plot_g2_miss_heatmap(axes["C"])
    panel_label(axes["C"], "C")
    _plot_p16_saturation(axes["D"])
    panel_label(axes["D"], "D")
    _plot_pareto_plane(axes["E"])
    panel_label(axes["E"], "E")
    _plot_headline_power(axes["F"])
    panel_label(axes["F"], "F")
    _plot_nstar_heatmap(axes["G"])
    panel_label(axes["G"], "G")
    return save_figure(fig, "Fig1_decision_monograph", fig_dir=FIG_DIR, extra_stems=("Fig1_decision_theory",))


def fig2_empirical_calibration(out: Path | None = None) -> Path:
    """Main Fig 2 — tier-A calibration triptych (qPCR / n ratios / risk ledger)."""
    evaluate_standard_scenarios()
    apply_journal_rc()
    fig = plt.figure(figsize=(DOUBLE_COL_W, 5.15), facecolor="white")
    gs = fig.add_gridspec(
        1, 3,
        width_ratios=[0.95, 1.32, 1.18],
        wspace=0.62,
        left=0.075,
        right=0.985,
        top=0.86,
        bottom=0.13,
    )
    axes = {"H": fig.add_subplot(gs[0, 0]), "I": fig.add_subplot(gs[0, 1]), "J": fig.add_subplot(gs[0, 2])}
    for ax in axes.values():
        ax._panel_offset = True  # type: ignore[attr-defined]
    _plot_qpcr_hit_rate(axes["H"])
    panel_label(axes["H"], "A")
    _plot_tierA_n_ratios(axes["I"])
    panel_label(axes["I"], "B")
    _plot_decision_risk_ledger(axes["J"])
    panel_label(axes["J"], "C")
    return save_figure(
        fig, "Fig2_tierA_calibration", fig_dir=FIG_DIR, dpi=_FIG2_DPI, bbox_inches=None,
    )


# --- Legacy aliases ---
def fig1_decision_theory(out: Path | None = None) -> Path:
    return fig1_decision_monograph(out)


def fig1_decision_map(out: Path | None = None) -> Path:
    return _legacy_fig1_map()


def fig2_g2_verdict(out: Path | None = None) -> Path:
    apply_journal_rc()
    fig, axes = create_triptych()
    _plot_headline_power(axes[0])
    _plot_pareto_plane(axes[1])
    _plot_fisher_heatmap(axes[2])
    return save_figure(fig, "Fig2_g2_verdict", fig_dir=FIG_DIR)


def fig3_qpcr_case_study(out: Path | None = None) -> Path:
    return fig2_empirical_calibration(out)


def fig5_tierA_anchor() -> Path:
    return fig2_empirical_calibration()


def _save_folklore_triptych_supplement() -> Path:
    apply_journal_rc()
    fig, axes = create_triptych()
    _plot_g1_all_positive(axes[0])
    _plot_g2_miss_scenarios(axes[1])
    _plot_p16_saturation(axes[2])
    return save_figure(fig, "FigS10_folklore_triptych", fig_dir=FIG_DIR)


def _save_fisher_heatmap_supplement() -> Path:
    apply_journal_rc()
    fig, ax = plt.subplots(figsize=(DOUBLE_COL_W * 0.55, 3.2), facecolor="white")
    _plot_fisher_heatmap(ax)
    fig.tight_layout()
    return save_figure(fig, "FigS11_fisher_heatmap_n20", fig_dir=FIG_DIR)


def figS1_g2_grid_supplement() -> Path:
    """Supplement: full E2 comparison grids at folklore n=20 (readable size)."""
    apply_journal_rc()
    fig = plt.figure(figsize=(DOUBLE_COL_W, 4.2), facecolor="white")
    gs = fig.add_gridspec(1, 3, wspace=0.38, left=0.08, right=0.98, top=0.90, bottom=0.12)
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    _plot_g2_miss_heatmap(axes[0])
    panel_label(axes[0], "A")
    _plot_fisher_heatmap(axes[1])
    panel_label(axes[1], "B")
    _plot_nstar_heatmap(axes[2])
    panel_label(axes[2], "C")
    return save_figure(fig, "FigS1_g2_comparison_grid", fig_dir=FIG_DIR)


def figS2_secondary_mechanisms() -> Path:
    """Supplement — E1 all-positive trap and E2 OC context (readable diptych)."""
    apply_journal_rc()
    fig, axes = create_diptych()
    _plot_g1_all_positive(axes[0])
    panel_label(axes[0], "A")
    _plot_headline_power(axes[1])
    panel_label(axes[1], "B")
    return save_figure(fig, "FigS2_secondary_mechanisms", fig_dir=FIG_DIR)


def generate_supplement_figures() -> list[Path]:
    """Optional legacy grids — not shipped in v7 main package."""
    return []


def generate_main_figures() -> list[Path]:
    export_comparison_grid_tables()
    export_grid_uq_tables()
    export_lattice_surface_tables()
    return [fig1_lod_replicate_planning(), fig2_empirical_calibration()]


if __name__ == "__main__":
    for p in generate_main_figures():
        print(p)
