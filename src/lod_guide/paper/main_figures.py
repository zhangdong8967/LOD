"""
Main-text figures Fig 1–5 — v4: TikZ Fig1, power heatmap Fig3, Tier-A grid Fig5.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from lod_guide.paper.figure_style import (
    C_ACCENT,
    C_GOLD,
    C_LIGHT,
    C_NEUTRAL,
    C_PRIMARY,
    C_SECONDARY,
    C_WARN,
    DOUBLE_COL_W,
    apply_journal_rc,
    binomial_se,
    create_grid,
    create_triptych,
    finish_axis,
    panel_label,
    save_figure,
)
from lod_guide.paper.flowchart_fig1 import render_fig1_decision_map
from lod_guide.research.all_positive_trap import exact_lower_bound_after_all_success
from lod_guide.research.reagent_discrimination import run_continuous_discrimination_study
from lod_guide.s5_sample_size import power_two_proportions, sample_size_two_proportions
from lod_guide.theory.exact_tests import exact_power_two_proportions
from lod_guide.theory.selective.sample_split import monte_carlo_compare_split_vs_unsplit

ROOT = Path(__file__).resolve().parents[3]
FIG_DIR = ROOT / "figures" / "methodology"
PAPER_FIG = ROOT / "paper_artifacts" / "figures"
DATA = ROOT / "data" / "research"

_TIERA_LABELS = {
    "zenodo_mus_wt_qpcr": "qPCR WT",
    "zenodo_mus_multiplex_qpcr": "qPCR mpx",
    "analyseit_ep17_probit": "EP17 probit",
    "analyseit_ep17_estradiol": "EP17 estradiol",
    "mendeley_carobene_lombardy_eqa": "Carobene EQA",
    "bioc_msstats_lobd_cptac": "CPTAC MS",
    "zenodo_radioimmuno_precision": "Radioimmuno",
    "zenodo_radioimmuno_linearity": "Radioimmuno lin.",
    "zenodo_rmn_qualification": "RMN ID50",
}

# Tier-A rows emphasized for LoD replicate planning (hit-rate / detection), not LoB/LoQ demos.
_LOD_FOCUS_FAMILIES = frozenset(
    {
        "qpcr_cq_continuous",
        "probit_hit_rate",
        "rmn_microneutralization_continuous",
    }
)


def _lod_focus_rows(rows: list[dict]) -> list[dict]:
    return [
        r
        for r in rows
        if not r.get("error")
        and (
            r.get("result_family") in _LOD_FOCUS_FAMILIES
            or "qpcr" in str(r.get("dataset_id", ""))
            or "probit" in str(r.get("dataset_id", ""))
        )
    ]


def _plot_qpcr_hit_rate(ax) -> None:
    """Tier-A qPCR: detection hit rate vs standard concentration (LoD-relevant)."""
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
    ax.errorbar(xs, ys, yerr=yerr, fmt="none", ecolor=C_NEUTRAL, elinewidth=0.7, capsize=2, alpha=0.55, zorder=2)
    ax.scatter(xs, ys, s=28 + 2 * ns, c=C_PRIMARY, edgecolors="white", linewidths=0.7, zorder=4)
    ax.axhline(0.95, color=C_NEUTRAL, ls=(0, (4, 3)), lw=0.9, label="95% detection")
    ax.set_xscale("log")
    ax.set(xlabel="Standard concentration (SQ, copies)", ylabel="Hit rate at concentration", ylim=(-0.05, 1.05))
    ax.legend(loc="lower right", fontsize=6.5)
    finish_axis(ax)


def _plot_lod_planning_n_bars(ax) -> None:
    """Headline replicate counts for G1 / G2 / G4 LoD claims."""
    from lod_guide.s4_models import detect_prob_at_least_k
    from lod_guide.s5_sample_size import sample_size_one_proportion, sample_size_two_proportions

    labels = ["G1\n95% LoD", "G2\n90 vs 80%", "G4\n19/20 rule"]
    n_g1 = int(np.ceil(sample_size_one_proportion(0.98, 0.95, power=0.80)))
    n_g2 = int(np.ceil(sample_size_two_proportions(0.90, 0.80, power=0.80)))
    n_g4 = 20
    for n_try in range(20, 500):
        if detect_prob_at_least_k(0.95, n_try, 19) >= 0.80:
            n_g4 = n_try
            break
    vals = [n_g1, n_g2, n_g4]
    cols = [C_PRIMARY, C_WARN, C_ACCENT]
    x = np.arange(3)
    ax.bar(x, vals, color=cols, width=0.55, edgecolor="white", linewidth=0.8, zorder=3)
    ax.axhline(20, color=C_GOLD, ls=(0, (5, 2)), lw=1.1, label=r"Folklore $n{=}20$")
    for xi, v in zip(x, vals):
        ax.text(xi, v + 4, str(v), ha="center", va="bottom", fontsize=7.5, fontweight="medium")
    ax.set_xticks(x, labels, fontsize=7)
    ax.set(ylabel=r"Planned replicates ($n$ or $n$ per arm)", ylim=(0, max(vals) * 1.15))
    ax.legend(loc="upper right", fontsize=6.5)
    finish_axis(ax)


def _tierA_rows() -> list[dict]:
    meta = _load_json("tierA_meta_analysis.json") or {}
    return [r for r in meta.get("rows", []) if not r.get("error")]


def _plot_radioimmuno_loq(ax) -> None:
    from lod_guide.data.download_real import RAW_DIR, parse_real_dataset
    from lod_guide.research.precision_profile import PoolPrecision, evaluate_precision_profile

    path = RAW_DIR / "Precision_radioimmuno.txt"
    if not path.exists():
        ax.text(0.5, 0.5, "Missing precision data", ha="center", va="center", transform=ax.transAxes)
        ax.axis("off")
        return
    parsed = parse_real_dataset("zenodo_radioimmuno_precision", path)
    pools = [
        PoolPrecision(str(r["sample_name"]), 3, float(r["mean"]), float(r["sd"]),
                      float(r.get("cv_pct", 100 * float(r["sd"]) / float(r["mean"]))), "radioimmuno")
        for r in parsed.get("pool_rows") or []
    ]
    res = evaluate_precision_profile(pools, target_cv_pct=20.0, evidence_tier="A")
    pts = sorted([p for p in res.pools if p.mean > 0 and np.isfinite(p.cv_pct)], key=lambda p: p.mean)
    xm = np.array([p.mean for p in pts])
    ym = np.array([p.cv_pct for p in pts])
    yerr = ym / np.sqrt(2)
    ax.errorbar(xm, ym, yerr=yerr, fmt="none", ecolor=C_NEUTRAL, elinewidth=0.7, capsize=1.8, alpha=0.5, zorder=2)
    ax.scatter(xm, ym, s=22, c="white", edgecolors=C_PRIMARY, linewidths=1.0, zorder=4)
    if xm.size >= 4:
        xg = np.geomspace(xm.min(), xm.max(), 60)
        ax.plot(xg, np.interp(np.log10(xg), np.log10(xm), ym), color=C_PRIMARY, lw=1.8, alpha=0.45, zorder=1)
    ax.axhline(20, color=C_NEUTRAL, ls=(0, (4, 3)), lw=0.9)
    if res.loq_estimate is not None:
        loq = float(res.loq_estimate)
        ax.axvline(loq, color=C_ACCENT, ls=(0, (3, 2)), lw=1.1)
        ax.scatter([loq], [20], s=90, c=C_ACCENT, marker="*", edgecolors="white", linewidths=0.6, zorder=6)
    ax.set_xscale("log")
    ax.set(xlabel="Mean (DPM)", ylabel="CV (%)", ylim=(0, max(ym.max() * 1.1, 22)))
    finish_axis(ax)


def _load_json(name: str) -> dict | None:
    p = DATA / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _fisher_power_grid_n20() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Precomputed exact-Fisher power grid at n=20 (cached for fast figure rebuild)."""
    cache_path = DATA / "fig3_fisher_power_heatmap_n20.json"
    pa_grid = np.linspace(0.78, 0.96, 19)
    pb_grid = np.linspace(0.52, 0.88, 19)
    spec = {"pa_grid": pa_grid.tolist(), "pb_grid": pb_grid.tolist(), "n_per_arm": 20}
    if cache_path.exists():
        loaded = json.loads(cache_path.read_text(encoding="utf-8"))
        if loaded.get("pa_grid") == spec["pa_grid"] and loaded.get("pb_grid") == spec["pb_grid"]:
            z = np.array(
                [[np.nan if v is None else float(v) for v in row] for row in loaded["z"]],
                dtype=float,
            )
            return pa_grid, pb_grid, z
    z = np.full((pa_grid.size, pb_grid.size), np.nan)
    for i, pa in enumerate(pa_grid):
        for j, pb in enumerate(pb_grid):
            if pa > pb + 0.015:
                z[i, j] = exact_power_two_proportions(float(pa), float(pb), 20, test="fisher")
    DATA.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps({**spec, "z": np.where(np.isnan(z), None, z).tolist()}, indent=2), encoding="utf-8")
    return pa_grid, pb_grid, z


