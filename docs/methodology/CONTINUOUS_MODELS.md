# Continuous Parameter-Space Models (examples are only slices)

## 1. Point of principle

Numbers such as **5/5**, **10/10**, **90% vs 80%**, **90% vs 50%** are **illustrative points**.  
The scientific object of this project is a **continuous data model**:

| Field | Domain | Object |
|-------|--------|--------|
| All-positive | \(p\in(0,1],\ n\in\{1,2,\ldots\}\) (practically \(n\) up to hundreds) | \(f(p,n)=p^n\), \(L(n)=\alpha^{1/n}\), \(B(n;p_0)=p_0^{n+1}\) |
| Discrimination | \((p_A,p_B)\in(0,1)^2\), \(p_A>p_B\); also \((\bar p,\Delta)\) | \(n^\star(p_A,p_B)\), \(\beta(n;p_A,p_B)\) |
| Concentration | \(r=c/\mathrm{LoD}\in(0,\infty)\) (log-grid) | \(p(r)\), pass\((r)\), miss\((r)\) |

CS04 / CS05 / CS06 are **annotations on these surfaces**, not the model itself.

---

## 2. Closed forms (infinite / continuous in parameters)

\[
P(X=n\mid p)=p^n,\qquad
p_L^{\mathrm{one}}=\alpha^{1/n},\qquad
P(p<p_0\mid X=n)=p_0^{n+1}\ \text{(Uniform prior)}.
\]

\[
n^\star(p_A,p_B)=\frac{\bigl[z_{1-\alpha/2}\sqrt{2\bar p(1-\bar p)}+z_{1-\beta}\sqrt{p_A(1-p_A)+p_B(1-p_B)}\bigr]^2}{(p_A-p_B)^2}.
\]

\[
\beta(n;p_A,p_B)=1-\mathrm{Power}(n;p_A,p_B,\alpha).
\]

For any \((p_A,p_B,n)\) or \((p,n)\) or \(r>0\), use the **query** API — do not restrict to hand-picked examples.

---

## 3. Code & artifacts

```bash
python -m lod_guide.research.continuous_models          # build dense fields
python -m lod_guide.research.continuous_figures         # surface plots
```

Writes:

- `data/research/continuous_models/all_positive_field.npz`
- `data/research/continuous_models/discrimination_field.npz`
- `data/research/continuous_models/discrimination_miss_n*.npz`
- `data/research/continuous_models/concentration_field.npz`
- `data/research/continuous_models/continuous_models_meta.json`

Point queries:

```python
from lod_guide.research.continuous_models import query_all_positive, query_discrimination
query_all_positive(0.83, 12)          # any p, n
query_discrimination(0.91, 0.77, 40) # any pair + n
```

---

## 4. Relation to clinical scenarios

| Scenario | Role vs continuous model |
|----------|---------------------------|
| CS04 | Vertical/horizontal **slices** of \(p^n\) and \(L(n)\) |
| CS05 / CS06 | Two **points** on \(n^\star(p_A,p_B)\) and \(\beta(20;\cdot)\) |
| CS15 | **Curve** along \(r\in(0,\infty)\) on the concentration field |

Labs should pick their actual \((p,n)\), \((p_A,p_B)\), or \(r\) and evaluate on the field — not copy example percentages.
