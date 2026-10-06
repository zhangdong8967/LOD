# 快速参考卡 - 修改时随时查看

**打印此页并放在手边！**

---

## 🎯 核心目标

| 指标 | 当前值 | 目标值 | 策略 |
|------|--------|--------|------|
| 主文词数 | 4645 | ≤3500 | 删减1145词（25%）|
| Abstract | ~250 | ≤250 | ✅ 已达标 |
| 图表数 | 5 | ≤6 | ✅ 已达标 |
| AI痕迹 | 高 | 低 | 改写10处关键句式 |

---

## 🚫 AI痕迹句式速查（必须改写）

| ❌ 避免使用 | ✅ 改为 |
|-----------|---------|
| "What has not been X—and what this work contributes—is Y" | "This work provides Y" |
| "This is not X. It is Y." | "The framework provides Y rather than X." |
| "We asked what...and how..." | "We evaluated..." |
| "—not a single illustrative contrast" | "(across the complete lattice)" |
| "Operationally, X names..." | "At X,..." |
| "Before data collection, the laboratory should lock..." | "Before data collection, specify..." |

**原则**：删除破折号解释、删除"This is not"句式、简化长从句

---

## 📏 词数删减优先级（按ROI排序）

| 区域 | 当前词数 | 删减目标 | 方法 | 预计时间 |
|------|---------|---------|------|---------|
| **1. Methods公式** | 300 | -120词 | 移Eq.(3)-(5)到Supplement | 20分钟 |
| **2. Results Box 1+2** | 200 | -120词 | 删除Box框架，简化为正文 | 30分钟 |
| **3. Introduction前3段** | 170 | -80词 | 压缩LoD定义重复 | 40分钟 |
| **4. Methods定理列举** | 150 | -120词 | "Formal proofs (Supplement)" | 15分钟 |
| **5. Discussion第2段** | 100 | -60词 | 删除validation committees例子 | 20分钟 |
| **总计** | 920 | **-500词** | **达到≤3500目标** | **2小时** |

**立即执行顺序**：1→4→2→3→5

---

## ✂️ 快速删减模板（复制粘贴）

### Introduction第1段
**删除**：
```
When a laboratory signs off limit of detection (LoD) verification after a reagent lot or instrument change, the validation packet often fixes about 20 low-level replicates regardless of the written claim. One file may require confirmation of manufacturer LoD₉₅...
```

**替换为**：
```
Laboratories commonly verify limit of detection (LoD) with approximately 20 replicates after reagent or instrument changes, without adjusting sample size for the specific detection claim.
```

---

### Methods Eq.(3)-(5)
**删除**：
```
[整个Eq. (3), (4), (5)公式块]
```

**替换为**：
```
We related concentration to hit rate using logistic dose-response (Supplement Eq. S1).¹

¹Full dose-response equations in Supplement §S1.
```

---

### Results Box 1
**删除整个Box**，替换为：
```
At p=0.95, a 19/20 rule (E3) passed with probability 0.74 at n=20 (Table 9), requiring n=22 for 95% pass probability. This E3 rule does not confirm p≥0.95 (E1 claim), which requires n≥24 (Table 8).
```

---

### Methods定理段
**删除**：
```
Theorem T1 (non-nested estimands)... Lemma T2a... Theorem T2b... Corollary T2c...
```

**替换为**：
```
Formal proofs of non-nested acceptance events (E1/E2/E3), asymptotic-exact power gaps, and Pareto inadmissibility of folklore n=20 are provided in Supplement §S2.
```

---

## 📊 表格快速检查清单

### Table 1（10分钟）
- [ ] 3列×3行
- [ ] 表头：Goal | Estimand | Sample size method
- [ ] 表注："E1, benchmark confirmation; E2, two-arm contrast; E3, fixed pass rule."

### Table 3（30分钟）
- [ ] **删除7列**，保留6列：pair, delta_p, n, power_exact_fisher, miss_beta, n_star_ceiling
- [ ] 数字精度：Δp=2位，Power/β=3位，n和n*=整数
- [ ] 表注包含："Full 1225-cell lattice: online Supplement Table03_comparison_grid_n20.csv."

### Table 7（45分钟）
- [ ] 添加序号列（1-9）
- [ ] **删除**：dataset_id, allowed_claim列
- [ ] **缩写citation**：
  - "Zenodo 12609243"（不要完整标题）
  - "CLSI EP17-A2 (Analyse-it)"
  - "Carobene et al. (2024)"
