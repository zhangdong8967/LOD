# Theory Monograph — LoD Verification as Formal Statistical Decision Theory

**Package:** `lod_guide` v0.5+  
**Architecture:** Three-layer proof system (A / B / C)  
**LaTeX draft:** [THEORY_MONOGRAPH.tex](THEORY_MONOGRAPH.tex)  
**Main figures:** Fig 1–5 (embedded in LaTeX §Main figures); plan in [`FIGURE_PLAN.md`](../paper_artifacts/captions/FIGURE_PLAN.md)  
**Companion clinical draft:** [METHODS_BRIEF.md](METHODS_BRIEF.md) (empirical illustrations only)

---

## 0. Positioning

This monograph treats clinical LoD folklore (fixed \(n=20\), all-positive pass, saturation
plates, parametric LoB without diagnostics) as **formal statistical objects** whose
failure modes are provable or boundable — not merely illustrated on datasets.

| Layer | Role | Examples |
|-------|------|----------|
| **A** | Analytic theorems (closed-form proofs) | P1, P2, P5, **P6**, P7, P15, P16 |
| **B** | Finite-sample bounds / exact enumeration | **P8 (Berry–Esseen)**, P17 split remedy, P18 |
| **C** | Numerical certificates (MC / grid) | P3, P4, P9–P14, P17 selective, c-equivalence |

Run all certificates:

```bash
pip install -e ".[dev]"
python examples/run_theory_verification.py
python -m pytest tests/test_theory_propositions.py tests/test_theory_depth.py tests/test_theory_layers.py -q
```

Compile LaTeX:

```bash
cd manuscript && pdflatex THEORY_MONOGRAPH.tex
```

---

## 1. Model and estimands

Let \(Y_j \in \{0,1\}\) be independent hits at concentration \(c\), \(P(Y_j=1)=p(c)\).

| ID | Estimand | Object |
|----|----------|--------|
| G1 | Hit-rate verification | \(\theta_1 = p(c^\star)\) or \(\mathrm{LoD}_\alpha\) |
| G2 | Reagent comparison | \(\theta_2 = p_A(c^\star) - p_B(c^\star)\) |
| G3 | Precision / LoQ | \(\mathrm{CV}(c) \le \tau\) |
| G4 | Reliability | \(P(S_n \ge k)\) |

---

## 2. Layer A — Analytic theorems

### P6 OVL monotonicity (NEW — analytic)

\[
\mathrm{OVL}(n;p_A,p_B)=\sum_k \min\{P_A(k),P_B(k)\} = 1 - \mathrm{TV}(f_n,g_n).
\]

**Theorem:** For \(p_A \neq p_B\), \(\mathrm{OVL}(n)\) is non-increasing in \(n\).

`theorem_p6_ovl_monotone()` — `theory/theorems/ovl.py`

### P1, P2, P5, P7, P15, P16

See prior sections; proofs in `theory/theorems/analytic.py` and `identification.py`.

---

## 3. Layer B — Finite-sample bounds

### P8 Berry–Esseen uniform bound (NEW)

For \(W_i = Y_{A,i}-Y_{B,i}\), \(\Delta=p_A-p_B\), \(v=\mathrm{Var}(W)\), \(\rho=E|W-\Delta|^3\):

\[
\sup_x |P(Z_n \le x) - \Phi(x)| \le \varepsilon_n = \frac{C\,\rho}{v^{3/2}\sqrt{n}},
\quad C = 0.4748 \text{ (Shevtsova 2011)}.
\]

Power gap scale: \(\mathrm{Power}_{\mathrm{asym}} - \mathrm{Power}_{\mathrm{Fisher}} \gtrsim 2\varepsilon_n \phi(z_{\alpha/2}-\kappa)\).

`berry_esseen.py`, `bounds/finite_sample.py`

### P17 Sample-splitting remedy (NEW)

Split \(B=(B_g, B_\ell)\): gate on \(B_g\), LoB on \(B_\ell\) with Bonferroni \(\alpha/2\).
Restores marginal Type I \(\approx\alpha\) under skew.

`selective/sample_split.py` — `theorem_p17_sample_split_remedy()`

### P18 Pareto inadmissibility

Unchanged — `theorems/admissibility.py`

---

## 4. Layer C — Numerical certificates

P3, P4, P9–P14, P17 gated inflation (unsplit), c-equivalence, minimax.

---

## 5. Main figures (Fig 1–5)

| Fig | Role | LaTeX label |
|-----|------|-------------|
| **1** | S0–S7 decision map + P17 branch | `fig:decision-map` |
| **2** | Folklore triple failure (G1 / G2 / P16) | `fig:folklore-failure` |
| **3** | Finite-sample theory (P8, P18) | `fig:finite-sample` |
| **4** | Remedies (n*, split, design) | `fig:remedy` |
| **5** | Tier-A radioimmuno LoQ anchor | `fig:tierA` |

Rebuild: `make paper-artifacts` → `paper_artifacts/figures/Fig*_*.pdf`.  
Module detail: Fig S1–S9 in [SUPPLEMENT.md](SUPPLEMENT.md).

---

## 6. Folklore SOP mapping

| Folklore | Result |
|----------|--------|
| 20/20 = LoD OK | **P7** |
| \(n=20\) compare | **P8**, **P18** |
| Saturation plate | **P16** |
| Always-normal LoB | **P5**, **P17** (split remedy) |
| \(1-(1-p)^n\) compare | **P1** |
| OVL separation with \(n\) | **P6** |

---

## 7. File index

| Path | Layer | Content |
|------|-------|---------|
| `theory/theorems/ovl.py` | A | P6 OVL monotonicity |
| `theory/bounds/berry_esseen.py` | B | Berry–Esseen \(\varepsilon_n\) |
| `theory/bounds/finite_sample.py` | B | P8 integrated bound |
| `theory/selective/sample_split.py` | B | P17 split remedy |
| `theory/selective/gated_error.py` | C | P17 selective decomposition |
| `manuscript/THEORY_MONOGRAPH.tex` | — | LaTeX submission draft |

---

## 8. Completed theory agenda (v0.5)

- [x] Berry–Esseen uniform bound for P8
- [x] Analytic OVL monotonicity (P6)
- [x] Sample-splitting gate with marginal Type I control (P17)
- [x] LaTeX manuscript draft

**Still open:** global c-optimality under misspecified link; Bayesian P7 reference priors.
