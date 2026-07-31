"""Journal-polished figures for paper_artifacts (composite panels, consistent style).

No in-figure titles/suptitles — captions live in the manuscript.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lod_guide.data.download_real import RAW_DIR, parse_real_dataset
from lod_guide.paper.figure_style import (
    DOUBLE_COL_W,
    GRID_COLOR,
    JOURNAL_BLUE,
    JOURNAL_GRAY,
    JOURNAL_GREEN,
    JOURNAL_ORANGE,
    JOURNAL_PURPLE,
    apply_journal_rc,
    create_panel_figure,
    panel_label,
    reference_line,
    save_figure,
    shade_between,
    style_data_axis,
    styled_bar,
)
from lod_guide.research.all_positive_trap import exact_lower_bound_after_all_success
from lod_guide.research.precision_profile import PoolPrecision, evaluate_precision_profile

ROOT = Path(__file__).resolve().parents[3]
FIG_DIR = ROOT / "figures" / "methodology"
PAPER_FIG = ROOT / "paper_artifacts" / "figures"


def _style() -> None:
    apply_journal_rc()


def fig4_all_positive_composite(out: Path | None = None) -> Path:
    """Supplement Fig S4: all-positive trap (probability + inference after n/n)."""
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_FIG.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "Fig4_all_positive_composite.png"

    fig, axes = create_panel_figure(2, height=2.75)
    ns = np.arange(1, 41, dtype=float)

    ax = axes[0]
    style_data_axis(ax)
    for p, c in [(0.95, JOURNAL_BLUE), (0.80, JOURNAL_ORANGE), (0.50, JOURNAL_GREEN)]:
        y = p**ns
        ax.plot(ns, y, color=c, lw=1.8, label=rf"$p={p:.2f}$")
        shade_between(ax, ns, y, 0, color=c, alpha=0.06)
    reference_line(ax, 5, axis="x", ls=":", color=JOURNAL_GRAY)
    reference_line(ax, 10, axis="x", ls="--", color=JOURNAL_GRAY)
    reference_line(ax, 20, axis="x", color=JOURNAL_ORANGE, label=r"$n=20$")
    ax.set_xlabel(r"Replicates $n$")
    ax.set_ylabel(r"$P(X=n)=p^n$")
    ax.legend(frameon=True, fontsize=6.5)
    ax.set_ylim(0, 1.02)
    panel_label(ax, "A")

    ax = axes[1]
    style_data_axis(ax)
    n_show = np.array([5, 10, 20, 30, 40])
    L = np.array([exact_lower_bound_after_all_success(int(n), 0.05, two_sided=False) for n in n_show])
    B = np.array([float(0.95 ** (int(n) + 1)) for n in n_show])
    x = np.arange(len(n_show))
    w = 0.36
    ax.bar(x - w / 2, L, width=w, color=JOURNAL_BLUE, label=r"CP lower ($\alpha=0.05$)", edgecolor="white", linewidth=0.8)
    ax.bar(x + w / 2, B, width=w, color=JOURNAL_PURPLE, label=r"$P(p<0.95\mid n/n)$", edgecolor="white", linewidth=0.8)
    reference_line(ax, 0.95, label=r"$p_0=0.95$")
    ax.set_xticks(x, [str(n) for n in n_show])
    ax.set_xlabel(r"$n$ after observing $n/n$")
    ax.set_ylabel("Probability / bound")
    ax.legend(frameon=True, loc="lower right", fontsize=6.5)
    ax.set_ylim(0, 1.05)
    panel_label(ax, "B")

    save_figure(fig, "Fig4_all_positive_composite", fig_dir=FIG_DIR)
    plt.close(fig)
    return out


def _radioimmuno_pools() -> list[PoolPrecision] | None:
    path = RAW_DIR / "Precision_radioimmuno.txt"
    if not path.exists():
        return None
    parsed = parse_real_dataset("zenodo_radioimmuno_precision", path)
    pools = []
    for r in parsed.get("pool_rows") or []:
        mean = float(r["mean"])
        sd = float(r["sd"])
        cv = float(r["cv_pct"]) if np.isfinite(r.get("cv_pct", float("nan"))) else (
            100.0 * sd / mean if mean else float("nan")
        )
        pools.append(PoolPrecision(str(r["sample_name"]), 3, mean, sd, cv, "radioimmuno"))
    return pools or None


def fig_loq_precision_profile_tierA(out: Path | None = None) -> Path:
    """Primary LoQ figure: tier-A radioimmuno precision profile."""
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_FIG.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigL_radioimmuno_loq_profile.png"

    pools = _radioimmuno_pools()
    if pools is None:
        # fallback empty marker file note via evaluate on empty → skip draw
        fig, ax = plt.subplots(figsize=(5.2, 3.6))
        ax.text(0.5, 0.5, "Radioimmuno precision file missing", ha="center", va="center")
        ax.axis("off")
        fig.savefig(out)
        fig.savefig(PAPER_FIG / "Fig8_loq_radioimmuno_tierA.png")
        plt.close(fig)
        return out

    res = evaluate_precision_profile(pools, target_cv_pct=20.0, evidence_tier="A")
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    pts = sorted([p for p in res.pools if p.mean > 0 and np.isfinite(p.cv_pct)], key=lambda p: p.mean)
    ax.plot([p.mean for p in pts], [p.cv_pct for p in pts], "o-", color="#0072B2", ms=3, lw=1.2)
    ax.axhline(20.0, color="#666666", ls="--", lw=1, label="Target CV 20%")
    if res.loq_estimate is not None:
        ax.axvline(res.loq_estimate, color="#009E73", ls=":", lw=1.5, label=rf"LoQ@20%≈{res.loq_estimate:.3g}")
    ax.set_xscale("log")
    ax.set_xlabel("Pool mean (DPM, log scale)")
    ax.set_ylabel("CV (%)")
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    fig.savefig(PAPER_FIG / "Fig8_loq_radioimmuno_tierA.png")
    fig.savefig(PAPER_FIG / "Fig8_loq_radioimmuno_tierA.pdf")
    plt.close(fig)
    return out


def fig_loq_precision_profile(out: Path | None = None) -> Path:
    """Supplemental LoQ figure: tier-C troponin EP17 demo (engine consistency only)."""
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_FIG.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigL1_loq_precision_profile.png"

    res = evaluate_precision_profile(target_cv_pct=20.0)
    sheets = sorted({p.stratum for p in res.pools})
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    colors = ["#0072B2", "#D55E00"]
    for sheet, col in zip(sheets[:2], colors):
        pts = [p for p in res.pools if p.stratum == sheet and p.mean > 0]
        pts = sorted(pts, key=lambda p: p.mean)
        ax.plot(
            [p.mean for p in pts],
            [p.cv_pct for p in pts],
            "o-",
            color=col,
            ms=4,
            lw=1.5,
            label=sheet,
        )
    ax.axhline(20.0, color="#666666", ls="--", lw=1, label="Target CV 20%")
    if res.loq_estimate is not None:
        ax.axvline(res.loq_estimate, color="#009E73", ls=":", lw=1.5, label=rf"LoQ@20%≈{res.loq_estimate:.3g}")
    ax.set_xscale("log")
    ax.set_xlabel("Pool mean concentration (log scale)")
    ax.set_ylabel("CV (%)")
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    fig.savefig(PAPER_FIG / "FigS1_loq_troponin_tierC_demo.png")
    fig.savefig(PAPER_FIG / "FigS1_loq_troponin_tierC_demo.pdf")
    # keep legacy name for older copies
    fig.savefig(PAPER_FIG / "FigS1_loq_precision_profile.png")
    fig.savefig(PAPER_FIG / "FigS1_loq_precision_profile.pdf")
    plt.close(fig)
    return out


def generate_journal_figures() -> list[Path]:
    from lod_guide.research.design_se_figures import fig9_design_se_comparison

    return [
        fig4_all_positive_composite(),
        fig_loq_precision_profile_tierA(),
        fig_loq_precision_profile(),
        fig9_design_se_comparison(),
    ]


if __name__ == "__main__":
    for p in generate_journal_figures():
        print(p)
