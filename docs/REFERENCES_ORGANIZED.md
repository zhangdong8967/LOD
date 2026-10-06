# 参考文献整理（按引用顺序）

## 数字验证结果

✅ **所有关键数字已验证准确：**
- 1225个唯一(pA,pB)对：✓ 正确
- 61% β>0.8：✓ 正确（来源：lattice_surface_model.json frac_miss_gt_0.8: 0.6106）
- 中位数n*=116：✓ 正确（来源：median_n_star: 116.01）
- 19/20规则p=0.95通过率73.6%：✓ 正确（binom计算0.7358）
- 20/20 CP下限<0.95：✓ 正确（0.8609 < 0.95）
- (0.90,0.80) n*≈199：✓ 正确（Fleiss-Chow: 198.7）
- 比率2.65-5.80：✓ 正确（53/20=2.65, 116/20=5.8）
- 比率范围2.6-10×：✓ 正确（最大199/20=9.95≈10×）

---

## 参考文献整理版本（按类别分组，然后按引用顺序编号）

### 一、核心CLSI指南文献（引用1-2）

**1.** Clinical and Laboratory Standards Institute. Verification of detection capability for clinical laboratory measurement procedures. 2nd ed. CLSI document EP17-A2. Wayne, PA: Clinical and Laboratory Standards Institute; 2012.
   - **核验**: CLSI官方页面确认
   - **用途**: EP17-A2定义、LoB/LoD/LoQ验证、manufacturer claim verification
   - **引用位置**: Introduction(多次), Methods, Discussion

**2.** Clinical and Laboratory Standards Institute. User verification of acceptability of a reagent lot change. 2nd ed. CLSI document EP26. Wayne, PA: Clinical and Laboratory Standards Institute; 2022.
   - **核验**: CLSI官方页面确认
   - **用途**: 试剂批次验证框架、analyte-specific criteria
   - **引用位置**: Introduction第1段, Discussion第4段

---

### 二、临床化学实证文献（引用3-5）

**3.** Algeciras-Schimnich A, Bruns DE, Boyd JC, Bryant SC, La Fortune KA, Grebe SKG. Failure of current laboratory protocols to detect lot-to-lot reagent differences: findings and possible solutions. Clin Chem. 2013;59(8):1187-1194. doi:10.1373/clinchem.2013.205070.
   - **核验**: PubMed PMID 23592508
   - **关键发现**: IGF-I lot validation需要>100 samples达到90% power
   - **引用位置**: Discussion第4段（临床化学相关性）

**4.** Katzman BM, Ness KM, Algeciras-Schimnich A. Verification of the CLSI EP26-A protocol for detection of reagent lot-to-lot differences. Clin Biochem. 2017;50(13-14):768-771. doi:10.1016/j.clinbiochem.2017.03.012.
   - **核验**: PubMed PMID 28322878
   - **关键发现**: EP26-A对6个analytes要求样本量1-48（vs常规20）
   - **引用位置**: Discussion第4段

**5.** Kim S, Chang J, Kim SK, Park S, Huh J, Jeong TD. Sample size and rejection limits for detecting reagent lot variability: analysis of the applicability of the Clinical and Laboratory Standards Institute (CLSI) EP26-A protocol to real-world clinical chemistry data. Clin Chem Lab Med. 2020;59(1):127-138. doi:10.1515/cclm-2020-0454.
   - **核验**: PubMed PMID 32628625
   - **关键发现**: 83个chemistry tests，样本量因analyte/critical difference而异
   - **引用位置**: Discussion第4段

---

### 三、LoD方法学文献（引用6-8）

**6.** Armbruster DA, Pry T. Limit of blank, limit of detection and limit of quantitation. Clin Biochem Rev. 2008;29(Suppl 1):S49-52.
   - **核验**: PubMed PMID 18852857, 有PMC全文
   - **用途**: LoB/LoD/LoQ基本定义
   - **引用位置**: Introduction第1段（背景定义）

**7.** Linnet K, Kondratovich M. Partly nonparametric approach for determining the limit of detection. Clin Chem. 2004;50(4):732-740. doi:10.1373/clinchem.2003.029983.
   - **核验**: PubMed PMID 14764645
   - **关键贡献**: LoD determination应考虑type I和type II errors
   - **引用位置**: Introduction第2段（分析特性vs统计性质区分）

