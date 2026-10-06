# Publication readiness — expert note

**Verdict (2026-08-01):** The package is aligned for a *Clinical Chemistry* **Article** (methods) with online supplement. Main text, figures, and compliance checklist are in place; author-facing placeholders (affiliations, full references, COI) remain before ScholarOne upload.

## Manuscript package

| Path | Role |
|------|------|
| [`manuscript/CLINICAL_CHEMISTRY_SUBMISSION.md`](../../manuscript/CLINICAL_CHEMISTRY_SUBMISSION.md) | Journal limits, main vs supplement split |
| [`manuscript/METHODS_BRIEF.md`](../../manuscript/METHODS_BRIEF.md) | Main Article — title page, Brief Summary, IMRAD |
| [`manuscript/FIGURE_LEGENDS_CC.md`](../../manuscript/FIGURE_LEGENDS_CC.md) | Legends + alt text |
| [`manuscript/SUPPLEMENT.md`](../../manuscript/SUPPLEMENT.md) | Online supplement (Fig S1; Tables 2, 4–6, 8) |
| [`manuscript/COVER_LETTER.md`](../../manuscript/COVER_LETTER.md) | Cover letter + AI disclosure |

```bash
make paper-artifacts   # refresh figures/tables/captions first
```

## Figure plan (v7 — one integrated figure)

| Location | Content |
|----------|---------|
| **Main Fig 1** | Panels A–C: miss β @ n=20 · required n* · hit-rate↔LoD map |
| **Supplement** | Tables + `Table03_comparison_grid_n20.csv` (no figures) |

**Main items:** Fig 1 + Tables 1, 3, 7 = **4** (within CC six-item cap).  
Plan: [`paper_artifacts/captions/FIGURE_PLAN.md`](../../paper_artifacts/captions/FIGURE_PLAN.md).

## What changed in v7 (integrated design figure)

1. **Single main figure** answers: why n=20 fails, how many replicates, hit-rate↔LoD range.
2. **Methods §2.3** adds Fleiss–Chow \(n^*\) and logistic \(c/\mathrm{LoD}_{95}\) formulas.
3. **Results §3** structured as four design questions tied to Fig 1A–C.
4. Supplement figures removed; 1225-cell integer 50–99% grid remains in Table 3 CSV.

## What changed in v6 (figure refactor)

1. **Framing:** assumption-gated *decision theory* (explicit risk \(L\)), not a sample-size calculator ([ELEVATED_FRAMING.md](ELEVATED_FRAMING.md)).
2. **Story-first figures:** protocol (Fig 1) + E2 headline curve (Fig 2); supplement holds grids and secondary mechanisms.
3. **Table 3 extensions:** `Table03_reference_pairs_n20.csv`, `Table03_comparison_grid_n20.csv`.
4. **Theory:** P1–P18 with machine certificates; P7 (all-positive trap), P8 (exact vs asymptotic), P18 (Pareto folklore).
5. **CC compliance:** structured abstract, Brief Summary block, IMRAD headings, alt text, main/supplement split documented.

## Run packaging

```bash
make paper-artifacts
python -m pytest tests/test_paper_artifacts.py tests/test_comparison_grid_export.py -q
```

## What a mathematician/statistician would praise

1. Estimand-first design with an explicit loss tying Type I, miss-\(\beta\), parametric mismatch, and design effect.
2. Saturation theorem (P1) + all-positive trap (P7) + exact/asymptotic gap (P8).
3. Separation of asymptotic design surfaces from exact small-sample confirmation.
4. Honest A/B/C/S evidence firewall with tier-A-only meta table.
5. Journal-style figures (captions outside PNGs; alt text prepared).

## What they would still attack for a *full* research article

1. Author list, affiliations, ORCID, and full Vancouver references (≤40) need completion.
2. Routine clinical chemistry electrolytes/enzymes/hematology **blank–LoD** raw deposits still scarce.
3. No prospective multi-lab **LoD claim verification** study.
4. Decision-risk weights are transparent conventions, not elicited utilities.

## Advice

Use **`METHODS_BRIEF.md` + `CLINICAL_CHEMISTRY_SUBMISSION.md`** for ScholarOne upload as a methods **Article**. Thicken routine-chemistry blank–LoD evidence or add a prospective partner-laboratory case before aiming at a full **Research Article** track.
