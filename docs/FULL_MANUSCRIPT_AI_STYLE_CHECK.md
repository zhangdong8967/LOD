# 全文AI风格检查与调整建议

**检查日期**: 2026年8月24日  
**范围**: Introduction, Results, Discussion + 图表清单

---

## 一、Introduction AI风格检查

### ✅ 整体评估: **已经很自然，仅需微调**

您的Introduction写得很好，基本没有AI痕迹。以下是微小建议：

### 建议微调的地方

#### 1. 第1段 - EP17/EP26引用
**当前（第1段末尾）**:
```
CLSI EP17-A2 provides a framework for evaluating and verifying 
detection capability, including the limit of detection (LoD), 
whereas CLSI EP26 addresses acceptance of a new reagent lot. 
Neither framework establishes a single replicate count for all 
measurement procedures.
```

**微调建议（可选）**:
```
CLSI EP17-A2 provides a framework for evaluating and verifying 
detection capability, including the limit of detection. CLSI EP26 
addresses acceptance of new reagent lots. Neither document 
establishes a universal replicate count; both permit procedure-
specific design.
```
**理由**: 稍微简化，更流畅

#### 2. 第2段 - "5%"区分
**当前（很好）**:
```
A separate issue is the distinction between the analytical 
characteristic being verified and the statistical properties 
of the verification study. An LoD is commonly defined as the 
concentration associated with a specified probability of 
detection, often 95%. At a 95% detection probability, an 
individual replicate has a 5% probability of non-detection 
under the stated conditions. This describes assay performance 
at the LoD; it does not describe the probability that a finite 
verification study will correctly support or reject the claim.
```

**评价**: ✅ 已经很好，无需修改。这段是核心，写得非常清楚。

#### 3. 第3段 - 19/20规则
**当前（很好）**:
```
An observed detection proportion therefore should not be 
interpreted as a measure of verification power. A rule requiring 
19 of 20 replicates to be positive defines an observed-result 
criterion but does not, by itself, specify a target type II 
error rate or statistical power.
```

**评价**: ✅ 逻辑清晰，无需修改

#### 4. 第4段 - 研究目标
**当前（很好）**:
```
We therefore evaluated the operating characteristics of fixed-
size verification designs across a broad range of detection 
probabilities, derived claim-specific sample-size requirements 
using exact binomial methods, and examined whether published 
validation protocols and institutional verification records 
were aligned with those requirements.
```

**评价**: ✅ 完整清晰，无需修改

### Introduction总结
- **AI痕迹**: 0处 ✅
- **需要修改**: 0处必需，1处可选（第1段简化）
- **质量评分**: 5/5

---

## 二、Results AI风格检查

### ⚠️ 需要调整：小标题和E2/E3标签

您的Results部分有一些小标题使用了"E2:", "E3:", "E1:"，这是主要的AI痕迹。

### 当前小标题结构（需修改）

```
Exact operating characteristics across the detection-probability lattice

E2: Lot comparison at the limit of detection
[内容...]

E3: Fixed pass criteria
[内容...]

E1: Benchmark confirmation
[内容...]

Retrospective audit of validation records

Tier A protocol-file audit

Hospital and published validation records
```

**问题**: "E2:", "E3:", "E1:"标签显眼

### 修订建议

#### 修订版小标题
```
Exact operating characteristics across the detection-probability lattice

Two-arm lot comparison at the limit of detection
[内容...]

Fixed pass criteria and observed positivity
[内容...]

Benchmark confirmation of detection probability
[内容...]

Retrospective audit of validation records

Tier A protocol-file audit

Hospital and published validation records
```

### Results段落修改示例

#### ❌ 修改前（第1个小标题下）
```
E2: Lot comparison at the limit of detection

At 20 replicates per arm, the exact 2-sided Fisher test had 
a type II error probability (β) >0.80 in 61% of the 1,225 
lattice cells (Fig. 1B; Table 3). Thus, the corresponding 
statistical power was <20% in these cells...
```

#### ✅ 修改后
```
Two-arm lot comparison at the limit of detection

For two-arm comparisons at 20 replicates per arm, the exact 
2-sided Fisher test had a type II error probability (β) 
exceeding 0.80 in 61% of the 1,225 lattice cells (Fig. 1B; 
Table 3). The corresponding statistical power was therefore 
below 20% in these cells...
```