**8.** Vaks JE, Hemyari P, Rullkoetter M, Santulli MJ, Schoenbrunner N. Verification of claimed limit of detection in molecular diagnostics. J Appl Lab Med. 2016;1(3):260-270. doi:10.1373/jalm.2016.020735.
   - **核验**: PubMed PMID 33626838
   - **关键发现**: 通过/失败概率取决于replicate number和claimed vs actual LoD关系
   - **引用位置**: Introduction第2-3段, Discussion第2-3段

---

### 四、统计方法核心文献（引用9-13）

**9.** Clopper CJ, Pearson ES. The use of confidence or fiducial limits illustrated in the case of the binomial. Biometrika. 1934;26(4):404-413. doi:10.1093/biomet/26.4.404.
   - **核验**: Oxford Academic确认
   - **用途**: E1 benchmark confirmation的精确置信区间
   - **引用位置**: Methods

**10.** Fleiss JL, Tytun A, Ury HK. A simple approximation for calculating sample sizes for comparing independent proportions. Biometrics. 1980;36(2):343-346.
   - **核验**: PubMed PMID 7407314
   - **用途**: E2两比例比较的渐近样本量公式
   - **引用位置**: Methods公式(2), Introduction

**11.** Casagrande JT, Pike MC, Smith PG. The power function of the "exact" test for comparing two binomial distributions. J R Stat Soc Series C Appl Stat. 1978;27(2):176-180. doi:10.2307/2346945.
   - **核验**: Oxford Academic确认
   - **用途**: 精确vs渐近功效差异，exact Fisher power计算
   - **引用位置**: Methods, Discussion第5段

**12.** Fisher RA. The logic of inductive inference. J R Stat Soc. 1935;98(1):39-82. doi:10.2307/2342435.
   - **核验**: JSTOR确认
   - **用途**: Fisher exact test理论基础
   - **引用位置**: Methods（E2主要检验方法）

**13.** Boschloo RD. Raised conditional level of significance for the 2 × 2-table when testing the equality of two probabilities. Statistica Neerlandica. 1970;24(1):1-9. doi:10.1111/j.1467-9574.1970.tb00104.x.
   - **核验**: Wiley确认
   - **用途**: Boschloo unconditional exact test（敏感性分析）
   - **引用位置**: Methods

---

### 五、统计方法补充文献（引用14-16）

**14.** Mehta CR, Patel NR. A network algorithm for performing Fisher's exact test in r × c contingency tables. J Am Stat Assoc. 1983;78(382):427-434. doi:10.1080/01621459.1983.10477989.
   - **核验**: Taylor & Francis确认
   - **用途**: Fisher exact test计算算法
   - **引用位置**: Methods

**15.** Agresti A. Categorical Data Analysis. 3rd ed. Hoboken, NJ: John Wiley & Sons; 2013.
   - **核验**: Wiley官方确认
   - **用途**: 分类数据分析一般参考
   - **引用位置**: Methods

**16.** Chow SC, Shao J, Wang H. Sample Size Calculations in Clinical Research. 2nd ed. Boca Raton, FL: Chapman & Hall/CRC; 2008.
   - **核验**: CRC Press确认
   - **用途**: 临床研究样本量计算一般参考
   - **引用位置**: Methods（可选）

---

### 六、公开数据集文献（引用17-25，按tier A优先）

**17.** Analyse-it Software, Ltd. EP17 detection capability: worked examples (CLSI EP17-A2). Available from: https://analyse-it.com/support/examples. Accessed September 22, 2026.
   - **类型**: Tier A工作簿（estradiol、probit）
   - **用途**: EP17标准演示案例、审计Table 7行1-2
   - **引用位置**: Results审计部分、Table 7

**18.** Piaggio A. Building an eDNA surveillance toolkit for invasive rodents on islands: can we detect wild-type and gene drive Mus musculus? [dataset]. Zenodo; 2024. doi:10.5281/zenodo.12609243.
   - **类型**: Tier A qPCR数据集（wt + multiplex）
   - **用途**: 分子诊断LoD验证实例、审计Table 7行3-4
   - **引用位置**: Results审计部分

**19.** Galitzine C, Egertson JD, Abbatiello S, Henderson CM, Pino LK, MacCoss M, et al. Nonlinear regression improves accuracy of characterization of multiplexed mass spectrometric assays. Mol Cell Proteomics. 2018;17(5):913-924. doi:10.1074/mcp.RA117.000322.
   - **核验**: PubMed PMID 29500274
   - **类型**: Tier A蛋白质组学（CPTAC blank-LoB）
   - **用途**: 质谱LoB/LoD determination、审计Table 7行5
   - **引用位置**: Results审计部分

