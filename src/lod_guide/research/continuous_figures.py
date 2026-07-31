"""Journal figures for continuous LoD parameter-space models."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lod_guide.paper.figure_style import apply_journal_rc
from lod_guide.research.continuous_models import (
    OUT_DIR,
    build_all_continuous_models,
    query_discrimination,
)

FIG_DIR = Path(__file__).resolve().parents[3] / "figures" / "methodology"


def _style() -> None:
    apply_journal_rc()


def _ensure_fields(fine: bool = False) -> None:
    if not (OUT_DIR / "all_positive_field.npz").exists():
        build_all_continuous_models(fine=fine)


def fig_all_positive_surface(out: Path | None = None) -> Path:
    _style()
    _ensure_fields(fine=False)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigC_continuous_all_positive_surface.png"
    data = np.load(OUT_DIR / "all_positive_field.npz")
    p, n, F = data["p_grid"], data["n_grid"], data["F"]
    # show subset for clarity
    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    im = ax.imshow(
        F,
        origin="lower",
        aspect="auto",
        extent=[p.min(), p.max(), n.min(), n.max()],
        cmap="YlOrRd",
        vmin=0,
        vmax=1,
    )
    ax.set_xlabel(r"True detection probability $p$ (continuous)")
    ax.set_ylabel(r"Replicates $n$ (1,2,...,)")
    # mark example slices
    ax.axvline(0.8, color="white", ls="--", lw=0.8, alpha=0.8)
    ax.axhline(5, color="white", ls=":", lw=0.8)
    ax.axhline(10, color="white", ls=":", lw=0.8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label=r"$p^n$")
    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def fig_nstar_surface(out: Path | None = None) -> Path:
    _style()
    _ensure_fields(fine=False)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigC_continuous_nstar_surface.png"
    data = np.load(OUT_DIR / "discrimination_field.npz")
    pa, pb, ns = data["p_a_grid"], data["p_b_grid"], data["n_star"]
    fig, ax = plt.subplots(figsize=(5.6, 4.2))
    Z = np.ma.array(ns, mask=~np.isfinite(ns))
    im = ax.imshow(
        Z.T,
        origin="lower",
        aspect="auto",
        extent=[pa.min(), pa.max(), pb.min(), pb.max()],
        cmap="viridis",
        vmin=10,
        vmax=500,
    )
    ax.plot([0.05, 0.99], [0.05, 0.99], color="white", lw=0.8, ls="--")
    # example points
    for x, y, lab in [(0.9, 0.8, "90vs80"), (0.9, 0.5, "90vs50")]:
        ax.scatter([x], [y], c="red", s=28, zorder=5)
        ax.text(x + 0.01, y - 0.04, lab, color="white", fontsize=7)
    ax.set_xlabel(r"$p_A$ (continuous)")
    ax.set_ylabel(r"$p_B$ (continuous)")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label=r"$n^\star$ (capped)")
    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def fig_concentration_continuum(out: Path | None = None) -> Path:
    _style()
    _ensure_fields(fine=False)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "FigC_continuous_concentration_r.png"
    data = np.load(OUT_DIR / "concentration_field.npz")
    r, miss, passa = data["r"], data["miss"], data["pass_A"]
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    ax.plot(r, passa, color="#009E73", lw=2, label=r"$P(\hat{p}\geq 0.95)$ kit A")
    ax.plot(r, miss, color="#CC79A7", lw=2, label=r"Miss $\beta$ A vs B ($n=20$)")
    ax.axvline(1.0, color="#666666", ls="--", lw=1)
    ax.set_xscale("log")
    ax.set_xlabel(r"$r=c/\mathrm{LoD}_{95}$ on $(0,\infty)$ (log grid)")
    ax.set_ylabel("Probability")
    ax.set_ylim(0, 1.02)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out


def generate_continuous_model_figures(*, fine_build: bool = False) -> list[Path]:
    build_all_continuous_models(fine=fine_build)
    return [
        fig_all_positive_surface(),
        fig_nstar_surface(),
        fig_concentration_continuum(),
    ]


if __name__ == "__main__":
    for p in generate_continuous_model_figures(fine_build=True):
        print(p)
        # print example queries
    print("query 90vs80@20", query_discrimination(0.9, 0.8, 20))
    print("query 90vs50@20", query_discrimination(0.9, 0.5, 20))
