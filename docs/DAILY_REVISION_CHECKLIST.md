# 每日修改检查清单

**目标**: 3天内完成文稿修改，达到Clinical Chemistry投稿标准

---

## Day 1 - Introduction & Methods 修改（今天）

### 上午任务 (2-3小时)

#### ✅ 准备工作 (15分钟)
- [ ] 备份当前版本: `cp manuscript/METHODS_BRIEF.md manuscript/METHODS_BRIEF_v1_backup.md`
- [ ] 创建工作副本: `cp manuscript/METHODS_BRIEF.md manuscript/METHODS_BRIEF_REVISION.md`
- [ ] 打开修改计划: `docs/MANUSCRIPT_REVISION_PLAN.md`

#### 📝 Introduction修改 (90分钟)

**段落1** - 压缩开场（当前66词 → 目标38词）
- [ ] 删除"When a laboratory signs off..."冗长从句
- [ ] 合并"One file may...Another may..."为单句
- [ ] 检查词数: `wc -w` 确认≤40词

**段落2** - 简化LoD定义（当前55词 → 目标28词）
- [ ] 删除"which classify each replicate..."解释性从句
- [ ] CLSI EP17-A2首次出现后可简写
- [ ] 检查词数: 确认≤30词

**段落3** - 删减"双5%"重复（当前48词 → 目标23词）
- [ ] 删除"Operationally"开头
- [ ] 移除冗余的"so a miss...probability 1-p=0.05"
- [ ] **关键**: 将完整"双5%"概念移到Methods脚注
- [ ] 检查词数: 确认≤25词

**段落4-5** - AI痕迹消除
- [ ] 改写"What has not been formalized—and what this work contributes—is..."
- [ ] 新版本: "This work formalizes an estimand-gated decision algorithm..."
- [ ] 删除"This is not X. It is Y"句式
- [ ] 改为: "The framework provides a design calculus for existing LoD vocabulary."

**段落6** - 简化"We asked"句式（当前80词 → 目标40词）
- [ ] 删除"We asked what...and how..."
- [ ] 改为: "We evaluated required sample sizes across the complete (p_A, p_B) integer lattice."
- [ ] 删除"—not a single illustrative contrast"破折号解释

**Introduction检查点**:
- [ ] 运行词数统计: `grep -A 50 "^## Introduction" manuscript/METHODS_BRIEF_REVISION.md | wc -w`
- [ ] 目标: 从~650词 → ~550词（删减100词）
- [ ] 无破折号超过3处
- [ ] 无"This is not...It is..."句式

---

### 下午任务 (2-3小时)

#### 📝 Methods修改 (120分钟)

**§2.1 Study design** - 删除冗长开场（当前60词 → 目标20词）
- [ ] 改写"This was an analytical study of prospective sample-size planning..."
- [ ] 新版本: "We analyzed prospective sample size planning for CLSI EP17-A2 LoD verification."
- [ ] 删除后续重复的"Operating characteristics were evaluated..."（已在后文说明）

**公式删减** - 移到Supplement
- [ ] 保留Eq. (2) Fleiss-Chow公式（核心）
- [ ] 删除Eq. (3)-(4)完整展示
- [ ] 替换为: "We related concentration to hit rate using logistic dose-response (Supplement Eq. S1)."
- [ ] 添加脚注: "Supplement provides full dose-response equations."
- [ ] **预计节省**: ~120词

**LoD₉₅定义段** - 移到脚注
- [ ] 删除内嵌段落"LoD$_{95}$ and the two 5% layers..."（约80词）
- [ ] 保留一句话: "LoD₉₅ corresponds to p=0.95 (analytical 5% miss rate); sample size planning adds inferential control (α, β).¹"
- [ ] 添加页脚注释

**S0-S7流程** - 简化描述
- [ ] 改写"Implementation followed an eight-step protocol..."
- [ ] 新版本: "Implementation followed an eight-step algorithm: claim specification (S0-S1), diagnostics (S2-S4), sample size planning (S5), exact confirmation (S6), and reporting (S7)."
- [ ] 删除"lock claim (S0), confirm binary readout (S1)..."列举（太啰嗦）

