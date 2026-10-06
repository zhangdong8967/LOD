# Estimand-Gated Detection Capability Design:
# A Formal Framework for Clinical Chemistry

**Target venue.** *Clinical Chemistry* (methodology / special report style).  
**Software companion.** `lod_guide` v0.2+ (S0–S7), fully auditable.

---

## 0. Claim of novelty (precise, not rhetorical)

Prior guidance (e.g. CLSI EP17-A2) enumerates **admissible estimation procedures** for LoB/LoD/LoQ and notes that no single protocol fits all measurands. What has **not** been formalized—and what this work contributes—is an **estimand-first, assumption-gated decision algorithm** that:

1. treats **goal (estimand)** as a first-class object (verify vs compare vs LoQ vs \(k/n\));
2. **refuses** parametric LoB when pre-specified diagnostics fail;
3. replaces folklore fixed \(n\) by **operating-characteristic–calibrated** \(n\);
4. proves that the popular reliability metric \(1-(1-p)^n\) is **information-destroying** for reagent comparison (saturation);
5. publishes a **transparent audit trail** so every path decision is independently recomputable;
6. elevates the algorithm to an **explicit decision risk** \(L=w_I\mathrm{TypeI}+w_{II}\beta+w_M\mathbf{1}\{\text{mismatch}\}+w_C(\mathrm{DE}-1)\) so folklore SOPs are falsifiable under a loss, not only under verbal critique.

This is not a redefinition of LoD. It is a **design and decision calculus** that can make existing vocabulary operationally rigorous—and thereby force revision of underpowered local SOPs and, potentially, future guideline annexes on sample size and path selection.

See also: [ELEVATED_FRAMING.md](ELEVATED_FRAMING.md).

---

## 1. Notation and probability space

Let \((\Omega,\mathcal{F},P)\) support independent assay replicates. For a fixed concentration \(c\) near the claimed detection limit:

- **Binary / hit-rate setting.** \(Y_j\in\{0,1\}\), \(P(Y_j=1)=p(c)\in(0,1)\).
- **Continuous setting.** \(X_j\in\mathbb{R}\) (or \([L,\infty)\) if left-censored at instrument floor \(L\)).
- **Count setting.** \(N_j\in\mathbb{N}_0\), typically \(N_j\sim\mathrm{Poisson}(\lambda(c))\) or overdispersed.
- **Strata.** Cluster labels \(G_j\in\{1,\ldots,m\}\) (day, lot, operator) inducing dependence.

Observed rates: \(\hat p_n = n^{-1}\sum_{j=1}^n Y_j\).

---

## 2. Estimands (ICH E9(R1)–aligned)

An LoD study without a declared estimand is not a statistical problem; it is a narrative. We lock one primary estimand per study.

| ID | Estimand (mathematical object) | Decision functional |
|----|--------------------------------|---------------------|
| E1 | \(\theta_1=p(c^\star)\) or \(\theta_1^{\mathrm{conc}}=\mathrm{LoD}_\alpha\) | Verify claim / CI coverage |
| E2 | \(\theta_2=p_A(c^\star)-p_B(c^\star)\) | Test \(H_0:\theta_2=0\) at level \(\alpha\) with power \(1-\beta\) at \(\theta_2=\Delta^\star\) |
| LoQ | \(\theta_3=\mathrm{CV}(c)\) or quantile precision | \(\theta_3\le \tau\) |
| E3 | \(\theta_4=P(S_n\ge k)\), \(S_n\sim\mathrm{Bin}(n,p)\) | \(\theta_4\ge \gamma\) |

**Identification assumptions** are stated per path (S4a/S4b) and are **audited**, not assumed silently.

---

## 3. Core propositions (with proofs)

### Proposition 1 (Saturation / information destruction)

Let \(0<p_B<p_A<1\) and \(\phi_n(p)=1-(1-p)^n\). Then

\[
\lim_{n\to\infty}\bigl(\phi_n(p_A)-\phi_n(p_B)\bigr)=0,
\]

and for any \(\varepsilon>0\) there exists \(N\) such that for all \(n\ge N\),

\[
0 < \phi_n(p_A)-\phi_n(p_B) < \varepsilon.
\]

**Proof.** \(0<(1-p_A)<(1-p_B)<1\), so \((1-p_A)^n\to 0\) and \((1-p_B)^n\to 0\) geometrically. Hence \(\phi_n(p_A)\to 1\), \(\phi_n(p_B)\to 1\), and the difference vanishes. \(\square\)

**Corollary (guideline implication).** Any comparative LoD claim that uses \(\phi_n\) as the performance metric becomes arbitrarily insensitive to true \(\Delta=p_A-p_B\) as \(n\) grows. Comparative designs **must** target \(\hat p\) (or LoD concentration contrasts), not “ever detected.”

### Proposition 2 (Exact binomial reliability)

