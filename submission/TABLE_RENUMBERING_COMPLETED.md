# 表格重新编号 - 已完成修正

**修正日期**: 2026年8月24日  
**问题**: 主文表格编号不连续（1, 3, 7）违反学术期刊规范  
**解决**: 重新编号为连续编号（1, 2, 3）

---

## ✅ 已完成的文件修正

### 1. Results 文件修正 ✓
**文件**: `submission/RESULTS_REVISED_NATURAL.txt`

已完成的替换：
- ✅ "Table 3" → "Table 2" (2处)
  - Line 12: "Fig. 1B; Table 2"
  - Line 18: "Table 2" (两次) + "Fig. 2C"
- ✅ "Table 7" → "Table 3" (1处)
  - Line 34: "Table 3; Supplementary Table 7b"

**验证**: 所有主文表格引用已更新为连续编号

---

### 2. Methods 文件检查 ✓
**文件**: `submission/METHODS_FINAL_FOR_MANUSCRIPT.docx.txt`

**结果**: 无需修改 ✓
- 仅引用 "Supplement Table 7b"（Supplement编号不变）
- 无主文Table 3或Table 7引用

---

### 3. Discussion 文件检查 ✓
**文件**: `submission/DISCUSSION_REVISED_NATURAL.txt`

**结果**: 无需修改 ✓
- 无任何主文表格引用

---

### 4. 图表清单更新 ✓
**文件**: `submission/FIGURE_TABLE_COMPLETE_CHECKLIST.md`

已更新：
- ✅ Table 3 → Table 2 标题和引用
- ✅ Table 7 → Table 3 标题和引用
- ✅ 添加"(原Table X)"标注方便对照

---

## ⚠️ 您仍需手动完成的工作

### 🔴 必须修改的Word文档

#### 1. 主稿文档
**文件**: `submission/Clinical_Chemistry_submission.docx`

**操作步骤**（按顺序）：

**Step 1**: 替换内容（从修正好的文本文件）
```
1. 打开 Clinical_Chemistry_submission.docx
2. 找到 Results 部分
3. 全选该部分，粘贴替换为:
   submission/RESULTS_REVISED_NATURAL.txt 的内容
```

**Step 2**: 查找替换（在Word中 Ctrl+H）

⚠️ **重要顺序**：必须先改Table 7，再改Table 3！

```
第一轮替换:
  查找: Table 7
  替换为: Table 3
  选项: 匹配全词
  操作: 逐个确认（不要"全部替换"）
  预计: Abstract中1-2处

第二轮替换:
  查找: Table 3
  替换为: Table 2
  选项: 匹配全词  
  操作: 逐个确认
  注意: 跳过 "Supplementary Table 3"
  预计: 如果Results已粘贴新版本，应该没有剩余
```

**Step 3**: 检查确认
```
- [ ] Abstract引用 "Table 3" (指向审计数据)
- [ ] Introduction无Table 3或7引用
- [ ] Methods无Table 3或7引用（只有Supplementary Table 7b）
- [ ] Results引用 "Table 2" 和 "Table 3"（已从新文件粘贴）
- [ ] Discussion无Table引用
- [ ] References无Table引用
```

---

#### 2. 表格文档
**文件**: `submission/Tables_main.docx`

**修改**:
```
Table 3: Protocol-specific E2 probability pairs...
→ 改为: Table 2: Protocol-specific E2 probability pairs...

Table 7: Tier A guidance deposit sample-size audit
→ 改为: Table 3: Tier A guidance deposit sample-size audit
```

**同时检查Table 1**:
```
列标题应该是:
  ✓ "Benchmark confirmation" (不是 "E1:")
  ✓ "Two-arm comparison" (不是 "E2:")
  ✓ "Qualitative pass criteria" (不是 "E3:")
```

---

#### 3. 图例文档（可能需要）
**文件**: `submission/Figure_legends.docx`

**检查**:
- 如果Figure 2 legend中引用了表格，确认是 "Table 2"
- 通常图例不直接引用表格，可能无需修改

---

## 📊 修正后的完整结构

### 主文图表（现在全部连续 ✓）
```
Figure 1: LoD replicate planning (4 panels: A, B, C, inset)
Figure 2: Tier A calibration (3 panels: A, B, C)
Table 1: Detection claim structures (3 claim types)
Table 2: Protocol-specific E2 pairs (8 pairs) ← 改
Table 3: Tier A audit summary (10 deposits) ← 改
```

