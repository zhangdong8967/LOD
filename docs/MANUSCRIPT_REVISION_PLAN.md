# 文稿完善修改计划（逐句修改指南）

**生成日期**: 2026-08-24  
**目标**: Clinical Chemistry Article投稿就绪  
**当前状态**: 4645词（目标≤3500主文）+ 图表基本完成

---

## 一、图表质量评估

### 1.1 主文图表（5项，符合≤6项要求）✅

| 项目 | 文件 | 状态 | 问题 |
|------|------|------|------|
| **Fig 1** | `Fig1_Fig1-lod-replicate-planning.png/pdf` | ✅ 已生成 | 需确认300 dpi TIFF格式 |
| **Fig 2** | `Fig2_Fig2-tierA-calibration.png/pdf` | ✅ 已生成 | 需确认300 dpi TIFF格式 |
| **Table 1** | `Table01_estimands_E1_E3.csv` | ✅ 已生成 | 需转为Word表格 |
| **Table 3** | `Table03_reference_pairs_n20.csv` | ✅ 已生成 | 需转为Word表格，添加表注 |
| **Table 7** | `Table07_tierA_meta.csv` | ✅ 已生成 | Citation列需缩写处理 |

**总体评价**: 图表数量和内容符合Clinical Chemistry要求。

### 1.2 图表具体问题

#### Figure 1问题：
1. ⚠️ **分辨率确认**: 需要检查PNG是否≥300 dpi
2. ⚠️ **色盲友好**: 热图配色需检查（建议viridis/RdYlBu）
3. ⚠️ **字体大小**: 轴标签在压缩后是否清晰（建议≥8 pt）
4. ✅ **图例**: 已包含alt text
5. ⚠️ **面板标注**: A、B、C、D标签是否在左上角黑体

**修改建议**：
```python
# 在figures.py中增加输出选项
matplotlib.rcParams['figure.dpi'] = 300
matplotlib.rcParams['font.size'] = 10  # 确保缩小后仍清晰
```

#### Figure 2问题：
1. ⚠️ **Panel A**: qPCR曲线如果来自真实数据，需在图例中注明数据源
2. ⚠️ **Panel B**: 横条图长度差异较大（2.6×到10×），考虑对数刻度或截断
3. ✅ **Panel C**: 决策风险对比清晰

#### Table质量问题：
1. ⚠️ **Table 1**: 
   - CSV格式需转为正式表格（3列×3行）
   - 表头需改为: "Goal | Estimand | Sample size method"
   - 去除下划线，用空格或连字符

2. ⚠️ **Table 3** (`Table03_reference_pairs_n20.csv`):
   - 8行×13列过宽，需横向压缩
   - 建议只保留关键列: pair, delta_p, n, power_exact_fisher, miss_beta, n_star_ceiling
   - 数字精度：保留3位小数即可（不要15位）
   - 添加表注: "Full grid: online Supplement Table03_comparison_grid_n20.csv"

3. ⚠️ **Table 7**:
   - Citation列太长（需缩写为"First author et al. (year)"）
   - n_ratio_vs_folklore列名改为"n*/n₂₀"
   - 去除dataset_id列（用序号1-9替代）

**立即行动**：
```bash
# 1. 生成高分辨率TIFF
cd /Users/zhangdong/PycharmProjects/PythonProject/LOD
python -c "
from lod_guide.paper.main_figures import export_high_res_tiff
export_high_res_tiff()  # 需要在代码中实现
"

# 2. 检查色盲友好
# 使用 https://www.color-blindness.com/coblis-color-blindness-simulator/
```

---

## 二、文稿篇幅问题（4645词 → 目标≤3500词）

### 2.1 超标分析
- **当前**: 4645词（含markdown链接、code blocks）
- **实际正文**: 估计约3800-4000词（去除markdown后）
- **目标**: ≤3500词
- **需删减**: 约300-500词（约10-15%）

### 2.2 建议删减区域

| 区域 | 当前词数估算 | 目标词数 | 删减策略 |
|------|-------------|---------|---------|
| Abstract | ~250 | 250 | ✅ 已达标 |
| Introduction | ~650 | 550 | 删减100词：压缩LoD定义重复 |
| Methods | ~1200 | 1000 | 删减200词：公式移到补充材料 |
| Results | ~900 | 800 | 删减100词：Box内容简化 |
| Discussion | ~600 | 500 | 删减100词：压缩限制性段落 |

**总删减目标**: ~500词

---

## 三、AI痕迹识别与修改

### 3.1 典型AI痕迹特征（需修改）

