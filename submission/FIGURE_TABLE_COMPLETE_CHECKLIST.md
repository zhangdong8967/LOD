# 图表完整清单与检查

**检查日期**: 2026年8月24日  
**投稿期刊**: Clinical Chemistry

---

## 一、主文图表（2图+3表，共5个） ✅

### Figure 1: LoD replicate planning

**文件**: `submission/Fig1_lod_replicate_planning.tif`  
**大小**: 4.7M ✅  
**格式**: TIFF (300+ dpi) ✅  
**面板**: 4个 (A, B, C, D)

#### 面板说明
- **Panel A**: Dose-response curve (concentration vs detection probability)
  - X轴: log(concentration)
  - Y轴: Detection probability (0-1)
  - 显示: Logistic fit + data points

- **Panel B**: E2 lattice β>0.8 heatmap
  - X轴: pB (50-99%)
  - Y轴: pA (50-99%)
  - 颜色: Red = β>0.8 (underpowered), Blue = β≤0.8
  - 标注: "61% cells β>0.8"

- **Panel C**: E2 lattice n* per arm heatmap
  - X轴: pB (50-99%)
  - Y轴: pA (50-99%)
  - 颜色渐变: 20-435
  - 标注: "Median n*=116"

- **Panel D**: Example logistic curve fit
  - X轴: Concentration
  - Y轴: Detection probability
  - 显示: Fit quality for tier A data

**引用位置**:
- Abstract: "enumerated exact Fisher surfaces... (Fig 1B-C)"
- Results: "Fig. 1B", "Fig. 1C"

**状态**: ✅ 文件存在

---

### Figure 2: Tier A calibration

**文件**: `submission/Fig2_tierA_calibration.tif`  
**大小**: 688K ✅  
**格式**: TIFF (300+ dpi) ✅  
**面板**: 3个 (A, B, C)

#### 面板说明
- **Panel A**: qPCR empirical detection curves
  - 显示: 3-4条qPCR浓度-检出率曲线
  - Y轴: Detection rate
  - X轴: Concentration (log scale)
  - 标注: Steep curves near LoD

- **Panel B**: Required/reported n ratios (bar chart)
  - X轴: Tier A deposits (9个)
  - Y轴: n_guidance / n_reported
  - 显示: 比率条形图
  - 参考线: y=1 (folklore 20)
  - 范围: 2.65-9.95

- **Panel C**: Protocol-specific E2 pairs (8对)
  - X轴: (pA, pB) pairs
  - Y轴: Required n* per arm
  - 显示: 8个点
  - 中位数线: 3.9× folklore 20

**引用位置**:
- Results: "Fig. 2A", "Fig. 2B", "Fig. 2C"
- Discussion: "Fig. 2"

**状态**: ✅ 文件存在

---

### Table 1: Detection claim structures

**内容**: E1/E2/E3定义（需修改列标题）  
**列**: Claim type | Estimand | Decision criterion | Example  
**行数**: 3行（benchmark confirmation, two-arm comparison, qualitative pass criteria）

**当前列标题（需修改）**:
- ❌ "E1: Benchmark confirmation"
- ❌ "E2: Two-arm comparison"
- ❌ "E3: Qualitative pass criteria"

**修订列标题**:
- ✅ "Benchmark confirmation"
- ✅ "Two-arm comparison"
- ✅ "Qualitative pass criteria"

**引用位置**: Methods第1段

**文件位置**: `submission/Tables_main.docx` (应包含)

**状态**: ⚠️ 需打开检查并修改标题

---

### Table 2: Protocol-specific E2 pairs (原Table 3)

**内容**: 8个(pA,pB)对的样本量要求  
**列**: pA | pB | Δ | n*(asymp) | n*(exact) | n_20 power | Source  
**行数**: 8行

**数据示例**:
```
pA    pB    Δ     n*_exact  n_20_power  Source
0.90  0.80  0.10  199       0.42        EP17 estradiol
0.95  0.85  0.10  ...       ...         qPCR wt
0.90  0.75  0.15  ...       ...         qPCR multiplex
...
```