**20.** Choi M, Galitzine C, Vitek O. MSstatsLOBD: limit of blank and limit of detection estimation for targeted proteomics. Bioconductor; 2024. Available from: https://bioconductor.org/packages/MSstatsLOBD.
   - **类型**: 软件包（配合引用19）
   - **用途**: MSstatsLOBD方法
   - **引用位置**: Supplement数据来源

**21.** Carobene A, Vidali M, Ceriotti F, Alberghini A, Arcangeli A, Bellandi W, et al. Verification of the commutability of Lombardy region EQA control materials for enzymes, calcium, and creatinine. Clin Chim Acta. 2026;580:120745. doi:10.1016/j.cca.2025.120745. Dataset: doi:10.17632/r4szpw8sn5.
   - **核验**: Mendeley Data确认
   - **类型**: Tier A多实验室临床化学（ALT/AST/ALP/CK/LDH/肌酐/Ca）
   - **用途**: 多中心常规化学验证、审计Table 7行6
   - **引用位置**: Results审计部分

**22.** Malkamäki M, Gandier JA, Meinander K, Linder MB. Specific protein quantification by radioimmuno-dot-blot assay for complex mixture samples utilizing Strep-tag and tritium-labeled StrepTactin. Anal Chem. 2025;97(2):1087-1096. doi:10.1021/acs.analchem.4c03393.
   - **核验**: PubMed确认
   - **类型**: Tier A放射免疫测定（精密度+线性度）
   - **用途**: 免疫测定LoD验证、审计Table 7行7-8
   - **引用位置**: Results审计部分

**23.** Malkamäki M, Gandier JA, Meinander K, Linder MB. Data for publication: specific protein quantification by radioimmuno-dot-blot assay [dataset]. Zenodo; 2024. doi:10.5281/zenodo.12664367.
   - **类型**: Tier A数据集（配合引用22）
   - **引用位置**: Supplement数据来源

**24.** Sawant S, Harit D, Tomaras G. Underlying dataset for the manuscript titled "Qualification of a reporter virus microneutralization assay for verification of influenza specific antibodies in human clinical trials" [dataset]. Zenodo; 2025. doi:10.5281/zenodo.17108929.
   - **类型**: Tier A微中和测定（RMN ID50）
   - **用途**: 病毒学定量验证、审计Table 7行9
   - **引用位置**: Results审计部分

**25.** Dierendonck C. Cation/Anion concentrations for LOD/LOQ determination [dataset]. Zenodo; 2022. doi:10.5281/zenodo.5909650, doi:10.5281/zenodo.5901444.
   - **类型**: Tier B离子色谱（阳离子+阴离子）
   - **用途**: 化学分析LoD/LoQ
   - **引用位置**: Supplement数据来源

---

### 七、医院/临床验证记录（引用26-28）

**26.** Bzdok J, Czibere L, Burggraf S, Landt O, Maier EM, Röschinger W, et al. Quality considerations and major pitfalls for high throughput DNA-based newborn screening for severe combined immunodeficiency and spinal muscular atrophy. PLoS One. 2024;19(7):e0306329. doi:10.1371/journal.pone.0306329.
   - **核验**: PubMed PMID 39024281
   - **类型**: 医院新生儿筛查（TREC/KREC/SMN1）
   - **用途**: 分子诊断LoD验证实例、审计Table 7b行11-13
   - **引用位置**: Results审计部分

**27.** Lim HJ, Kang ER, Park MY, Kim BK, Kim MJ, Jung S, et al. Development of a multiplex real-time PCR assay for the simultaneous detection of four bacterial pathogens causing pneumonia. PLoS One. 2021;16(6):e0253402. doi:10.1371/journal.pone.0253402.
   - **核验**: PubMed PMID 34138982
   - **类型**: 临床PCR多重检测
   - **用途**: 多病原体检测验证、审计Table 7b行14
   - **引用位置**: Results审计部分

**28.** Hansen G, Marino J, Wang ZX, Beavis KG, Rodríguez-Barradas MC, Hemarajata P, et al. Direct comparison of SARS-CoV-2 analytical limits of detection across seven molecular assays. J Clin Microbiol. 2021;59(2):e01535-20. doi:10.1128/JCM.01535-20.
   - **核验**: PubMed PMID 33087440
   - **类型**: 临床微生物学（SARS-CoV-2）
   - **用途**: 跨平台LoD比较、审计Table 7b行15
   - **引用位置**: Results审计部分