**Formal results段** - 大幅简化（当前150词 → 目标30词）
- [ ] 删除"Theorem T1...Lemma T2a...Theorem T2b...Corollary T2c..."详细列举
- [ ] 替换为: "Formal proofs of non-nested acceptance events (E1/E2/E3), asymptotic-exact power gaps, and Pareto inadmissibility of folklore n=20 are provided in Supplement §S2."
- [ ] **节省**: ~120词

**Methods检查点**:
- [ ] 运行词数统计: `grep -A 200 "^## Methods" manuscript/METHODS_BRIEF_REVISION.md | wc -w`
- [ ] 目标: 从~1200词 → ~1000词（删减200词）
- [ ] Eq. (2)保留，其他移到Supplement
- [ ] 无超过30词的单句

---

### 晚上检查 (30分钟)

- [ ] 总词数检查: `wc -w manuscript/METHODS_BRIEF_REVISION.md`
- [ ] 当前进度: 应从4645词 → 约4300词（删减300词）
- [ ] 记录修改日志:
  ```bash
  echo "Day 1 完成: Introduction -100词, Methods -200词" >> REVISION_LOG.txt
  ```

---

## Day 2 - Results & Discussion 修改

### 上午任务 (2小时)

#### 📝 Results修改

**删除Box 1** - 改为简化正文（当前95词 → 目标38词）
- [ ] 删除整个Box框架
- [ ] 替换为: "At p=0.95, a 19/20 rule (E3) passed with probability 0.74 at n=20 (Table 9), requiring n=22 for 95% pass probability. This E3 rule does not confirm p≥0.95 (E1 claim), which requires n≥24 (Table 8)."
- [ ] **节省**: 57词

**删除Box 2** - 改为简化正文（当前110词 → 目标48词）
- [ ] 删除整个Box框架和子标题
- [ ] 替换为: "At n=20 per arm, 61% of lattice cells had miss probability β>0.8 (Fig 1B). Median required n* was 116 (range 20-435), rising sharply as contrast narrowed (Fig 1C inset; Table 3f). Asymptotic power formulas overestimated exact Fisher power in 778/1225 cells (Table 3e)."
- [ ] **节省**: 62词

**Results其余简化**
- [ ] 删除"For E2 we computed operating-characteristic surfaces..."重复描述（Methods已说明）
- [ ] 删除"Representative quantitative...near the limit of detection (LoD)"（Figure legend已覆盖）
- [ ] **预计节省**: 约50词

**Results检查点**:
- [ ] 目标: 从~900词 → ~800词（删减100词）
- [ ] 所有Box已转为正文
- [ ] 与Figure legend无重复描述

---

### 下午任务 (2小时)

#### 📝 Discussion修改

**段落2** - 压缩validation committees描述（当前60词 → 目标28词）
- [ ] 删除"Validation committees and laboratory information system (LIS) sign-off workflows rarely audit..."
- [ ] 改为: "Validation workflows rarely audit whether detection claims were adequately powered. Near-threshold results may depend on whether lot equivalence was demonstrated or merely observed at conventional n."
- [ ] **节省**: 32词

**段落3开头** - 简化重复（当前35词 → 目标20词）
- [ ] "For lot comparison at c* (E2), conventional n=20 per arm left most hit-rate pairs..."
- [ ] 改为: "For lot comparisons (E2), n=20 yielded high miss probability for most hit-rate pairs (Fig 1B; Table 3)."
- [ ] **节省**: 15词

**限制性段落** - 删减或移到Supplement
- [ ] 检查是否有超过100词的limitations段落
- [ ] 考虑保留1-2句核心限制，其余移到Supplement

**Discussion检查点**:
- [ ] 目标: 从~600词 → ~500词（删减100词）
- [ ] 避免Results内容重复
- [ ] 突出临床意义，而非方法细节

---

### 晚上任务 (1小时)

#### 📊 表格格式化开始

**Table 1处理** (20分钟)
- [ ] 打开Excel，新建工作簿
- [ ] 手动创建3×4表格（见TABLE_FORMATTING_GUIDE.md）
- [ ] 添加表注
- [ ] 另存为Table01_formatted.xlsx

