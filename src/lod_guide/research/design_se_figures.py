"""
Fig 9 — asymptotic SE(log10 LoD) design comparison (c-optimal vs minimax vs folklore).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lod_guide.paper.figure_style import (
    JOURNAL_BLUE,
    JOURNAL_GRAY,
    JOURNAL_GREEN,
    JOURNAL_LIGHT_GRAY,
    JOURNAL_ORANGE,
    apply_journal_rc,
    create_panel_figure,
    panel_label,
    save_figure,
    style_data_axis,
    styled_bar,
)
from lod_guide.research.minimax_probit_design import minimax_design_search
from lod_guide.theory.c_optimal_lod_design import compare_to_reference_designs
from lod_guide.theory.lod_dose_response import default_synthetic_truth

ROOT = Path(__file__).resolve().parents[3]
FIG_DIR = ROOT / "figures" / "methodology"
PAPER_FIG = ROOT / "paper_artifacts" / "figures"
DATA = ROOT / "data" / "research"


def _load_or_compute_payload() -> dict:
    c_path = DATA / "c_optimal_lod_design.json"
    m_path = DATA / "minimax_probit_design.json"
    if c_path.exists() and m_path.exists():
        c = json.loads(c_path.read_text(encoding="utf-8"))
        m = json.loads(m_path.read_text(encoding="utf-8"))
        return {"c_optimal_study": c, "minimax_study": m, "source": "json"}

    truth = default_synthetic_truth()
    c = compare_to_reference_designs(truth, seed=0)
    m = minimax_design_search(truth)
    return {
        "c_optimal_study": c,
        "minimax_study": {"minimax_search": m},
        "source": "computed",
    }


def fig9_design_se_comparison(out: Path | None = None) -> Path:
    """Manuscript Fig 9: SE(log10 LoD) at plan slope and worst-case over slope ratios."""
    apply_journal_rc()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_FIG.mkdir(parents=True, exist_ok=True)
    out = out or FIG_DIR / "Fig9_design_se_comparison.png"

    payload = _load_or_compute_payload()
    c_study = payload["c_optimal_study"]
    m_search = payload["minimax_study"]["minimax_search"]

    ref_se = float(c_study["reference_equal_log_equal_n"]["se_log10_lod"])
    copt_se = float(c_study["c_optimal"]["se_log10_lod"])
    folk = m_search["folklore_equal_log_equal"]
    mm = m_search["minimax_design"]

    fig, axes = create_panel_figure(2, height=2.75)
    plan_labels = ["Folklore\n(equal log)", "c-optimal\n(grid)", "Minimax\n(dense)"]
    plan_se = np.array([ref_se, copt_se, float(mm["se_at_plan"])])
    worst_labels = ["Folklore", "Minimax"]
    worst_se = np.array([float(folk["worst_case_se"]), float(mm["worst_case_se"])])

    ax = axes[0]
    style_data_axis(ax)
    bars = styled_bar(ax, np.arange(3), plan_se, colors=[JOURNAL_LIGHT_GRAY, JOURNAL_BLUE, JOURNAL_GREEN], width=0.62, labels=plan_labels)
    ax.set_ylabel(r"SE($\log_{10}$ LoD$_{95}$) at plan $\beta$")
    for b, v in zip(bars, plan_se):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.008, f"{v:.3f}", ha="center", va="bottom", fontsize=6.5)
    panel_label(ax, "A")

    ax = axes[1]
    style_data_axis(ax)
    bars2 = styled_bar(ax, np.arange(2), worst_se, colors=[JOURNAL_LIGHT_GRAY, JOURNAL_ORANGE], width=0.55, labels=worst_labels)
    ax.set_ylabel(r"Worst-case SE over $\beta\in[0.5,1.5]\beta_{\mathrm{plan}}$")
    ratio = folk["worst_case_se"] / mm["worst_case_se"] if mm["worst_case_se"] else float("nan")
    ax.text(0.98, 0.95, rf"Ratio ≈ {ratio:.2f}×", transform=ax.transAxes, ha="right", va="top", fontsize=6.8, color=JOURNAL_ORANGE)
    for b, v in zip(bars2, worst_se):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.012, f"{v:.3f}", ha="center", va="bottom", fontsize=6.5)
    panel_label(ax, "B")

    save_figure(fig, "Fig9_design_se_comparison", fig_dir=FIG_DIR)
    plt.close(fig)
    return out


if __name__ == "__main__":
    print(fig9_design_se_comparison())
