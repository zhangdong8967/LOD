# Methods 修订版 - 自然叙事风格

## 修订说明
去除过多E1/E2/E3标签和编号，改为流畅的段落式叙事，更符合Clinical Chemistry期刊风格

---

## Methods

### Study Design and Definition of Detection Claims

We conducted a prespecified computational sample-size analysis of low-end detection verification and applied the resulting framework to archived validation records. Our analysis was organized around three detection-claim structures commonly encountered when reviewing verification protocols. We refer to these as benchmark confirmation, two-arm difference testing, and qualitative pass criteria.

Benchmark confirmation addressed whether the detection probability at a prespecified concentration was consistent with a benchmark, typically 0.95. The estimand was the single-replicate detection probability p(c*) at the verification concentration c*. A claim was considered supported when the lower one-sided 95% Clopper–Pearson confidence limit for p(c*) was at least p₀. For sample-size planning, statistical power was defined as the probability of satisfying this confirmation criterion under a prespecified alternative detection probability. When an archived protocol did not specify an alternative probability, its recorded design was evaluated using its exact operating characteristic.

Two-arm difference testing arose from lot-to-lot or material-to-material wording at the limit of detection. The question was whether positivity at c* differed between new and reference materials. The estimand was the difference in detection probabilities, θ₂ = pₐ(c*) - pᵦ(c*). We used the 2-sided Fisher exact test of H₀: θ₂=0 at α=0.05 as the primary inferential framework. Under a prespecified alternative pair (pₐ, pᵦ), power was the probability of rejecting the null hypothesis. Equal allocation (nₐ=nᵦ) was used for the primary lattice analysis. A protocol statement of "equivalent" was not interpreted as formal equivalence unless an equivalence or noninferiority margin was explicitly prespecified.

Qualitative pass criteria represented fixed acceptance rules such as at least k positive results among n replicates. A 19-of-20 criterion was common in archived protocols. The operating characteristic was the binomial pass probability P(X≥k|n,p). This quantity was treated separately from statistical confirmation of a 95% detection-probability benchmark.

The primary analysis assumed independent replicate results. Unless otherwise specified, α=0.05 and the target power was 80% (β=0.20). The required sample size was defined as the smallest integer satisfying the prespecified operating characteristic. For two-arm comparisons, n* refers to the number of replicates required in each arm.

### Sample Size Planning and Exact Operating Characteristics

Sample-size planning used asymptotic approximations for initial calculation followed by exact enumeration for the final design. For two-arm comparisons with equal allocation, the initial approximation was the standard formula for comparing 2 independent binomial proportions:

n* = [z_{α/2}√(2p̄(1-p̄)) + z_{1-β}√(pₐ(1-pₐ)+pᵦ(1-pᵦ))]² / (pₐ-pᵦ)²

where p̄=(pₐ+pᵦ)/2. The smallest integer n satisfying the exact Fisher power target was then identified by integer search.

For the primary two-arm analysis, we enumerated all 1,225 unique probability pairs on a 1-percentage-point grid spanning 50% through 99%. For each pair and candidate sample size n, exact Fisher power was calculated by summing the joint binomial probabilities of all outcome pairs that met the prespecified Fisher rejection criterion. The lattice represented a discrete sensitivity surface. Exact-test power calculations followed the framework described by Casagrande et al.

The conventional 20-replicate design was evaluated separately as a fixed comparator. For each probability pair, we calculated power and type II error (β) at n=20 per arm. A secondary underpowering indicator was defined as β>0.80, corresponding to power below 20%.

For benchmark-confirmation claims, the sample-size search evaluated the probability of obtaining a lower one-sided 95% Clopper–Pearson confidence limit at or above p₀ under the prespecified alternative probability. For qualitative pass criteria, sample-size calculations were based directly on the binomial pass probability. Exact binomial calculations used the methods of Clopper and Pearson and standard categorical-data formulations.

