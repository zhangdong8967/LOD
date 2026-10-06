# AI痕迹检测与消除指南

**目标**: 将文稿从"AI辅助写作"改写为"自然学术写作"

---

## 一、AI写作的5大典型特征

### 1. 过度正式的连接词和句式

#### 特征：
- "What has **not** been X—and what this work contributes—is Y"
- "That is where this study comes in"
- "This is not X. It is Y."
- "Herein, we present..."

#### 为什么是AI痕迹：
人类学术作者很少使用这种对称的、戏剧性的句式。这是ChatGPT/GPT-4的"招牌动作"。

#### 修改策略：
**删除前置铺垫，直接陈述**

| AI版本 | 人类版本 |
|--------|---------|
| What has not been formalized—and what this work contributes—is an estimand-first algorithm. | This work formalizes an estimand-first algorithm. |
| This is not a redefinition of LoD. It is a design calculus. | The framework provides a design calculus for existing LoD definitions. |
| That is where our study comes in. | We address this gap by... |
| Herein, we present a novel approach. | We present a sample size algorithm. |

---

### 2. 过度使用破折号和em dash（—）

#### 特征：
- 每段都有1-2个破折号
- 用于插入解释性从句
- 替代括号或逗号

#### 为什么是AI痕迹：
GPT模型倾向于用破折号插入"思考过程"，而人类作者更多用分号或独立句子。

#### 修改策略：
**破折号→句号/逗号/括号**

| AI版本 | 人类版本 |
|--------|---------|
| The verification concentration—the low level named in the IFU—is denoted c*. | The verification concentration (c*) is the low level named in the IFU. |
| We computed surfaces—not a single contrast—across 1225 cells. | We computed surfaces across 1225 cells rather than isolated contrasts. |
| Conventional n=20—which appears in many SOPs—was inadequate. | Conventional n=20, common in SOPs, was inadequate for most contrasts. |

**破折号使用限制**：全文≤5处

---

### 3. 过度嵌套的从句（Nested clauses）

#### 特征：
- 单句超过30词
- 包含2个以上"which/that/when"从句
- 主语和谓语被多层修饰分隔

#### 为什么是AI痕迹：
GPT模型倾向于在一个句子中塞入所有相关信息，而人类作者会分拆为多个短句。

#### 修改策略：
**拆分为2-3个短句**

**AI版本（60词，3层嵌套）**：
> When a laboratory signs off limit of detection (LoD) verification after a reagent lot or instrument change, the validation packet often fixes about 20 low-level replicates regardless of the written claim, which may require confirmation of manufacturer LoD₉₅ at the protocol verification concentration c*, or may declare equivalent lot performance at that concentration.

**人类版本（38词，无嵌套）**：
> Laboratories commonly verify LoD with 20 replicates after reagent or instrument changes, without adjusting sample size for the specific claim. Some protocols test manufacturer LoD₉₅ at verification concentration c*; others compare lot equivalence at c*.

**技巧**：
- 找到句子中的"which"和"that"
- 如果超过1个，考虑拆分
- 目标：每句≤25词

---

### 4. 重复定义和"教科书式"解释

#### 特征：
- 用3句话说明一个简单概念
- "也就是说"/"换句话说"重复
- 先定义符号，再解释含义，再说明物理意义

#### 为什么是AI痕迹：
GPT模型为了"确保理解"，会从多个角度重复同一信息。人类作者默认读者有基础知识。

#### 修改策略：
**一句话说清楚，读者不懂会查**

**AI版本（48词，3句重复）**：
> Operationally, LoD₉₅ names the concentration at which a single replicate is detected with probability p=0.95, so a miss at that concentration is a rare event with probability 1-p=0.05. That analytical 5% is the physical meaning of a detection limit: non-detection at LoD should be uncommon.

**人类版本（23词，1句）**：
> At LoD₉₅, single-replicate detection probability equals 0.95, making non-detection a rare event (5%).

**删减规则**：
- 如果两句话表达同一意思的90%，删除一句
- 物理意义解释移到Methods或脚注

---

### 5. 平行结构过于工整

#### 特征：
- "X treats A, refuses B, replaces C"（三个动词完全平行）
- "First, we...Then, we...Finally, we..."（机械对称）
- 列举项都是相同长度和结构

