# Core literature — close-reading notes (manuscript-ready)

**Purpose:** Writing material for *Assumption-Gated Decision Theory for Clinical LoD Evaluation*.  
**Verify:** Page numbers and numeric examples against PDF before final citation.  
**Full text:** 2/4 core papers OA locally; 2 paywalled (abstract + known results below).

| PMID | Citation | PDF local |
|------|----------|-----------|
| 18852857 | Armbruster DA, Pry T. LoB/LoD/LoQ. *Clin Biochem Rev* 2008;29 Suppl:S49–52 | Yes |
| 14764644 | Linnet K, Kondratovich M. *Clin Chem* 2004;50:732–740 | Abstract only |
| 33626838 | Kondratovich M, Linnet K. *J Appl Lab Med* 2017;1(4):429–438 (DOI 10.1373/jalm.2016.020735) | Abstract only |
| 29438992 | Galitzine C et al. *Mol Cell Proteomics* 2018;17:913–924 | Yes (PMC) |

---

## 1. Armbruster & Pry 2008 (PMID 18852857) — standards vocabulary & folklore n=20

**File:** `literature/papers/pdfs/18852857_limit_of_blank_limit_of_detection_and_limit_of_quantitation.pdf`

### What they establish

- Accessible summary of **CLSI EP17** LoB / LoD / LoQ definitions for clinical laboratorians.
- LoB = mean(blank) + 1.645×SD(blank) under Gaussian blank assumption (Type I α≈5%).
- LoD = LoB + 1.645×SD(low-concentration sample) — empirical low-level sample required, not “mean+2SD of blank alone.”
- LoQ = lowest concentration meeting **predefined bias + imprecision** goals (may exceed LoD).

### Quotable for Introduction

- “A recommended practical number of LoB and LoD samples … **60** [manufacturer establish], while a laboratory **verifying** a manufacturer’s LoD … is **20**.” (p. S50)
- Critique of blank-only LoD: Needleman–Romberg — “It defines only the ability to measure nothing.”
- EP17 allows **non-parametric** routes when Gaussian assumptions fail.

### Gap we fill (C1, framing)

Armbruster explains *what* EP17 says and the 60 vs 20 split but does **not**:

- Give powered \(n\) for **comparative** LoD claims (G2).
- Formalize **diagnostic gating** before parametric LoB.
- Quantify folklore risk under an explicit loss \(L\).

**Manuscript use:** Intro paragraph 2 — cite as accessible EP17 summary; pivot to “verification \(n=20\) is not powered for every estimand.”

---

## 2. Linnet & Kondratovich 2004 (PMID 14764644) — partly nonparametric LoD

**DOI:** 10.1373/clinchem.2003.029983 | **PDF:** paywalled — abstract in `notes/records/14764644.json`

### Problem

ISO-style LoD procedures assume **Gaussian blanks**, Gaussian low samples, linear calibration. Clinical chemistry blanks are often **skewed**; calibration may be nonlinear.

### Method (core formulas)

- **LoB (nonparametric):** \((n \cdot 0.95 + 0.5)\)-th ordered blank observation → 95th percentile without normality.
- **LoD:** \(\mathrm{LoD} = \mathrm{LoB} + c_\beta \cdot \mathrm{SDS}\), where SDS = analytical SD at low concentration; \(c_\beta = z_{1-\beta}/(1 - 1/(4f))\) ≈ **1.65** at β=5%, \(f\) = df for SDS.
- Presents **confidence limits** and **sample size** considerations + simulation validation.

### Results to cite

- Works when blank distributions deviate from normality (motivates our **S2 skew gate** and P5 mismatch).
- Extends ISO α/β framing into clinical chemistry practice.

### Gap we fill

- Single-path **estimation** paper; no estimand menu (G1–G4), no **two-proportion** kit comparison, no exact Fisher confirmation layer.
- Sample-size discussion is for **establishment**, not folklore verification of comparative claims.

**Manuscript use:** Methods §2.3 continuous LoB — “when S2 rejects normality, follow Linnet-type nonparametric LoB (EP17-aligned).” Cite for **P5** parametric mismatch motivation.

---

## 3. Kondratovich & Linnet 2017 JALM (PMID 33626838) — EP17 verification probability

**DOI:** 10.1373/jalm.2016.020735 | **PDF:** paywalled (Oxford/JALM)

### Problem

EP17 verification: test claimed LoD concentration; **pass** if 95% CI for detection proportion contains 95%. At finite \(n\), systematic/random errors cause **false pass/fail**. PCR molecular assays add Poisson structure.

### Method

- **Poisson-binomial** model for PCR hit rates.
- Computes **P(pass verification)** vs number of replicates and vs ratio (test concentration / true LoD).

### Key results (abstract — verify in PDF when obtained)

- P(pass) depends on \(n\) with **local minima/maxima** between 0.975 and 0.995 for \(n=20\)–1000 when sample is at true LoD.
- Detecting difference between claimed vs actual LoD **increases with \(n\)**.
- Provides **planning tables/graphs** for molecular diagnostics.

