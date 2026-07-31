# Exact Small-Sample Methods for LoD Discrimination

## Problem

Fleiss–Chow / pooled-z sample size and power are continuous and useful for design surfaces, but at folklore \(n\approx 20\) Type I error and power can be mis-calibrated. Referees expect exact or unconditional procedures for 2×2 detection tables.

## Methods implemented

1. **Fisher exact** (conditional on margins) — classical, often conservative.
2. **Boschloo** — unconditional exact test using Fisher \(p\) as the test statistic; maximizes null rejection probability over nuisance \(p\) under \(H_0: p_A=p_B=p\).
3. **Exact power** — enumerate all \((i,j)\in\{0,\ldots,n\}^2\), weight by \(\mathrm{Bin}(i;n,p_A)\mathrm{Bin}(j;n,p_B)\), sum rejecting cells.
4. **Exact \(n^\star\)** — binary search for minimal equal-arm \(n\) with exact power ≥ target (feasible when asymptotic \(n^\star\) is moderate).

Code: `lod_guide.theory.exact_tests` and `lod_guide.s5_sample_size.power_two_proportions_exact`.

## Reporting policy

- Design surfaces / continuous fields: asymptotic OK (with disclaimer).
- Confirmatory small-\(n\) inference: report Boschloo (primary) + Fisher (reference) + pooled-z (comparability).
- Headlines such as “miss \(\beta\) at \(n=20\)” should cite **exact Fisher (or Boschloo) power**, not only the normal approximation.

## Run

```bash
python -m lod_guide.research.exact_power_study
```
