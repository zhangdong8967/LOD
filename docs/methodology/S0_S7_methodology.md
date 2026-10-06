# LoD Laboratory Guidance Algorithm — Methodology (S0–S7)

**Positioning (locked).** `lod_guide` **complements and operationalizes** EP17-class options; it **challenges practice myths** (fixed \(n\), always-normal LoB, saturated comparative metrics) and underspecified local SOPs; it **does not** claim to supersede EP17 / YY / WS / IFU as legal or standards documents. Publication framing: *an assumption-gated, estimand-specific sample-size and path-selection framework bridging EP17 options and laboratory practice.*

See [CHALLENGE_MANIFESTO.md](CHALLENGE_MANIFESTO.md). Machine constants: `lod_guide.challenge.POSITIONING_STATEMENT`.

**Package.** `src/lod_guide` — step modules mirror this document’s IDs.

---

## S0 — Goals (frozen estimands E1–E3)

| ID | Goal | Primary use-cases |
|----|------|-------------------|
| E1 | Single-method LoD verification | `verify_manufacturer_lod_claim`, `ldt_lod_establishment` |
| E2 | Compare two reagents / lots | `kit_a_vs_kit_b_near_lod`, `lot_to_lot_lod_check` |
| LoQ | LoQ / precision claim | `functional_sensitivity_loq` |
| E3 | Qualitative \(k/n\) claim | `nat_hit_rate_kn`, `immunoassay_qualitative_cutoff` |

Mixing goals is forbidden in a single run: sample-size formulae differ.

---

## S1 — Result types

`binary` | `continuous` | `count` | `multiclass` (requires `success_definition`).

---

## S2 — Diagnostic thresholds (frozen v0.1)

| Check | Warn | Fail |
|-------|------|------|
| \|skewness\| | 0.5 | 1.0 |
| \|excess kurtosis\| | 1.0 | 2.0 |
| Normality test α | — | 0.05 |
| Censoring / floor rate | 10% | 25% |
| ICC | 0.10 | 0.25 |
| Levene α | — | 0.05 |
| Between-stratum CV | 0.15 | 0.30 |

`parametric_candidate = shape_ok ∧ censoring_ok ∧ heterogeneity_ok`.

Override only via `DiagnosticThresholds(...)` with documented justification.

---

## S3 — Correction gate

Order: none → log → Box–Cox → sqrt → robust MAD.  
**Hard stop:** if none restore candidacy → `failed_use_nonparametric` → S4b.

---

## S4 — Models

- **S4a:** normal / lognormal / gamma / Poisson / probit hit-rate  
- **S4b:** percentile LoB/LoD, bootstrap rates  

Never use \(1-(1-p)^n\) to *compare* reagents (saturation trap).

---

## S5 — Sample-size engine

| Goal | Engine |
|------|--------|
| E2 | Two-proportion Fleiss/Chow \(n\) + optional MC power; exact Fisher/Boschloo layer for small \(n\) (see [EXACT_SMALL_SAMPLE.md](EXACT_SMALL_SAMPLE.md)) |
| E1 | One-proportion vs claim \(p_0\) |
| LoQ | CV-of-mean or CI half-width for mean |
| E3 | Minimal \(n\) with \(P(X\ge k)\ge\) target |

Design effect: \(n \leftarrow n\cdot[1+(m-1)\rho]\).

---

## S6 — Report

Mandatory fields: goal, diagnostics, correction, path, \(n\), assumptions pass/fail, warnings, positioning sentence.

---

## S7 — Sensitivity

Vary \(\Delta\) and ICC; show folklore \(n=20\) power vs required \(n_{80\%}\).

---

## Quick start

```bash
pip install -e .
python examples/run_guidance_demo.py
python -m lod_guide.figures
pytest -q
```
