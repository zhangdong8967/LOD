"""
LOD 重复实验检出概率分析与可视化

模型：n 次独立重复实验，单次成功率 p，
     至少检出 1 次的概率 P = 1 - (1-p)^n
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from scipy.special import comb

OUTPUT_DIR = Path(__file__).resolve().parent / "figures"
OUTPUT_DIR.mkdir(exist_ok=True)

# 中文字体：优先 macOS / Windows 系统字体
_CJK_FONTS = [
    "PingFang SC",
    "Heiti SC",
    "STHeiti",
    "Songti SC",
    "SimHei",
    "Microsoft YaHei",
    "Noto Sans CJK SC",
    "WenQuanYi Micro Hei",
]
_available = {f.name for f in font_manager.fontManager.ttflist}
for _font in _CJK_FONTS:
    if _font in _available:
        plt.rcParams["font.sans-serif"] = [_font, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False


def prob_at_least_one(p: float, n: int) -> float:
    """至少一次成功的概率。"""
    return 1.0 - (1.0 - p) ** n


def required_replicates(p: float, target_p: float) -> float:
    """达到目标检出率所需重复次数（连续解）。"""
    if not 0 < p < 1:
        raise ValueError("p 须在 (0, 1) 内")
    if not 0 < target_p < 1:
        raise ValueError("target_p 须在 (0, 1) 内")
    return np.log(1 - target_p) / np.log(1 - p)


def required_replicates_ceil(p: float, target_p: float) -> int:
    """达到目标检出率所需重复次数（向上取整，实际操作次数）。"""
    return int(np.ceil(required_replicates(p, target_p)))


def binomial_at_least_one(p: float, n: int) -> float:
    """二项分布：恰好 0 次成功的概率为 (1-p)^n，故至少一次为 1-(1-p)^n。"""
    return 1.0 - comb(n, 0) * p ** 0 * (1 - p) ** n


def monte_carlo_at_least_one(p: float, n: int, trials: int = 100_000, seed: int = 42) -> float:
    """蒙特卡洛：模拟 n 次独立伯努利试验，估计至少一次成功的比例。"""
    rng = np.random.default_rng(seed)
    # 每次实验：n 次独立试验，看是否至少成功 1 次
    successes = rng.binomial(n, p, size=trials)
    return np.mean(successes >= 1)


def plot_probability_vs_n():
    """图1：不同单次成功率 p 下，重复次数 n 与检出概率的关系。"""
    n = np.arange(1, 51)
    p_values = [0.5, 0.7, 0.8, 0.9, 0.95]
    colors = plt.cm.viridis(np.linspace(0.15, 0.9, len(p_values)))

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for p, color in zip(p_values, colors):
        probs = prob_at_least_one(p, n)
        ax.plot(n, probs, label=f"p = {p}", color=color, linewidth=2)

    for target, ls in [(0.95, "--"), (0.80, "-."), (0.50, ":")]:
        ax.axhline(target, color="gray", linestyle=ls, alpha=0.6, linewidth=1)
        ax.text(50.5, target, f"{target:.0%}", va="center", fontsize=9, color="gray")

    ax.set_xlabel("重复实验次数 n", fontsize=12)
    ax.set_ylabel("至少一次检出概率 P", fontsize=12)
    ax.set_title("重复实验次数与检出概率（1 − (1−p)ⁿ）", fontsize=13)
    ax.set_xlim(1, 50)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig1_probability_vs_n.png", dpi=150)
    plt.close(fig)


def plot_p09_examples():
    """图2：p=0.9 时典型 n 值与目标检出率对应的 n。"""
    p = 0.9
    example_ns = [3, 5, 6, 10, 20, 30]
    targets = [0.50, 0.80, 0.95]
    target_labels = ["50%", "80%", "95%"]
    required_ns = [required_replicates_ceil(p, t) for t in targets]

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    # 左：典型 n 的检出率
    ax = axes[0]
    probs = [prob_at_least_one(p, n) for n in example_ns]
    bars = ax.bar(
        [str(n) for n in example_ns],
        probs,
        color=plt.cm.Blues(np.linspace(0.4, 0.9, len(example_ns))),
        edgecolor="white",
    )
    ax.axhline(0.95, color="red", linestyle="--", alpha=0.7, label="95% 目标")
    ax.axhline(0.80, color="orange", linestyle="--", alpha=0.7, label="80% 目标")
    ax.axhline(0.50, color="green", linestyle="--", alpha=0.7, label="50% 目标")
    for bar, prob in zip(bars, probs):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{prob:.4f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_xlabel("重复次数 n（p = 0.9）")
    ax.set_ylabel("检出概率 P")
    ax.set_title("不同重复次数下的检出率")
    ax.set_ylim(0, 1.08)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    # 右：达到目标检出率所需 n
    ax = axes[1]
    x = np.arange(len(targets))
    bars = ax.bar(x, required_ns, color=["#2ecc71", "#f39c12", "#e74c3c"], width=0.5)
    ax.bar(x + 0.35, [20], width=0.25, color="#3498db", alpha=0.7, label="实践常用 n=20")
    for bar, n_req in zip(bars, required_ns):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"n ≈ {n_req}", ha="center", fontsize=10)
    ax.set_xticks(x + 0.175)
    ax.set_xticklabels(target_labels)
    ax.set_xlabel("目标检出率")
    ax.set_ylabel("所需重复次数 n")
    ax.set_title("达到目标检出率所需重复次数（p = 0.9）")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig2_p09_examples.png", dpi=150)
    plt.close(fig)


def plot_required_n_heatmap():
    """图3：单次成功率 p 与目标检出率下的所需重复次数热力图。"""
    p_grid = np.linspace(0.3, 0.99, 40)
    target_grid = np.linspace(0.5, 0.99, 30)
    n_matrix = np.zeros((len(target_grid), len(p_grid)))

    for i, target in enumerate(target_grid):
        for j, p in enumerate(p_grid):
            n_matrix[i, j] = required_replicates(p, target)

    fig, ax = plt.subplots(figsize=(9, 6))
    im = ax.imshow(
        n_matrix,
        aspect="auto",
        origin="lower",
        extent=[p_grid[0], p_grid[-1], target_grid[0], target_grid[-1]],
        cmap="YlOrRd",
        vmin=1,
        vmax=50,
    )
    ax.plot([0.9, 0.9], [0.5, 0.99], "k--", linewidth=1.5, alpha=0.8)
    ax.scatter([0.9], [0.95], c="white", edgecolors="black", s=80, zorder=5)
    ax.scatter([0.9], [0.80], c="white", edgecolors="black", s=80, zorder=5)
    ax.scatter([0.9], [0.50], c="white", edgecolors="black", s=80, zorder=5)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("所需重复次数 n")
    ax.set_xlabel("单次实验成功率 p")
    ax.set_ylabel("目标检出率 P")
    ax.set_title("参数空间：达到目标检出率所需的重复次数")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig3_required_n_heatmap.png", dpi=150)
    plt.close(fig)


def plot_monte_carlo_validation():
    """图4：解析公式与蒙特卡洛模拟对比，展示抽样机制。"""
    p = 0.9
    n_values = [3, 6, 10, 20, 30]
    analytical = [prob_at_least_one(p, n) for n in n_values]
    simulated = [monte_carlo_at_least_one(p, n, trials=200_000) for n in n_values]

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    ax = axes[0]
    x = np.arange(len(n_values))
    w = 0.35
    ax.bar(x - w / 2, analytical, w, label="解析公式 1−(1−p)ⁿ", color="#3498db")
    ax.bar(x + w / 2, simulated, w, label="蒙特卡洛模拟", color="#e67e22", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels([str(n) for n in n_values])
    ax.set_xlabel("重复次数 n（p = 0.9）")
    ax.set_ylabel("至少一次成功概率")
    ax.set_title("解析解 vs 蒙特卡洛验证")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # 右：单次实验轨迹示意（20 次重复，展示“全失败才未检出”）
    ax = axes[1]
    rng = np.random.default_rng(0)
    n_demo, trials_demo = 20, 80
    outcomes = rng.binomial(n_demo, p, size=trials_demo)
    colors = ["#e74c3c" if o == 0 else "#27ae60" for o in outcomes]
    ax.bar(range(trials_demo), np.ones(trials_demo), color=colors, width=1.0, edgecolor="none")
    detect_rate = np.mean(outcomes >= 1)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xlabel("独立实验序号")
    ax.set_ylabel("")
    ax.set_yticks([])
    ax.set_title(
        f"抽样示意：每次实验 {n_demo} 次重复\n"
        f"绿=至少检出1次，红=全部失败（模拟检出率 {detect_rate:.1%}）"
    )
    from matplotlib.patches import Patch
    ax.legend(
        handles=[
            Patch(facecolor="#27ae60", label="至少 1 次成功"),
            Patch(facecolor="#e74c3c", label="n 次全部失败"),
        ],
        loc="upper right",
        fontsize=9,
    )

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig4_monte_carlo.png", dpi=150)
    plt.close(fig)


def plot_failure_probability():
    """图5：失败概率 (1-p)^n 的指数衰减——深层机制可视化。"""
    p = 0.9
    n = np.arange(1, 41)
    fail_prob = (1 - p) ** n
    detect_prob = 1 - fail_prob

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()
    line1 = ax1.plot(n, detect_prob, "b-", linewidth=2.5, label="检出概率 1−(1−p)ⁿ")
    line2 = ax2.plot(n, fail_prob, "r--", linewidth=2, label="全失败概率 (1−p)ⁿ")
    ax1.axhline(0.95, color="gray", linestyle=":", alpha=0.8)
    ax1.axvline(20, color="purple", linestyle=":", alpha=0.8, label="实践常用 n=20")
    ax1.set_xlabel("重复次数 n")
    ax1.set_ylabel("检出概率", color="b")
    ax2.set_ylabel("全失败概率（对数尺度）", color="r")
    ax2.set_yscale("log")
    ax1.set_ylim(0.5, 1.01)
    ax1.set_title("对偶视角：检出概率与“n 次全失败”概率（p = 0.9）", fontsize=12)
    lines = line1 + line2
    ax1.legend(lines, [l.get_label() for l in lines], loc="center right")
    ax1.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig5_failure_decay.png", dpi=150)
    plt.close(fig)


def print_summary_table():
    """打印数值摘要表。"""
    p = 0.9
    print("\n" + "=" * 60)
    print("LOD 重复实验检出概率 — 数值摘要（p = 0.9）")
    print("=" * 60)
    print(f"{'目标检出率':<12} {'所需 n (连续)':<16} {'所需 n (取整)':<12}")
    print("-" * 60)
    for target in [0.50, 0.80, 0.95]:
        n_cont = required_replicates(p, target)
        n_int = required_replicates_ceil(p, target)
        print(f"{target:>6.0%}       {n_cont:>10.2f}       {n_int:>8}")
    print("-" * 60)
    print(f"{'典型 n':<12} {'检出概率':<16} {'说明'}")
    for n in [3, 5, 6, 10, 20, 30]:
        prob = prob_at_least_one(p, n)
        note = ""
        if n == 20:
            note = "← 实践常用"
        print(f"n = {n:<6}   {prob:.10f}   {note}")
    print("=" * 60 + "\n")


def plot_required_n_by_p():
    """图6：不同单次成功率 p 下，达到各目标检出率所需的 n。"""
    p_values = np.linspace(0.05, 0.95, 50)
    targets = [0.50, 0.80, 0.95]
    colors = ["#2ecc71", "#f39c12", "#e74c3c"]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for target, color in zip(targets, colors):
        n_req = [required_replicates(p, target) for p in p_values]
        ax.plot(p_values, n_req, label=f"目标 {target:.0%}", color=color, linewidth=2)

    ax.axvline(0.9, color="gray", linestyle="--", alpha=0.7, label="p = 0.9")
    ax.axhline(20, color="purple", linestyle=":", alpha=0.7, label="实践常用 n = 20")
    ax.set_xlabel("单次实验成功率 p")
    ax.set_ylabel("所需重复次数 n（连续解）")
    ax.set_title("不同 p 下达到目标检出率所需的重复次数")
    ax.set_ylim(0, 35)
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig6_required_n_by_p.png", dpi=150)
    plt.close(fig)


def main():
    print("生成可视化图表...")
    plot_probability_vs_n()
    plot_p09_examples()
    plot_required_n_heatmap()
    plot_monte_carlo_validation()
    plot_failure_probability()
    plot_required_n_by_p()
    print_summary_table()
    print(f"图表已保存至: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