**Table 3处理** (40分钟)
- [ ] 打开Table03_reference_pairs_n20.csv
- [ ] 按TABLE_FORMATTING_GUIDE删除7列，保留6列
- [ ] 调整数字精度：Δp=2位，Power/β=3位
- [ ] 添加表注（引用完整网格CSV）
- [ ] 另存为Table03_formatted.xlsx

**Day 2检查点**:
- [ ] 总词数: 应达到约3900词（距目标3500还需删减400词）
- [ ] Table 1和3完成Excel版本
- [ ] 记录进度: `echo "Day 2完成: Results -100词, Discussion -100词, Table 1+3格式化" >> REVISION_LOG.txt`

---

## Day 3 - 终审 & 表格完成

### 上午任务 (2小时)

#### 📊 完成Table 7格式化 (90分钟)

- [ ] 打开Table07_tierA_meta.csv
- [ ] 插入序号列1-9
- [ ] 删除dataset_id和allowed_claim列
- [ ] **逐行缩写citation**（最耗时）:
  - [ ] Row 1: "Zenodo 12609243"
  - [ ] Row 2: "Zenodo 12609243"
  - [ ] Row 3: "CLSI EP17-A2 (Analyse-it)"
  - [ ] Row 4: "CLSI EP17-A2 (Analyse-it)"
  - [ ] Row 5: "Carobene et al. (2024)"
  - [ ] Row 6: "Bioconductor MSstatsLOBD"
  - [ ] Row 7: "Malkamäki et al. (2024)"
  - [ ] Row 8: "Malkamäki et al. (2024)"
  - [ ] Row 9: "Sawant et al., Zenodo 17108929"
- [ ] 重命名列头（见TABLE_FORMATTING_GUIDE）
- [ ] 另存为Table07_formatted.xlsx

#### 🔍 最后词数删减（如需要）

**如果仍超3500词，启用备用删减**:
- [ ] Introduction第2段完全删除（EP17背景）→ 节省40词
- [ ] Discussion最后一段（future work）移到Supplement → 节省60词
- [ ] Methods中"Public data sources"段压缩50% → 节省80词

---

### 下午任务 (3小时)

#### 📝 Word文档组装 (90分钟)

- [ ] 打开submission/manuscript.docx（pandoc已生成）
- [ ] 检查并修复markdown残留（[链接](url)，code blocks等）
- [ ] 插入Table 1（从Excel复制 → 粘贴为"保留格式"）
- [ ] 插入Table 3
- [ ] 插入Table 7
- [ ] 调整表格格式:
  - [ ] 顶部/底部粗边框（2.25 pt）
  - [ ] 表头下细边框（0.75 pt）
  - [ ] 删除所有竖线
  - [ ] 表头加粗10pt
  - [ ] 表体9pt
  - [ ] 表注8pt斜体
- [ ] 添加图例页（复制FIGURE_LEGENDS_CC.md内容）

#### ✅ 质量检查 (90分钟)

**文本质量检查**:
- [ ] 运行Grammarly（免费版即可）检查:
  - [ ] 被动语态≤20%
  - [ ] 无拼写错误
  - [ ] 语气"Formal but clear"
- [ ] 运行Hemingway Editor检查:
  - [ ] 句子平均长度≤25词
  - [ ] Grade level ≤ 12
- [ ] AI痕迹检查（可选，使用GPTZero.me）:
  - [ ] AI概率<30%

**格式检查**:
- [ ] Abstract ≤250词: `______` 词 ✅/❌
- [ ] Brief Summary ≤100词: `______` 词 ✅/❌
- [ ] 主文≤3500词: `______` 词 ✅/❌
- [ ] References ≤40条: `______` 条 ✅/❌
- [ ] 图表≤6项: 5项（Fig 1-2, Table 1,3,7）✅
- [ ] 所有缩写首次展开 ✅/❌
- [ ] 无markdown残留 ✅/❌

**交叉引用检查**:
- [ ] 搜索"Table 1" → 所有引用存在
- [ ] 搜索"Table 3" → 所有引用存在
- [ ] 搜索"Table 7" → 所有引用存在
- [ ] 搜索"Fig 1" → 所有引用存在
- [ ] 搜索"Fig 2" → 所有引用存在
- [ ] 搜索"Supplement" → 所有引用的表/公式存在于补充材料

