# 立意升维：假设门控的 LoD 决策理论

**Audience:** 投稿信 / Abstract / Introduction 骨架（中文提纲，可直接改写为英文 methods 文）  
**定位:** 高水平 **methods / technical brief**（*Clinical Chemistry*、*Clin Chem Lab Med*）；全文研究论文仍需补常规生化 raw 或合作实验室案例。

---

## 一句话立意（Elevated claim）

在 EP17 给出的**合法选项空间**内，把“选哪条统计路径、要多大 \(n\)”表述为**可审计的假设门控决策问题**：用诊断门控控制参数失配风险，用精确小样本方法控制确认阶段的 Type I / miss-\(\beta\)，并证明民间固定 SOP（\(n=20\)、全阳即过、恒正态 LoB、饱和 \(1-(1-p)^n\) 比较）在明确风险函数下不可辩护。

英文锁定句：

> **Assumption-gated decision theory for LoD evaluation** — within EP17-class option sets, path choice and sample size become auditable risk minimization under diagnostic gates and exact small-sample confirmation; folklore SOPs are indefensible under an explicit loss.

---

## 立意核心（给作者，勿堆进正文）

**一句话：** EP17 有定义和路径菜单；验证方案里的 **claim** 很少被翻译成 **n 和路径**——我们补的是这一步前瞻性设计。

**逻辑顺序：** claim → estimand E1–E3 → S2–S3 诊断 → S4 路径 → S5 的 n → 精确确认 → 分层证据。

**勿用：** 三层/Layer、决策编译器、可证伪对象、inferential contract。  
**详稿：** [`研究深度阐述.md`](研究深度阐述.md)、[`SIGNIFICANCE_AND_DEPTH.md`](../../manuscript/SIGNIFICANCE_AND_DEPTH.md)。

---

## 相对旧表述升了什么

| 旧表述 | 升维后 |
|--------|--------|
| “辅助 EP17 的样本量计算器 / 软件包” | EP17 选项空间上的**决策理论操作化** |
| “揭穿 n=20 不够力” | 在风险 \(L\) 下 folklore 相对 powered 设计的 **loss 倍率** |
| “多数据集都支持算法” | **A/B/C/S 防火墙**；主结果仅 Table 7（tier A） |
| “有 P1–P6” | **P1–P8**（补全阳陷阱 + 精确/渐近缺口） |
| “LoQ 用 troponin 演示” | **主文 LoQ = tier-A radioimmuno**；troponin = tier-C 引擎一致性 |

---

## 风险函数（Methods 核心）

\[
L = w_I\cdot\mathrm{TypeI} + w_{II}\cdot\beta + w_M\cdot\mathbf{1}\{\text{parametric mismatch}\} + w_C\cdot(\mathrm{DE}-1)
\]

S0–S7 不是流程装饰，而是使 \(L\) 可计算、可审计的路径图。标准情景数值见 `data/research/decision_risk.json`。

---

## 主结果预告（Results 骨架）

1. **Table 7** — tier-A public deposits’ gate / LoQ / \(n\) vs folklore 汇总（禁止并入 C/S；当前 A=10）。  
2. **Fig 4** — 全阳陷阱：\(p^n\) 与 \(n/n\) 后的 CP 下界 / 后验风险（图内无标题，仅 A/B）。  
3. **Table 3 + P8** — folklore \(n=20\) 下渐近功效高估精确 Fisher 功效。  
4. **Fig 8** — radioimmuno 精度剖面 LoQ@CV20%（tier A）。  
5. **Table 8** — E1 Wilson vs Clopper–Pearson 覆盖（堵住“只做了 E2 exact”）。

英文短文草稿与 Supplement 嵌入：`manuscript/METHODS_BRIEF.md`、`manuscript/SUPPLEMENT.md`。

---

## 明确不声称

- 未在全部临床化学面板上验证算法。  
- tier C（troponin demo）与 tier S（仿真）≠ 多中心临床真相。  
- 不取代 EP17 / YY / WS / IFU 的法规地位。

---

## 投稿路径建议

1. **近端:** methods / technical brief + `paper_artifacts/` 作 Supplement。  
2. **全文顶刊:** 再补 ≥1 常规生化/血液学 raw 或单一合作实验室前瞻案例 + 完整英文稿。

复现：

```bash
make paper-artifacts
python -m lod_guide.research.decision_risk
python -m lod_guide.research.tierA_meta_analysis
python -m lod_guide.research.one_proportion_coverage
```
