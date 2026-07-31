"""
Journal-grade LOD discrimination analysis (English figures).

Core question: if reagent A has true LoD detection rate p_A and reagent B
has p_B (e.g. 0.90 vs 0.80), how many independent replicates are required
to detect this difference with adequate statistical power?

Theory
------
Each reagent is assayed n times at a fixed concentration near LoD.
Let X_i ~ Binomial(n, p_i),  hat{p}_i = X_i / n,  i in {A, B}.

Two-sided two-proportion z-test (pooled variance under H0):
    z = (hat{p}_A - hat{p}_B)
        / sqrt( hat{p}(1-hat{p}) (1/n_A + 1/n_B) )
    hat{p} = (X_A + X_B) / (n_A + n_B)

Approximate sample size per arm for power 1-beta at level alpha
(Fleiss / Chow formula for equal n):

    n = [ z_{1-alpha/2} * sqrt(2 * p_bar * (1-p_bar))
        + z_{1-beta}   * sqrt(p_A*(1-p_A) + p_B*(1-p_B)) ]^2
        / (p_A - p_B)^2

    where p_bar = (p_A + p_B) / 2

Critical insight: the "at least one success" metric P = 1-(1-p)^n
saturates near 1 for both p=0.8 and p=0.9 when n is large, and therefore
CANNOT discriminate reagents. Discrimination requires comparing observed
positive rates hat{p}, not the complementary "ever detected" event.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from scipy import stats
from scipy.stats import binom, norm

# ---------------------------------------------------------------------------
# Paths & journal style
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
FIG_DIR = ROOT / "figures" / "journal"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def apply_journal_style() -> None:
    """Nature / Cell-like typography for English figures."""
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 9,
            "axes.labelsize": 10,
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "legend.frameon": False,
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.05,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "mathtext.fontset": "dejavusans",
        }
    )


# Colorblind-safe palette (Okabe–Ito inspired)
C_A = "#0072B2"  # blue
C_B = "#D55E00"  # vermillion
C_C = "#009E73"  # bluish green
C_D = "#CC79A7"  # reddish purple
C_E = "#E69F00"  # orange
C_GRAY = "#666666"


# ---------------------------------------------------------------------------
# Analytical formulae
# ---------------------------------------------------------------------------

def z_crit(alpha: float, two_sided: bool = True) -> float:
    if two_sided:
        return float(norm.ppf(1 - alpha / 2))
    return float(norm.ppf(1 - alpha))


def sample_size_two_proportions(
    p_a: float,
    p_b: float,
    alpha: float = 0.05,
    power: float = 0.80,
    two_sided: bool = True,
) -> float:
    """
    Equal-arm sample size (continuous) for two-proportion z-test.

    n = [z_{1-a/2} sqrt(2 p_bar (1-p_bar))
       + z_{1-b}   sqrt(p_a(1-p_a)+p_b(1-p_b))]^2 / (p_a-p_b)^2
    """
    if abs(p_a - p_b) < 1e-12:
        return float("inf")
    za = z_crit(alpha, two_sided)
    zb = float(norm.ppf(power))
    p_bar = 0.5 * (p_a + p_b)
    num = za * np.sqrt(2 * p_bar * (1 - p_bar)) + zb * np.sqrt(
        p_a * (1 - p_a) + p_b * (1 - p_b)
    )
    return float((num / (p_a - p_b)) ** 2)


def power_two_proportions(
    p_a: float,
    p_b: float,
    n: int,
    alpha: float = 0.05,
    two_sided: bool = True,
    n_b: int | None = None,
) -> float:
    """
    Approximate power of two-proportion z-test with equal (or unequal) n.
    Uses non-centrality under H1 with unpooled SE.
    """
    if n_b is None:
        n_b = n
    n_a = n
    if abs(p_a - p_b) < 1e-12:
        return float(alpha if two_sided else alpha)  # under H0 ~ alpha

    # Critical value under H0 (pooled)
    p_bar = (n_a * p_a + n_b * p_b) / (n_a + n_b)  # for SE under H1 we use true
    # Use classic formula: reject if |diff| > z_a * se0, power via se1
    se0 = np.sqrt(p_bar * (1 - p_bar) * (1 / n_a + 1 / n_b))
    se1 = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    delta = abs(p_a - p_b)
    za = z_crit(alpha, two_sided)
    # Continuity-free normal approximation
    if two_sided:
        # Power = Phi(-za + delta/se1) + Phi(-za - delta/se1) ≈ Phi(-za + delta/se1)
        # More accurately using H0 critical threshold:
        # reject if |hat_diff| > za * se0  (approx)
        # E[hat_diff]=delta, Var=se1^2
        crit = za * se0
        power = float(norm.sf(crit, loc=delta, scale=se1) + norm.cdf(-crit, loc=delta, scale=se1))
    else:
        crit = za * se0
        power = float(norm.sf(crit, loc=delta, scale=se1))
    return float(np.clip(power, 0.0, 1.0))


def exact_power_fisher_or_binom(
    p_a: float,
    p_b: float,
    n: int,
    alpha: float = 0.05,
    n_sims: int = 50_000,
    seed: int = 42,
) -> float:
    """
    Monte Carlo power of two-sided Fisher's exact test (exact for small n).
    """
    rng = np.random.default_rng(seed)
    xa = rng.binomial(n, p_a, size=n_sims)
    xb = rng.binomial(n, p_b, size=n_sims)
    # Use chi-square / z-test on each replicate for speed; Fisher is slow at 50k
    # Pooled z two-sided
    p_pool = (xa + xb) / (2 * n)
    se = np.sqrt(np.maximum(p_pool * (1 - p_pool) * (2 / n), 1e-16))
    z = (xa / n - xb / n) / se
    # when se==0 (both all 0 or all 1), treat as non-significant
    se_ok = se > 1e-12
    pvals = 2 * norm.sf(np.abs(z))
    pvals = np.where(se_ok, pvals, 1.0)
    return float(np.mean(pvals < alpha))


def overlapping_coefficient(p_a: float, p_b: float, n: int) -> float:
    """
    Overlap coefficient (OVL) of two Binomial(n,p)/n sampling distributions
    of hat{p}. High overlap => hard to discriminate.
    OVL = sum_k min( P(X_A=k), P(X_B=k) )
    """
    ks = np.arange(0, n + 1)
    pa = binom.pmf(ks, n, p_a)
    pb = binom.pmf(ks, n, p_b)
    return float(np.minimum(pa, pb).sum())


def at_least_one_prob(p: float, n: int) -> float:
    return 1.0 - (1.0 - p) ** n


def discrimination_summary(
    p_a: float = 0.90,
    p_b: float = 0.80,
    alpha: float = 0.05,
    power_target: float = 0.80,
) -> dict:
    n_req = sample_size_two_proportions(p_a, p_b, alpha, power_target)
    n_ceil = int(np.ceil(n_req))
    rows = []
    for n in [10, 20, 30, 50, 100, 150, 200, n_ceil]:
        rows.append(
            {
                "n": n,
                "power_approx": power_two_proportions(p_a, p_b, n, alpha),
                "power_mc": exact_power_fisher_or_binom(p_a, p_b, n, alpha, n_sims=20_000),
                "ovl": overlapping_coefficient(p_a, p_b, n),
                "P_at_least_A": at_least_one_prob(p_a, n),
                "P_at_least_B": at_least_one_prob(p_b, n),
                "delta_at_least": abs(at_least_one_prob(p_a, n) - at_least_one_prob(p_b, n)),
            }
        )
    return {
        "p_a": p_a,
        "p_b": p_b,
        "delta": abs(p_a - p_b),
        "alpha": alpha,
        "power_target": power_target,
        "n_required_continuous": n_req,
        "n_required_ceil": n_ceil,
        "grid": rows,
    }


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def fig1_sampling_distributions(p_a=0.90, p_b=0.80, ns=(20, 50, 100, 200)):
    """Distribution of hat{p} for two reagents at increasing n."""
    apply_journal_style()
    fig, axes = plt.subplots(1, len(ns), figsize=(7.2, 2.4), sharey=True)
    for ax, n in zip(axes, ns):
        ks = np.arange(0, n + 1)
        rates = ks / n
        pa = binom.pmf(ks, n, p_a)
        pb = binom.pmf(ks, n, p_b)
        width = 0.8 / n if n > 1 else 0.4
        ax.bar(rates, pa, width=width, color=C_A, alpha=0.55, label=f"$p_A={p_a:.2f}$", align="center")
        ax.bar(rates, pb, width=width, color=C_B, alpha=0.55, label=f"$p_B={p_b:.2f}$", align="center")
        ovl = overlapping_coefficient(p_a, p_b, n)
        ax.axvline(p_a, color=C_A, ls="--", lw=0.9)
        ax.axvline(p_b, color=C_B, ls="--", lw=0.9)
        ax.set_xlim(max(0, min(p_a, p_b) - 0.35), min(1, max(p_a, p_b) + 0.35))
        ax.set_xlabel(r"Observed rate $\hat{p}$")
        ax.set_title(f"$n={n}$\nOVL={ovl:.2f}")
        if ax is axes[0]:
            ax.set_ylabel("Probability mass")
            ax.legend(loc="upper left", fontsize=7)
    fig.suptitle(
        "Sampling distributions of observed LoD detection rates",
        y=1.08,
        fontsize=11,
        fontweight="bold",
    )
    fig.tight_layout()
    path = FIG_DIR / "Fig1_sampling_distributions.pdf"
    fig.savefig(path)
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    return path


def fig2_power_vs_n(p_pairs=None, alpha=0.05):
    """Power curves for several reagent pairs."""
    apply_journal_style()
    if p_pairs is None:
        p_pairs = [
            (0.90, 0.80, C_A),
            (0.95, 0.85, C_C),
            (0.90, 0.70, C_B),
            (0.50, 0.40, C_D),
        ]
    n_grid = np.arange(5, 301)
    fig, ax = plt.subplots(figsize=(4.5, 3.4))
    for p_a, p_b, color in p_pairs:
        powers = [power_two_proportions(p_a, p_b, int(n), alpha) for n in n_grid]
        n80 = sample_size_two_proportions(p_a, p_b, alpha, 0.80)
        ax.plot(
            n_grid,
            powers,
            color=color,
            lw=1.8,
            label=rf"$p_A={p_a:.2f},\; p_B={p_b:.2f}$ ($n_{{80\%}}\approx{int(np.ceil(n80))}$)",
        )
        ax.axvline(n80, color=color, ls=":", lw=0.9, alpha=0.7)
    ax.axhline(0.80, color=C_GRAY, ls="--", lw=1)
    ax.axhline(0.90, color=C_GRAY, ls=":", lw=0.8)
    ax.text(305, 0.80, "80% power", va="center", fontsize=7, color=C_GRAY)
    ax.set_xlabel("Replicates per reagent ($n$)")
    ax.set_ylabel("Statistical power ($1-\\beta$)")
    ax.set_title("Power to discriminate two LoD detection rates")
    ax.set_xlim(0, 300)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower right", fontsize=7)
    fig.tight_layout()
    path = FIG_DIR / "Fig2_power_curves.pdf"
    fig.savefig(path)
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    return path


def fig3_saturation_trap(p_a=0.90, p_b=0.80):
    """
    Show that 'at least one success' saturates and fails to discriminate,
    whereas hat{p} retains the gap.
    """
    apply_journal_style()
    n = np.arange(1, 61)
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))

    ax = axes[0]
    ax.plot(n, 1 - (1 - p_a) ** n, color=C_A, lw=2, label=rf"$p={p_a:.2f}$")
    ax.plot(n, 1 - (1 - p_b) ** n, color=C_B, lw=2, label=rf"$p={p_b:.2f}$")
    ax.fill_between(n, 1 - (1 - p_a) ** n, 1 - (1 - p_b) ** n, color=C_GRAY, alpha=0.15)
    ax.set_xlabel("Replicates $n$")
    ax.set_ylabel(r"$P(\geq 1\ \mathrm{positive})=1-(1-p)^n$")
    ax.set_title("A. 'At least once' saturates\n(gap collapses)")
    ax.legend()
    ax.set_ylim(0.5, 1.01)

    ax = axes[1]
    # Expected hat{p} is constant; SE shrinks
    se_a = np.sqrt(p_a * (1 - p_a) / n)
    se_b = np.sqrt(p_b * (1 - p_b) / n)
    ax.plot(n, np.full_like(n, p_a, dtype=float), color=C_A, lw=2, label=rf"$E[\hat{{p}}_A]={p_a:.2f}$")
    ax.plot(n, np.full_like(n, p_b, dtype=float), color=C_B, lw=2, label=rf"$E[\hat{{p}}_B]={p_b:.2f}$")
    ax.fill_between(n, p_a - 1.96 * se_a, p_a + 1.96 * se_a, color=C_A, alpha=0.2)
    ax.fill_between(n, p_b - 1.96 * se_b, p_b + 1.96 * se_b, color=C_B, alpha=0.2)
    ax.set_xlabel("Replicates $n$")
    ax.set_ylabel(r"Observed positive rate $\hat{p}$")
    ax.set_title("B. Observed rate retains gap\n(95% CI shrinks with $n$)")
    ax.legend(loc="center right")
    ax.set_ylim(0.55, 1.05)

    fig.suptitle(
        "Why metric choice determines whether reagent differences are detectable",
        y=1.05,
        fontsize=11,
        fontweight="bold",
    )
    fig.tight_layout()
    path = FIG_DIR / "Fig3_saturation_vs_rate.pdf"
    fig.savefig(path)
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    return path


def fig4_sample_size_heatmap(
    p_a_grid=None,
    deltas=None,
    alpha=0.05,
    power=0.80,
):
    """Heatmap of required n for (p_A, delta=p_A-p_B)."""
    apply_journal_style()
    if p_a_grid is None:
        p_a_grid = np.linspace(0.55, 0.95, 41)
    if deltas is None:
        deltas = np.array([0.05, 0.10, 0.15, 0.20, 0.25])

    # Matrix: rows = delta, cols = p_A
    mat = np.full((len(deltas), len(p_a_grid)), np.nan)
    for i, d in enumerate(deltas):
        for j, pa in enumerate(p_a_grid):
            pb = pa - d
            if 0.01 < pb < 0.99:
                mat[i, j] = sample_size_two_proportions(pa, pb, alpha, power)

    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    im = ax.imshow(
        mat,
        aspect="auto",
        origin="lower",
        extent=[p_a_grid[0], p_a_grid[-1], deltas[0] - 0.025, deltas[-1] + 0.025],
        cmap="YlOrRd",
        vmin=20,
        vmax=400,
    )
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(rf"Required $n$ per arm ($\alpha={alpha}$, power={power:.0%})")
    # Annotate common case
    ax.scatter([0.90], [0.10], s=40, c="white", edgecolors="black", zorder=5)
    ax.annotate(
        r"$p_A=0.90,\ \Delta=0.10$",
        xy=(0.90, 0.10),
        xytext=(0.72, 0.22),
        fontsize=7,
        arrowprops=dict(arrowstyle="->", lw=0.8, color="black"),
        color="black",
    )
    ax.set_xlabel(r"Higher-performing reagent rate $p_A$")
    ax.set_ylabel(r"Difference $\Delta = p_A - p_B$")
    ax.set_title("Sample size to discriminate two reagents near LoD")
    ax.set_yticks(deltas)
    fig.tight_layout()
    path = FIG_DIR / "Fig4_sample_size_heatmap.pdf"
    fig.savefig(path)
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    return path


def fig5_operating_characteristics(p_a=0.90, p_b=0.80, alpha=0.05):
    """Multi-panel OC: power, OVL, CI width, required n annotation."""
    apply_journal_style()
    n_grid = np.arange(5, 251)
    powers = np.array([power_two_proportions(p_a, p_b, int(n), alpha) for n in n_grid])
    ovls = np.array([overlapping_coefficient(p_a, p_b, int(n)) for n in n_grid])
    ci_half = 1.96 * np.sqrt(0.5 * (p_a + p_b) * (1 - 0.5 * (p_a + p_b)) / n_grid)
    n80 = sample_size_two_proportions(p_a, p_b, alpha, 0.80)
    n90 = sample_size_two_proportions(p_a, p_b, alpha, 0.90)

    fig = plt.figure(figsize=(7.2, 5.0))
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.32)

    ax = fig.add_subplot(gs[0, 0])
    ax.plot(n_grid, powers, color=C_A, lw=2)
    ax.axhline(0.8, color=C_GRAY, ls="--", lw=0.9)
    ax.axvline(n80, color=C_B, ls=":", lw=1)
    ax.axvline(20, color=C_E, ls=":", lw=1)
    ax.text(20, 0.15, "n=20", rotation=90, va="bottom", ha="right", fontsize=7, color=C_E)
    ax.text(n80, 0.82, f"$n_{{80\\%}}={int(np.ceil(n80))}$", fontsize=7, color=C_B)
    ax.set_xlabel("$n$ per reagent")
    ax.set_ylabel("Power")
    ax.set_title("A. Power vs replicates")
    ax.set_ylim(0, 1.02)

    ax = fig.add_subplot(gs[0, 1])
    ax.plot(n_grid, ovls, color=C_D, lw=2)
    ax.axvline(20, color=C_E, ls=":", lw=1)
    ax.axvline(n80, color=C_B, ls=":", lw=1)
    ax.set_xlabel("$n$ per reagent")
    ax.set_ylabel("Overlap coefficient (OVL)")
    ax.set_title("B. Distributional overlap")
    ax.set_ylim(0, 1.02)

    ax = fig.add_subplot(gs[1, 0])
    ax.plot(n_grid, 2 * ci_half, color=C_C, lw=2)
    ax.axhline(abs(p_a - p_b), color=C_GRAY, ls="--", lw=0.9, label=r"$\Delta=p_A-p_B$")
    ax.axvline(20, color=C_E, ls=":", lw=1)
    ax.set_xlabel("$n$ per reagent")
    ax.set_ylabel("Approx. 95% CI width of $\\hat{p}$")
    ax.set_title("C. Precision of rate estimate")
    ax.legend(fontsize=7)

    ax = fig.add_subplot(gs[1, 1])
    # Contour-like bar: power at fixed ns of practical interest
    ns_show = [10, 20, 30, 50, 100, 150, int(np.ceil(n80)), int(np.ceil(n90))]
    ns_show = sorted(set(ns_show))
    pows = [power_two_proportions(p_a, p_b, n, alpha) for n in ns_show]
    colors = [C_E if n == 20 else (C_B if abs(n - n80) < 2 else C_A) for n in ns_show]
    bars = ax.bar([str(n) for n in ns_show], pows, color=colors, edgecolor="white")
    ax.axhline(0.8, color=C_GRAY, ls="--", lw=0.9)
    for bar, p in zip(bars, pows):
        ax.text(bar.get_x() + bar.get_width() / 2, p + 0.02, f"{p:.0%}", ha="center", fontsize=6.5)
    ax.set_xlabel("$n$ per reagent")
    ax.set_ylabel("Power")
    ax.set_title(rf"D. Power snapshot ($p_A={p_a}, p_B={p_b}$)")
    ax.set_ylim(0, 1.15)

    fig.suptitle(
        "Operating characteristics for discriminating LoD performance",
        fontsize=11,
        fontweight="bold",
        y=0.98,
    )
    path = FIG_DIR / "Fig5_operating_characteristics.pdf"
    fig.savefig(path)
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    return path


def fig6_missed_difference_illustration(p_a=0.90, p_b=0.80, n_small=20, n_large=None, seed=7):
    """Simulate many LoD validation campaigns; show how often difference is missed."""
    apply_journal_style()
    if n_large is None:
        n_large = int(np.ceil(sample_size_two_proportions(p_a, p_b, 0.05, 0.80)))

    n_campaigns = 2000

    def simulate(n, seed_offset):
        rng = np.random.default_rng(seed + seed_offset)
        xa = rng.binomial(n, p_a, size=n_campaigns)
        xb = rng.binomial(n, p_b, size=n_campaigns)
        diffs = xa / n - xb / n
        p_pool = (xa + xb) / (2 * n)
        se = np.sqrt(np.maximum(p_pool * (1 - p_pool) * (2 / n), 1e-16))
        z = np.where(se > 1e-12, diffs / se, 0.0)
        pvals = 2 * norm.sf(np.abs(z))
        sig = (pvals < 0.05) & (se > 1e-12)
        return diffs, sig

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0), sharey=True)
    for ax, n, offset, title in [
        (axes[0], n_small, 0, f"A. Underpowered ($n={n_small}$)"),
        (axes[1], n_large, 1, f"B. Adequately powered ($n={n_large}$)"),
    ]:
        diffs, sig = simulate(n, offset)
        ax.hist(diffs[~sig], bins=30, color=C_GRAY, alpha=0.55, label="Not significant", density=True)
        ax.hist(diffs[sig], bins=30, color=C_C, alpha=0.75, label="Significant ($p<0.05$)", density=True)
        ax.axvline(p_a - p_b, color="black", ls="--", lw=1.2, label=rf"True $\Delta={p_a-p_b:.2f}$")
        ax.axvline(0, color=C_B, ls=":", lw=1)
        ax.set_title(f"{title}\nEmpirical power = {sig.mean():.0%}")
        ax.set_xlabel(r"$\hat{p}_A - \hat{p}_B$")
        if ax is axes[0]:
            ax.set_ylabel("Density")
            ax.legend(fontsize=7, loc="upper left")
    fig.suptitle(
        "Monte Carlo: insufficient replicates miss true LoD differences",
        fontsize=11,
        fontweight="bold",
        y=1.05,
    )
    fig.tight_layout()
    path = FIG_DIR / "Fig6_missed_difference_MC.pdf"
    fig.savefig(path)
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    return path


def fig7_formula_panel():
    """Compact visual of the key formulae (for SI / methods aesthetics)."""
    apply_journal_style()
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.axis("off")
    lines = [
        (r"$\mathbf{Model}$", 0.92),
        (r"$X_i \sim \mathrm{Binomial}(n, p_i),\ \hat{p}_i = X_i / n,\ i \in \{A, B\}$", 0.82),
        (r"$\mathbf{Pooled\ z\ test}$", 0.68),
        (r"$z = (\hat{p}_A - \hat{p}_B)\ /\ \sqrt{\hat{p}(1-\hat{p})(1/n_A + 1/n_B)}$", 0.58),
        (r"$\mathbf{Equal\text{-}arm\ sample\ size}$", 0.44),
        (r"$n = [z_{1-\alpha/2}\sqrt{2\bar{p}(1-\bar{p})} + z_{1-\beta}\sqrt{p_A(1-p_A)+p_B(1-p_B)}]^2 / (p_A-p_B)^2$", 0.34),
        (r"$\mathbf{Overlap\ coefficient}$", 0.20),
        (r"$\mathrm{OVL} = \sum_{k=0}^{n} \min(P(X_A=k),\ P(X_B=k))$", 0.10),
    ]
    for text, y in lines:
        ax.text(0.03, y, text, transform=ax.transAxes, va="center", ha="left", fontsize=10)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Key formulae for LoD reagent discrimination", fontweight="bold", loc="left", pad=10)
    # subtle box
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color("#CCCCCC")
        spine.set_linewidth(0.8)
    path = FIG_DIR / "Fig7_key_formulae.pdf"
    fig.savefig(path)
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def print_table(summary: dict) -> None:
    print("\n" + "=" * 78)
    print("LoD REAGENT DISCRIMINATION — SAMPLE SIZE & POWER")
    print("=" * 78)
    print(f"  p_A = {summary['p_a']:.2f},  p_B = {summary['p_b']:.2f},  "
          f"Δ = {summary['delta']:.2f}")
    print(f"  α = {summary['alpha']},  target power = {summary['power_target']:.0%}")
    print(f"  Required n (continuous) ≈ {summary['n_required_continuous']:.1f}")
    print(f"  Required n (ceil)       = {summary['n_required_ceil']}")
    print("-" * 78)
    print(f"{'n':>6} {'Power≈':>8} {'Power MC':>10} {'OVL':>8} "
          f"{'P≥1(A)':>10} {'P≥1(B)':>10} {'Δ(≥1)':>10}")
    print("-" * 78)
    for r in summary["grid"]:
        print(
            f"{r['n']:6d} {r['power_approx']:8.3f} {r['power_mc']:10.3f} {r['ovl']:8.3f} "
            f"{r['P_at_least_A']:10.6f} {r['P_at_least_B']:10.6f} {r['delta_at_least']:10.6f}"
        )
    print("=" * 78)
    print(
        "NOTE: With the 'at least one positive' metric, Δ collapses toward 0 as n grows;\n"
        "      discrimination must use observed positive rates hat{p}, not 1-(1-p)^n."
    )
    print("=" * 78 + "\n")


def main():
    apply_journal_style()
    summary = discrimination_summary(0.90, 0.80, alpha=0.05, power_target=0.80)
    print_table(summary)

    print("Generating journal figures (PDF + PNG @ 300 dpi)...")
    paths = [
        fig1_sampling_distributions(),
        fig2_power_vs_n(),
        fig3_saturation_trap(),
        fig4_sample_size_heatmap(),
        fig5_operating_characteristics(),
        fig6_missed_difference_illustration(),
        fig7_formula_panel(),
    ]
    print(f"Saved {len(paths)} figures to: {FIG_DIR}")
    for p in paths:
        print(f"  - {p.name} (+ .png)")


if __name__ == "__main__":
    main()
