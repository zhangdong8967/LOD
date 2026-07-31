"""
不同医学检验项目类型的 LOD / 重复实验概率模型

当前核心模型（lod_detection_analysis.py）针对：
  二分类定性结果 + 伯努利试验 + 「至少 1 次阳性」

本模块将同一「重复 n 次、评估可靠性」的问题，推广到：
  1. 二分类（阴阳性）— 直接适用 + k/n 判读
  2. 连续变量（生化、免疫定量）— 先由分布导出单次「检出概率 p」，再套二项框架
  3. 计数型（血细胞等）— Poisson / 正态近似
  4. 多分类（血型等）— 需先定义「成功」事件（正确分类 / 检出目标类等）
"""

from __future__ import annotations

import math
from typing import Literal, Sequence

import numpy as np
from scipy.stats import binom, norm, poisson


# ---------------------------------------------------------------------------
# 通用：已知单次成功概率 p 后的重复实验框架（所有类型的汇合点）
# ---------------------------------------------------------------------------

def prob_at_least_one(p: float, n: int) -> float:
    """n 次独立试验至少 1 次成功。"""
    return 1.0 - (1.0 - p) ** n


def prob_at_least_k(p: float, n: int, k: int) -> float:
    """n 次独立伯努利试验至少 k 次成功（CLSI 等常用的 k/n 判读）。"""
    if k < 0 or k > n:
        return 0.0
    return float(binom.sf(k - 1, n, p))  # P(X >= k) = 1 - P(X <= k-1)


def required_n_for_target(
    p: float,
    target: float,
    rule: Literal["at_least_one", "at_least_k"] = "at_least_one",
    k: int = 1,
) -> float:
    """反解达到目标概率所需的重复次数（连续解）。"""
    if not 0 < p < 1 or not 0 < target < 1:
        raise ValueError("p 与 target 均须在 (0, 1)")

    if rule == "at_least_one":
        return math.log(1 - target) / math.log(1 - p)

    # 对 k/n 规则无闭式反解，用搜索
    for n in range(1, 10_000):
        if prob_at_least_k(p, n, k) >= target:
            return float(n)
    return float("inf")


# ---------------------------------------------------------------------------
# 类型 1：二分类阴阳性（当前模型直接适用）
# ---------------------------------------------------------------------------

def binary_single_prob_at_concentration(
    concentration: float,
    lod_50: float,
    slope: float = 1.0,
) -> float:
    """
    用 logistic 曲线描述浓度 c 处的单次检出概率（EP17 常见思路）。

    p(c) = 1 / (1 + exp(-slope * (c - lod_50)))
    lod_50：50% 检出概率对应浓度（与 EP17 LoD 定义一致）
  """
    return 1.0 / (1.0 + math.exp(-slope * (concentration - lod_50)))


# ---------------------------------------------------------------------------
# 类型 2：连续变量（定量检测）
# ---------------------------------------------------------------------------

def continuous_detection_prob(
    true_value: float,
    sigma: float,
    cutoff: float,
) -> float:
    """
    连续测量 Y ~ N(μ, σ²)，判定「检出」当 Y > cutoff（如 LoB + kσ）。

    单次「检出」概率 p = P(Y > cutoff)。
    适用于：免疫定量、生化项目在低浓度/空白附近的检出判定。
    """
    if sigma <= 0:
        raise ValueError("sigma 须 > 0")
    return float(norm.sf(cutoff, loc=true_value, scale=sigma))


def continuous_quantification_cv(sigma: float, mean: float) -> float:
    """定量项目：CV% = 100 * σ / μ（低浓度处常用 LoQ 判据）。"""
    if mean <= 0:
        return float("inf")
    return 100.0 * sigma / mean


def loq_concentration_from_cv_target(
    sigma_per_sqrt_c: float,
    cv_target_pct: float,
) -> float:
    """
    简化 LoQ：假设 σ(c) = k * sqrt(c)（Poisson 计数常见），
    CV(c) = 100 * k / sqrt(c)。反解达到 CV 目标所需的最低 c。
    """
    if cv_target_pct <= 0 or sigma_per_sqrt_c <= 0:
        raise ValueError("参数须为正")
    k = sigma_per_sqrt_c
    return (100.0 * k / cv_target_pct) ** 2


# ---------------------------------------------------------------------------
# 类型 3：计数型（血细胞等）
# ---------------------------------------------------------------------------