**改进**:
- 去除"E2:"标签
- 小标题更描述性
- 开头更自然（"For two-arm comparisons..."）

#### ❌ 修改前（E3部分）
```
E3: Fixed pass criteria

The 19-of-20 criterion was evaluated as an E3 binomial pass 
rule. When the true detection probability was 0.95, the 
probability of satisfying the criterion in a 20-replicate 
experiment was 0.736 (73.6%) (Supplementary Table 9).
```

#### ✅ 修改后
```
Fixed pass criteria and observed positivity

The 19-of-20 criterion was evaluated as a qualitative pass 
rule. When the true detection probability was 0.95, the 
probability of satisfying the criterion in a 20-replicate 
experiment was 0.736 (73.6%) (Supplementary Table 9).
```

**改进**:
- 去除"E3"标签
- "qualitative pass rule"代替"E3 binomial pass rule"

#### ❌ 修改前（E1部分）
```
E1: Benchmark confirmation

E1 was evaluated using the lower one-sided 95% Clopper–
Pearson confidence limit for the detection probability at 
the claimed concentration. With 20 of 20 positive results 
at a nominal detection probability of 0.95, the lower 
confidence limit remained below 0.95, and the E1 
confirmation criterion was therefore not met at n=20 
(Supplementary Table 8).
```

#### ✅ 修改后
```
Benchmark confirmation of detection probability

Benchmark confirmation was evaluated using the lower one-
sided 95% Clopper–Pearson confidence limit for the detection 
probability at the claimed concentration. With 20 of 20 
positive results at a nominal detection probability of 0.95, 
the lower confidence limit remained below 0.95, and the 
confirmation criterion was therefore not met at n=20 
(Supplementary Table 8).
```

**改进**:
- 去除"E1:"标签和段中"E1"引用
- 用"benchmark confirmation"代替"E1 confirmation"

### Results中其他需要检查的地方

#### Table引用一致性
**搜索以下模式并统一**:
- "Table 3" vs "table 3" → 统一为"Table 3"
- "Supplementary Table 9" vs "Supplement Table 9" → 统一为"Supplementary Table"
- "Fig. 1B" vs "Fig 1B" → 统一为"Fig. 1B"（带句号）

### Results总结
- **AI痕迹**: "E1:", "E2:", "E3:"标签（3处）
- **需要修改**: 3个小标题 + 段内E1/E2/E3引用（约6处）
- **质量评分**: 3/5 → 修改后5/5

---

## 三、Discussion AI风格检查

### ✅ 整体评估: **已经很自然，仅1-2处微调**

您的Discussion写得非常好，几乎没有AI痕迹。

### 需要检查的地方

#### 1. 第1段总结
**当前（很好）**:
```
This study examined whether a fixed replicate count provides 
sufficient statistical evidence for the specific detection 
claims stated in laboratory verification protocols. Three 
findings were consistent across the prespecified analyses...
```

**评价**: ✅ 开门见山，清晰有力，无需修改

#### 2. 第2段 - EP17防御
**当前（非常好）**:
```
These results do not indicate that CLSI EP17-A2 establishes 
an inappropriate universal replicate count. EP17-A2 specifies 
a minimal verification design for a claimed LoD and explicitly 
allows additional measurements or design factors when greater 
power is desired. The distinction is important because...
```

**评价**: ✅ 这段是关键防御，写得完美，绝对不要改

#### 3. 第3段 - E1/E2/E3讨论
**当前**:
```
The separation of E1, E2, and E3 was central to this analysis. 
E1 concerns confirmation of a prespecified detection-probability 
benchmark; E2 concerns a difference between 2 detection 
probabilities; and E3 concerns the probability of meeting a 
fixed observed-result rule. These are different inferential 
events even when the protocol language refers to the same 
nominal LoD or 95% detection probability. In particular, the 
19-of-20 criterion evaluated here should be interpreted as an 
E3 acceptance rule rather than as a synonym for the EP17-A2 
verification procedure.
```

