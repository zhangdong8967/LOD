# Seed bibliography (English only)

Vancouver-style drafts. Expand after running the queries in [`SEARCH_PROTOCOL.md`](SEARCH_PROTOCOL.md).

**Legend:** S = standard/guidance · P = peer-reviewed methods · D = software/dataset · T = textbook/statistical reference

---

## Standards and regulatory (S)

| ID | Reference | Role in `lod_guide` | Access |
|----|-----------|---------------------|--------|
| S1 | Clinical and Laboratory Standards Institute. *Evaluation of Detection Capability for Clinical Laboratory Measurement Procedures*; EP17-A2. 2nd ed. Wayne, PA: CLSI; 2012. | LoB/LoD/LoQ definitions; parametric vs nonparametric; probit; verification designs | [CLSI EP17](https://clsi.org/shop/standards/ep17/) (purchase); [FDA recognition 30531](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfStandards/detail.cfm?standard__identification_no=30531) |
| S2 | CLSI. *Evaluation of Detection Capability Implementation Guide*; EP17IG. 2021. | Laboratory verification workflow; workbook link | [CLSI EP17IG](https://clsi.org/shop/standards/ep17ig/) (purchase) |
| S3 | CLSI. *Measurement Procedure Comparison and Bias Estimation Using Patient Samples*; EP09. | Discussion cross-ref for low-end method comparison | CLSI (purchase) |
| S4 | CLSI. *Evaluation of Precision of Quantitative Measurement Procedures*; EP05-A3. | Precision profile / LoQ linkage | CLSI (purchase) |
| S5 | International Organization for Standardization. ISO 11843 series (*Capability of detection*). | Theoretical α/β framing cited by Linnet et al. | ISO (purchase) |
| S6 | U.S. FDA. Recognized Consensus Standard: CLSI EP17-A2. | Regulatory context | See S1 FDA link |
| S7 | ICH. *E9(R1) Statistical Principles for Clinical Trials: Addendum on Estimands and Sensitivity Analysis*. 2020. | Estimand-first framing (G1–G4) | [ICH E9(R1)](https://database.ich.org/) |

---

## Core methods papers (P) — already mapped to this work

| ID | Reference | Maps to | DOI / PMC |
|----|-----------|---------|-----------|
| P1 | Linnet K, Kondratovich M. Partly nonparametric approach for determining the limit of detection. *Clin Chem*. 2004;50(4):732-740. | Non-Gaussian LoB; order statistics; LoD sample size | [10.1373/clinchem.2003.029983](https://doi.org/10.1373/clinchem.2003.029983) |
| P2 | Kondratovich M, Linnet K. Verification of claimed limit of detection in molecular diagnostics. *J Appl Lab Med*. 2017;1(4):429-438. | EP17 verification pass/fail probability; n=20 behavior | [10.1373/jalm.2016.020735](https://doi.org/10.1373/jalm.2016.020735) |
| P3 | Armbruster DA, Pry T. Limit of blank, limit of detection and limit of quantitation. *Clin Lab Med*. 2008;29(1):49-52. | Introductory LoB/LoD/LoQ; manufacturer 60 vs lab 20 | [PMC2556583](https://pmc.ncbi.nlm.nih.gov/articles/PMC2556583/) → `papers/armbruster2008_lob_lod_loq_clinlab.pdf` |
| P4 | Galitzine C, et al. Nonlinear regression improves accuracy of characterization of multiplexed mass spectrometric assays. *Mol Cell Proteomics*. 2018;17(1):3-12. | MSstatsLOBD; tier-A CPTAC data | [10.1074/mcp.RA117.000322](https://doi.org/10.1074/mcp.RA117.000322) |
| P5 | Boschloo RD. Raised conditional level of significance for the 2×2 table when testing the hypothesis of independence in an contingency table. *Stat Neerl*. 1970;24(2):191-199. | Exact confirmation layer (G2) | — |
| P6 | Malkamäki S, et al. Radioimmuno-dot-blot (Anal Chem 2024). | Tier-A precision/linearity deposits | [10.1021/acs.analchem.4c03393](https://doi.org/10.1021/acs.analchem.4c03393) |
| P7 | Carobene A, et al. Commutability of Lombardy Region EQA control materials. *Clin Chim Acta*. 2025. | Tier-A multilab chemistry (precision / DE, not blank–LoB) | [10.17632/r4szpw8sn5](https://data.mendeley.com/datasets/r4szpw8sn5) |

---

## Statistical references (T)

| ID | Reference | Maps to |
|----|-----------|---------|
| T1 | Fleiss JL, Levin B, Paik MC. *Statistical Methods for Rates and Proportions*. 3rd ed. Wiley; 2003. Ch. 4. | G2 sample size (Fleiss–Chow) |
| T2 | Chow SC, Shao J, Wang H. *Sample Size Calculations in Clinical Research*. 2nd ed. CRC; 2008. | Two-proportion power; exact vs asymptotic |
| T3 | Agresti A. *Categorical Data Analysis*. 3rd ed. Wiley; 2013. | Fisher, Boschloo, Wilson, Clopper–Pearson |

---

## Software and open data (D)

| ID | Resource | Local copy |
|----|----------|------------|
| D1 | Analyse-it Detection Capability (EP17-A2) | `software/analyseit_ep17_examples.html`; xlsx in `data/raw/EP17-A2-Example-*.xlsx` |
| D2 | Bioconductor **MSstatsLOBD** | `software/bioconductor_msstatslobd_vignette.html` |
| D3 | OpenEpi two-proportion sample size | `papers/openepi_two_proportion_sample_size.pdf` |
| D4 | **lod_guide** (this repo) | `src/lod_guide/` |

---

## Folklore challenge anchors (C1–C5 → literature gap)

| Claim | Standard allows | Our formalization | Search theme |
|-------|-----------------|-------------------|--------------|
| C1 Fixed n=20 for all LoD tasks | EP17 verification designs | G2 powered n; P8 exact–asymptotic gap | Block B |
| C2 Always-normal LoB | EP17 nonparametric path | S2 gate; P5 mismatch | Block A + C |
| C3 Ignore ICC / pooling | EP05 / design effect | S2 ICC; P4 design effect | Block E |
| C4 Compare via 1−(1−p)^n | Not EP17 comparative estimand | P1 saturation | Block B |
| C5 One protocol for all result types | EP17 multi-path menu | S1 routing; tier-A families | Block A |

---

## BibTeX (seed)

```bibtex
@book{clsi_ep17_a2_2012,
  author    = {{Clinical and Laboratory Standards Institute}},
  title     = {Evaluation of Detection Capability for Clinical Laboratory Measurement Procedures},
  edition   = {2nd},
  year      = {2012},
  publisher = {CLSI},
  address   = {Wayne, PA}
}

@article{linnet2004_lod,
  author  = {Linnet, Kristian and Kondratovich, Marina},
  title   = {Partly Nonparametric Approach for Determining the Limit of Detection},
  journal = {Clinical Chemistry},
  volume  = {50},
  number  = {4},
  pages   = {732--740},
  year    = {2004},
  doi     = {10.1373/clinchem.2003.029983}
}

@article{kondratovich2017_lod_verify,
  author  = {Kondratovich, Marina and Linnet, Kristian},
  title   = {Verification of Claimed Limit of Detection in Molecular Diagnostics},
  journal = {The Journal of Applied Laboratory Medicine},
  volume  = {1},
  number  = {4},
  pages   = {429--438},
  year    = {2017},
  doi     = {10.1373/jalm.2016.020735}
}
```