If \(Y_j\stackrel{\mathrm{iid}}{\sim}\mathrm{Bernoulli}(p)\), then

\[
P\Bigl(\sum_{j=1}^n Y_j \ge 1\Bigr)=1-(1-p)^n,
\]

and more generally

\[
P(S_n\ge k)=\sum_{i=k}^n \binom{n}{i}p^i(1-p)^{n-i}.
\]

**Proof.** Immediate from the binomial pmf / complement of \(P(S_n=0)\). \(\square\)

### Proposition 3 (Asymptotic two-proportion power)

Let \(X_A\sim\mathrm{Bin}(n,p_A)\), \(X_B\sim\mathrm{Bin}(n,p_B)\), \(\hat p_i=X_i/n\), and let \(Z_n\) be the pooled two-sided \(z\)-statistic. Under standard Lindeberg conditions,

\[
\sqrt{n}\,(\hat p_A-\hat p_B-\Delta)\Rightarrow \mathcal{N}\bigl(0,\,p_A(1-p_A)+p_B(1-p_B)\bigr),
\]

and the usual Fleiss–Chow sample-size formula is the inversion of the asymptotic power of the level-\(\alpha\) test for \(H_0:\Delta=0\) at alternative \(\Delta=p_A-p_B\).

**Design equation (equal arms).**

\[
n=
\frac{
\bigl[
z_{1-\alpha/2}\sqrt{2\bar p(1-\bar p)}
+
z_{1-\beta}\sqrt{p_A(1-p_A)+p_B(1-p_B)}
\bigr]^2
}{(p_A-p_B)^2},
\quad
\bar p=\tfrac{p_A+p_B}{2}.
\]

**Numerical certificate.** For \((p_A,p_B)=(0.90,0.80)\), \(\alpha=0.05\), \(1-\beta=0.80\): \(n\approx 199\). Monte Carlo power at \(n=199\) matches the asymptotic target within simulation error (see `lod_guide.theory` tests).

### Proposition 4 (Design effect under exchangeable clusters)

If \(\mathrm{Corr}(Y_{js},Y_{jt})=\rho\) within cluster size \(m\) (compound symmetry), then

\[
\mathrm{Var}(\bar Y)=\frac{p(1-p)}{n_{\mathrm{eff}}},
\quad
n_{\mathrm{eff}}=\frac{n}{1+(m-1)\rho},
\quad
\mathrm{DE}=1+(m-1)\rho.
\]

**Proof.** Standard ANOVA / Kish design-effect algebra for equal cluster sizes. \(\square\)

**Implication.** Ignoring \(\rho>0\) understates required \(n\) by factor DE.

### Proposition 5 (Parametric LoB inconsistency under skew)

Suppose blank measurements \(X\) have cdf \(F\) with \(F\neq\Phi_{\mu,\sigma}\). The functional

\[
\mathrm{LoB}_{\mathrm{par}}(F)=\mu_F+z_{1-\alpha}\sigma_F
\]

satisfies \(\mathrm{LoB}_{\mathrm{par}}(F)\neq F^{-1}(1-\alpha)\) unless \(F\) is Gaussian (up to affine transform). Hence the Type I blank exceedance rate is not \(\alpha\).

**Proof.** Equality of mean–SD threshold and upper quantile characterizes the Gaussian location-scale family among continuous laws with finite variance (classical; or verify by counterexample: unit exponential, \(\alpha=0.05\)). \(\square\)

**Operational rule.** Pre-test normality/skew/censoring; if rejected, use \(\widehat{F}^{-1}(1-\alpha)\) (nonparametric LoB).

### Proposition 6 (Overlap coefficient and discriminability)

For \(X_i\sim\mathrm{Bin}(n,p_i)\),

\[
\mathrm{OVL}(n;p_A,p_B)=\sum_{k=0}^n \min\bigl\{P(X_A=k),P(X_B=k)\bigr\}
\]

is nonincreasing in \(n\) for fixed \(p_A\neq p_B\) in the large-sample regime (distributions concentrate at distinct means). High OVL \(\Leftrightarrow\) low separation of \(\hat p\).

---

### Proposition 7 (All-positive trap)

If \(X\sim\mathrm{Binomial}(n,p)\) and one observes \(X=n\), then:

1. \(P(X=n\mid p)=p^n\) (can be large for modest \(p\) when \(n\) is small);
2. the exact one-sided lower \((1-\alpha)\) bound is \(p_L=\alpha^{1/n}\); the two-sided Clopper–Pearson lower uses \((\alpha/2)^{1/n}\);
3. under a \(\mathrm{Uniform}(0,1)\) prior, \(P(p<p_0\mid X=n)=p_0^{n+1}\).

**Implication.** A laboratory “100% detection” result with \(n=5\) or \(10\) does **not** validate a 95% LoD hit-rate claim. See `docs/methodology/ALL_POSITIVE_TRAP.md` and `lod_guide.research.all_positive_trap`.