**微调建议**:
```
The separation of these three claim structures was central to 
this analysis. Benchmark confirmation concerns a prespecified 
detection-probability target; two-arm comparison concerns a 
difference between detection probabilities; and qualitative 
pass criteria concern the probability of meeting a fixed 
observed-result rule. These are different inferential events 
even when the protocol language refers to the same nominal LoD 
or 95% detection probability. In particular, the 19-of-20 
criterion evaluated here should be interpreted as a qualitative 
acceptance rule rather than as a synonym for the EP17-A2 
verification procedure.
```

**改进**:
- 去除"E1, E2, and E3"标签
- 用描述性名称
- 最后一句"E3"→"qualitative"

#### 4. 其余段落
**第4段（临床化学相关性）**: ✅ 完美，无需修改  
**第5段（精确vs渐近）**: ✅ 完美，无需修改  
**第6段（审计解释）**: ✅ 完美，无需修改  
**第7段（前瞻性应用）**: ✅ 完美，无需修改

### Discussion总结
- **AI痕迹**: 1段有E1/E2/E3标签
- **需要修改**: 1段（第3段）
- **质量评分**: 4.5/5 → 修改后5/5

---

## 四、图表清单与检查

### 主文图表（2图+3表=5个，符合Clinical Chemistry要求）

#### Figure 1: LoD replicate planning
**文件**: `submission/Fig1_lod_replicate_planning.tif` (4.7M) ✅  
**面板**: A-D (4个面板)  
**引用位置**: Abstract, Results  
**说明**: 
- Panel A: Dose-response curve
- Panel B: E2 lattice β>0.8 heatmap
- Panel C: E2 lattice n* heatmap
- Panel D: Logistic curve fit
**状态**: ✅ 文件存在

#### Figure 2: Tier A calibration
**文件**: `submission/Fig2_tierA_calibration.tif` (688K) ✅  
**面板**: A-C (3个面板)  
**引用位置**: Results  
**说明**:
- Panel A: qPCR empirical curves
- Panel B: Required/reported n ratios
- Panel C: Protocol-specific E2 pairs
**状态**: ✅ 文件存在

#### Table 1: Detection claim structures
**说明**: E1/E2/E3定义表（需修改标题去除E1/E2/E3标签）  
**引用位置**: Methods  
**列**: Claim type, Estimand, Decision criterion, Example  
**状态**: ⚠️ 需检查是否在Tables_main.docx中

#### Table 3: Protocol-specific E2 pairs
**说明**: 8个(pA,pB)对的n*和比率  
**引用位置**: Results, Fig 2C  
**状态**: ⚠️ 需检查是否在Tables_main.docx中

#### Table 7: Tier A guidance n summary
**说明**: 10个tier A deposits的n_required vs n_reported  
**引用位置**: Abstract, Results  
**状态**: ⚠️ 需检查是否在Tables_main.docx中

### Supplement图表

#### Supplement Tables (7个)
- **Table 2**: S0-S7 pipeline decision map
- **Table 3**: E2 lattice full grid (3a-3f子表)
  - 3e: Asymptotic vs exact comparison
  - 3f: Summary by Δ
- **Table 4**: Theory certificates P1-P18
- **Table 5**: Public data sources
- **Table 6**: Type I error simulation
- **Table 7b**: 16 audit rows详细信息（重要！）
- **Table 8**: E1 Clopper-Pearson
- **Table 9**: E3 binomial pass probabilities (9a-9c子表)

#### Supplement Figures (9个)
- **Fig S1-S4**: 诊断图
- **Fig S5-S7**: OC曲线
- **Fig S8-S9**: 敏感性分析

### 图表文件检查清单

```bash
submission/
├── Fig1_lod_replicate_planning.tif    ✅ 4.7M
├── Fig2_tierA_calibration.tif         ✅ 688K
├── Figure_legends.docx                ✅ 13K (图例文件)
├── Tables_main.docx                   ✅ 12K (主表文件)
└── Online_Supplement.pdf              ✅ 150K (Supplement)
```

### 需要确认的事项

1. **Tables_main.docx包含**:
   - [ ] Table 1 (Detection claim structures)
   - [ ] Table 3 (Protocol-specific E2 pairs, 8行)
   - [ ] Table 7 (Tier A summary, 10行)

2. **Figure_legends.docx包含**:
   - [ ] Figure 1 legend (描述A-D面板)
   - [ ] Figure 2 legend (描述A-C面板)