#### 为什么是AI痕迹：
GPT模型追求语法对称，而人类写作有自然的节奏变化。

#### 修改策略：
**打破对称，混合长短句**

**AI版本（完美平行）**：
> The framework treats goal as a first-class object, refuses parametric LoB under failed diagnostics, and replaces folklore n=20 with powered designs.

**人类版本（不规则节奏）**：
> The framework prioritizes detection goals, rejects parametric LoB when diagnostics fail, and provides powered sample sizes rather than conventional n=20.

---

## 二、自动化检测工具

### 1. GPTZero (https://gptzero.me)
- **用途**: AI概率评分
- **目标**: AI概率<30%
- **免费限额**: 5000词/月

**操作**：
1. 复制Introduction+Methods前500词
2. 粘贴到GPTZero
3. 如果AI概率>50%，重点修改标红句子

---

### 2. Grammarly Tone Detector
- **用途**: 检测语气是否过于正式
- **目标**: "Formal but approachable"

**操作**：
1. Grammarly免费版即可
2. 上传全文
3. 查看Tone分数：如果显示"Very formal"或"Academic"过度，需简化

---

### 3. Hemingway Editor (hemingwayapp.com)
- **用途**: 检测句子复杂度
- **目标**: Grade level ≤12, 无"Very hard to read"句子

**操作**：
1. 粘贴段落到Hemingway
2. 紫色高亮=过长句子（立即拆分）
3. 红色高亮=极难句子（必须重写）

---

## 三、逐段修改实战

### Introduction第1段（AI痕迹最严重）

**原始版本（AI特征：嵌套从句+破折号+重复）**：
> When a laboratory signs off **limit of detection (LoD)** verification after a reagent lot or instrument change, the validation packet often fixes about 20 low-level replicates regardless of the written claim. One file may require confirmation of manufacturer $LoD_{95}$ at the **protocol verification concentration** $c^{\ast}$—the low level named in the manufacturer instructions for use (IFU) or local validation plan. Another may declare equivalent lot performance at that concentration. For **hit-rate–based** assays, which classify each replicate as detected or not at low level, the **Clinical and Laboratory Standards Institute (CLSI) EP17-A2** guideline on detection capability treats each protocol phrase as a statement about the **single-trial detection probability** $p(c^{\ast})$: the probability that one replicate at $c^{\ast}$ is detected, usually benchmarked at $p=0.95$.

**问题诊断**：
- ❌ 第1句60词，3层嵌套（when...after...regardless）
- ❌ 破折号解释（—the low level...）
- ❌ "which classify..."冗余从句
- ❌ 冒号后重复定义

**修改后版本（自然写作）**：
> Laboratories commonly verify limit of detection (LoD) with approximately 20 replicates after reagent or instrument changes, without adjusting sample size for the specific detection claim. Some protocols test manufacturer LoD₉₅ at a verification concentration c*; others compare lot equivalence at c*. For assays that classify replicates as detected or not, CLSI EP17-A2 interprets protocol phrases as statements about single-trial detection probability p(c*), typically benchmarked at p=0.95.

**改进**：
- ✅ 第1句32词（从60词压缩47%）
- ✅ 无破折号
- ✅ "which classify"删除（读者能理解"assays that classify"）
- ✅ 冒号解释删除

---

### Methods核心段（AI特征：过度正式）

**原始版本**：
> This was an analytical study of prospective sample-size planning for Clinical and Laboratory Standards Institute (CLSI) EP17-A2 limit of detection (LoD) verification. The study design centered on prespecified planning contracts at the verification concentration $c^{\ast}$ (E1, E2, E3 as enumerated in Table 1). For each claim we first obtained $n^{\ast}$ from asymptotic or exact binomial planning and then evaluated exact confirmation at that $n$. Operating characteristics were evaluated with finite-sample binomial probabilities; asymptotic normal approximations were documented as comparator intervals only, not as the primary decision layer.

**AI痕迹**：
- ❌ "This was an analytical study"（GPT开场白）
- ❌ "centered on"过于正式
- ❌ "as enumerated in"冗余
- ❌ 最后一句60词（过长）