**关键统计**: 中位数比率 = 3.9× (vs folklore 20)

**引用位置**: 
- Results: "Table 2" (多次)
- Fig. 2C配套

**文件位置**: `submission/Tables_main.docx` (应包含)

**状态**: ⚠️ 需打开检查

---

### Table 3: Tier A guidance n summary (原Table 7)

**内容**: 10个tier A deposits的审计结果  
**列**: Source | Claim type | n_reported | n_guidance | Ratio | Note  
**行数**: 10行

**数据示例**:
```
Source              Claim   n_rep  n_guid  Ratio  Note
EP17 estradiol      E1      20     53      2.65   Immunoassay
EP17 probit         E2      20     116     5.80   Concentration-detect
qPCR wt             E2      20     199     9.95   Molecular
...
```

**关键统计**: 9/10超过20，比率2.65-9.95

**引用位置**: 
- Abstract: "Table 3"
- Results: "Table 3" (多次)

**文件位置**: `submission/Tables_main.docx` (应包含)

**状态**: ⚠️ 需打开检查，确认Claim列用描述名称非E1/E2/E3

---

## 二、Supplement图表

### Supplementary Tables (7个大表，多个子表)

#### Table 2: S0-S7 pipeline decision map
**内容**: 算法流程图（Step → Decision → Next）  
**位置**: Online_Supplement.pdf  
**引用**: Supplement §S2f

#### Table 3: E2 lattice full grid
**子表**:
- 3a: Full 1225-cell grid (CSV附件)
- 3b: Summary by pA
- 3c: Summary by pB
- 3d: Summary by Δ
- **3e**: Asymptotic vs exact comparison (778 cells differ) ⭐
- **3f**: Summary statistics by Δ bins ⭐

**关键数据** (Table 3f):
```
Δ range    Median n*  % β>0.8  Notes
0.01-0.05  350        95%      Very close pairs
0.06-0.10  116        75%      Near-LoD typical
0.11-0.15  65         50%      Moderate difference
>0.15      30         20%      Large difference
```

**引用位置**: Results多次引用3e, 3f

#### Table 4: Theory certificates P1-P18
**内容**: 18个命题 + 5个定理 + 4个补充定理 = 27个  
**列**: Proposition | Statement | Status | Method  
**引用**: Supplement §S2b

#### Table 5: Public data sources
**内容**: 10 tier A + 3 tier B数据集详细信息  
**列**: ID | Family | Platform | Tier | DOI | Note  
**引用**: Methods最后一段

#### Table 6: Type I error simulation
**内容**: H₀下Type I error率（n=20, 1000次模拟）  
**列**: (pA=pB) | Observed α | CI_95 | Expected α=0.05  
**数据**: 0.046 [0.035, 0.059] 包含0.05 ✓  
**引用**: Supplement §S2d

#### Table 7b: 16 audit rows详细信息 ⭐⭐⭐
**内容**: 16行完整审计记录（10 tier A + 6其他）  
**列**: Row | Source | Verbatim claim | Mapped type | n_rep | n_req | p_A | p_B | Power | Note

**非常重要！这是审计证据的核心表**

**引用位置**: 
- Abstract: "Supplementary Table 7b"
- Methods: "Supplement Table 7b"
- Results: "Supplementary Table 7b"

**数据示例**:
```
Row  Source             Claim_verbatim                 Type  n_rep  n_req  Ratio
1    EP17 estradiol     "19/20 at LoD"                E1    20     53     2.65
2    EP17 probit        "equivalent lots"              E2    20     116    5.80
3    qPCR wt            "confirm 95% at c*"           E1    20     199    9.95
...
16   Hospital PCR       "95% detection (19/20)"       E1    20     ...    ...
```

**状态**: ⚠️ 需确认Mapped type列使用描述名称非E1/E2/E3