#### 🚨 高危AI痕迹：

**特征1：过度正式的连接词**
- ❌ "What has **not** been formalized—and what this work contributes—is..."
- ✅ 改为: "This work formalizes..."

**特征2：平行结构过于工整**
- ❌ "treats **goal** as a first-class object; **refuses** parametric LoB; replaces folklore..."
- ✅ 改为: "This framework treats detection goals as primary design inputs, rejects parametric LoB under failed diagnostics, and..."

**特征3：过度使用破折号和em dash**
- ❌ "—not a redefinition of LoD."
- ✅ 改为: "(not a redefinition of LoD)"

**特征4：重复的"This is not X. It is Y"句式**
- ❌ "This is not a redefinition of LoD. It is a **design and decision calculus**..."
- ✅ 改为: "The framework provides a design calculus for existing LoD vocabulary rather than proposing new definitions."

**特征5：过度嵌套的从句**
- ❌ "When a laboratory signs off **limit of detection (LoD)** verification after a reagent lot or instrument change, the validation packet often fixes about 20 low-level replicates regardless of the written claim."
- ✅ 改为: "Laboratories often verify LoD with 20 replicates after reagent or instrument changes, regardless of the claim being tested."

### 3.2 逐句修改示例（Introduction前3段）

#### **段落1（当前版本）**：
> "When a laboratory signs off **limit of detection (LoD)** verification after a reagent lot or instrument change, the validation packet often fixes about 20 low-level replicates regardless of the written claim. One file may require confirmation of manufacturer $LoD_{95}$ at the **protocol verification concentration** $c^{\ast}$—the low level named in the manufacturer instructions for use (IFU) or local validation plan. Another may declare equivalent lot performance at that concentration."

**修改后版本**：
> "Laboratories commonly verify limit of detection (LoD) with approximately 20 replicates after reagent or instrument changes, without adjusting sample size for the specific detection claim. Some protocols test manufacturer LoD₉₅ at a verification concentration c*; others compare lot equivalence at that concentration."

**修改理由**：
- 删除冗长从句："When...change" → 直接陈述
- 简化破折号解释：移除"—the low level..."
- 合并两个"One file...Another"句子
- 词数：66 → 38（节省28词，42%）

---

#### **段落2（当前版本）**：
> "For **hit-rate–based** assays, which classify each replicate as detected or not at low level, the **Clinical and Laboratory Standards Institute (CLSI) EP17-A2** guideline on detection capability treats each protocol phrase as a statement about the **single-trial detection probability** $p(c^{\ast})$: the probability that one replicate at $c^{\ast}$ is detected, usually benchmarked at $p=0.95$."

**修改后版本**：
> "For assays that classify replicates as detected or not, CLSI EP17-A2 interprets protocol phrases as statements about single-trial detection probability p(c*), typically benchmarked at p=0.95."

**修改理由**：
- 删除"hit-rate–based"的解释性从句
- 首次使用后CLSI EP17-A2可简写
- 合并冒号后的解释
- 词数：55 → 28（节省27词，49%）

---

#### **段落3（当前版本）**：
> "Operationally, $LoD_{95}$ names the concentration at which a single replicate is detected with probability $p=0.95$, so a miss at that concentration is a rare event with probability $1-p=0.05$. That analytical 5% is the physical meaning of a detection limit: non-detection at LoD should be uncommon."

**修改后版本**：
> "At LoD₉₅, single-replicate detection probability equals 0.95, making non-detection a rare event (5%). This analytical 5% defines the physical meaning of a detection limit."

**修改理由**：
- 删除"Operationally"开头
- 删除冗余解释"so a miss...probability 1-p=0.05"（读者能理解）
- 合并句子
- 词数：48 → 23（节省25词，52%）

---

### 3.3 全文修改优先级

#### **高优先级删减区域**（立即修改）：

**1. Introduction第3段**（LoD定义重复）：
- 当前："Operationally, LoD₉₅ names...That analytical 5%...Verification then asks..."
- **删减策略**：将"双5%"概念移到Methods的Box或脚注
- **节省**：~80词

**2. Methods §2.3公式展示**：
- 当前：Eq. (2), (3), (4), (5)全部内嵌
- **删减策略**：保留Eq. (2) Fleiss-Chow；其余移到Supplement或脚注
- **节省**：~120词

**3. Results Box 1-2**：
- 当前：两个Box各80-100词
- **删减策略**：压缩为单句高亮，详细数据引用Table
- **节省**：~100词

**4. Discussion第2段**（validation committees rarely audit...）：
- **删减策略**：删除例子描述，保留核心观点
- **节省**：~60词