3. **Online_Supplement.pdf包含**:
   - [ ] All Supplementary Tables (2-9)
   - [ ] All Supplementary Figures (S1-S9)
   - [ ] Methods补充 (§S2a-S2f)

---

## 五、图表引用一致性检查

### 需要统一的格式

#### Figure引用格式
**推荐**: "Fig. 1A" (带句号，无空格)  
**需统一**:
- ❌ "Fig 1A" → ✅ "Fig. 1A"
- ❌ "Figure 1A" → ✅ "Fig. 1A" (正文中)
- ✅ "Figure 1" (图例标题中保留)

#### Table引用格式
**推荐**: "Table 3" (首字母大写)  
**需统一**:
- ❌ "table 3" → ✅ "Table 3"
- ✅ "Supplementary Table 9" (一致)

#### Supplement引用格式
**推荐**: "Supplementary Table" (不缩写)  
**需统一**:
- ⚠️ "Supplement Table 7b" → ✅ "Supplementary Table 7b"
- ✅ "Supplementary Table 3e" (一致)

---

## 六、修改优先级

### 🔴 高优先级（必须修改）
1. **Results小标题**: 去除E1/E2/E3标签 (3处)
2. **Results段内**: 去除"E1/E2/E3"引用 (约6处)
3. **Discussion第3段**: 去除E1/E2/E3标签 (1段)

### 🟡 中优先级（强烈建议）
4. **图表引用一致性**: 统一Fig./Table格式 (全文)
5. **Table 1标题**: 去除E1/E2/E3列标签（如有）

### 🟢 低优先级（可选）
6. **Introduction第1段**: 微调EP17/EP26句子
7. **检查Tables_main.docx**: 确认3个表都在

---

## 七、完整修改检查清单

### Introduction
- [ ] 通读一遍，确认无E1/E2/E3标签
- [ ] （可选）第1段EP17/EP26微调
- [ ] 确认引用编号连续

### Methods
- [x] 已完成修改（之前的工作）
- [ ] 替换到稿件中
- [ ] 检查公式格式

### Results
- [ ] 修改3个小标题（去除E1:/E2:/E3:）
- [ ] 修改段内E1/E2/E3引用（~6处）
- [ ] 统一图表引用格式
- [ ] 确认Table 3, Table 7引用正确

### Discussion
- [ ] 修改第3段（去除E1/E2/E3标签）
- [ ] 确认其他段落无AI痕迹
- [ ] 检查引用编号

### 图表文件
- [ ] 确认Fig1.tif, Fig2.tif存在且完整
- [ ] 打开Tables_main.docx检查3个表
- [ ] 打开Figure_legends.docx检查图例
- [ ] 打开Online_Supplement.pdf检查内容

---

## 八、快速修改脚本（搜索替换）

### 在Word中使用查找替换

```
查找: "E1:"
替换为: "Benchmark confirmation:"

查找: "E2:"
替换为: "Two-arm comparison:"

查找: "E3:"
替换为: "Fixed pass criteria:"

查找: " E1 "
替换为: " benchmark confirmation "

查找: " E2 "
替换为: " two-arm comparison "

查找: " E3 "
替换为: " qualitative pass criterion "

查找: "E1 confirmation"
替换为: "benchmark-confirmation"

查找: "E1 records"
替换为: "benchmark-confirmation records"

查找: "E2 records"
替换为: "two-arm records"

查找: "E3 records"
替换为: "qualitative-pass-criteria records"

查找: "Fig 1"
替换为: "Fig. 1"

查找: "Fig 2"
替换为: "Fig. 2"

查找: "table "
替换为: "Table "

查找: "Supplement Table"
替换为: "Supplementary Table"
```

**注意**: 
- 替换前先全文保存备份
- 逐个确认，不要全部替换
- "E1-E3"在某些上下文中可保留（如"three claim structures (E1-E3)"）

---

## 九、最终输出文件

我将创建3个修订文件：
1. `RESULTS_REVISED_NATURAL.md` - Results部分完整修订版
2. `DISCUSSION_REVISED_NATURAL.md` - Discussion部分完整修订版
3. `FIGURE_TABLE_CHECKLIST.md` - 图表完整清单和检查

---

**检查完成日期**: 2026年8月24日  
**总AI痕迹**: ~10处（主要在Results）  
**修改预计时间**: 30分钟  
**修改后质量**: 5/5全文