#### Table 8: E1 Clopper-Pearson
**子表**:
- 8a: CP lower limits for k/n combinations
- 8b: Sample size for p0=0.95 confirmation

**数据示例** (8a):
```
k/n      CP_lower   Satisfies p0≥0.95?
20/20    0.8609     No
21/21    0.8649     No
...
53/53    0.9500     Yes ✓
```

**引用位置**: Results "Supplementary Table 8"

#### Table 9: E3 binomial pass probabilities
**子表**:
- **9a**: P(X≥k|n,p) for various k/n rules
- **9b**: Required n for target pass probability
- **9c**: E2 vs E3 comparison scenarios

**关键数据** (9a):
```
Rule    n   k   p=0.95  p=0.90  p=0.85
19/20   20  19  0.736   0.392   0.176
20/20   20  20  0.358   0.122   0.039
```

**引用位置**: 
- Results: "Supplementary Table 9", "9b", "9c"

---

### Supplementary Figures (9个)

#### Fig. S1: Normality diagnostics
- Q-Q plot
- Shapiro-Wilk test results

#### Fig. S2: Skewness/kurtosis
- Distribution comparison

#### Fig. S3: Censoring analysis
- Left-censored data handling

#### Fig. S4: Heterogeneity check
- Levene test results

#### Fig. S5-S7: Operating characteristic curves
- S5: E1 OC curves (various n)
- S6: E2 OC curves (power vs Δ)
- S7: E3 OC curves (pass probability vs n)

#### Fig. S8: Design effect sensitivity
- ICC影响图

#### Fig. S9: Boschloo vs Fisher power
- 两种精确检验比较

---

## 三、支持文件

### Figure_legends.docx (13K)

**应包含内容**:
```
Figure 1. LoD replicate planning and lattice analysis.
(A) Dose-response curve showing...
(B) E2 lattice heatmap showing β>0.8 regions...
(C) E2 lattice heatmap showing required n* per arm...
(D) Example logistic curve fit for tier A qPCR data...

Figure 2. Tier A calibration and protocol audit.
(A) Empirical qPCR detection curves...
(B) Required-to-reported sample-size ratios...
(C) Protocol-specific E2 probability pairs...
```

**状态**: ⚠️ 需打开检查内容完整性

---

### Tables_main.docx (12K)

**应包含**:
- Table 1: Detection claim structures (3行)
- Table 2: Protocol-specific E2 pairs (8行) ← 原Table 3
- Table 3: Tier A guidance n summary (10行) ← 原Table 7

**格式要求**:
- 每个表独立页
- 标题在表上方
- 注释在表下方
- 无边框或简单边框

**状态**: ⚠️ 需打开完整检查

---

### Online_Supplement.pdf (150K)

**应包含**:
1. **Supplementary Methods** (§S2a-S2f)
   - §S2a: Estimand framework
   - §S2b: Theory certificates detailed proofs
   - §S2c: Dose-response modeling
   - §S2d: Exact inference procedures
   - §S2e: Design effect calculations
   - §S2f: Software map

2. **All Supplementary Tables** (2, 3a-3f, 4, 5, 6, 7b, 8a-8b, 9a-9c)

3. **All Supplementary Figures** (S1-S9)

4. **CSV附件** (可选，或单独上传)
   - Table 3a full grid (1225行)

**状态**: ⚠️ 需打开检查章节完整性

---

## 四、引用一致性检查

### Figure引用格式统一

**推荐**: "Fig. 1A" (主文), "Fig. S1" (Supplement)

**需全文查找替换**:
```
查找: "Fig 1"        → 替换为: "Fig. 1"
查找: "Fig 2"        → 替换为: "Fig. 2"
查找: "Figure 1"     → 替换为: "Fig. 1" (正文中)
查找: "figure 1"     → 替换为: "Fig. 1"
```

**例外**: 图例标题保留"Figure 1"

---

### Table引用格式统一

**推荐**: "Table 3", "Supplementary Table 9"