**29.** Jiang Y, Wang H, Bai G, Zhong G, Liu Y. Development and clinical verification of a novel multiplex PCR test for detection of respiratory pathogens via fluorescence melting curve analysis. Sci Rep. 2025;15:30503. doi:10.1038/s41598-025-16434-2.
   - **核验**: 预印本或2025年发表
   - **类型**: 临床验证（呼吸道病原体）
   - **用途**: 多重PCR验证、审计Table 7b行16
   - **引用位置**: Results审计部分

---

## 最终推荐引用顺序（按首次出现位置）

### Introduction引用顺序：
1. EP17-A2 [1]
2. EP26 [2]
3. Algeciras-Schimnich 2013 [3] (或放在Discussion)
4. Katzman 2017 [4] (或放在Discussion)
5. Kim 2020 [5] (或放在Discussion)
6. Armbruster & Pry 2008 [6]
7. Linnet & Kondratovich 2004 [7]
8. Vaks et al. 2016 [8]

### Methods引用顺序：
9. Clopper & Pearson 1934 [9]
10. Fleiss et al. 1980 [10]
11. Casagrande et al. 1978 [11]
12. Fisher 1935 [12]
13. Boschloo 1970 [13]
14. Mehta & Patel 1983 [14]
15. Agresti 2013 [15]

### Results引用顺序（数据集）：
16. Analyse-it EP17 [17]
17. Piaggio Zenodo qPCR [18]
18. Galitzine 2018 proteomics [19]
19. Carobene Lombardy [21]
20. Malkamäki radioimmuno [22]
21. Sawant RMN [24]
22. 医院验证记录 [26-29]

### Discussion引用顺序：
- EP17-A2 [1] (重复引用)
- Vaks [8] (重复引用)
- Algeciras-Schimnich [3]
- Katzman [4]
- Kim [5]
- Casagrande [11] (重复引用)

---

## 建议采纳的最终参考文献列表（29篇，Vancouver格式）

**按首次出现位置编号：**

1. Clinical and Laboratory Standards Institute. Verification of detection capability for clinical laboratory measurement procedures. 2nd ed. CLSI document EP17-A2. Wayne, PA: Clinical and Laboratory Standards Institute; 2012.

2. Clinical and Laboratory Standards Institute. User verification of acceptability of a reagent lot change. 2nd ed. CLSI document EP26. Wayne, PA: Clinical and Laboratory Standards Institute; 2022.

3. Armbruster DA, Pry T. Limit of blank, limit of detection and limit of quantitation. Clin Biochem Rev. 2008;29(Suppl 1):S49-52.

4. Linnet K, Kondratovich M. Partly nonparametric approach for determining the limit of detection. Clin Chem. 2004;50(4):732-740.

5. Vaks JE, Hemyari P, Rullkoetter M, Santulli MJ, Schoenbrunner N. Verification of claimed limit of detection in molecular diagnostics. J Appl Lab Med. 2016;1(3):260-270.

6. Algeciras-Schimnich A, Bruns DE, Boyd JC, Bryant SC, La Fortune KA, Grebe SKG. Failure of current laboratory protocols to detect lot-to-lot reagent differences: findings and possible solutions. Clin Chem. 2013;59(8):1187-1194.

7. Katzman BM, Ness KM, Algeciras-Schimnich A. Verification of the CLSI EP26-A protocol for detection of reagent lot-to-lot differences. Clin Biochem. 2017;50(13-14):768-771.

8. Kim S, Chang J, Kim SK, Park S, Huh J, Jeong TD. Sample size and rejection limits for detecting reagent lot variability: analysis of the applicability of the Clinical and Laboratory Standards Institute (CLSI) EP26-A protocol to real-world clinical chemistry data. Clin Chem Lab Med. 2020;59(1):127-138.

9. Clopper CJ, Pearson ES. The use of confidence or fiducial limits illustrated in the case of the binomial. Biometrika. 1934;26(4):404-413.

10. Fleiss JL, Tytun A, Ury HK. A simple approximation for calculating sample sizes for comparing independent proportions. Biometrics. 1980;36(2):343-346.

11. Casagrande JT, Pike MC, Smith PG. The power function of the "exact" test for comparing two binomial distributions. J R Stat Soc Series C Appl Stat. 1978;27(2):176-180.

12. Fisher RA. The logic of inductive inference. J R Stat Soc. 1935;98(1):39-82.

