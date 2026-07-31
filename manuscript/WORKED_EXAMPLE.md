# Worked example — lot comparison at LoD (G2)

**Use in manuscript:** Introduction §1.3 (main text); optional **Box 1** in formatted submission.  
**Numbers:** from `data/research/decision_risk.json`, `data/research/reagent_discrimination_continuous.json` (α = 0.05, two-sided).

---

## Box 1. When the protocol says “equivalent at LoD”

### Protocol language (typical)

A laboratory validates a new **lot B** of a qualitative immunoassay against **reference lot A**. The validation protocol states:

> *At the manufacturer LoD concentration (e.g., 5 pg/mL), demonstrate that lot B is **equivalent** to lot A with respect to detection sensitivity.*

Replicates are run at \(c^\star\) on both lots. The SOP fixes **\(n = 20\)** per arm and applies a **two-sided test** at α = 0.05; if \(P > 0.05\), the report concludes “no difference” and lot B is released.

### Step 1 — Name the estimand

The written claim is **comparative**: it concerns \(\theta_2 = p_A(c^\star) - p_B(c^\star)\), not whether either lot alone meets a 95% benchmark. That is estimand **G2** (two-proportion discrimination at a stated concentration).

If the protocol instead required each lot to **individually** meet a 95% detection benchmark, the estimand would be **G1** (two separate one-proportion verifications). Sample size and pass rules differ; conflating the two invalidates the report even when the bench work is identical.

### Step 2 — State the effect size the study should detect

Suppose prior data or the manufacturer IFU suggest that lot A detects about **90%** of replicates at \(c^\star\) and a clinically relevant shift for lot B would be **80%** (a 10-percentage-point loss). The planning contrast is \(p_A = 0.90\), \(p_B = 0.80\), \(\Delta = 0.10\).

This is a modest gap in laboratory terms; it is not a edge-case simulation.

### Step 3 — Compare folklore \(n\) with powered \(n\)

| Design | \(n\) per arm | Exact Fisher power | Missed-difference probability (\(\beta\)) |
|--------|---------------|--------------------|-------------------------------------------|
| Folklore SOP | 20 | **0.07** | **0.93** |
| Powered (80% target) | **199** | 0.80 (asymptotic at \(n^\star\); exact enumeration at this \(n\) is reported in planning JSON) | 0.20 |

With \(n = 20\), a non-significant test **does not support equivalence**. It supports **insufficient evidence**: if the true rates are 90% and 80%, the study has roughly a **93%** chance of failing to reject equality.

Under equal default weights in the decision risk \(L\) (Type I + Type II + mismatch + design-effect terms; Methods §2.2), the folklore design carries about **3.9×** the risk of the powered plan for this scenario (`decision_risk.json`).

### Step 4 — What changes in the report

**Before data collection**, the planning output would record:

- Estimand: G2  
- Planning contrast: \(p_A = 0.90\), \(p_B = 0.80\)  
- Required \(n\) per arm: 199 (Fleiss–Chow; Methods §2.3)  
- Confirmation: exact Fisher / Boschloo layer flagged for any post hoc analysis at smaller \(n\)

**After data collection**, interpretation is tied to the locked estimand. A significant test supports a sensitivity difference; a non-significant test at \(n = 199\) is at least **interpretable** at the design \(\beta\). At \(n = 20\), neither outcome should be written as “equivalent.”

### Step 5 — Common protocol error (estimand mix)

Some SOPs add a rule such as “**≥ 19/20 positives on each lot**” and treat satisfaction on both arms as equivalence. That rule belongs to **G4** (\(k/n\) reliability) or **G1** (marginally adequate hit rate), not to **G2**. A kit can pass 19/20 on both arms while differing materially in \(p\), and two arms can both fail a 95% claim while appearing “similar.” The worked example shows why the **claim sentence in the protocol** must precede \(n\) and pass rules.

---

## Short insert for Introduction (~200 words)

Consider a protocol that requires a new reagent lot to be “equivalent” to a reference lot at the manufacturer LoD concentration \(c^\star\). That wording targets **G2**: the difference in hit rates \(p_A(c^\star) - p_B(c^\star)\). A common SOP nevertheless fixes **\(n = 20\)** replicates per arm and interprets a non-significant two-sided test as equivalence. If the true rates are 90% and 80—a plausible 10-point sensitivity gap—exact Fisher power at α = 0.05 is only **0.07**; the study will usually **not** detect the difference it was meant to adjudicate. Fleiss–Chow planning for 80% power instead requires **\(n \approx 199\)** per arm for the same contrast. The issue is not arithmetic error on the bench; it is that **replicate number was never derived from the comparative claim**. The same validation file might instead require each lot to meet a 95% detection benchmark (**G1**) or a 19/20 qualitative rule (**G4**); those are different estimands with different \(n\). `lod_guide` begins by forcing that translation before path or sample-size calculations (Fig 1).

---

## Companion example — single-lot verification (G1, one sentence each)

Protocol: *Verify manufacturer 95% LoD at \(c^\star\) with \(n = 20\); pass if all replicates are positive.*

At true \(p = 0.90\), \(P(\text{20/20 positive}) = 0.90^{20} \approx 0.12\). Observing 20/20 is compatible with \(p < 0.95\); one-sided Clopper–Pearson lower bounds at \(n = 20\) remain well below 0.95 (Fig 2A; P7). **G1** requires a one-proportion design against \(p_0 = 0.95\), not an all-positive pass rule.

---

## Reproduce

```bash
python -m lod_guide.research.decision_risk
python -m lod_guide.research.reagent_discrimination
make paper-artifacts
```

Key files: `data/research/decision_risk.json`; Table 3 / Fig 3A in `paper_artifacts/`.
