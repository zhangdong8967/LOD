# AI 率降低修改记录

**基线 AI 率（检测报告）**: 18.5%  
**Round 2 后**: 16.9%  
**Round 3 后**: 16.5%  
**Round 6 后（默认 qwen，前最佳）**: 16.4%  
**Round 7 全量改写**: 19.1%（部分段落恶化，已回退）  
**Round 7b 混合版**: 16.6%  
**Round 8 当前最佳**: **16.5%**  
**Round 9（稳健稀释）**: 16.8–16.9% — Table 1 叙述 + estradiol 公开案例 + 计算实现；未编造调查/IRB  
**Round 10（2026-10-06）**: 本地启发式 **20.0%**（`ai-detect --config scripts/ai_detect_heuristics.yaml`，无 Ollama 加权；结论 pass，warn=55%）。GPTZero 未跑（环境无 `GPTZERO_API_KEY`）。Ollama 全文加权当时卡住，未并入本次分数。  
**Round 11（2026-10-06）**: 再拆 Intro/Methods/Results/Discussion/Abstract 套话与平行句；科学 en-dash 改为 ASCII 连字符（Clopper-Pearson、50%-99% 等，避免启发式误计为 AI 破折号）。组装通过；本地启发式 **17.0%**（pass；相对 Round 10 的 20% 下降）。主文 Intro–Discussion ≈2948 词。常见套话词扫描为 0。GPTZero 仍未跑（无 API key）。  
**当前锁定**: Round 11 投稿 Word；科学数字未改  
**原则**: 仅改写句式与节奏；**不编造**未在文中出现的调查或病例数

## 已修改段落（对应高 AI 风险区）

| 区域 | 原特征 | 应用技巧 | 状态 |
|------|--------|----------|------|
| Introduction 末段 | “This study maps…” 平行句 | 1, 5, 6, 7 | ✅ |
| Introduction E1–E3 | 列举式对称 | 1, 3 | ✅ |
| Methods 研究设计 | “We assigned… calculated… compared” | 5, 6 | ✅ |
| Methods E1/E2/E3 定义 | 三个 “tested/compared/evaluated” | 1, 5 | ✅ |
| Methods E2 格点 | “evaluated surface… collapse…” | 2, 3, 5, 7 | ✅ |
| Methods D1–D3 | 三段平行名词短语 | 1, 6 | ✅ |
| Results 开篇 | “We organized findings around three…” | 5 | ✅ |
| Results E2 格点 | 均匀短句链 | 2, 3, 5, 7 | ✅ |
| Results E3/E1 | 机械 “This E3 rule does not…” | 3, 6 | ✅ |
| Results tier A | “Nine deposits gave… Two illustrate…” | 5, 2 | ✅ |
| Discussion 全文 | 重复 “Our results… For lot… For single-arm…” | 1, 4, 5, 6, 7 | ✅ |
| Abstract Methods | “We mapped… we computed…” | 6 | ✅ |
| Round 4 | Brief Summary p7, Intro p16, Methods E1–E3 p26, lattice p36, Results E2 p46, Discussion p51–58 | 1–7 | ✅ |
| Round 5 | Intro p16, Table 1 p26, lattice p32, D1–D3 p36, Results E2 p43/p44, E3/E1 p46, Box 4 p59 | 1–7 | ✅ |
| Round 7b 混合版 | 16.6%（保留 p46/p19/p44/p16/p51 有效改动） | — | ✅ |
| Round 8 | p16/p26/p32/p36/p57 精修 | 1–7 | ✅ |
| Round 9 | Table 1 叙述、estradiol 案例、计算实现、Discussion 开头（无编造调查） | 1–7 | ✅ |

## 刻意未采用（科学诚信）

- ❌ 编造 “45 家实验室调查”“120 份验证包审查”等未在数据中的数字  
- ❌ 添加 “三家医院试点”等未在 tier A 证据中的表述  

## 复测命令

```bash
cd /Users/zhangdong/PycharmProjects/PythonProject/LOD
make submission-package
ai-detect submission/Clinical_Chemistry_submission.docx   # 若已安装
```

## 词数影响

修改后主文词数变化应 <5%；所有 Table/Fig 引用与统计量未改。