def _plot_exact_power_remedy(ax) -> None:
    """Panel B: exact Fisher power at folklore n vs powered n (90% vs 80%)."""
    p_a, p_b = 0.90, 0.80
    n_folk, n_pow = 20, int(np.ceil(sample_size_two_proportions(p_a, p_b)))
    powers = [
        exact_power_two_proportions(p_a, p_b, n_folk, test="fisher"),
        exact_power_two_proportions(p_a, p_b, n_pow, test="fisher"),
    ]
    labels = [r"Folklore $n=20$", rf"Powered $n={n_pow}$"]
    x = np.arange(2)
    ax.bar(x, powers, width=0.52, color=[C_WARN, C_PRIMARY], edgecolor="white", linewidth=0.9, zorder=3)
    ax.axhline(0.80, color=C_NEUTRAL, ls=(0, (4, 3)), lw=0.9, label="80% target")
    for xi, pw in zip(x, powers):
        ax.text(xi, pw + 0.03, f"{pw:.2f}", ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(x, labels, fontsize=7)
    ax.set(ylabel="Exact Fisher power (90% vs 80%)", ylim=(0, 0.95))
    ax.legend(loc="upper left", fontsize=6.5)
    finish_axis(ax)


def _save_p17_lob_supplement() -> Path:
    """Former Fig 4B — LoB sample-split (Supplement only)."""
    apply_journal_rc()
    fig, ax = plt.subplots(figsize=(DOUBLE_COL_W * 0.55, 2.8), facecolor="white")

    def draw_gamma(n: int, r: np.random.Generator) -> np.ndarray:
        return r.gamma(4.0, 0.25, size=n)

    cmp = monte_carlo_compare_split_vs_unsplit(draw_gamma, n_blank=80, alpha=0.05, n_mc=2000, seed=42)
    n_mc = int(cmp["n_mc"])
    names = ["Unsplit gated LoB", "Sample-split (P17)"]
    rates = [cmp["unsplit_exceedance"], cmp["split_exceedance"]]
    errs = [binomial_se(r, n_mc) for r in rates]
    x = np.arange(2)
    ax.bar(x, rates, width=0.52, color=[C_SECONDARY, C_ACCENT], edgecolor="white", linewidth=0.9,
           yerr=errs, capsize=3, error_kw={"elinewidth": 0.9, "ecolor": C_NEUTRAL}, zorder=3)
    ax.axhline(0.05, color=C_NEUTRAL, ls=(0, (4, 3)), lw=1.0, label=r"Nominal $\alpha{=}0.05$")
    ax.set_xticks(x, names, fontsize=8)
    ax.set(ylabel="Blank exceedance rate (MC ± SE)", ylim=(0, max(rates) + max(errs) + 0.02))
    ax.legend(loc="upper right", fontsize=7)
    finish_axis(ax)
    fig.tight_layout()
    path = save_figure(fig, "FigS_lob_p17_split", fig_dir=FIG_DIR)
    plt.close(fig)
    return path


def fig1_decision_map(out: Path | None = None) -> Path:
    return render_fig1_decision_map()


def fig2_folklore_triptych(out: Path | None = None) -> Path:
    apply_journal_rc()
    fig, axes = create_triptych()

    # --- A: all-positive ---
    ax = axes[0]
    ns = np.arange(1, 41)
    styles = [
        (0.95, C_PRIMARY, 2.4, 0.10),
        (0.80, C_WARN, 1.6, 0.05),
        (0.50, C_NEUTRAL, 1.3, 0.04),
    ]
    for p, col, lw, alpha in styles:
        y = p**ns
        ax.fill_between(ns, 0, y, color=col, alpha=alpha, zorder=1)
        ax.plot(ns, y, color=col, lw=lw, label=rf"$p={p:.2f}$", zorder=3)
    ax.axhline(0.95, color=C_NEUTRAL, ls=(0, (4, 3)), lw=0.9, zorder=2)
    ax.axvline(20, color=C_GOLD, ls=(0, (5, 2)), lw=1.1, zorder=2)
    lb20 = exact_lower_bound_after_all_success(20, 0.05, two_sided=False)
    ax.scatter([20], [0.95**20], s=48, c=C_PRIMARY, edgecolors="white", linewidths=1.0, zorder=5)
    ax.scatter([20], [lb20], s=48, c=C_SECONDARY, edgecolors="white", linewidths=1.0, zorder=5)
    ax.annotate(
        rf"20/20 $\Rightarrow$ CP$_{{0.05}}$={lb20:.2f}",
        xy=(20, lb20),
        xytext=(26, 0.42),
        fontsize=7,
        arrowprops=dict(arrowstyle="-|>", color=C_SECONDARY, lw=0.8, shrinkA=2),
        color=C_SECONDARY,
    )
    ax.set(xlabel=r"Replicates $n$", ylabel=r"$\Pr(X{=}n\mid p)=p^n$", xlim=(0, 40), ylim=(0, 1.02))
    ax.legend(loc="upper right", handlelength=1.6, fontsize=7)
    finish_axis(ax)
    panel_label(ax, "A")

    # --- B: miss beta horizontal bars ---
    ax = axes[1]
    scenarios = [("90 vs 80", 0.90, 0.80), ("95 vs 85", 0.95, 0.85), ("90 vs 70", 0.90, 0.70), ("50 vs 40", 0.50, 0.40)]
    labels = [s[0] for s in scenarios]
    miss = [1.0 - exact_power_two_proportions(a, b, 20, test="fisher") for _, a, b in scenarios]
    nstar = [int(np.ceil(sample_size_two_proportions(a, b))) for _, a, b in scenarios]
    ypos = np.arange(len(labels))
    bar_cols = [C_SECONDARY if i == 0 else C_WARN for i in range(len(labels))]
    ax.barh(ypos, miss, height=0.52, color=bar_cols, alpha=0.88, edgecolor="white", linewidth=0.8, zorder=3)
    ax.axvline(0.20, color=C_NEUTRAL, ls=(0, (4, 3)), lw=0.9, zorder=2)
    for yi, m, ns_, lab in zip(ypos, miss, nstar, labels):
        if yi == 0:
            ax.text(m + 0.02, yi, rf"$\beta={m:.2f}$ · $n^*\!={ns_}$", va="center", ha="left", fontsize=7, color=C_SECONDARY)
        else:
            ax.text(m + 0.015, yi, rf"${m:.2f}$", va="center", ha="left", fontsize=6.5, color=C_NEUTRAL)
    ax.set(yticks=ypos, yticklabels=labels, xlabel=r"Miss probability $\beta$ (Fisher, $n{=}20$)", xlim=(0, 1.02))
    ax.invert_yaxis()
    finish_axis(ax, grid="x")
    panel_label(ax, "B")

    # --- C: identifiability ---
    ax = axes[2]
    ident = _load_json("identification_study.json")
    if ident:
        cats = ["Interior\nlevels", "Saturation\nplateau"]
        vals = [float(ident["good_design"]["se_log10_lod"]), float(ident["saturation_design"]["se_log10_lod"])]
        colors = [C_ACCENT, C_SECONDARY]
        x = np.arange(2)
        ax.bar(x, vals, color=colors, width=0.52, edgecolor="white", linewidth=0.9, zorder=3)
        ax.set_yscale("log")
        ax.set_xticks(x, cats, fontsize=7.5)
        ax.set_ylabel(r"SE$(\log_{10}\mathrm{LoD}_{95})$")
        ax.set_ylim(min(vals) * 0.45, max(vals) * 2.2)
        fold = vals[1] / vals[0]
        ax.annotate(rf"{fold:.0f}$\times$", xy=(1, vals[1]), xytext=(1.15, vals[1] * 0.55),
                    fontsize=7.5, color=C_SECONDARY, ha="left",
                    arrowprops=dict(arrowstyle="-|>", color=C_SECONDARY, lw=0.8))
    finish_axis(ax)
    panel_label(ax, "C")

    return save_figure(fig, "Fig2_folklore_triptych", fig_dir=FIG_DIR)


def fig3_finite_sample_theory(out: Path | None = None) -> Path:
    """v4: power curves + exact-Fisher heatmap at n=20 + Pareto plane."""
    apply_journal_rc()
    p_a, p_b = 0.90, 0.80
    fig, axes = create_triptych()

    # A — power vs n
    ax = axes[0]
    ns = np.unique(np.linspace(10, 199, 36).astype(int))
    pw_a = np.array([power_two_proportions(p_a, p_b, int(n)) for n in ns])
    pw_f = np.array([exact_power_two_proportions(p_a, p_b, int(n), test="fisher") for n in ns])
    ax.fill_between(ns, pw_f, pw_a, color=C_PRIMARY, alpha=0.12, zorder=1)
    ax.plot(ns, pw_a, color=C_PRIMARY, lw=2.0, label="Asymptotic", zorder=3)
    ax.plot(ns, pw_f, color=C_SECONDARY, lw=2.0, ls="--", label="Exact Fisher", zorder=3)
    ax.axvline(20, color=C_GOLD, ls=(0, (5, 2)), lw=1.1, zorder=2)
    ax.axhline(0.80, color=C_NEUTRAL, ls=(0, (4, 3)), lw=0.8, zorder=2)
    i20 = int(np.argmin(np.abs(ns - 20)))
    ax.scatter([20], [pw_f[i20]], s=52, c=C_GOLD, edgecolors="white", linewidths=1.0, zorder=5)
    ax.set(xlabel=r"$n$ per arm", ylabel="Power (90% vs 80%)", xlim=(8, 205), ylim=(0, 0.95))
    ax.legend(loc="lower right", fontsize=6.5, framealpha=0.95)
    finish_axis(ax)
    panel_label(ax, "A")

    # B — heatmap: exact Fisher power at folklore n=20
    ax = axes[1]
    pa_grid, pb_grid, z = _fisher_power_grid_n20()
    sns.heatmap(
        z,
        ax=ax,
        cmap=sns.color_palette("YlGnBu", as_cmap=True),
        vmin=0.0,
        vmax=0.85,
        cbar_kws={"label": "Exact Fisher power", "shrink": 0.82, "pad": 0.02},
        xticklabels=[f"{p:.0%}" if k % 4 == 0 else "" for k, p in enumerate(pb_grid)],
        yticklabels=[f"{p:.0%}" if k % 4 == 0 else "" for k, p in enumerate(pa_grid)],
        linewidths=0.15,
        linecolor="#F0F0F0",
        rasterized=True,
    )
    ax.set(xlabel=r"$p_B$", ylabel=r"$p_A$")
    ax.text(0.03, 1.03, r"$n{=}20$", transform=ax.transAxes, fontsize=7, color=C_GOLD, fontweight="bold")
    # mark 90 vs 80 cell
    ia = int(np.argmin(np.abs(pa_grid - 0.90)))
    ib = int(np.argmin(np.abs(pb_grid - 0.80)))
    ax.scatter(ib + 0.5, ia + 0.5, s=60, facecolors="none", edgecolors=C_SECONDARY, linewidths=1.5, zorder=5)
    panel_label(ax, "B")

    # C — Pareto
    ax = axes[2]
    pareto = _load_json("pareto_exact_sample_size.json")
    if pareto:
        cert = pareto["certificate"]
        ax.axvspan(0, 0.05, ymin=0.80 / 0.95, ymax=1.0, color=C_ACCENT, alpha=0.08, zorder=0)
        ax.axhline(0.80, color=C_NEUTRAL, ls=(0, (4, 3)), lw=0.9)
        ax.axvline(0.05, color=C_NEUTRAL, ls=(0, (4, 3)), lw=0.9)
        for pt, lab, col, mk in [
            (cert["folklore"], r"$n{=}20$", C_GOLD, "o"),
            (cert["best_pareto_dominator"], r"$n{=}25$", C_WARN, "o"),
            (cert["powered"], r"$n^*{=}199$", C_PRIMARY, "D"),
        ]:
            ax.scatter(pt["type_i_fisher"], pt["power_fisher"], s=88, c=col, marker=mk,
                       edgecolors="white", linewidths=0.9, zorder=4, label=lab)
        ax.legend(loc="lower right", fontsize=6.5, frameon=True, borderpad=0.4)
        f, p = cert["folklore"], cert["powered"]
        ax.annotate("", xy=(p["type_i_fisher"], p["power_fisher"]), xytext=(f["type_i_fisher"], f["power_fisher"]),
                    arrowprops=dict(arrowstyle="-|>", color=C_SECONDARY, lw=1.0, ls="--"))
        ax.set(xlabel="Type I (null)", ylabel="Power (90 vs 80)", xlim=(0, 0.07), ylim=(0, 0.90))
    finish_axis(ax, grid="both")
    panel_label(ax, "C")

    return save_figure(fig, "Fig3_finite_sample_theory", fig_dir=FIG_DIR)


def fig4_remedy_composite(out: Path | None = None) -> Path:
    apply_journal_rc()
    fig, axes = create_triptych()

    # --- A: n* ---
    ax = axes[0]
    study = run_continuous_discrimination_study()
    ser = study["series"]["90pct"]
    x = np.asarray(ser["p_competitor_pct"], float)
    y = np.asarray(ser["n_star_80"], float)
    o = np.argsort(x)
    x, y = x[o], y[o]
    ax.semilogy(x, y, color=C_PRIMARY, lw=2.2, marker="o", ms=3.5, markevery=4,
                markerfacecolor="white", markeredgewidth=1.1, zorder=3)
    ax.axhline(20, color=C_GOLD, ls=(0, (5, 2)), lw=1.0, label=r"Folklore $n{=}20$")
    n_star = int(study["headline"]["n_star_90_vs_80"])
    ax.scatter([80], [n_star], s=65, c=C_WARN, edgecolors="white", linewidths=1.1, zorder=5)
    ax.annotate(rf"$n^*\!={n_star}$", xy=(80, n_star), xytext=(72, n_star * 2.2),
                fontsize=7, color=C_WARN,
                arrowprops=dict(arrowstyle="-|>", color=C_WARN, lw=0.8))
    ax.set(xlabel=r"Competitor rate $p$ (%)", ylabel=r"$n^*$ per arm (80% power)", xlim=(50, 99))
    ax.legend(loc="upper left", fontsize=7)
    finish_axis(ax)
    panel_label(ax, "A")

    # --- B: exact power at folklore vs powered n ---
    ax = axes[1]
    _plot_exact_power_remedy(ax)
    panel_label(ax, "B")

    # --- C: design ---
    ax = axes[2]
    c_path, m_path = DATA / "c_optimal_lod_design.json", DATA / "minimax_probit_design.json"
    if c_path.exists() and m_path.exists():
        c_study = json.loads(c_path.read_text(encoding="utf-8"))
        mm = json.loads(m_path.read_text(encoding="utf-8"))["minimax_search"]["minimax_design"]
        labels = ["Folklore", "c-optimal", "Minimax"]
        vals = [
            float(c_study["reference_equal_log_equal_n"]["se_log10_lod"]),
            float(c_study["c_optimal"]["se_log10_lod"]),
            float(mm["se_at_plan"]),
        ]
        cols = [C_LIGHT, C_PRIMARY, C_ACCENT]
        bars = ax.bar(labels, vals, color=cols, width=0.54, edgecolor="white", linewidth=0.9, zorder=3)
        ax.set_ylabel(r"SE$(\log_{10}\mathrm{LoD}_{95})$")
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.005, f"{v:.3f}", ha="center", va="bottom", fontsize=6.5)
        fold = vals[0] / vals[2]
        ax.text(2, vals[2] + 0.012, rf"{fold:.1f}$\times$ vs folklore", ha="center", fontsize=6.5, color=C_ACCENT)
    finish_axis(ax)
    panel_label(ax, "C")

    return save_figure(fig, "Fig4_remedy_composite", fig_dir=FIG_DIR)