---

## 4. The S0–S7 algorithm as a measurable decision map

Define the laboratory input

\[
\mathcal{I}=(\mathrm{Goal},\,\mathrm{Type},\,\mathbf{x},\,\mathbf{g},\,\pi_{\mathrm{pilot}},\,\alpha,\beta,\Delta^\star,\ldots)
\]

and the algorithm output

\[
\mathcal{A}(\mathcal{I})=(\mathrm{Path},\,n^\star,\,\mathrm{Report},\,\mathrm{AuditHash}).
\]

**Determinism.** Given fixed seeds for Monte Carlo branches, \(\mathcal{A}\) is a pure function: identical inputs reproduce identical path, \(n^\star\), and audit hash (SHA-256 of canonical JSON).

**Gate.** Let \(D(\mathbf{x},\mathbf{g})\in\{0,1\}^q\) be diagnostic indicators (skew, kurtosis, Shapiro \(p\), censoring rate, ICC, Levene \(p\), between-stratum CV). Parametric candidacy:

\[
\mathrm{PC}= \mathbf{1}\{\text{all fail-thresholds unmet}\}.
\]

If \(\mathrm{PC}=0\) after the ordered correction class \(\mathcal{T}\), path \(=\) nonparametric.

Thresholds are **versioned** (`DiagnosticThresholds` v0.1.0) and must be cited in the paper’s Supplemental Methods.

---

## 5. Transparency requirements (for mathematicians & statisticians)

Every published analysis must deposit:

1. **Protocol** — estimand, α/β/Δ★, thresholds, seed, software version.  
2. **Raw or simulated data** — with license/citation for real sources.  
3. **Audit JSON** — step-wise inputs/outputs + SHA-256.  
4. **Operating characteristic tables** — analytic vs Monte Carlo power.  
5. **Sensitivity** — \(n^\star(\Delta,\rho,\text{skew})\).

Absence of any item fails our internal “Clinical Chemistry bar.”

---

## 5b. Propositions P7–P18 and decision risk (elevation)

**Proposition 7 (all-positive trap).** After observing \(n/n\) detections, the one-sided Clopper–Pearson lower bound equals \(\alpha^{1/n}\). For small \(n\) this bound can lie far below a 95% LoD claim even while \(P(X=n\mid p)=p^n\) remains large for modest \(p\). Machine certificate: `P7_all_positive_trap` (**Layer A**).

**Proposition 8 (exact vs asymptotic gap).** For close alternatives at folklore \(n\) (e.g. \(p_A=0.90\), \(p_B=0.80\), \(n=20\)), asymptotic pooled-\(z\) power exceeds exact Fisher power by a material margin; design surfaces must not be confused with confirmatory power. Machine certificate: `P8_exact_vs_asymptotic_gap` (**Layer B**).

**Propositions P15–P18 (theory depth).** P15–P16: LoD identifiability vs saturation trap (**Layer A**). P18: folklore \(n=20\) Pareto-inadmissible under exact Fisher OC (**Layer B**). P12–P14, P17: c-optimal design, minimax slope robustness, gated LoB selective inflation (**Layer C**).

Full three-layer map: [archive/manuscript_retired/THEORY_MONOGRAPH.md](../../archive/manuscript_retired/THEORY_MONOGRAPH.md).

**Decision risk.** Path selection under S2–S5 minimizes a transparent weighted loss (see `lod_guide.research.decision_risk`). Equal-weight exhibits show folklore \(n=20\) for 90 vs 80 incurs substantially higher \(L\) than powered \(n^\star\), and parametric LoB on exponential blanks incurs higher \(L\) than the nonparametric path.

---

## 6. What would change in future guidelines

If accepted as operational doctrine, guideline annexes should require:

- estimand declaration before LoD experiments;
- powered \(n\) for comparative kit claims (not fixed 20);
- mandatory diagnostics before parametric LoB;
- prohibition of \(\phi_n=1-(1-p)^n\) as a comparative endpoint;
- design-effect adjustment when replicates are clustered.

That is the disruptive pathway: **not renaming LoD**, but **making underpowered and assumption-blind LoD evaluation scientifically indefensible**.

---

## 7. Limitations (stated up front)

- Asymptotic \(z\)-power is approximate for small \(n\); we provide Monte Carlo cross-checks.  
- Diagnostic thresholds are conventions, not unique optima; sensitivity analyses are mandatory.  
- Real-data catalogue currently emphasizes public qPCR LoD sets; continuous clinical chemistry panels should be expanded as data use agreements allow.  
- Regulatory adoption requires consensus bodies; this paper supplies the formal and computational substrate.

---

## 8. Reproducibility commands

```bash
pip install -e ".[dev]"
python examples/run_transparent_analysis.py
python -m pytest -q tests/test_theory_propositions.py
```

Audit artifacts: `data/audit/`.