**数字一致性检查**:
- [ ] Abstract中的"61%"与Fig 1B一致
- [ ] "n=20"在全文使用统一
- [ ] "α=0.05"在全文统一
- [ ] 所有百分比格式统一（0.95 vs 95%）

---

### 晚上任务 (1小时)

#### 🖼️ 图表最终处理

**转换为TIFF** (如期刊要求):
```bash
cd paper_artifacts/figures

# 使用ImageMagick转换（如已安装）
convert Fig1_Fig1-lod-replicate-planning.png -density 300 -compress lzw Fig1.tif
convert Fig2_Fig2-tierA-calibration.png -density 300 -compress lzw Fig2.tif

# 或使用Python（如ImageMagick未安装）
python << EOF
from PIL import Image
img1 = Image.open('Fig1_Fig1-lod-replicate-planning.png')
img1.save('Fig1.tif', dpi=(300,300), compression='tiff_lzw')
img2 = Image.open('Fig2_Fig2-tierA-calibration.png')
img2.save('Fig2.tif', dpi=(300,300), compression='tiff_lzw')
EOF
```

- [ ] Fig1.tif生成成功
- [ ] Fig2.tif生成成功
- [ ] 文件大小检查（<10 MB）
- [ ] 色盲检查（上传到https://www.color-blindness.com/coblis-color-blindness-simulator/）

#### 📦 最终打包

- [ ] 创建submission文件夹结构:
  ```
  submission/
  ├── manuscript.docx          (主文)
  ├── figures/
  │   ├── Fig1.tif
  │   └── Fig2.tif
  ├── tables/                  (可选，有些期刊要求单独上传)
  │   ├── Table01.xlsx
  │   ├── Table03.xlsx
  │   └── Table07.xlsx
  ├── supplement.pdf           (如已生成)
  └── cover_letter.docx
  ```

- [ ] 所有文件命名符合期刊要求（无空格，无特殊字符）

---

## 最终检查清单（Day 3结束前）

### 必需项 ✅
- [ ] 主文词数≤3500
- [ ] Abstract≤250词，Brief Summary≤100词
- [ ] 图表≤6项（当前5项）
- [ ] References≤40条
- [ ] 所有表格为Word格式（非CSV）
- [ ] 所有图表有legend和alt text
- [ ] 无markdown残留语法
- [ ] 所有缩写首次展开

### 质量项 ✅
- [ ] Grammarly检查通过（无重大语法错误）
- [ ] 被动语态<20%
- [ ] 平均句长<25词
- [ ] 无AI典型句式（见MANUSCRIPT_REVISION_PLAN §3.1）
- [ ] 图表分辨率≥300 dpi
- [ ] 色盲友好配色

### 完整性项 ✅
- [ ] 作者信息完整（姓名、单位、ORCID）
- [ ] 通讯作者联系方式
- [ ] COI声明（无冲突或声明）
- [ ] Funding声明
- [ ] 数据可用性声明
- [ ] AI使用声明（cover letter）

---

## 紧急情况处理

### 如果Day 1结束时词数仍>4000:
→ 立即启用备用删减方案（见Day 3上午）

### 如果表格格式化超时:
→ 优先完成Table 3（核心结果），Table 1/7可用简化版本

### 如果图表TIFF转换失败:
→ PNG在300+ dpi下通常可接受，咨询期刊编辑部

---

## 成功标准

完成3天修改后，您的投稿包应该：

✅ **内容**: 科学严谨，无过度声称  
✅ **格式**: 100%符合Clinical Chemistry要求  
✅ **可读性**: 清晰简洁，无AI痕迹  
✅ **完整性**: 所有必需文件就绪  

**下一步**: 提交给合作者内部审阅 → 2-3天反馈 → ScholarOne上传

---

## 每日自我奖励 🎉

- Day 1完成: ☕ 喝杯好咖啡
- Day 2完成: 🍕 吃顿好的
- Day 3完成: 🎊 庆祝投稿就绪！

**加油！您的项目科学质量已经很高，现在只是包装工作。**