def poisson_detection_prob(lambda_: float) -> float:
    """
    计数型：X ~ Poisson(λ)，「检出」= 计数 > 0（或 > 背景阈值）。

    p = P(X > 0) = 1 - e^{-λ}
    """
    if lambda_ < 0:
        raise ValueError("lambda 须 >= 0")
    return 1.0 - math.exp(-lambda_)


def poisson_count_at_least_threshold(lambda_: float, threshold: int) -> float:
    """P(X >= threshold)，threshold=1 时等价于 poisson_detection_prob。"""
    if threshold <= 0:
        return 1.0
    return float(poisson.sf(threshold - 1, lambda_))


def normal_approx_count_detection(
    lambda_: float,
    sigma_extra: float = 0.0,
    cutoff: float = 0.0,
) -> float:
    """
    血细胞计数等：λ 较大时用正态近似 N(λ, λ + σ_extra²)。
    """
    var = lambda_ + sigma_extra ** 2
    if var <= 0:
        return 0.0
    return float(norm.sf(cutoff, loc=lambda_, scale=math.sqrt(var)))


# ---------------------------------------------------------------------------
# 类型 4：多分类（血型、病原体分型等）
# ---------------------------------------------------------------------------

def multiclass_success_prob(
    mode: Literal["correct_class", "detect_target", "any_non_null"],
    probs: Sequence[float],
    true_class: int = 0,
    target_classes: Sequence[int] | None = None,
    null_class: int | None = None,
) -> float:
    """
    多分类单次试验的「成功」概率 p，须先定义成功事件：

    - correct_class:  判为真实类别
    - detect_target:  判为某一目标类集合（如 Rh 阳性）
    - any_non_null:   非「未检出/无效」类（类似定性检出）
    """
    probs = list(probs)
    n = len(probs)
    if n < 2:
        raise ValueError("probs 至少 2 类")

    if mode == "correct_class":
        if not 0 <= true_class < n:
            raise ValueError("true_class 越界")
        return probs[true_class]

    if mode == "detect_target":
        if target_classes is None:
            raise ValueError("detect_target 模式须提供 target_classes")
        return sum(probs[i] for i in target_classes if 0 <= i < n)

    if mode == "any_non_null":
        if null_class is None:
            raise ValueError("any_non_null 模式须提供 null_class")
        return 1.0 - probs[null_class]

    raise ValueError(f"未知 mode: {mode}")


def blood_type_example_probs(
    true_type: str,
    misclass_rate: float = 0.02,
) -> dict[str, float]:
    """
    简化血型示例：A/B/O/AB 四分类，其余为 misclass 分摊到非真类。
    用于说明多分类需单独建模误判结构，不能直接用单一 p=0.9。
    """
    types = ["A", "B", "O", "AB"]
    if true_type not in types:
        raise ValueError(f"true_type 须为 {types}")
    remain = misclass_rate / (len(types) - 1)
    return {t: (1.0 - misclass_rate if t == true_type else remain) for t in types}


# ---------------------------------------------------------------------------
# 统一视角：检验项目分类表
# ---------------------------------------------------------------------------

TEST_TYPE_MATRIX = """
┌─────────────────┬──────────────────┬────────────────────┬─────────────────────────┐
│ 检验类型        │ 单次试验模型     │ 「成功」如何定义     │ 当前仓库支持            │
├─────────────────┼──────────────────┼────────────────────┼─────────────────────────┤
│ 二分类阴阳性    │ Bernoulli(p)     │ 阳性/检出          │ ✅ lod_detection_analysis│
│ 连续变量定量    │ N(μ,σ²) 或异方差 │ Y>cutoff 或 CV<目标  │ ✅ 本模块 continuous_*  │
│ 计数型(血细胞)  │ Poisson(λ)       │ 计数>阈值            │ ✅ 本模块 poisson_*     │
│ 多分类(血型)    │ Categorical      │ 正确类/目标类/非无效 │ ✅ 本模块 multiclass_*  │
└─────────────────┴──────────────────┴────────────────────┴─────────────────────────┘
"""