**需全文查找替换**:
```
查找: "table "            → 替换为: "Table "
查找: "Supplement Table"  → 替换为: "Supplementary Table"
```

---

### Panel引用格式统一

**推荐**: "Fig. 1A" (无空格)

**需统一**:
- ❌ "Fig. 1 A" → ✅ "Fig. 1A"
- ❌ "Fig.1A" → ✅ "Fig. 1A"

---

## 五、投稿上传顺序

### ScholarOne文件上传清单

```
1. Cover_letter.docx              (15K)  ✅
2. Clinical_Chemistry_submission.docx (25K)  ✅ (主稿)
3. Fig1_lod_replicate_planning.tif (4.7M) ✅
4. Fig2_tierA_calibration.tif     (688K) ✅
5. Figure_legends.docx            (13K)  ⚠️ 需检查
6. Tables_main.docx               (12K)  ⚠️ 需检查
7. Online_Supplement.pdf          (150K) ⚠️ 需检查
```

**文件类型要求**:
- 主稿: .docx
- 图: .tif (TIFF, 300+ dpi, RGB或CMYK)
- 表: .docx (可嵌入主稿或独立)
- Supplement: .pdf

---

## 六、最终检查任务清单

### 高优先级 🔴

- [ ] **打开Tables_main.docx**，确认包含Table 1, 3, 7
- [ ] **Table 1**: 修改列标题，去除E1/E2/E3标签
- [ ] **Table 7**: 确认Claim列用描述名称
- [ ] **打开Figure_legends.docx**，确认图例完整
- [ ] **打开Online_Supplement.pdf**，确认所有表和图都在
- [ ] **Supplementary Table 7b**: 确认16行数据完整

### 中优先级 🟡

- [ ] **全文搜索**: "Fig 1" → "Fig. 1"
- [ ] **全文搜索**: "Fig 2" → "Fig. 2"
- [ ] **全文搜索**: "table " → "Table "
- [ ] **全文搜索**: "Supplement Table" → "Supplementary Table"
- [ ] **检查**: 所有图表引用连续无跳号

### 低优先级 🟢

- [ ] **Fig1.tif**: 打开检查分辨率>300dpi
- [ ] **Fig2.tif**: 打开检查分辨率>300dpi
- [ ] **Figure legends**: 检查alt text（可访问性）
- [ ] **Supplement**: 检查书签/目录

---

## 七、常见问题排查

### Q1: Table 1的E1/E2/E3标签在哪里？
**A**: 可能在：
- 列标题（第一列）
- 行标题
- 表格标题
- 表注

**修改**: 全部改为描述性名称

### Q2: Supplementary Table 7b的Claim type列？
**A**: 应显示：
- "Benchmark confirmation" (不是"E1")
- "Two-arm comparison" (不是"E2")
- "Qualitative pass criterion" (不是"E3")

### Q3: 图表编号跳号？
**A**: 主文只有Fig 1-2, Table 1,3,7（不连续，正常）
Supplement: 所有表2-9, 图S1-S9（连续）

### Q4: Supplement PDF文件大小限制？
**A**: Clinical Chemistry通常允许<10MB
当前150K远低于限制 ✓

---

## 八、图表质量标准

### Figure质量要求
- ✅ 分辨率: ≥300 dpi
- ✅ 格式: TIFF (首选) 或 EPS
- ✅ 颜色: RGB (在线) 或 CMYK (印刷)
- ✅ 字体: 嵌入或转曲
- ✅ 线宽: ≥0.5 pt
- ✅ 文字大小: 8-12 pt

### Table质量要求
- ✅ 格式: Word表格或文本表格
- ✅ 边框: 简单（顶/底线）
- ✅ 对齐: 数字右对齐，文字左对齐
- ✅ 注释: 表下方，用 a, b, c标注
- ✅ 缩写: 在表注中解释

---

**检查完成日期**: 2026年8月24日  
**文件总数**: 7个投稿文件 + 多个Supplement组件  
**状态**: ✅ 主图存在，⚠️ 需检查3个docx文件内容
