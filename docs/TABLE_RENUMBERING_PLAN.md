# 表格重新编号修正方案

**问题**: 主文表格编号不连续（1, 3, 7）违反期刊规范  
**解决**: 重新编号为连续编号（1, 2, 3）

---

## 重新编号方案

| 原编号 | 新编号 | 内容 | 行数 |
|--------|--------|------|------|
| Table 1 | **Table 1** | Detection claim structures (E1/E2/E3定义) | 3行 ✓保持 |
| Table 3 | **Table 2** | Protocol-specific E2 pairs (8个协议对) | 8行 ⚠️改 |
| Table 7 | **Table 3** | Tier A guidance n summary (10个审计) | 10行 ⚠️改 |

**Supplement表格不变**（编号独立，保持2, 3-9等）

---

## 全文替换清单

### 需要替换的位置

#### 1. Abstract
```
查找: "Table 7"
替换为: "Table 3"
```

#### 2. Methods
```
查找: "Table 1"
保持不变 ✓
```

#### 3. Results
```
查找: "Table 3"
替换为: "Table 2"
(出现约4-5次)

查找: "Table 7"
替换为: "Table 3"
(出现约2-3次)
```

#### 4. Figure 2 caption/legend
```
查找: "Table 3"
替换为: "Table 2"
```

---

## 修正后的主文图表结构

```
主文:
  Figure 1 (4 panels)
  Figure 2 (3 panels)
  Table 1 (3 rows)
  Table 2 (8 rows) ← 原Table 3
  Table 3 (10 rows) ← 原Table 7

总计: 2图 + 3表 = 5个 ✓ 符合Clinical Chemistry要求
编号: Fig 1-2, Table 1-3 全部连续 ✓
```

---

## Supplement不受影响

Supplement保持独立编号系统：
- Supplementary Table 2, 3, 4, 5, 6, 7b, 8, 9
- Supplementary Figure S1-S9

**注意**: Supplement可以不连续（如没有Table 1），这是允许的。

---

## 详细替换操作

### Word文档中操作

1. **打开主稿** `Clinical_Chemistry_submission.docx`

2. **Ctrl+H 查找替换**，按以下顺序：

   **第1步**: 先处理Table 7
   ```
   查找: Table 7
   替换为: Table 3
   选项: 匹配全词
   操作: 逐个检查并替换（约3-4处）
   ```

   **第2步**: 再处理Table 3  
   ```
   查找: Table 3
   替换为: Table 2
   选项: 匹配全词
   操作: 逐个检查并替换（约5-6处）
   ```
   
   **注意**: 不要替换 "Supplementary Table 3"！

3. **检查Figure_legends.docx**
   ```
   查找: Table 3
   替换为: Table 2
   (如果图例中引用了表格)
   ```

4. **Tables_main.docx** - 修改表格标题
   ```
   Table 3: Protocol-specific... 
   → 改为: Table 2: Protocol-specific...
   
   Table 7: Tier A guidance...
   → 改为: Table 3: Tier A guidance...
   ```

---

## 安全替换的正则表达式

如果使用高级查找：

```regex
# 仅匹配主文Table 7（不含Supplementary）
查找: (?<!Supplementary )Table 7
替换为: Table 3

# 仅匹配主文Table 3（不含Supplementary）
查找: (?<!Supplementary )Table 3
替换为: Table 2
```

**警告**: Word不支持正则，需要手动逐个确认！

---

## 预期替换次数

| 位置 | Table 7→3 | Table 3→2 |
|------|-----------|-----------|
| Abstract | 1次 | 0次 |
| Introduction | 0次 | 0次 |
| Methods | 0次 | 1次 |
| Results | 2-3次 | 4-5次 |
| Discussion | 0次 | 0-1次 |
| Figure legends | 0次 | 1次 |
| **总计** | **约3-4次** | **约6-7次** |

---

## 替换后检查清单

- [ ] Abstract中 "Table 3" 指向审计数据 ✓
- [ ] Results第1段 "Table 1" 指向claim structures ✓
- [ ] Results中 "Table 2" 指向8个协议对 ✓
- [ ] Results中 "Table 3" 指向10个审计 ✓
- [ ] Fig. 2C引用 "Table 2" ✓
- [ ] 没有误改 "Supplementary Table 3" ✓
- [ ] Tables_main.docx中表格标题已更新 ✓

---

## 为什么之前用了1, 3, 7？

可能的原因（推测）：
- Supplement中有Table 2-9
- 误以为主文和Supplement共享编号空间
- 实际上：主文和Supplement是独立编号系统

**正确理解**:
- 主文: Table 1, 2, 3, ... (连续)
- Supplement: Supplementary Table 1, 2, 3, ... (也连续，但独立)
- 两者不冲突！

---

## 修正后的完整清单

### 主文图表（连续编号）
1. Figure 1 (LoD replicate planning, 4 panels)
2. Figure 2 (Tier A calibration, 3 panels)
3. **Table 1** (Detection claim structures, 3 rows)
4. **Table 2** (Protocol-specific pairs, 8 rows) ← 改
5. **Table 3** (Tier A audit summary, 10 rows) ← 改

### Supplement图表（独立编号）
- Supplementary Table 2, 3, 4, 5, 6, 7b, 8, 9
- Supplementary Figure S1-S9

**所有编号现在都连续 ✓**

---

**修正日期**: 2026年8月24日  
**预计修改时间**: 10分钟  
**风险**: 低（简单查找替换）  
**收益**: 符合期刊规范 ✓