- [ ] 列名改为：# | Assay family | Param? | Path | n* | n₂₀ | n*/n₂₀ | Source

---

## 🖼️ 图表质量速查

| 检查项 | Fig 1 | Fig 2 | 要求 |
|--------|-------|-------|------|
| DPI | 600 ✅ | 400 ✅ | ≥300 |
| 格式 | PNG | PNG | TIFF最佳 |
| 尺寸 | 8101×4535 | 2848×1677 | 合适 |
| 大小 | 0.91 MB | 0.26 MB | <10 MB ✅ |

**转TIFF命令**（可选）：
```bash
cd paper_artifacts/figures
convert Fig1_Fig1-lod-replicate-planning.png -density 300 Fig1.tif
convert Fig2_Fig2-tierA-calibration.png -density 300 Fig2.tif
```

---

## ⏱️ 时间分配速查（3天计划）

### Day 1 (5小时)
- 上午：Introduction修改（2h）→ 删减100词
- 下午：Methods修改（2.5h）→ 删减200词
- 晚上：检查点（0.5h）→ 应达到4300词

### Day 2 (5小时)
- 上午：Results修改（2h）→ 删减100词
- 下午：Discussion修改（1h）→ 删减100词
- 晚上：Table 1+3格式化（2h）

### Day 3 (6小时)
- 上午：Table 7格式化（1.5h）+ 最终删减（0.5h）
- 下午：Word组装（1.5h）+ 质量检查（1.5h）
- 晚上：图表转TIFF（0.5h）+ 打包（0.5h）

**总计**：16小时工作量

---

## 🔍 终审检查（提交前）

```bash
# 1. 词数检查
wc -w submission/manuscript.docx  # 需转为纯文本检查

# 2. 搜索markdown残留
grep -n '\[.*\](http' submission/manuscript.docx  # 应无结果

# 3. 搜索AI痕迹
grep -n "What has not been" submission/manuscript.docx  # 应无结果
grep -n "This is not.*It is" submission/manuscript.docx  # 应无结果

# 4. 交叉引用完整性
grep -o "Table [0-9]" submission/manuscript.docx | sort | uniq -c
grep -o "Fig [0-9]" submission/manuscript.docx | sort | uniq -c
```

---

## 💡 实用技巧

### 词数实时监控（Mac）
```bash
# 创建监控脚本
cat > watch_wordcount.sh << 'EOF'
#!/bin/bash
while true; do
  clear
  echo "===== 词数监控 ====="
  echo "目标: ≤3500词"
  echo "当前: $(wc -w < manuscript/METHODS_BRIEF_REVISION.md) 词"
  echo "距离目标: $(($(wc -w < manuscript/METHODS_BRIEF_REVISION.md) - 3500)) 词"
  sleep 5
done
EOF
chmod +x watch_wordcount.sh
./watch_wordcount.sh
```

### 批量替换AI句式
```bash
# 在manuscript/METHODS_BRIEF_REVISION.md中批量替换
sed -i.bak 's/What has not been formalized—and what this work contributes—is/This work formalizes/g' manuscript/METHODS_BRIEF_REVISION.md
```

### 快速备份
```bash
# 每完成一个section就备份
cp manuscript/METHODS_BRIEF_REVISION.md manuscript/backups/REVISION_$(date +%Y%m%d_%H%M).md
```

---

## 📞 紧急联系（如遇技术问题）

- **Pandoc转换失败**：检查markdown语法，特别是表格和公式
- **表格Excel崩溃**：逐行复制到新工作簿
- **图片无法打开**：检查文件权限 `chmod 644 *.png`
- **词数统计不准**：用 `wc -w` 而非Word计数（markdown会虚高）

---

## ✅ 每日完成奖励

- ☑️ Day 1完成 → 删减300词 → ☕ 咖啡休息
- ☑️ Day 2完成 → 删减200词+表格 → 🍕 晚餐奖励  
- ☑️ Day 3完成 → 投稿就绪 → 🎉 庆祝！

**记住**：您的科学工作已经很优秀，现在只是"包装"工作！

---

**此卡片打印提示**：建议打印2页（正反面），放在电脑旁边随时参考
