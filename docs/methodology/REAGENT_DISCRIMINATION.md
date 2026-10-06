# Evaluating Reagent LoD Differences (90% vs 80%, 90% vs 50%)

## 1. Must this be evaluated in our research?

**Yes — mandatorily.** Comparative LoD claims without a powered design produce a specific false conclusion:

> “No significant difference between reagents”

when a true difference exists. That error rate is the **Type II error**

\[
\beta(n; p_A,p_B,\alpha)=1-\mathrm{Power}(n; p_A,p_B,\alpha).
\]

Our Goal **E2** evaluation algorithm (`E2-DISCRIM-EVAL-v1`) exists precisely to compute \(n^\star\) and \(\beta(n)\) before laboratories declare equivalence.

---

## 2. Mathematical relations

Equal-arm Fleiss–Chow sample size for \(H_0:p_A=p_B\) vs \(H_1:p_A\neq p_B\):

\[
n^\star=
\frac{
\bigl[
z_{1-\alpha/2}\sqrt{2\bar p(1-\bar p)}
+
z_{1-\beta}\sqrt{p_A(1-p_A)+p_B(1-p_B)}
\bigr]^2
}{(p_A-p_B)^2}.
\]

Miss probability at a chosen \(n\): \(\beta=1-\mathrm{power}\) (analytic + Monte Carlo).

---

## 3. Continuous percent grid (99% → 50%) — primary design surface

Sparse vignettes (90 vs 80, 90 vs 50) are **illustrative slices only**. The deposited continuum is:

- Competitor hit rates \(p \in \{99\%,98\%,\ldots,50\%\}\) (integer percent).
- Reference curves at \(p_{\mathrm{ref}} \in \{99\%,95\%,90\%\}\).
- For each pair with \(p < p_{\mathrm{ref}}\): \(n^\star(80\%)\), miss \(\beta\) at folklore \(n=20\), and \(c/\mathrm{LoD}_{95}\).

Artifact: `data/research/reagent_discrimination_continuous.json`.  
Figure: `figures/methodology/FigD2_nstar_and_relative_lod.png` (panels A–C).

Headline checks from the continuum (re-run to refresh):

| Contrast on grid | Role |
|------------------|------|
| 99% vs 98% | Near-boundary discrimination — \(n^\star\) huge |
| 99% vs 50% | Easy separation — small \(n^\star\) |
| 90% vs 80% | Classic folklore-failure vignette (still on the continuous curve) |

---

## 4. Selected vignette numbers (\(\alpha=0.05\), target power 80%)

| Contrast | \(\Delta\) | \(n^\star\) (80% power) | Miss prob at \(n=5\) | \(n=10\) | \(n=20\) |
|----------|------------|-------------------------|----------------------|----------|----------|
| **90% vs 80%** | 0.10 | **≈ 199 / arm** | ≈ **0.93** | ≈ **0.89** | ≈ **0.86** |
| **90% vs 50%** | 0.40 | **≈ 22 / arm** | ≈ **0.48** | ≈ **0.20** | ≈ **0.04** |

Interpretation:

- **90 vs 80:** folklore \(n=20\) fails to find the difference about **86%** of the time — usually the wrong “no difference” conclusion.
- **90 vs 50:** much easier; \(n\approx 22\) suffices for 80% power; even \(n=10\) already has only ~20% miss risk.

(Exact values: run the module; MC cross-checks are stored in JSON.)

---

## 4. Concentration relative to LoD

Map hit rate \(p\) to concentration via a logistic curve with LoD defined by \(p(\mathrm{LoD}_{95})=0.95\):

\[
\frac{c}{\mathrm{LoD}_{95}}
=
10^{(\mathrm{logit}(p)-\mathrm{logit}(0.95))/\mathrm{slope}}.
\]

With slope \(=2\) per \(\log_{10}\) decade (illustrative):

| \(p\) | Approx. \(c/\mathrm{LoD}_{95}\) |
|-------|--------------------------------|
| 0.95 | 1.00 |
| 0.90 | < 1 (slightly below claimed LoD) |
| 0.80 | further below |
| 0.50 | near \(c_{50}\), substantially below \(\mathrm{LoD}_{95}\) |

**Design note:** comparing two kits at a **shared** concentration \(c^\star\) uses the kits’ \((p_A,p_B)\) at that \(c^\star\). The relative-LoD map tells you whether that operating point is at / below / above a 95% LoD claim.

---

## 5. Evaluation algorithm (must-run checklist)

1. Lock estimand \(\theta=p_A(c^\star)-p_B(c^\star)\).  
2. State \(\alpha\), target \(1-\beta\), pilot \((p_A,p_B)\).  
3. Compute \(n^\star\).  
4. Tabulate \(\beta(n)\) for \(n\in\{5,10,20,\ldots,n^\star\}\).  
5. Monte Carlo verify miss rates.  
6. Report relative \(c/\mathrm{LoD}\) context.  
7. **Forbid** “no difference” language unless the study was powered for the Δ of interest.

Code: `lod_guide.research.reagent_discrimination`.

```bash
python -m lod_guide.research.reagent_discrimination
python -m lod_guide.research.discrimination_figures
```

Outputs: `data/research/reagent_discrimination_eval.json`, `FigD1–D3`.