**5. Methods中的定理引用**：
- 当前："Theorem T1...Lemma T2a...Corollary T2c..."
- **删减策略**：简化为"Formal proofs (Supplement §S2)"
- **节省**：~80词

**总计**：约440词删减（达到≤3500词目标）

---

## 四、逐句修改清单（按优先级）

### Phase 1：高危AI痕迹修改（1-2小时）

#### 🔴 **修改点1-10**（Introduction）：

**原句1.1**:
> "What has **not** been formalized—and what this work contributes—is an **estimand-first, assumption-gated decision algorithm**..."

**修改为**:
> "This work formalizes an estimand-gated decision algorithm..."

---

**原句1.2**:
> "This is not a redefinition of LoD. It is a **design and decision calculus**..."

**修改为**:
> "The framework provides a design calculus for existing LoD vocabulary."

---

**原句1.3**:
> "Before data collection, the laboratory should lock one primary planning contract at $c^{\ast}$. The contracts are..."

**修改为**:
> "Before data collection, laboratories specify one detection claim at c*: benchmark confirmation (E1), two-arm contrast (E2), or acceptance by a k/n rule (E3)."

---

**原句1.4**:
> "We asked what $n^{\ast}$ each common verification sentence implies before data collection, and how operating-characteristic and design surfaces vary across all prespecified $(p_A,p_B)$ on the integer lattice—not a single illustrative contrast."

**修改为**:
> "We evaluated required sample sizes across the complete (p_A, p_B) integer lattice, not isolated examples."

---

**原句1.5** (Introduction末段):
> "This study maps validation-file phrases to planning contracts, evaluates **full-lattice** E2 surfaces with exact confirmation at small $n$, and calibrates guidance $n$ on ten public deposits against conventional 20."

**修改为**:
> "This study maps protocol phrases to sample size requirements using exact binomial methods and calibrates guidance on ten public datasets."

---

#### 🟡 **修改点11-20**（Methods）：

**原句2.1**:
> "This was an analytical study of prospective sample-size planning for Clinical and Laboratory Standards Institute (CLSI) EP17-A2 limit of detection (LoD) verification."

**修改为**:
> "We analyzed prospective sample size planning for CLSI EP17-A2 LoD verification."

---

**原句2.2** (公式前导):
> "For each claim we first obtained $n^{\ast}$ from asymptotic or exact binomial planning and then evaluated exact confirmation at that $n$."

**修改为**:
> "We calculated n* using asymptotic formulas and confirmed with exact binomial methods."

---

**原句2.3** (LoD定义重复):
> "**LoD$_{95}$ and the two 5% layers.** At $LoD_{95}$, $\Pr(\text{miss}\mid c^{\ast})=1-p_0=0.05$ under the Bernoulli model—the operational rare-miss probability that defines a detection limit. Sample-size planning adds the inferential layer..."

**修改为** (移到脚注):
> "LoD₉₅ corresponds to single-replicate detection probability p=0.95 (analytical 5% miss rate). Sample size planning adds inferential control (α, β).¹"

**脚注1**: "At LoD₉₅, Pr(miss|c*)=0.05 operationally; α=0.05 controls false rejection; β bounds miss probability under alternatives."

---

**原句2.4** (Eq. 3-4展示):
> "[删除完整公式展示，仅保留引用]"

**修改为**:
> "We related concentration to hit rate using logistic dose-response (Supplement Eq. S1)."

---

**原句2.5** (S0-S7流程):
> "Implementation followed an eight-step protocol (S0–S7 in software): lock claim (S0), confirm binary readout (S1), plan $n$ (S5), confirm at the design point with exact Fisher, Wilson/Clopper–Pearson, or binomial enumeration (S6), and report (S7)."

**修改为**:
> "Implementation followed an eight-step algorithm: claim specification (S0-S1), diagnostics (S2-S4), sample size planning (S5), exact confirmation (S6), and reporting (S7)."

---

#### 🟢 **修改点21-30**（Results & Discussion）：

**原句3.1** (Box 1):
> "**Box 1.** At $p=0.95$, a 19/20 rule with $n=20$ (E3) had $\Pr(\text{pass})=0.74$ (Table 9). For $\Pr(\text{pass}\mid p=0.95)\ge 0.95$ with cutoff 19, $n^{\ast}=22$ (Table 9b). For E1 at $p_0=0.95$ and $n=20$, one-sided Clopper–Pearson limits remained below 0.95 even with 20/20 positives (Table 8). Clinical and Laboratory Standards Institute (CLSI) EP17-A2 Section 7.3 minimum verification aligns with E3; reporting E3 pass as confirmation of $p\ge0.95$ (E1) overstates what was demonstrated."

