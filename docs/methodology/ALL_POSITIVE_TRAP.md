# The All-Positive Trap (n/n hits ≠ reliable LoD)

## 1. The laboratory illusion

A common informal argument:

> We tested \(n=5\) (or \(10\)) replicates at the claimed LoD concentration;  
> all were positive (100% detection); therefore the LoD claim is solid.

**This is false.** Observing \(n/n\) positives is **compatible with many true** single-trial probabilities \(p\), including values far below 95% or 99%.

---

## 2. Exact sampling relation

Let \(X\sim\mathrm{Binomial}(n,p)\) be the number of positives. Then

\[
\boxed{P(X=n\mid p)=p^n.}
\]

| True \(p\) | \(n=5\): \(P(\text{5/5})\) | \(n=10\): \(P(\text{10/10})\) | \(n=20\): \(P(\text{20/20})\) |
|------------|----------------------------|-------------------------------|-------------------------------|
| 0.70 | \(0.70^5\approx\mathbf{0.17}\) | \(0.70^{10}\approx\mathbf{0.028}\) | \(\approx 0.0008\) |
| 0.80 | \(0.80^5\approx\mathbf{0.33}\) | \(0.80^{10}\approx\mathbf{0.11}\) | \(\approx 0.012\) |
| 0.90 | \(0.90^5\approx\mathbf{0.59}\) | \(0.90^{10}\approx\mathbf{0.35}\) | \(\approx 0.12\) |
| 0.95 | \(0.95^5\approx\mathbf{0.77}\) | \(0.95^{10}\approx\mathbf{0.60}\) | \(\approx 0.36\) |

So with **only 5 replicates**, if the true detection probability is merely **80%**, there is still about a **1 in 3 chance** of seeing a perfect 5/5 study. That “100% result” is then **sampling luck**, not proof of a tight LoD.

---

## 3. What \(n/n\) actually implies (frequentist)

After observing \(X=n\):

| Bound type | Formula | \(n=5\) | \(n=10\) | \(n=20\) |
|------------|---------|---------|----------|----------|
| One-sided 95% lower | \(\alpha^{1/n}=0.05^{1/n}\) | \(\approx\mathbf{0.55}\) | \(\approx\mathbf{0.74}\) | \(\approx\mathbf{0.86}\) |
| Two-sided 95% CP lower | \((\alpha/2)^{1/n}=0.025^{1/n}\) | \(\approx\mathbf{0.48}\) | \(\approx\mathbf{0.69}\) | \(\approx\mathbf{0.83}\) |

**Meaning (one-sided):** a perfect 5/5 study only supports \(p\gtrsim 55\%\) at 95% lower confidence — **not** a 95% LoD hit-rate claim.

---

## 4. Bayesian residual risk (Uniform prior exhibit)

With prior \(p\sim\mathrm{Uniform}(0,1)\) and likelihood \(p^n\), the posterior is \(\mathrm{Beta}(n+1,1)\), and

\[
\boxed{P(p < p_0\mid X=n)=p_0^{n+1}.}
\]

For claim \(p_0=0.95\):

| \(n\) | \(P(p<0.95\mid n/n)\) |
|-------|----------------------|
| 5 | \(0.95^{6}\approx\mathbf{0.74}\) |
| 10 | \(0.95^{11}\approx\mathbf{0.57}\) |
| 20 | \(0.95^{21}\approx\mathbf{0.34}\) |

Even after 5/5 positives, under this neutral prior there remains ~**74%** posterior probability that true \(p\) is **still below 0.95**.

(Other priors change the number; the qualitative warning remains: small-\(n\) perfection is weak evidence.)

---

## 5. Link to the guidance algorithm

| Folklore reading | Algorithm reading (S0/S5/S6) |
|------------------|------------------------------|
| “100% ⇒ LoD OK” | Estimand is \(p\) or LoD at target \(p_0\), not the event \(\{X=n\}\) |
| \(n=5\) enough if all + | Need \(n\) so that \(p_L\ge p_0\) or powered test vs \(p_0\) |
| Perfect hit rate ends debate | Report \(p^n\), \(p_L=\alpha^{1/n}\), and residual risk |

This is claim **C1** sharpened: fixed small \(n\) fails not only for comparing reagents, but even for **verifying a single high hit-rate claim** when the study returns 100% positives by chance.

---

## 6. Code & figures

```bash
python -m lod_guide.research.all_positive_trap
python -m lod_guide.research.all_positive_figures
```

Outputs: `data/research/all_positive_trap.json`, `figures/methodology/FigT1–T3_*.png`.