13. Boschloo RD. Raised conditional level of significance for the 2 × 2-table when testing the equality of two probabilities. Statistica Neerlandica. 1970;24(1):1-9.

14. Mehta CR, Patel NR. A network algorithm for performing Fisher's exact test in r × c contingency tables. J Am Stat Assoc. 1983;78(382):427-434.

15. Agresti A. Categorical Data Analysis. 3rd ed. Hoboken, NJ: John Wiley & Sons; 2013.

16. Analyse-it Software, Ltd. EP17 detection capability: worked examples (CLSI EP17-A2). Available from: https://analyse-it.com/support/examples. Accessed September 22, 2026.

17. Piaggio A. Building an eDNA surveillance toolkit for invasive rodents on islands: can we detect wild-type and gene drive Mus musculus? [dataset]. Zenodo; 2024. doi:10.5281/zenodo.12609243.

18. Galitzine C, Egertson JD, Abbatiello S, Henderson CM, Pino LK, MacCoss M, et al. Nonlinear regression improves accuracy of characterization of multiplexed mass spectrometric assays. Mol Cell Proteomics. 2018;17(5):913-924.

19. Carobene A, Vidali M, Ceriotti F, Alberghini A, Arcangeli A, Bellandi W, et al. Verification of the commutability of Lombardy region EQA control materials for enzymes, calcium, and creatinine. Clin Chim Acta. 2026;580:120745. Dataset: doi:10.17632/r4szpw8sn5.

20. Malkamäki M, Gandier JA, Meinander K, Linder MB. Specific protein quantification by radioimmuno-dot-blot assay for complex mixture samples utilizing Strep-tag and tritium-labeled StrepTactin. Anal Chem. 2025;97(2):1087-1096.

21. Sawant S, Harit D, Tomaras G. Underlying dataset for the manuscript titled "Qualification of a reporter virus microneutralization assay for verification of influenza specific antibodies in human clinical trials" [dataset]. Zenodo; 2025. doi:10.5281/zenodo.17108929.

22. Dierendonck C. Cation concentrations for LOD/LOQ determination [dataset]. Zenodo; 2022. doi:10.5281/zenodo.5909650.

23. Dierendonck C. Anion concentrations for LOD/LOQ determination [dataset]. Zenodo; 2022. doi:10.5281/zenodo.5901444.

24. Bzdok J, Czibere L, Burggraf S, Landt O, Maier EM, Röschinger W, et al. Quality considerations and major pitfalls for high throughput DNA-based newborn screening for severe combined immunodeficiency and spinal muscular atrophy. PLoS One. 2024;19(7):e0306329.

25. Lim HJ, Kang ER, Park MY, Kim BK, Kim MJ, Jung S, et al. Development of a multiplex real-time PCR assay for the simultaneous detection of four bacterial pathogens causing pneumonia. PLoS One. 2021;16(6):e0253402.

26. Hansen G, Marino J, Wang ZX, Beavis KG, Rodríguez-Barradas MC, Hemarajata P, et al. Direct comparison of SARS-CoV-2 analytical limits of detection across seven molecular assays. J Clin Microbiol. 2021;59(2):e01535-20.

27. Jiang Y, Wang H, Bai G, Zhong G, Liu Y. Development and clinical verification of a novel multiplex PCR test for detection of respiratory pathogens via fluorescence melting curve analysis. Sci Rep. 2025;15:30503.

28. Choi M, Galitzine C, Vitek O. MSstatsLOBD: limit of blank and limit of detection estimation for targeted proteomics. Bioconductor; 2024. Available from: https://bioconductor.org/packages/MSstatsLOBD.

29. Malkamäki M, Gandier JA, Meinander K, Linder MB. Data for publication: specific protein quantification by radioimmuno-dot-blot assay [dataset]. Zenodo; 2024. doi:10.5281/zenodo.12664367.

---

## 使用建议

### 主文本引用：
- Introduction: [1-8]
- Methods: [1,2,9-15]
- Results: [16-27]
- Discussion: [1,3-8,11]

### 可精简版本（如需减少引用数量）：
保留核心15篇：
- CLSI: [1,2]
- 临床化学: [3-8]
- 统计核心: [9-11,13]
- 数据集代表: [16,17,19,20]

---

**整理完成日期**: 2026年8月24日  
**验证方法**: PubMed、CLSI官网、期刊官网、Zenodo DOI  
**数字验证**: Python scipy.stats计算 + 研究输出JSON确认