def fig5_tierA_anchor(out: Path | None = None) -> Path:
    """Tier-A LoD replicate-planning anchor (hit-rate deposits + headline n*)."""
    apply_journal_rc()
    rows = _tierA_rows()
    lod_rows = _lod_focus_rows(rows)
    fig, grid = create_grid(2, 2, height=5.4)

    # A — tier-A qPCR hit rate vs concentration (detection, not LoQ)
    ax = grid[0, 0]
    _plot_qpcr_hit_rate(ax)
    panel_label(ax, "A")

    # B — guidance n / folklore on LoD-focused tier-A deposits
    ax = grid[0, 1]
    ratio_rows = [r for r in lod_rows if r.get("n_ratio_vs_folklore") is not None]
    if not ratio_rows:
        ratio_rows = [r for r in rows if r.get("n_ratio_vs_folklore") is not None]
    labels = [_TIERA_LABELS.get(r["dataset_id"], r["dataset_id"][:12]) for r in ratio_rows]
    ratios = [float(r["n_ratio_vs_folklore"]) for r in ratio_rows]
    y = np.arange(len(labels))
    ax.barh(y, ratios, height=0.55, color=C_PRIMARY, alpha=0.88, edgecolor="white", linewidth=0.8, zorder=3)
    ax.axvline(1.0, color=C_GOLD, ls=(0, (5, 2)), lw=1.1, label=r"Folklore ratio $=1$")
    ax.set(yticks=y, yticklabels=labels, xlabel=r"Guidance $n$ / folklore $n{=}20$")
    ax.invert_yaxis()
    finish_axis(ax, grid="x")
    ax.legend(loc="lower right", fontsize=6.5)
    panel_label(ax, "B")

    # C — LoD-focused deposits: archive size vs planned n
    ax = grid[1, 0]
    sized = [r for r in lod_rows if r.get("guidance_n") and r.get("n_rows")]
    if not sized:
        sized = [r for r in rows if r.get("guidance_n") and r.get("n_rows")]
    xs = [float(r["n_rows"]) for r in sized]
    ys = [float(r["guidance_n"]) for r in sized]
    ax.scatter(xs, ys, s=55, c=C_ACCENT, edgecolors="white", linewidths=0.9, zorder=3)
    for r, x, y in zip(sized, xs, ys):
        ax.annotate(_TIERA_LABELS.get(r["dataset_id"], "")[:8], (x, y), textcoords="offset points",
                    xytext=(4, 4), fontsize=6, color=C_NEUTRAL)
    ax.axhline(20, color=C_GOLD, ls=(0, (5, 2)), lw=1.0, label=r"Folklore $n{=}20$")
    ax.set(xscale="log", xlabel="Public deposit rows (log)", ylabel="Planned $n$ (LoD claims)")
    ax.legend(loc="lower right", fontsize=6.5)
    finish_axis(ax)
    panel_label(ax, "C")

    # D — headline n* for G1 / G2 / G4 vs folklore
    ax = grid[1, 1]
    _plot_lod_planning_n_bars(ax)
    panel_label(ax, "D")

    # Supplement: legacy LoQ panel (out of main-text scope)
    fig_loq, ax_loq = plt.subplots(figsize=(DOUBLE_COL_W * 0.55, 3.0), facecolor="white")
    _plot_radioimmuno_loq(ax_loq)
    fig_loq.tight_layout()
    save_figure(fig_loq, "FigL_radioimmuno_loq_profile", fig_dir=FIG_DIR)
    plt.close(fig_loq)

    path = save_figure(
        fig, "Fig5_tierA_lod_grid", fig_dir=FIG_DIR,
        extra_stems=(),
    )
    plt.close(fig)
    return path


def generate_main_figures() -> list[Path]:
    return [
        fig1_decision_map(),
        fig2_folklore_triptych(),
        fig3_finite_sample_theory(),
        fig4_remedy_composite(),
        fig5_tierA_anchor(),
        _save_p17_lob_supplement(),
    ]


if __name__ == "__main__":
    for p in generate_main_figures():
        print(p)
