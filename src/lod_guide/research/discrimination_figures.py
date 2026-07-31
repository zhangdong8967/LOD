"""Figures for reagent discrimination evaluation (continuous 99→50% + vignettes)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lod_guide.paper.figure_style import apply_journal_rc, panel_label
from lod_guide.research.reagent_discrimination import (
    LogisticLoDCurve,
    miss_probability,
    run_continuous_discrimination_study,
)
from lod_guide.s5_sample_size import sample_size_two_proportions

FIG_DIR = Path(__file__).resolve().parents[3] / "figures" / "methodology"


def _style() -> None:
    apply_journal_rc()


def fig_miss_prob_curves(out: Path | None = None) -> Path:
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigD1_miss_probability_beta.png"
    n = np.arange(5, 251)
    pairs = [
        (0.90, 0.80, "#D55E00", "90% vs 80%"),
        (0.90, 0.50, "#0072B2", "90% vs 50%"),
        (0.95, 0.80, "#009E73", "95% vs 80%"),
    ]
    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    for pa, pb, color, lab in pairs:
        beta = [miss_probability(pa, pb, int(ni)) for ni in n]
        n80 = int(np.ceil(sample_size_two_proportions(pa, pb)))
        ax.plot(n, beta, color=color, lw=2, label=rf"{lab} ($n_{{80\%}}={n80}$)")
        ax.axvline(n80, color=color, ls=":", lw=0.9, alpha=0.7)
    ax.axhline(0.20, color="#666666", ls="--", lw=1, label=r"Target $\beta=0.20$")
    ax.axvline(20, color="#E69F00", ls="--", lw=1.2, label="Folklore $n=20$")
    ax.set_xlabel("Replicates per reagent ($n$)")
    ax.set_ylabel(r"Miss probability $\beta=1-\mathrm{power}$")
    ax.set_ylim(0, 1.02)
    ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def fig_n_star_continuous(out: Path | None = None, *, study: dict | None = None) -> Path:
    """
    FigD2: continuous discrimination on integer percent rates 99→50.

    A — n*(80% power) vs competitor hit-rate % for reference rates 99/95/90%.
    B — miss β at folklore n=20 on the same grid.
    C — relative concentration c/LoD_95 for every integer % from 50→99.
    """
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigD2_nstar_and_relative_lod.png"
    study = study or run_continuous_discrimination_study()

    colors = {"99pct": "#0072B2", "95pct": "#009E73", "90pct": "#D55E00"}
    labels = {"99pct": r"ref $p=99\%$", "95pct": r"ref $p=95\%$", "90pct": r"ref $p=90\%$"}

    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.5))

    # Panel A: n*
    ax = axes[0]
    for key, color in colors.items():
        ser = study["series"][key]
        x = np.asarray(ser["p_competitor_pct"], dtype=float)
        y = np.asarray(ser["n_star_80"], dtype=float)
        # plot ascending in p for readability
        order = np.argsort(x)
        ax.plot(x[order], y[order], color=color, lw=1.8, label=labels[key])
    ax.axhline(20, color="#E69F00", ls="--", lw=1.2, label=r"Folklore $n=20$")
    ax.set_yscale("log")
    ax.set_xlabel(r"Competitor hit rate $p$ (%)")
    ax.set_ylabel(r"Required $n$ per arm (80% power)")
    ax.set_xlim(50, 99)
    ax.legend(fontsize=6.5, loc="upper right")
    panel_label(ax, "A")
    # Mark classic vignette 90 vs 80
    ax.scatter([80], [study["headline"]["n_star_90_vs_80"]], color="#D55E00", s=28, zorder=5, edgecolors="k", lw=0.4)

    # Panel B: miss @ 20
    ax = axes[1]
    for key, color in colors.items():
        ser = study["series"][key]
        x = np.asarray(ser["p_competitor_pct"], dtype=float)
        y = np.asarray(ser["miss_prob_at_n20"], dtype=float)
        order = np.argsort(x)
        ax.plot(x[order], y[order], color=color, lw=1.8, label=labels[key])
    ax.axhline(0.20, color="#666666", ls="--", lw=1.0, label=r"Target $\beta=0.20$")
    ax.set_xlabel(r"Competitor hit rate $p$ (%)")
    ax.set_ylabel(r"Miss probability at folklore $n=20$")
    ax.set_xlim(50, 99)
    ax.set_ylim(0, 1.02)
    ax.legend(fontsize=6.5, loc="lower left")
    panel_label(ax, "B")
    if study["headline"].get("miss20_90_vs_80") is not None:
        ax.scatter(
            [80],
            [study["headline"]["miss20_90_vs_80"]],
            color="#D55E00",
            s=28,
            zorder=5,
            edgecolors="k",
            lw=0.4,
        )

    # Panel C: relative LoD continuum
    ax = axes[2]
    rel = study["relative_lod_continuum"]
    xp = np.array([r["p_pct"] for r in rel], dtype=float)
    yp = np.array([r["relative_c_lod95"] for r in rel], dtype=float)
    ax.plot(xp, yp, color="#0072B2", lw=2.0)
    ax.axhline(1.0, color="#666666", ls="--", lw=0.9)
    ax.axvline(95, color="#666666", ls=":", lw=0.9)
    for mark, col in [(50, "#D55E00"), (80, "#E69F00"), (90, "#009E73"), (95, "#000000"), (99, "#56B4E9")]:
        i = int(np.where(xp == mark)[0][0])
        ax.scatter([mark], [yp[i]], color=col, s=32, zorder=5)
    ax.set_yscale("log")
    ax.set_xlabel(r"Hit rate $p$ (%)")
    ax.set_ylabel(r"$c/\mathrm{LoD}_{95}$ (logistic map)")
    ax.set_xlim(50, 99)
    panel_label(ax, "C")

    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


# Back-compat alias used by older callers
def fig_n_star_bars(out: Path | None = None) -> Path:
    return fig_n_star_continuous(out=out)


def fig_relative_lod_map(out: Path | None = None) -> Path:
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigD3_relative_concentration_vs_p.png"
    curve = LogisticLoDCurve(slope=2.0, gamma_lod=0.95)
    # Dense continuum matching 50–99% study grid, plus smooth log curve
    p_pct = np.arange(50, 100, dtype=float)
    p = p_pct / 100.0
    rel = np.array([curve.lod_multiplier_for_p(float(pi)) for pi in p])
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.plot(p_pct, rel, color="#0072B2", lw=2, label=r"logistic $p\leftrightarrow c/\mathrm{LoD}_{95}$")
    ax.axhline(1.0, color="#666666", ls="--", lw=0.9)
    ax.axvline(95, color="#666666", ls="--", lw=0.9)
    marks = [50, 80, 90, 95, 99]
    for m, col in zip(marks, ["#D55E00", "#E69F00", "#009E73", "#000000", "#56B4E9"]):
        rc = curve.lod_multiplier_for_p(m / 100.0)
        ax.scatter([m], [rc], color=col, zorder=5, s=40)
        ax.annotate(
            rf"${m}\%$",
            xy=(m, rc),
            xytext=(m + 0.5, rc * (1.15 if m < 95 else 0.75)),
            fontsize=7,
            color=col,
        )
    ax.set_yscale("log")
    ax.set_xlabel(r"Single-trial detection probability $p$ (%)")
    ax.set_ylabel(r"Concentration relative to $\mathrm{LoD}_{95}$")
    ax.set_xlim(50, 99)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def generate_discrimination_figures() -> list[Path]:
    continuous = run_continuous_discrimination_study()
    return [
        fig_miss_prob_curves(),
        fig_n_star_continuous(study=continuous),
        fig_relative_lod_map(),
    ]


if __name__ == "__main__":
    for p in generate_discrimination_figures():
        print(p)
