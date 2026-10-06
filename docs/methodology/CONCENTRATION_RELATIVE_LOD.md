# Concentration Relative to LoD: Below / At / Above

## 1. Why this must be evaluated

LoD studies are not only about \(n\). The **concentration of the challenge material** relative to the (claimed or true) LoD changes:

1. the true hit rate \(p(c)\);
2. the chance a single kit “passes” a ≥95% claim;
3. the gap \(\Delta p\) between kits and thus the probability of **missing** a real difference.

Algorithm ID: `CONC-REL-LOD-EVAL-v1` (`lod_guide.research.concentration_relative`).

Define \(r = c / \mathrm{LoD}_{95}^{\mathrm{ref}}\) with \(p(\mathrm{LoD}_{95})=\gamma=0.95\) on a reference logistic curve.

---

## 2. Qualitative effects

| Zone | \(r\) | What happens to **single-kit** verification | What happens to **kit comparison** |
|------|-------|-----------------------------------------------|--------------------------------------|
| **Below LoD** | \(r<1\) | True \(p<\gamma\). Correct methods often **fail** rate≥claim; folklore “all positive” also rarer. Risk: reject a good LoD because \(c\) was too low. | \(\Delta p\) depends on curve separation; can be large, but interpretation mixes “concentration error” with “kit difference.” |
| **At LoD** | \(r=1\) | Intended point: reference kit \(p\approx\gamma\). Fair test of the claim. | \(\Delta p\) reflects true near-claim performance differences (e.g. 95% vs ~80% if kit B’s LoD is worse). |
| **Above LoD** | \(r>1\) | True \(p\to 1\): **easy pass** (high \(P(\text{all +})\)). Weak evidence for the claim. | \(\Delta p\to 0\) (**saturation**): miss probability \(\beta\) rises → false “no difference” even when LoDs differ. |

---

## 3. Model

Kit hit rate at relative level \(r\):

\[
p(r)=\mathrm{expit}\bigl(\mathrm{slope}\cdot(\log_{10} r - \delta)+\mathrm{logit}(\gamma)\bigr),
\]

where \(\delta=\log_{10}(\mathrm{LoD}_{\mathrm{kit}}/\mathrm{LoD}_{\mathrm{ref}})\) (worse kit ⇒ \(\delta>0\)).

Default demonstration: kit B shifted so that at \(r=1\), \(p_B\approx 0.80\).

---

## 4. Typical numeric pattern (\(n=20\), claim 95%)

Run:

```bash
python -m lod_guide.research.concentration_relative
python -m lod_guide.research.concentration_figures
```

Expect qualitatively:

- **\(r=0.5\) (below):** Kit A pass rate for \(\hat p\ge 0.95\) is low; comparison may still have power if \(\Delta p\) is large.
- **\(r=1.0\) (at):** Kit A near claim; Kit B lower; discrimination at folklore \(n=20\) often still underpowered for modest gaps.
- **\(r=2.0\) (above):** both kits high \(p\); verification easy; **miss β for A vs B high** (false equivalence).

Exact numbers are deposited in `data/research/concentration_relative_lod.json`.

---

## 5. Algorithm checklist (labs)

1. Declare target estimand (E1 verify vs E2 compare).  
2. Declare intended \(r=c/\mathrm{LoD}\) (or absolute \(c\) + claimed LoD).  
3. Run `CONC-REL-LOD-EVAL-v1` (or pilot \(p\) at that \(c\)).  
4. Choose \(n\) from S5 **at that operating point**, not from folklore.  
5. Report zone (below/at/above) in S6 — never omit concentration context.

**Mandatory in this research:** yes — concentration mis-location is as important as underpowered \(n\).
