"""Figures: concentration relative to LoD — verification pass & discrimination miss."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lod_guide.paper.figure_style import apply_journal_rc, panel_label
from lod_guide.research.concentration_relative import evaluate_concentration_grid

FIG_DIR = Path(__file__).resolve().parents[3] / "figures" / "methodology"


def _style() -> None:
    apply_journal_rc()


def fig_concentration_effects(out: Path | None = None) -> Path:
    _style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigR1_concentration_relative_effects.png"
    grid = evaluate_concentration_grid(
        relative_levels=tuple(np.round(np.logspace(np.log10(0.25), np.log10(3.0), 25), 4))
    )
    r = np.array([row["r_c_over_LoD_ref"] for row in grid["rows"]])
    pa = np.array([row["p_A"] for row in grid["rows"]])
    pb = np.array([row["p_B"] for row in grid["rows"]])
    pass_a = np.array([row["P_pass_A_rate_ge_claim"] for row in grid["rows"]])
    miss = np.array([row["compare_miss_beta"] for row in grid["rows"]])

    fig, axes = plt.subplots(1, 3, figsize=(9.2, 3.2))

    ax = axes[0]
    ax.plot(r, pa, color="#0072B2", lw=2, label="Kit A (ref LoD)")
    ax.plot(r, pb, color="#D55E00", lw=2, label="Kit B (worse LoD)")
    ax.axvline(1.0, color="#666666", ls="--", lw=1)
    ax.set_xscale("log")
    ax.set_xlabel(r"$c/\mathrm{LoD}_{95}^{\mathrm{ref}}$")
    ax.set_ylabel(r"True hit rate $p(c)$")
    panel_label(ax, "A")
    ax.legend(fontsize=7)
    ax.set_ylim(0, 1.02)

    ax = axes[1]
    ax.plot(r, pass_a, color="#009E73", lw=2)
    ax.axvline(1.0, color="#666666", ls="--", lw=1)
    ax.set_xscale("log")
    ax.set_xlabel(r"$c/\mathrm{LoD}_{95}^{\mathrm{ref}}$")
    ax.set_ylabel(r"$P(\hat{p} \geq 0.95)$ at $n=20$")
    panel_label(ax, "B")
    ax.set_ylim(0, 1.02)

    ax = axes[2]
    ax.plot(r, miss, color="#CC79A7", lw=2)
    ax.axvline(1.0, color="#666666", ls="--", lw=1)
    ax.axhline(0.2, color="#666666", ls=":", lw=0.9)
    ax.set_xscale("log")
    ax.set_xlabel(r"$c/\mathrm{LoD}_{95}^{\mathrm{ref}}$")
    ax.set_ylabel(r"Miss $\beta$ for A vs B at $n=20$")
    panel_label(ax, "C")
    ax.set_ylim(0, 1.02)

    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def generate_concentration_figures() -> list[Path]:
    return [fig_concentration_effects()]


if __name__ == "__main__":
    print(generate_concentration_figures()[0])