**修改为** (删除Box，改为正文):
> "At p=0.95, a 19/20 rule (E3) passed with probability 0.74 at n=20 (Table 9), requiring n=22 for 95% pass probability. This E3 rule does not confirm p≥0.95 (E1 claim), which requires n≥24 (Table 8)."

**节省**: 95 → 38词

---

**原句3.2** (Box 2):
> "**Box 2 (lattice summary + reference pairs).** **Lattice @ $n=20$:** 61% of cells have $\beta>0.8$; median exact Fisher power 7.5%. **Design surface:** median $n^{\ast}=116$; at $\Delta=10$ pp median $n^{\ast}\approx199$; at $\Delta=40$ pp median $n^{\ast}=20$ (Table 3f). **Eight reference pairs** (Table 3) span contrasts from 4 to 49 pp; e.g. 90/50 needs $n^{\ast}=20$ per arm for 80% power whereas 90/80 needs $n^{\ast}\approx199$. **Asymptotic–exact gap:** pooled-$z$ can overstate Fisher power on many cells (778/1225 with gap $>0.05$; Table 3e)."

**修改为** (删除Box，简化为正文):
> "At n=20 per arm, 61% of lattice cells had miss probability β>0.8 (Fig 1B). Median required n* was 116 (range 20-435), rising sharply as contrast narrowed (Fig 1C inset; Table 3f). Asymptotic power formulas overestimated exact Fisher power in 778/1225 cells (Table 3e)."

**节省**: 110 → 48词

---

**原句4.1** (Discussion第2段):
> "Validation committees and laboratory information system (LIS) sign-off workflows rarely audit whether the detection claim was powered at the prespecified hit rates. Near-threshold calls on respiratory or sepsis panels can nonetheless turn on whether two lots were equivalent at the protocol verification concentration ($c^{\ast}$) or only documented as all-positive at folklore $n$."

**修改为**:
> "Validation workflows rarely audit whether detection claims were adequately powered. Near-threshold results may depend on whether lot equivalence was demonstrated or merely observed at conventional n."

**节省**: 60 → 28词

---

**原句4.2** (Discussion第3段开头):
> "For lot comparison at $c^{\ast}$ (E2), conventional $n=20$ per arm left most hit-rate pairs on the planning lattice with high miss probability ($\beta$) (Fig. 1B; Table 3)."

**修改为**:
> "For lot comparisons (E2), n=20 yielded high miss probability for most hit-rate pairs (Fig 1B; Table 3)."

**节省**: 35 → 20词

---

### Phase 2：词数压缩（3-4小时）

执行上述高优先级删减区域的修改。

### Phase 3：终审（1-2小时）

1. 通读全文，检查逻辑连贯性
2. 运行Grammarly检查被动语态和复杂句
3. 检查所有缩写首次出现时是否展开
4. 确认数字和引用准确性

---

## 五、技术清单（在修改文本前完成）

### 5.1 图表技术问题

```bash
# 1. 生成高分辨率TIFF (300+ dpi)
cd /Users/zhangdong/PycharmProjects/PythonProject/LOD
python scripts/export_high_res_figures.py  # 需创建此脚本

# 2. 色盲检查
# 上传 Fig1.png 到 https://www.color-blindness.com/coblis-color-blindness-simulator/
# 检查红绿色盲模式下是否可区分

# 3. 表格Word格式化
# 在Excel中打开CSV文件
# Table 3: 只保留6列（删除7列）
# Table 7: Citation列手动缩写为"First author et al."
```

### 5.2 文本文件准备

```bash
# 创建工作副本
cp manuscript/METHODS_BRIEF.md manuscript/METHODS_BRIEF_REVISION.md

# 备份当前版本
git add manuscript/METHODS_BRIEF.md
git commit -m "Pre-revision backup: 4645 words"
```

---

## 六、修改时间表

| 日期 | 任务 | 预计时间 | 责任人 |
|------|------|---------|--------|
| Day 1上午 | 修改点1-10（Introduction AI痕迹） | 2h | 您 |
| Day 1下午 | 修改点11-20（Methods压缩） | 2h | 您 |
| Day 2上午 | 修改点21-30（Results/Discussion） | 2h | 您 |
| Day 2下午 | 词数验证 + 图表技术处理 | 3h | 您 |
| Day 3 | 终审 + 同行预读反馈 | 4h | 您+合作者 |

**预计总时间**: 13-15小时工作量

