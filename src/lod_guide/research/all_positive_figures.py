"""Journal figures for the all-positive / small-n trap."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lod_guide.paper.figure_style import apply_journal_rc, panel_label
from lod_guide.research.all_positive_trap import (
    exact_lower_bound_after_all_success,
    prob_all_positive,
    probability_true_p_below_claim_given_all_positive_uniform,
)

FIG_DIR = Path(__file__).resolve().parents[3] / "figures" / "methodology"


def _style() -> None:
    apply_journal_rc()


def fig_p_to_the_n(out: Path | None = None) -> Path:
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigT1_all_positive_probability.png"
    p = np.linspace(0.5, 1.0, 400)
    fig, ax = plt.subplots(figsize=(5.0, 3.6))
    for n, color in zip((5, 10, 20, 60), ["#D55E00", "#E69F00", "#0072B2", "#009E73"]):
        ax.plot(p, p**n, color=color, lw=2, label=rf"$n={n}$: $P=p^{{{n}}}$")
    ax.axhline(0.5, color="#666666", ls=":", lw=0.8)
    ax.axvline(0.8, color="#666666", ls=":", lw=0.8)
    ax.scatter([0.8], [0.8**5], color="#D55E00", zorder=5)
    ax.annotate(
        rf"$p=0.8,n=5$: ${(0.8**5):.2f}$",
        xy=(0.8, 0.8**5),
        xytext=(0.55, 0.55),
        fontsize=8,
        arrowprops=dict(arrowstyle="->", lw=0.8),
    )
    ax.set_xlabel(r"True single-trial detection probability $p$")
    ax.set_ylabel(r"$P(\text{all }n\text{ positive})=p^n$")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_ylim(0, 1.02)
    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def fig_lower_bounds_and_bayes(out: Path | None = None) -> Path:
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigT2_after_nn_inference.png"
    ns = np.array([5, 10, 15, 20, 30, 40, 60])
    alpha = 0.05
    claim = 0.95
    cp_low = np.array(
        [exact_lower_bound_after_all_success(int(n), alpha, two_sided=False) for n in ns]
    )
    cp_low2 = np.array(
        [exact_lower_bound_after_all_success(int(n), alpha, two_sided=True) for n in ns]
    )
    bayes = np.array(
        [
            probability_true_p_below_claim_given_all_positive_uniform(int(n), claim)[
                "P_true_p_below_claim_given_all_positive"
            ]
            for n in ns
        ]
    )

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.3))
    ax = axes[0]
    ax.plot(ns, cp_low, "o-", color="#0072B2", lw=2, label=r"One-sided $0.05^{1/n}$")
    ax.plot(ns, cp_low2, "s--", color="#56B4E9", lw=1.5, label=r"Two-sided CP $(0.025)^{1/n}$")
    ax.axhline(claim, color="#D55E00", ls="--", lw=1.2, label=r"Claim $p_0=0.95$")
    ax.set_xlabel(r"Replicates $n$ after observing $n/n$ positives")
    ax.set_ylabel(r"Lower bound for $p$")
    panel_label(ax, "A")
    ax.legend(fontsize=7)
    ax.annotate(f"n=5: {cp_low[0]:.2f}", xy=(5, cp_low[0]), xytext=(12, 0.45), fontsize=7)

    ax = axes[1]
    ax.plot(ns, bayes, "s-", color="#CC79A7", lw=2)
    ax.set_xlabel(r"Replicates $n$ after $n/n$ positives")
    ax.set_ylabel(r"$P(p < 0.95 \mid X=n)$ under Uniform prior")
    panel_label(ax, "B")
    ax.set_ylim(0, 1.02)
    for n, y in ((5, bayes[0]), (10, bayes[1])):
        ax.annotate(f"n={n}: {y:.2f}", xy=(n, y), xytext=(n + 4, y + 0.05), fontsize=7)

    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def fig_heatmap_all_positive(out: Path | None = None) -> Path:
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigT3_all_positive_heatmap.png"
    ns = np.array([3, 5, 8, 10, 15, 20, 30])
    ps = np.array([0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.99])
    mat = np.array([[prob_all_positive(float(p), int(n)) for n in ns] for p in ps])

    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    im = ax.imshow(mat, aspect="auto", origin="lower", cmap="YlOrRd", vmin=0, vmax=1)
    ax.set_xticks(range(len(ns)))
    ax.set_xticklabels([str(n) for n in ns])
    ax.set_yticks(range(len(ps)))
    ax.set_yticklabels([f"{p:.2f}" for p in ps])
    ax.set_xlabel(r"Study size $n$")
    ax.set_ylabel(r"True $p$")
    for i in range(len(ps)):
        for j in range(len(ns)):
            ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center", fontsize=6.5)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label=r"$p^n$")
    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def generate_all_positive_trap_figures() -> list[Path]:
    return [fig_p_to_the_n(), fig_lower_bounds_and_bayes(), fig_heatmap_all_positive()]


if __name__ == "__main__":
    for p in generate_all_positive_trap_figures():
        print(p)