**修改后版本**：
> We analyzed prospective sample size planning for CLSI EP17-A2 LoD verification. Planning centered on three detection claims at verification concentration c* (E1, E2, E3; Table 1). We calculated required n* using asymptotic formulas and confirmed with exact binomial methods. Operating characteristics were evaluated with finite-sample binomial probabilities; asymptotic approximations served as comparators, not primary decision criteria.

**改进**：
- ✅ 删除"This was an analytical study"
- ✅ 简化"as enumerated"
- ✅ 拆分长句（60→35+25词）

---

## 四、全文修改工作流

### Step 1: 粗删减（2小时）
**目标**: 4645词 → 4000词

1. 删除所有"This is not X. It is Y."句式
2. 删除所有破折号解释（改为括号或句号）
3. 删除Methods中的公式展示（移到Supplement）
4. 删除Results中的Box 1-2（改为正文）

---

### Step 2: 句子拆分（2小时）
**目标**: 无超过30词的句子

1. 在Hemingway Editor中粘贴每段
2. 所有紫色/红色句子拆分为2句
3. 删除"which/that/when"从句中的1个

---

### Step 3: 去AI化检查（1小时）
**目标**: GPTZero AI概率<30%

1. 上传前500词到GPTZero
2. 重写标红的高AI概率句子
3. 删除所有"Herein/Operationally/What has not"开头

---

### Step 4: 终审（1小时）
**目标**: 自然流畅

1. Grammarly全文检查
2. 朗读Introduction（卡顿的地方需修改）
3. 检查是否每段有不同节奏（避免机械重复）

---

## 五、常见问题

### Q1: 删除这些"AI痕迹"会降低学术性吗？
**A**: 不会。顶级期刊（Nature, Science, Cell）的论文很少用破折号和嵌套从句。简洁=专业。

### Q2: 如何判断修改是否成功？
**A**: 三个标准：
1. Hemingway Grade ≤12
2. GPTZero AI概率<30%
3. 您自己朗读时不觉得别扭

### Q3: 如果GPTZero误判怎么办？
**A**: 工具仅供参考。重点是消除上述5大特征，而非追求完美分数。

---

## 六、修改前后对比示例（完整段落）

### Introduction第3段

**修改前（AI痕迹严重，48词）**：
> Operationally, $LoD_{95}$ names the concentration at which a single replicate is detected with probability $p=0.95$, so a miss at that concentration is a rare event with probability $1-p=0.05$. That analytical 5% is the physical meaning of a detection limit: non-detection at LoD should be uncommon. Verification then asks whether a batch of $n$ replicates at $c^{\ast}$ provides acceptable inferential evidence that $p(c^{\ast})$ meets the claim, layering a second 5%—typically the Type I error rate $\alpha=0.05$—over the physical rare-miss threshold.

**AI特征**：
- "Operationally"开头（GPT喜欢用）
- "so...so..."重复推理
- "That analytical 5%"回指（教科书式）
- "layering a second 5%"隐喻（过于文学化）

**修改后（自然写作，35词）**：
> At LoD₉₅, single-replicate detection probability equals 0.95 (analytical 5% miss rate). Sample size planning adds inferential control: Type I error α typically 0.05, and power 1-β typically 0.80. These two layers—analytical and inferential—are often confused in validation documents.

**改进**：
- ✅ 删除"Operationally"
- ✅ 合并重复解释
- ✅ 添加实际意义（"confused in validation"）
- ✅ 词数：48→35（节省27%）

---

## 七、最终检查清单

修改完成后，确认：

- [ ] 全文破折号≤5处
- [ ] 无"This is not...It is..."句式
- [ ] 无"What has not been..."开头
- [ ] 无"Herein/Operationally"
- [ ] 平均句长≤25词（Hemingway检查）
- [ ] 无超过30词的单句
- [ ] GPTZero AI概率<35%
- [ ] Grammarly Tone = "Formal but clear"
- [ ] 朗读Introduction不卡顿

---

**记住**：AI是起草工具，人类修改是发表关键。您的科学思想是原创的，现在只是换一种自然的方式表达它。

**预计总时间**: 6-8小时全文去AI化修改
