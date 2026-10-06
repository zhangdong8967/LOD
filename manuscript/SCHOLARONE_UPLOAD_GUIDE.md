# ScholarOne 上传指南（Clinical Chemistry）

**更新日期**: 2026-10-04  
**稿件目录**: `manuscript/`

## 期刊限制核对（已通过脚本验证）

| 项目 | 限制 | 当前 |
|------|------|------|
| 正文（Intro–Discussion） | ≤3,500 | **3,188** ✅ |
| Abstract | ≤250 | **~242** ✅ |
| Brief Summary | ≤100 | **~80** ✅ |
| References | ≤40 | **29** ✅ |
| Main figures + tables | ≤6 | **5**（Fig 1–2 + Table 1–3）✅ |

## 上传顺序（推荐）

1. **Cover letter** → `Cover_letter.docx`
2. **Main manuscript** → `Clinical_Chemistry_submission.docx`  
   （含标题页、Brief Summary、Abstract、IMRAD、Data availability、Acknowledgments、References）
3. **Figure 1** → `figures/Fig1_lod_replicate_planning.tif`
4. **Figure 2** → `figures/Fig2_tierA_calibration.tif`
5. **Figure legends** → `Figure_legends.docx`
6. **Tables** → `Tables_main.docx`（Table 1–3）
7. **Online Supplement** → `Online_Supplement.pdf`

**不要上传**（仅内部用）：`Clinical_Chemistry_author_bundle.docx`、`*.png`、本指南与 checklist。

## 投稿类型

- **Article**（methods / original research）
- 勾选 AI disclosure（Cover letter 已含声明）

## 关键词（标题页已写）

limit of detection; sample size; verification; CLSI EP17; reproducibility of results; laboratory medicine

## 上传前 3 分钟人工核对

1. Word 打开主稿：Methods 中式 **(2)** 为公式对象，且有 `where` + p̄ 定义行  
2. Introduction 末段含三种 claim 结构与 90%/80% / n≈199 动机  
3. References 为英文 Vancouver，29 条均在正文引用  
4. Cover letter 标题与主稿一致（分行页眉）  
5. Tables 标题为 Table 1 / 2 / 3（Table 2 中 n=20 为公式）  

## 重新生成

```bash
python scripts/assemble_manuscript_submission.py
```