Fisher exact inference was the primary analysis for two-arm comparisons because of small expected cell counts near the detection boundary. A Boschloo exact test was evaluated as a sensitivity analysis because it provides an unconditional alternative that can have greater power while maintaining exact type I error control. The sensitivity analysis did not replace the primary Fisher-based sample-size surface.

Where replicate clustering was considered, a design-effect sensitivity analysis was performed. For clusters of size m with intracluster correlation coefficient ρ, the design effect was DE=1+(m-1)ρ, and the inflated replicate requirement was n=⌈n*·DE⌉. The primary analysis used DE=1, corresponding to independent replicate results.

For datasets containing multiple concentrations, detection probability as a function of concentration was modeled using logistic dose-response regression when an empirical curve was required. Concentration was analyzed on the log scale. These models were used only to obtain protocol-specific detection probabilities for the retrospective analysis.

### Retrospective Audit of Validation Records

We performed a prespecified retrospective audit of publicly accessible validation records to determine whether reported replicate designs were aligned with the corresponding statistical claims. The audit comprised 16 document-level records, including 10 protocol or dataset records, 3 open-access institutional replicate panels, and 3 published limit-of-detection tables. Source-specific bibliographic information and verbatim excerpts are provided in Supplement Table 7b.

For each record, we extracted the limit-of-detection or lot-verification statement describing the analytical claim, mapped the statement to one of the three claim structures, and recorded the reported replicate count, acceptance criterion, detection-probability target, and lot or material structure. We then calculated the claim-specific required sample size using the same prespecified planner used for the lattice analysis and calculated the exact operating characteristic of the reported design.

Representative phrase mappings included: "≥19/20 at LoD" mapped to qualitative pass criterion; "confirm 95% detection at c*" mapped to benchmark confirmation; "lots equivalent at LoD" mapped to two-arm difference testing with stated discrimination, noninferiority, or equivalence; "no significant lot difference" mapped to two-arm difference testing with prespecified (pₐ,pᵦ), not equivalence from p>0.05 alone.

A reported 20-replicate design was recorded as n=20. When the replicate count could not be determined, the sample size was coded as not reported rather than imputed. Archived wording was treated as evidence of the reported verification design, not as evidence that the underlying laboratory procedure had been independently revalidated.

When a source provided explicit values for p₀, pₐ, or pᵦ, those values were used directly. When the protocol did not report a detection probability but provided concentration-response data, p(c*) was estimated from the corresponding empirical detection curve using the prespecified logistic model.

### Public Data Sources and Reproducibility

The public-data component included 10 openly accessible replicate-level datasets spanning clinical chemistry and related in vitro diagnostic applications. Additional publicly available institutional and published records were included for the retrospective audit but were analyzed as document-level evidence. The complete source list, eligibility criteria, extracted wording, mapped claim, and analytical path are provided in Supplement Table 7b.

All calculations were implemented in Python 3.10 using lod_guide version 0.5.0. Exact calculations were deterministic; no random simulation was used for the primary sample-size calculations or lattice enumeration. Source data, analysis scripts, software version information, and the audit ledger were retained to allow reconstruction of the figures and tables. Detailed implementation steps, diagnostic checks, and sensitivity analyses are provided in Supplementary Methods §S2.

The statistical framework was based on CLSI EP17-A2 for detection-capability verification, CLSI EP26 for reagent-lot verification, exact binomial inference, and exact methods for comparing 2 independent binomial proportions.

---

## 主要修改对比

| 原版特征 | 修订版改进 |
|---------|----------|
| E1/E2/E3标签反复出现 | 改为"benchmark confirmation"等自然描述 |
| 编号段落(1. 2. 3.) | 流畅段落叙事 |
| "Article labels only—not CLSI" | 删除（只说一次即可） |
| Box 3作为独立框 | 融入审计段落 |
| "Operationally we test..." | "We used...test as the primary framework" |
| 过多小标题 | 整合为三个主标题 |

保留：所有技术细节、公式、统计方法、数字准确性