def summarize_test_type(
    test_type: Literal["binary", "continuous", "count", "multiclass"],
    n: int = 20,
    **kwargs,
) -> dict:
    """给定项目类型与参数，返回单次 p 及 n 次重复后的可靠性。"""
    if test_type == "binary":
        p = kwargs.get("p")
        if p is None:
            p = binary_single_prob_at_concentration(
                kwargs.get("concentration", 0),
                kwargs.get("lod_50", 1.0),
                kwargs.get("slope", 1.0),
            )
    elif test_type == "continuous":
        p = continuous_detection_prob(
            kwargs.get("true_value", 0.0),
            kwargs.get("sigma", 1.0),
            kwargs.get("cutoff", 0.0),
        )
    elif test_type == "count":
        lam = kwargs.get("lambda_", kwargs.get("rate", 1.0))
        threshold = kwargs.get("threshold", 1)
        if threshold <= 1:
            p = poisson_detection_prob(lam)
        else:
            p = poisson_count_at_least_threshold(lam, threshold)
    elif test_type == "multiclass":
        p = multiclass_success_prob(
            kwargs.get("mode", "correct_class"),
            kwargs.get("probs", [0.25, 0.25, 0.25, 0.25]),
            true_class=kwargs.get("true_class", 0),
            target_classes=kwargs.get("target_classes"),
            null_class=kwargs.get("null_class"),
        )
    else:
        raise ValueError(test_type)

    k = kwargs.get("k", 1)
    rule = kwargs.get("rule", "at_least_one")
    if rule == "at_least_one":
        p_n = prob_at_least_one(p, n)
    else:
        p_n = prob_at_least_k(p, n, k)

    return {
        "test_type": test_type,
        "single_trial_p": p,
        "n_replicates": n,
        "rule": rule,
        "k": k,
        "replicate_probability": p_n,
    }


if __name__ == "__main__":
    print(TEST_TYPE_MATRIX)
    print()

    examples = [
        ("二分类 @ LoD 浓度", summarize_test_type("binary", n=20, concentration=1.0, lod_50=1.0, slope=2.0)),
        ("二分类 p=0.9 高把握", summarize_test_type("binary", n=20, p=0.9)),
        ("连续变量低浓度", summarize_test_type("continuous", n=20, true_value=2.0, sigma=1.5, cutoff=3.0)),
        ("血细胞 Poisson λ=5", summarize_test_type("count", n=20, lambda_=5.0)),
        ("血型正确分类 98%", summarize_test_type(
            "multiclass", n=20, mode="correct_class",
            probs=[0.98, 0.006, 0.006, 0.006], true_class=0,
        )),
    ]
    for title, res in examples:
        print(f"【{title}】")
        for k, v in res.items():
            print(f"  {k}: {v}")
        print()

    # 可选：生成对比图
    try:
        from pathlib import Path
        import matplotlib.pyplot as plt

        out = Path(__file__).resolve().parent / "figures"
        out.mkdir(exist_ok=True)

        n_range = np.arange(1, 41)
        scenarios = [
            ("二分类 p=0.1 (低浓度 LOD)", lambda n: prob_at_least_one(0.1, n)),
            ("二分类 p=0.5 (LoD 定义点)", lambda n: prob_at_least_one(0.5, n)),
            ("二分类 p=0.9", lambda n: prob_at_least_one(0.9, n)),
            ("连续 μ=2,σ=1.5,cut=3", lambda n: prob_at_least_one(
                continuous_detection_prob(2.0, 1.5, 3.0), n)),
            ("Poisson λ=0.5 (极低计数)", lambda n: prob_at_least_one(
                poisson_detection_prob(0.5), n)),
            ("血型正确率 98%", lambda n: prob_at_least_one(0.98, n)),
        ]
        fig, ax = plt.subplots(figsize=(10, 6))
        for label, fn in scenarios:
            ax.plot(n_range, [fn(int(n)) for n in n_range], label=label, linewidth=2)
        ax.axhline(0.95, color="gray", linestyle="--", alpha=0.6)
        ax.axvline(20, color="purple", linestyle=":", alpha=0.6)
        ax.set_xlabel("重复次数 n")
        ax.set_ylabel("至少 1 次「成功」的概率")
        ax.set_title("不同检验类型映射到单次 p 后的重复可靠性（统一二项层）")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.02)
        fig.tight_layout()
        fig.savefig(out / "fig7_test_types_comparison.png", dpi=150)
        plt.close(fig)
        print(f"对比图已保存: {out / 'fig7_test_types_comparison.png'}")
    except ImportError:
        pass