---

## 七、质量检查清单（提交前）

### 文本质量：
- [ ] 词数≤3500（不含abstract/references/tables/legends）
- [ ] Abstract≤250词
- [ ] Brief Summary≤100词 + 含作者拼音
- [ ] 所有缩写首次使用时展开（每个section独立）
- [ ] 无markdown残留（`[link](url)`，code blocks）
- [ ] 无AI典型句式（见3.1节特征1-5）
- [ ] 被动语态≤20%（Grammarly检查）
- [ ] 句子长度≤25词平均（Hemingway Editor检查）

### 图表质量：
- [ ] Fig 1-2为TIFF格式，≥300 dpi
- [ ] 色盲友好（通过色盲模拟器测试）
- [ ] 面板标签A-D在左上角10pt黑体
- [ ] 图例字体≥8pt（打印后可读）
- [ ] Alt text已添加到legends页面
- [ ] Table 1-3-7为Word表格格式
- [ ] Table 3数字精度≤3位小数
- [ ] Table 7 citation缩写

### 格式符合性：
- [ ] 主文≤6项（当前5项✅）
- [ ] References≤40条（当前40条✅）
- [ ] Vancouver编号格式
- [ ] 图例单独页（含alt text）
- [ ] 表格在references后单独页
- [ ] 无补充材料图表混入主文

---

## 八、下一步行动（立即开始）

### 今天完成（Day 1）：

1. **创建修订文件**：
```bash
cd /Users/zhangdong/PycharmProjects/PythonProject/LOD
cp manuscript/METHODS_BRIEF.md manuscript/METHODS_BRIEF_REVISION.md
```

2. **开始Introduction修改**（使用上述修改点1.1-1.5）：
   - 打开`METHODS_BRIEF_REVISION.md`
   - 找到Introduction第1段
   - 逐句对照本文档"三、3.2节"进行修改
   - 每修改完一段运行`wc -w`检查词数下降

3. **Methods公式删减**：
   - 保留Eq. (2)
   - Eq. (3)-(5)移到Supplement
   - 添加脚注："Full dose-response model: Supplement Eq. S1-S3"

4. **删除Box 1-2**：
   - 用修改点3.1-3.2的简化版本替换

**今日目标**: 词数从4645 → 约4000（删减15%）

---

## 九、常见问题

**Q1: 删除这么多内容会不会影响科学完整性？**  
A: 不会。删除的是冗余解释和重复定义，核心科学内容（理论、数据、结论）完全保留。期刊审稿人更看重简洁表达。

**Q2: 如何判断修改后是否"去AI化"成功？**  
A: 三个标准：
1. Grammarly Tone检测："Formal"→"Conversational"
2. 句子长度：平均≤20词
3. 破折号和em dash使用≤5处/全文

**Q3: Table 7的citation太长怎么处理？**  
A: 手动缩写示例：
- 原: "Carobene A. et al. Commutability of Lombardy Region EQA control materials..."
- 改为: "Carobene et al. (2024)"
- 完整引用放references列表

**Q4: 如果删减后仍超3500词怎么办？**  
A: 启用备用删减方案：
- 将Discussion限制性段落移到Supplement
- Introduction删除第2段（EP17背景）→简化为一句话
- Methods删除Formal results段落→仅保留Supplement引用

---

## 十、成功标准

修改完成后，您的文稿应该：

✅ **词数**: ≤3500  
✅ **可读性**: Flesch Reading Ease ≥50  
✅ **AI痕迹**: 通过GPTZero检测（AI概率<30%）  
✅ **图表**: 符合CC技术要求  
✅ **格式**: 符合ScholarOne上传清单  

**最终目标**: 2-3天内完成修订，进入内部审阅阶段。

---

## 附录A：快速参考句式替换表

| AI痕迹句式 | 修改后句式 |
|-----------|-----------|
| "What has not been X—and what this work contributes—is Y" | "This work provides Y" |
| "This is not X. It is Y." | "The framework provides Y rather than X." |
| "Before data collection, the laboratory should lock..." | "Before data collection, specify..." |
| "We asked what...and how..." | "We evaluated..." |
| "—not a single illustrative contrast" | "across the complete lattice" |
| "each protocol phrase as a statement about..." | "protocol phrases as statements about..." |
| "Operationally, X names..." | "At X,..." |
| "That analytical 5% is the physical meaning of..." | "This 5% defines..." |

---

**文档状态**: 初稿完成，等待您开始执行修改  
**预期完成时间**: 3个工作日  
**下次更新**: 完成Phase 1后更新进度
