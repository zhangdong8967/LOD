# Publication readiness — expert note

**Verdict (post elevation): methods technical brief draft + Supplement now exist under `manuscript/`; still not a full Clinical Chemistry research submission without journal formatting, affiliations, and broader blank–LoD raw where possible.**

## Manuscript package

| Path | Role |
|------|------|
| [`manuscript/METHODS_BRIEF.md`](../../manuscript/METHODS_BRIEF.md) | English methods / technical brief |
| [`manuscript/SUPPLEMENT.md`](../../manuscript/SUPPLEMENT.md) | Embeds main Fig 1–5 + supplement Fig S1–S9 + Tables 1–8 from `paper_artifacts/` |

```bash
make paper-artifacts   # refresh figures/tables first
```

## What changed in this elevation

1. **Framing:** assumption-gated *decision theory* (explicit risk \(L\)), not a sample-size calculator ([ELEVATED_FRAMING.md](ELEVATED_FRAMING.md)).
2. **Figures:** no descriptive in-figure titles/suptitles; panel letters only; captions in `paper_artifacts/captions/`.
3. **Tables:** manuscript-ready copies under `tables/manuscript/`; **Table 7** tier-A meta (primary empirical); **Table 8** G1 coverage.
4. **Theory:** P7 (all-positive trap) + P8 (exact vs asymptotic gap); denser P6 grid.
5. **LoQ narrative:** primary **Fig 5** = tier-A radioimmuno; troponin = tier-C demo (Fig S1). Main text uses **5 composite figures** only (`paper_artifacts/captions/FIGURE_PLAN.md`).

## Run packaging

```bash
make paper-artifacts
```

## What a mathematician/statistician would praise

1. Estimand-first design with an explicit loss tying Type I, miss-\(\beta\), parametric mismatch, and design effect.
2. Saturation theorem (P1) + all-positive trap (P7) + exact/asymptotic gap (P8).
3. Separation of asymptotic design surfaces from exact small-sample confirmation.
4. Honest A/B/C/S evidence firewall with tier-A-only meta table.
5. Journal-style figures (captions outside PNGs).

## What they would still attack for a *full* research article

1. Brief exists, but journal Word/LaTeX layout, author list, and full Vancouver references still need hand finishing.
2. Routine clinical chemistry electrolytes/enzymes/hematology **blank–LoD** raw deposits still scarce; multi-lab **precision** now covered by Carobene Lombardy EQA (tier A).
3. No prospective multi-lab **LoD claim verification** study (Carobene is commutability/EQA precision, not EP17 blank design).
4. Decision-risk weights are transparent conventions, not elicited utilities.

## Advice

Use **`manuscript/METHODS_BRIEF.md` + `SUPPLEMENT.md`** as the submission skeleton for a methods / software note. Thicken routine-chemistry blank–LoD evidence before aiming at the top of *Clinical Chemistry* as a full research article.
