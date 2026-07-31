"""
English journal-style figures for the guidance algorithm (methodology figures).

No in-figure titles/suptitles — captions live in paper_artifacts/captions/.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lod_guide.paper.figure_style import apply_journal_rc, panel_label
from lod_guide.s5_sample_size import power_two_proportions, sample_size_two_proportions
from lod_guide.s7_sensitivity import sensitivity_compare_reagents

FIG_DIR = Path(__file__).resolve().parents[2] / "figures" / "methodology"


def _style() -> None:
    apply_journal_rc()


def fig_decision_overview(out: Path | None = None) -> Path:
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigM1_decision_overview.png"
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.axis("off")
    steps = [
        "S0 Goal",
        "S1 Type",
        "S2 Diagnostics",
        "S3 Correction",
        "S4a/S4b Model",
        "S5 Sample size",
        "S6 Report",
        "S7 Sensitivity",
    ]
    x = np.linspace(0.06, 0.94, len(steps))
    for i, (xi, lab) in enumerate(zip(x, steps)):
        ax.add_patch(
            plt.Rectangle(
                (xi - 0.05, 0.4),
                0.1,
                0.25,
                fill=True,
                facecolor="#4C72B0",
                alpha=0.85,
                transform=ax.transAxes,
            )
        )
        ax.text(
            xi,
            0.525,
            lab,
            ha="center",
            va="center",
            color="white",
            fontsize=7,
            transform=ax.transAxes,
            wrap=True,
        )
        if i < len(steps) - 1:
            ax.annotate(
                "",
                xy=(x[i + 1] - 0.05, 0.525),
                xytext=(xi + 0.05, 0.525),
                xycoords=ax.transAxes,
                textcoords=ax.transAxes,
                arrowprops=dict(arrowstyle="->", color="#333333", lw=1),
            )
    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def fig_power_delta(out: Path | None = None) -> Path:
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigM2_power_vs_n_by_delta.png"
    fig, ax = plt.subplots(figsize=(4.8, 3.4))
    n = np.arange(10, 301)
    p_a = 0.90
    for d, color in zip([0.05, 0.10, 0.15, 0.20], ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]):
        p_b = p_a - d
        pw = [power_two_proportions(p_a, p_b, int(ni)) for ni in n]
        n80 = sample_size_two_proportions(p_a, p_b)
        ax.plot(n, pw, color=color, lw=1.8, label=rf"$\Delta={d:.2f}$ ($n_{{80\%}}\approx{int(np.ceil(n80))}$)")
    ax.axhline(0.8, color="#666666", ls="--", lw=1)
    ax.axvline(20, color="#E69F00", ls=":", lw=1)
    ax.set_xlabel("Replicates per reagent ($n$)")
    ax.set_ylabel("Power")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def fig_sensitivity_icc(out: Path | None = None) -> Path:
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigM3_sensitivity_icc.png"
    sens = sensitivity_compare_reagents()
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))
    ax = axes[0]
    deltas = [r["delta"] for r in sens["by_delta"]]
    ns = [r["n_80"] for r in sens["by_delta"]]
    p20 = [r["power_n20"] for r in sens["by_delta"]]
    ax.bar([str(d) for d in deltas], ns, color="#0072B2")
    ax.set_xlabel(r"$\Delta = p_A - p_B$")
    ax.set_ylabel(r"Required $n$ (80% power)")
    panel_label(ax, "A")

    ax = axes[1]
    ax.bar([str(d) for d in deltas], p20, color="#D55E00")
    ax.axhline(0.8, color="#666666", ls="--", lw=1)
    ax.set_xlabel(r"$\Delta = p_A - p_B$")
    ax.set_ylabel("Power at folklore $n=20$")
    ax.set_ylim(0, 1)
    panel_label(ax, "B")

    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def generate_all_methodology_figures() -> list[Path]:
    return [fig_decision_overview(), fig_power_delta(), fig_sensitivity_icc()]


def fig_challenge_folklore_vs_algorithm(out: Path | None = None) -> Path:
    """English figure: folklore n=20 power vs algorithm-required n."""
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigC1_challenge_folklore_vs_algorithm.png"
    scenarios = [
        ("90% vs 80%", 0.90, 0.80),
        ("95% vs 85%", 0.95, 0.85),
        ("90% vs 70%", 0.90, 0.70),
        ("50% vs 40%", 0.50, 0.40),
    ]
    labels = [s[0] for s in scenarios]
    n_req = [int(np.ceil(sample_size_two_proportions(a, b))) for _, a, b in scenarios]
    p20 = [power_two_proportions(a, b, 20) for _, a, b in scenarios]

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
    ax = axes[0]
    ax.bar(labels, n_req, color="#0072B2")
    ax.axhline(20, color="#E69F00", ls="--", lw=1.5, label="Folklore $n=20$")
    ax.set_ylabel("Required $n$ per arm (80% power)")
    ax.tick_params(axis="x", rotation=15)
    ax.legend(fontsize=7)
    panel_label(ax, "A")

    ax = axes[1]
    ax.bar(labels, p20, color="#D55E00")
    ax.axhline(0.8, color="#666666", ls="--", lw=1, label="Target power 80%")
    ax.set_ylabel("Power if laboratories use $n=20$")
    ax.set_ylim(0, 1.05)
    ax.tick_params(axis="x", rotation=15)
    ax.legend(fontsize=7)
    panel_label(ax, "B")

    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def fig_diverse_data_map(out: Path | None = None) -> Path:
    """Map of real + simulated diversity used by the guidance algorithm."""
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigC2_diverse_data_landscape.png"
    rows = [
        ("Real qPCR Cq (Zenodo)", "continuous", "real"),
        ("Normal blanks", "continuous", "sim"),
        ("Skewed + hetero blanks", "continuous", "sim"),
        ("Censored floor", "continuous", "sim"),
        ("Bimodal weak+", "continuous", "sim"),
        ("Reagents 90 vs 80", "binary", "sim"),
        ("Low p=0.10 LoD", "binary", "sim"),
        ("Poisson day mixture", "count", "sim"),
        ("ABO multiclass", "multiclass", "sim"),
    ]
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    type_y = {"continuous": 3, "binary": 2, "count": 1, "multiclass": 0}
    for i, (name, rtype, src) in enumerate(rows):
        y = type_y[rtype]
        x = i
        color = "#009E73" if src == "real" else "#56B4E9"
        ax.scatter([x], [y], s=120, c=color, zorder=3)
        ax.text(x, y + 0.18, name, ha="center", va="bottom", fontsize=6.5, rotation=25)
    ax.set_yticks(list(type_y.values()))
    ax.set_yticklabels(list(type_y.keys()))
    ax.set_xticks([])
    ax.set_xlim(-0.5, len(rows) - 0.5)
    ax.set_ylim(-0.5, 3.8)
    from matplotlib.patches import Patch

    ax.legend(
        handles=[Patch(color="#009E73", label="Real (public)"), Patch(color="#56B4E9", label="Simulated")],
        loc="upper right",
        fontsize=8,
    )
    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def generate_challenge_figures() -> list[Path]:
    return [fig_challenge_folklore_vs_algorithm(), fig_diverse_data_map()]


if __name__ == "__main__":
    paths = generate_all_methodology_figures() + generate_challenge_figures()
    for p in paths:
        print(p)
