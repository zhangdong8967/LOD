"""
Why n=5 LoD replicates is an unreasonable design — one clear figure.

Panel A: exact outcome distribution at true LoD95 (only 5 replicates).
Panel B: operating characteristic — n=5 passes too often when performance is poor,
         and still fails often when performance is truly at LoD95.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy.stats import binom

from lod_guide.paper.figure_style import (
    C_INK,
    C_MIST,
    C_SAGE,
    C_SLATE,
    C_WINE,
    DOUBLE_COL_W,
    apply_journal_rc,
    panel_label,
    save_figure,
)

FIG_DIR = Path(__file__).resolve().parents[3] / "figures" / "methodology"
OUT_NAME = "Fig_n5_unreasonable_lod_design"

P_LOD95 = 0.95
N_SMALL = 5
N_REF = 20


def _pass_prob(p: float | np.ndarray, n: int, k: int) -> float | np.ndarray:
    return 1.0 - binom.cdf(k - 1, n, p)


def fig_n5_unreasonable_design() -> Path:
    apply_journal_rc()
    plt.rcParams["font.sans-serif"] = [
        "PingFang SC",
        "Heiti SC",
        "Arial Unicode MS",
        "Helvetica Neue",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    xs = np.arange(N_SMALL + 1)
    pmf5 = binom.pmf(xs, N_SMALL, P_LOD95)
    p_pass_5 = float(pmf5[-1])
    p_fail_5 = 1.0 - p_pass_5
    p_at_most_4 = float(1.0 - pmf5[-1])

    ps = np.linspace(0.55, 1.0, 300)
    oc5 = _pass_prob(ps, N_SMALL, N_SMALL)          # rule: 5/5
    oc20 = _pass_prob(ps, N_REF, N_REF - 1)         # rule: 19/20

    p80_pass5 = float(_pass_prob(0.80, N_SMALL, N_SMALL))
    p80_pass20 = float(_pass_prob(0.80, N_REF, N_REF - 1))

    fig = plt.figure(figsize=(DOUBLE_COL_W, 4.15), facecolor="white")
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1.0], hspace=0.42, wspace=0.28)

    # --- Panel A: outcome distribution at true LoD95 ---
    ax_a = fig.add_subplot(gs[0, 0])
    colors = [C_WINE if x < N_SMALL else C_SAGE for x in xs]
    bars = ax_a.bar(xs, pmf5, color=colors, edgecolor="white", linewidth=1.0, width=0.72, zorder=3)
    ax_a.axvline(N_SMALL - 0.5, color=C_INK, ls="--", lw=1.0, alpha=0.55, zorder=2)
    ax_a.text(N_SMALL - 0.48, 0.86, "通过线\n(5/5)", fontsize=7, color=C_INK, ha="left", va="top")

    for bar, prob in zip(bars, pmf5):
        if prob < 0.02:
            continue
        ax_a.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.015,
            f"{prob:.0%}",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="medium",
            color=C_INK,
        )

    ax_a.set_xticks(xs)
    ax_a.set_xticklabels([f"{x}/5" for x in xs], fontsize=8)
    ax_a.set_xlabel("一次验证中阳性次数", fontsize=9)
    ax_a.set_ylabel("出现概率", fontsize=9)
    ax_a.set_ylim(0, 0.92)
    ax_a.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    panel_label(ax_a, "A")
    ax_a.set_title(
        f"真实 LoD₉₅ 浓度下，只做 5 次重复：\n"
        f"仅 {p_pass_5:.0%} 全阳，{p_at_most_4:.0%} 达不到 5/5",
        fontsize=9,
        pad=8,
    )

    fail_patch = mpatches.Patch(color=C_WINE, label=f"未全阳（{p_at_most_4:.0%}）")
    pass_patch = mpatches.Patch(color=C_SAGE, label=f"5/5 全阳（{p_pass_5:.0%}）")
    ax_a.legend(handles=[fail_patch, pass_patch], loc="upper left", fontsize=7, framealpha=0.95)

    # --- Panel B: n=5 vs n=20 outcome spread at true LoD95 ---
    ax_b = fig.add_subplot(gs[0, 1])
    xs20 = np.arange(14, N_REF + 1)
    pmf20 = binom.pmf(xs20, N_REF, P_LOD95)
    colors20 = [C_WINE if x < N_REF - 1 else C_SAGE for x in xs20]
    ax_b.bar(xs20 - 14, pmf20, color=colors20, edgecolor="white", linewidth=1.0, width=0.82, zorder=3)
    ax_b.axvline((N_REF - 1) - 14 - 0.5, color=C_INK, ls="--", lw=1.0, alpha=0.55, zorder=2)
    ax_b.text((N_REF - 1) - 14 - 0.45, 0.86, "通过线\n(≥19/20)", fontsize=7, color=C_INK, ha="left", va="top")

    for x, prob in zip(xs20, pmf20):
        if prob < 0.04:
            continue
        ax_b.text(
            x - 14,
            prob + 0.015,
            f"{prob:.0%}",
            ha="center",
            va="bottom",
            fontsize=7.5,
            fontweight="medium",
            color=C_INK,
        )

    ax_b.set_xticks(xs20 - 14)
    ax_b.set_xticklabels([f"{x}/20" for x in xs20], fontsize=7, rotation=35, ha="right")
    ax_b.set_xlabel("一次验证中阳性次数", fontsize=9)
    ax_b.set_ylabel("出现概率", fontsize=9)
    ax_b.set_ylim(0, 0.92)
    ax_b.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    panel_label(ax_b, "B")
    ax_b.set_title(
        f"同样真实 LoD₉₅，重复 20 次：\n"
        f"结果集中在 18–20/20（更稳定）",
        fontsize=9,
        pad=8,
    )

    # --- Panel C (bottom, full width): discrimination / false pass ---
    ax_c = fig.add_subplot(gs[1, :])
    ax_c.fill_between(ps, oc5, oc20, where=(oc5 > oc20), color=C_WINE, alpha=0.10, zorder=1)
    ax_c.plot(ps, oc5, color=C_WINE, lw=2.4, label=f"n = 5（要求 5/5 全阳）", zorder=4)
    ax_c.plot(ps, oc20, color=C_SAGE, lw=2.4, label=f"n = 20（要求 ≥19/20）", zorder=4)
    ax_c.axvline(P_LOD95, color=C_SLATE, ls=":", lw=1.1, alpha=0.9, zorder=2)
    ax_c.text(0.952, 0.08, "真实\nLoD₉₅", fontsize=7, color=C_SLATE, ha="left")

    ax_c.scatter([0.80], [p80_pass5], s=48, color=C_WINE, zorder=6, edgecolors="white", linewidths=0.8)
    ax_c.scatter([0.80], [p80_pass20], s=48, color=C_SAGE, zorder=6, edgecolors="white", linewidths=0.8)
    ax_c.annotate(
        f"真实检出率仅 80% 时：\n"
        f"n=5 仍有 {p80_pass5:.0%} 概率“全阳通过”\n"
        f"n=20 仅 {p80_pass20:.0%}",
        xy=(0.80, p80_pass5),
        xytext=(0.62, 0.72),
        fontsize=8,
        color=C_INK,
        arrowprops=dict(arrowstyle="->", color=C_WINE, lw=1.0),
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=C_MIST, alpha=0.98),
    )

    ax_c.annotate(
        f"真实 LoD₉₅ 时：\n"
        f"n=5 有 {p_fail_5:.0%} 概率\n"
        f"因未全阳而失败",
        xy=(P_LOD95, p_pass_5),
        xytext=(0.88, 0.42),
        fontsize=8,
        color=C_INK,
        arrowprops=dict(arrowstyle="->", color=C_SAGE, lw=1.0),
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=C_MIST, alpha=0.98),
    )

    ax_c.set_xlim(0.55, 1.0)
    ax_c.set_ylim(0, 1.02)
    ax_c.set_xlabel("真实单次检出概率（浓度越低，该值越小）", fontsize=9)
    ax_c.set_ylabel("一次验证被判“通过”的概率", fontsize=9)
    ax_c.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax_c.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    panel_label(ax_c, "C")
    ax_c.legend(loc="lower right", fontsize=8, framealpha=0.95)
    ax_c.set_title(
        "n = 5 的致命缺陷：性能不足时容易误判为通过，性能达标时却又容易误判为失败",
        fontsize=9.5,
        pad=8,
    )

    fig.suptitle(
        "LoD 验证只做 5 次重复不合理：样本太少，结果随机性大，无法可靠判定",
        fontsize=11,
        fontweight="semibold",
        y=1.01,
        color=C_INK,
    )

    save_figure(fig, OUT_NAME, fig_dir=FIG_DIR)
    plt.close(fig)
    return FIG_DIR / f"{OUT_NAME}.png"


if __name__ == "__main__":
    path = fig_n5_unreasonable_design()
    print(path)
    print(path.with_suffix(".pdf"))