### Supplement（独立编号，不受影响）
```
Supplementary Table 2, 3, 4, 5, 6, 7b, 8, 9
Supplementary Figure S1-S9
```

**关键理解**:
- 主文 Table 1-3 和 Supplement Table 2-9 是**独立编号系统**
- 两者不冲突，都可以有Table 3
- 区别在于前缀："Table X" vs "Supplementary Table X"

---

## 🔍 最终验证清单

在Word中完成修改后，检查：

### Abstract
- [ ] 提到审计数据时引用 "Table 3" ✓

### Methods  
- [ ] 只引用 "Supplementary Table 7b" ✓
- [ ] 无 "Table 3" 或 "Table 7" ✓

### Results
- [ ] "Table 1" 指向 claim structures ✓
- [ ] "Table 2" 指向 8个协议对 ✓
- [ ] "Table 3" 指向 10个审计 ✓
- [ ] 无 "Table 7" 残留 ✓

### Figures
- [ ] Figure 1 caption完整 ✓
- [ ] Figure 2 caption提到 "Table 2" (如果提到表格) ✓

### Tables_main.docx
- [ ] Table 1 列标题无E1/E2/E3 ✓
- [ ] Table 2 标题正确 ✓
- [ ] Table 3 标题正确 ✓
- [ ] 表格内容未变动 ✓

---

## 📝 Word查找替换的安全技巧

### ✅ 正确方法
```
1. 使用 Ctrl+F 先"查找"，确认所有位置
2. 记录查找到几处
3. 使用 Ctrl+H "替换"
4. 点击"查找下一处"逐个检查
5. 确认是主文Table（非Supplementary）后点"替换"
6. 重复直到完成
7. 最后用Ctrl+F再次确认无残留
```

### ❌ 错误方法
```
✗ 直接点"全部替换" - 可能误改Supplementary Table
✗ 不检查上下文 - 可能改错位置
✗ 先改Table 3再改Table 7 - 会导致混乱
```

---

## 为什么之前编号是1, 3, 7？

**推测原因**:
1. 早期版本可能计划更多主文表格
2. 误以为主文和Supplement共享编号空间
3. 按照分析顺序编号（不符合期刊要求）

**正确理解**:
- 主文: 按出现顺序连续编号 1, 2, 3, ...
- Supplement: 独立连续编号 1, 2, 3, ...（加前缀区分）
- 期刊要求: 两个系统都必须连续，但互不干扰

---

## 估计完成时间

| 任务 | 预计时间 |
|------|----------|
| 主稿查找替换 | 5分钟 |
| Tables_main.docx修改标题 | 2分钟 |
| Figure_legends检查 | 1分钟 |
| 最终验证 | 2分钟 |
| **总计** | **10分钟** |

---

## 修正影响范围

**已自动修正的文件** (无需您操作):
- ✅ submission/RESULTS_REVISED_NATURAL.txt
- ✅ submission/FIGURE_TABLE_COMPLETE_CHECKLIST.md

**需要您手动修改的文件**:
- ⚠️ submission/Clinical_Chemistry_submission.docx (主稿)
- ⚠️ submission/Tables_main.docx (表格文件)
- ⚠️ submission/Figure_legends.docx (可能需要检查)

**无需修改的文件**:
- ✓ submission/METHODS_FINAL_FOR_MANUSCRIPT.docx.txt (已检查，无需改)
- ✓ submission/DISCUSSION_REVISED_NATURAL.txt (已检查，无需改)
- ✓ submission/Online_Supplement.pdf (Supplement编号不变)

---

## 下一步行动

1. **立即**: 打开 `Clinical_Chemistry_submission.docx`
2. **替换**: Results部分粘贴新版本
3. **查找替换**: Table 7→3, Table 3→2（按此顺序）
4. **修改**: Tables_main.docx 中的标题
5. **验证**: 对照上面的清单逐项检查
6. **完成**: 稿件现在符合期刊规范 ✓

---

**Status**: 代码文件已全部修正 ✓  
**Remaining**: Word文档需手动修改（10分钟）  
**Risk**: 低（简单查找替换，已提供详细步骤）  
**Benefit**: 符合Clinical Chemistry期刊编号规范 ✓
