# Pre-Specified Analysis Protocol (lod_guide)

**Protocol ID:** `LOD-GUIDE-CC-2026-v1`  
**Intended manuscript:** *Clinical Chemistry* methodology  
**Software:** `lod_guide` ≥ 0.3.0

This protocol is locked **before** confirmatory interpretation. Exploratory pilot data may inform \(\pi_{\mathrm{pilot}}\) but must be declared.

---

## 1. Objectives

Primary: demonstrate that an **estimand-gated, assumption-gated** LoD design algorithm (S0–S7) yields:

- path decisions with explicit pass/fail diagnostics;
- sample sizes with stated operating characteristics;
- transparent audit hashes.

Secondary: show that folklore \(n=20\) is underpowered for \(\Delta=0.10\) near \(p\approx 0.85\); that \(1-(1-p)^n\) saturates for comparative claims; that parametric LoB fails on exponential blanks.

---

## 2. Estimands

Exactly one primary estimand per analysis run, from `lod_guide.theory.estimands`.

| Analysis block | Estimand |
|----------------|----------|
| A1 Reagent discrimination | E2: \(\theta_2=p_A-p_B\), \(\Delta^\star=0.10\), \(p_A=0.90\), \(p_B=0.80\) |
| A2 Skewed blanks | E1 concentration/LoB path under continuous type |
| A3 Real qPCR (Zenodo) | E1 on NTC blanks + optional E2 on hit rates by SQ |
| A4 Proposition battery | P1–P6 machine certificates |

---

## 3. Error rates and power

- Two-sided \(\alpha=0.05\) unless noted.  
- Target power \(1-\beta=0.80\) for E2.  
- Diagnostic thresholds: `DiagnosticThresholds` v0.1.0 (frozen).

---

## 4. Data

1. **Simulated** (seeds declared in audit): full `simulate.ALL_SIMULATORS` catalogue.  
2. **Real:** Zenodo 12609243 Mus WT and multiplex qPCR LoD/LoQ CSVs (citation in audit).  
3. No post-hoc exclusion except non-finite values (pre-specified).

---

## 5. Analysis steps (immutable order)

S0→S1→S2→S3→S4→S5→S6→S7, then write Audit JSON + SHA-256.

Monte Carlo seeds: `seed=0` for proposition power checks unless audit overrides.

---

## 6. Success criteria (confirmatory)

1. All of P1–P6 certificates `passed=True`.  
2. E2 A1 reports \(n^\star\in[190,210]\) and warns that \(n=20\) power \(<0.25\).  
3. Skewed/hetero simulation selects nonparametric path or failed correction.  
4. Audit file exists with `sha256_content` and matching recomputation.

---

## 7. Deviations

Any deviation from this protocol must be labeled **exploratory** in the manuscript and audit `notes`.