### Direct support for our C1 / G2 / Table 3 narrative

- Closest prior art to “**n=20 is not neutral**” for verification — but focused on **single-method EP17 pass/fail**, not **90% vs 80% reagent discrimination**.
- We extend: exact Fisher/Boschloo, decision risk ratio (~3.9× folklore vs powered), operating-characteristic Monte Carlo.

**Manuscript use:** Results §3.1 — “Prior work quantified EP17 verification pass probability (Kondratovich 2017); we generalize to comparative estimands and exact small-sample confirmation.”

---

## 4. Galitzine et al. 2018 MCP (PMID 29438992) — MSstatsLOBD / tier-A proteomics

**File:** `literature/papers/pdfs/29438992_nonlinear_regression_improves_accuracy_of_characterization_o.pdf`  
**DOI:** 10.1074/mcp.RA117.000322 | **Software:** Bioconductor `MSstatsLOBD`

### Problem

Linear/logistic fit for intensity–concentration curves **underestimates** LoB/LoD when intensities **plateau at low concentration** (common in multiplex MS).

### Method

- **Nonlinear regression** capturing noise → linear → saturation regimes (Fig. 1).
- **LoB:** intersection of upper **95% prediction interval** of blank noise with fit (not mean CI).
- **LoD:** intersection of blank noise upper PI with lower PI of analyte response (90% two-sided PI interpretation).
- Implemented in **MSstats**; evaluated on 11 experimental sets (DIA/PRM/SRM) + simulation.

### Key numbers

- When low-concentration plateau present: nonlinear LoB/LoD **20–40% higher** than linear fit.
- Without plateau: nonlinear ≡ weighted linear.

### Link to our tier-A evidence

- CPTAC calibration data in `data/raw/CPTAC_MSstatsLOBD_calibration_raw.csv` derives from this ecosystem.
- **Domain boundary:** targeted proteomics blank–LoB, **not** general clinical chemistry analyzer panels.

**Manuscript use:** Table 7 / Fig 7 tier-A row; Discussion — “proteomics LoB path is nonlinear MS-specific; our S0–S7 routes continuous chemistry blanks separately.”

---

## 5. Synthesis — how prior work maps to `lod_guide`

| Prior contribution | What they solve | What we add |
|--------------------|-----------------|-------------|
| EP17 / Armbruster | Legal LoB/LoD/LoQ options | Executable S0–S7 + estimand lock (G1–G4) |
| Linnet 2004 | Nonparametric LoD under skew | S2 gate + auditable path + P5 mismatch |
| Kondratovich 2017 | Verification pass probability at claimed LoD | G2 two-proportion power; exact Fisher; loss \(L\) |
| Galitzine 2018 | MS LoB/LoD nonlinear fit | Tier-A proteomics case; not pooled with chemistry |
| Folklore n=20 | — | P7 all-positive trap; P8 exact–asymptotic gap; ~3.9× risk ratio |

---

## 6. Block B2/C — secondary readings (downloaded / abstract)

| PMID | Title (short) | Relevance | PDF |
|------|---------------|-----------|-----|
| 15899655 | Linnet 2005 bootstrap SE for LoD (HPLC) | Extends 2004; bootstrap uncertainty | Abstract |
| 28932796 | hs-cTnI validation across city (LoB n=60) | Real-world EP17-style LoB verify; multilab | Yes |
| 28932798 | LOCI method LoD performance | Method validation example | Yes |

**28932796 takeaway:** LoB verification used **n=60** blanks across 5 analyzers — contrasts with folklore 20; supports manufacturer vs lab \(n\) asymmetry argument.

---

## 7. Citation snippets (draft — check pagination)

```text
Armbruster DA, Pry T. Limit of blank, limit of detection and limit of quantitation.
  Clin Biochem Rev. 2008;29 Suppl 1:S49-S52. PMID:18852857.

Linnet K, Kondratovich M. Partly nonparametric approach for determining the limit of detection.
  Clin Chem. 2004;50(4):732-740. doi:10.1373/clinchem.2003.029983.

Kondratovich M, Linnet K. Verification of claimed limit of detection in molecular diagnostics.
  J Appl Lab Med. 2017;1(4):429-438. doi:10.1373/jalm.2016.020735.

Galitzine C, et al. Nonlinear regression improves accuracy of characterization of multiplexed
  mass spectrometric assays. Mol Cell Proteomics. 2018;17(5):913-924.
  doi:10.1074/mcp.RA117.000322.
```

---

## 8. Files produced by pipeline

```
literature/papers/pdfs/          # OA PDFs (PMID_slug.pdf)
literature/notes/records/        # One JSON per PMID (metadata + abstract + pdf preview)
literature/notes/deep/           # This file + block scaffolds
literature/notes/READING_INDEX.md
literature/notes/manifest.json
```

Re-run after adding institutional PDFs:

```bash
python literature/scripts/literature_fetch.py --priority core
python literature/scripts/literature_summarize.py --priority core
```
