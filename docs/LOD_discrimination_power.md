# Discriminating LoD Performance Between Reagents: Power and Sample Size

> Companion to `lod_discrimination_power.py`. Publication-oriented English analysis of whether insufficient replicates can mask true differences in LoD detection rates (e.g. 90% vs 80%).

---

## 1. Problem statement

In LoD verification, two reagents (or lots / methods) may have different true positive rates at a fixed concentration near the claimed LoD:

\[
p_A = 0.90,\qquad p_B = 0.80,\qquad \Delta = p_A - p_B = 0.10.
\]

Each reagent is tested independently \(n\) times. Observed rates:

\[
X_i \sim \mathrm{Binomial}(n, p_i),\qquad \hat{p}_i = \frac{X_i}{n},\quad i\in\{A,B\}.
\]

**Question.** How large must \(n\) be so that a statistical test rejects \(H_0:\,p_A=p_B\) with adequate power (e.g. 80%) when \(\Delta=0.10\) is true?

If \(n\) is too small, sampling noise dominates \(\Delta\), and validation campaigns will frequently conclude “no difference” even though performance truly differs.

---

## 2. Key formulae

### 2.1 Two-proportion pooled \(z\)-test

\[
z = \frac{\hat{p}_A - \hat{p}_B}{\sqrt{\hat{p}(1-\hat{p})\bigl(\tfrac{1}{n_A}+\tfrac{1}{n_B}\bigr)}},
\quad
\hat{p}=\frac{X_A+X_B}{n_A+n_B}.
\]

Reject \(H_0\) at level \(\alpha\) if \(|z| > z_{1-\alpha/2}\).

### 2.2 Equal-arm sample size (Fleiss / Chow)

\[
n
=
\frac{
\Bigl[
z_{1-\alpha/2}\sqrt{2\bar{p}(1-\bar{p})}
+
z_{1-\beta}\sqrt{p_A(1-p_A)+p_B(1-p_B)}
\Bigr]^2
}{(p_A-p_B)^2},
\quad
\bar{p}=\tfrac{p_A+p_B}{2}.
\]

### 2.3 Overlap coefficient (OVL)

Sampling distributions of \(\hat{p}\) for the two reagents overlap:

\[
\mathrm{OVL}
=
\sum_{k=0}^{n}
\min\bigl(P(X_A=k),\,P(X_B=k)\bigr).
\]

High OVL \(\Rightarrow\) hard to discriminate.

### 2.4 The saturation trap (critical methodological point)

The complementary metric

\[
P(\geq 1\ \text{positive}) = 1-(1-p)^n
\]

**saturates near 1** for both \(p_A=0.90\) and \(p_B=0.80\) once \(n\) is moderate. The gap between reagents **collapses**, so this metric **cannot** resolve LoD performance differences. Discrimination must use the **observed positive rate** \(\hat{p}\), not “ever detected.”

---

## 3. Numerical benchmark (\(p_A=0.90\), \(p_B=0.80\), \(\alpha=0.05\))

| \(n\) per arm | Approx. power | Monte Carlo power | OVL | Note on \(1-(1-p)^n\) |
|---------------|---------------|-------------------|-----|------------------------|
| 20 | **0.14** | **0.14** | 0.53 | Gap already collapsed (\(\approx 1\) for both) |
| 50 | 0.29 | 0.31 | 0.31 | Still underpowered |
| 100 | 0.51 | 0.52 | 0.15 | ~50% chance to detect \(\Delta=0.10\) |
| **199** | **0.80** | **0.81** | 0.05 | Target 80% power |

**Takeaway:** the common laboratory choice \(n=20\) has only ~14% power to detect a true 90% vs 80% gap — roughly **six in seven** validation campaigns will miss the difference.

---

## 4. Journal figures (English)

All panels are saved as PDF + PNG (300 dpi) under `figures/journal/`:

| File | Content |
|------|---------|
| `Fig1_sampling_distributions` | Overlapping \(\hat{p}\) PMFs at \(n=20,50,100,200\) |
| `Fig2_power_curves` | Power vs \(n\) for multiple \((p_A,p_B)\) pairs |
| `Fig3_saturation_vs_rate` | Why \(1-(1-p)^n\) fails; why \(\hat{p}\) works |
| `Fig4_sample_size_heatmap` | Required \(n\) over \((p_A,\Delta)\) |
| `Fig5_operating_characteristics` | Power, OVL, CI width, snapshot bars |
| `Fig6_missed_difference_MC` | Monte Carlo: underpowered vs powered campaigns |
| `Fig7_key_formulae` | Formula panel for Methods / SI |

Style: Helvetica/Arial, Okabe–Ito colourblind-safe palette, spines trimmed, vector PDF + Type-42 fonts.

---

## 5. Design implications for LoD studies

1. **Choose the estimand.** To compare reagents, estimate \(\hat{p}\) at a fixed concentration; do not rely on “at least one positive.”
2. **Power the comparison.** For \(\Delta=0.10\) near 80–90% detection, expect **hundreds** of replicates per arm for 80% power — \(n=20\) is typically underpowered.
3. **Report uncertainty.** Always show 95% CIs (Wilson or Clopper–Pearson) for \(\hat{p}\).
4. **Plan for smaller deltas.** Distinguishing 90% vs 85% (\(\Delta=0.05\)) requires substantially larger \(n\).
5. **Align with guidelines.** Pair this power calculation with CLSI EP17-style LoD verification designs rather than replacing them.

---

## 6. API (Python)

```python
from lod_discrimination_power import (
    sample_size_two_proportions,
    power_two_proportions,
    overlapping_coefficient,
    discrimination_summary,
)

n = sample_size_two_proportions(0.90, 0.80, alpha=0.05, power=0.80)
pwr = power_two_proportions(0.90, 0.80, n=20)
ovl = overlapping_coefficient(0.90, 0.80, n=20)
```

---

## 7. Relation to the earlier \(1-(1-p)^n\) module

| Module | Question answered |
|--------|-------------------|
| `lod_detection_analysis.py` | How large is \(P(\geq 1\ \text{hit})\) for one reagent? |
| `lod_discrimination_power.py` | Can we tell two reagents apart given \(n\)? |

Both are needed: the first for reliability of a single method; the second for **comparative LoD claims** — the scientifically harder problem when performance gaps are modest.
