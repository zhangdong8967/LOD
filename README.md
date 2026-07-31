# LoD Laboratory Guidance Algorithm

**Target:** *Clinical Chemistry*–grade methodology.  
**Locked stance:** Complement and operationalize EP17-class documents; challenge folklore SOPs; **do not** supersede EP17 as a legal/standards document.

**Thesis:** Estimand-gated, assumption-gated LoD **design** is the missing operational layer above LoB/LoD/LoQ vocabulary—making underpowered folklore verification scientifically indefensible without inventing a competing legal LoD definition.

## Theoretical core

| Document | Content |
|----------|---------|
| [manuscript/THEORY_MONOGRAPH.md](manuscript/THEORY_MONOGRAPH.md) | **Three-layer theory (A/B/C):** P1–P18 theorems, bounds, certificates |
| [docs/methodology/CLINICAL_CHEMISTRY_THEORY.md](docs/methodology/CLINICAL_CHEMISTRY_THEORY.md) | Estimands, Propositions P1–P8 with proofs, decision map |
| [docs/methodology/ANALYSIS_PROTOCOL.md](docs/methodology/ANALYSIS_PROTOCOL.md) | Pre-specified confirmatory protocol `LOD-GUIDE-CC-2026-v1` |
| [docs/methodology/CHALLENGE_MANIFESTO.md](docs/methodology/CHALLENGE_MANIFESTO.md) | Challenge claims C1–C5 |

Machine-checkable certificates live in `lod_guide.theory` (three layers under `theory/theorems/`, `theory/bounds/`, `theory/certificates/`).

## One-click run (recommended)

```bash
chmod +x run.sh    # first time only
./run.sh           # full: theory + research + tests + paper + Fig1 TikZ + theory PDF
./run.sh --quick   # skip download, benchmark, paper build
make run           # same as ./run.sh
```

Master log: `data/audit/run_all_analyses_latest.json`.  
Layout map: [`docs/PROJECT_LAYOUT.md`](docs/PROJECT_LAYOUT.md) · generated outputs: [`outputs/README.md`](outputs/README.md).

### Sample-split LoB in S0–S7 pipeline (P17)

```python
from lod_guide import run_guidance
from lod_guide.s4_gated_lob import LoBEstimationMode

run_guidance(
    goal="G1_VERIFY_LOD",
    result_type="continuous",
    values=blank_array,
    lob_estimation_mode=LoBEstimationMode.GATED_SAMPLE_SPLIT,
)
```

Modes: `standard` | `gated_unsplit` | `gated_sample_split`.

Theory only:

```bash
python examples/run_theory_verification.py
```

## Install

```bash
pip install -e ".[dev]"
```

## Clinical scenarios (lab needs → scripts)

See [docs/methodology/CLINICAL_SCENARIOS.md](docs/methodology/CLINICAL_SCENARIOS.md).

```bash
python examples/run_clinical_scenarios.py          # catalogue + all demos
python examples/scenarios/cs01_verify_single_hitrate.py
python examples/scenarios/cs05_compare_kits_90_vs_80.py
python examples/scenarios/cs08_miss_probability_audit.py
```

**Covered core needs:** single-reagent LoD verify (CS01–CS04), kit/lot comparison including 90↔80 / 90↔50 and miss-β (CS05–CS08), molecular qPCR (CS10), skew gate (CS14).  
**Partial:** LoQ profile (CS09), hematology (CS11), multiclass (CS13).

## What must convince a statistician

1. **Estimand locked before formula** (G1–G4).  
2. **Proofs** for saturation, binomial identity, Fleiss–Chow operating characteristics, design effect, parametric LoB mismatch.  
3. **Diagnostics gate** with versioned thresholds before parametric LoB.  
4. **Audit JSON + SHA-256** for every confirmatory run.  
5. **Diverse evidence:** multi-assay public ladder (qPCR, EP17 immunoassay/probit, IC) + audited stress DGPs + exact Fisher/Boschloo layer — see docs/methodology/EVIDENCE_LADDER.md.

## Paper artifacts (figures / tables / review)

```bash
make paper-artifacts
```

Writes `paper_artifacts/` with manuscript **Fig 1–5** + supplement **Fig S1–S9**, Table 1–8, captions, and internal review.

Project layout (source vs generated, cleanup): [`docs/PROJECT_LAYOUT.md`](docs/PROJECT_LAYOUT.md).

**Methods brief + Supplement (embeds those artifacts):**

- [`manuscript/METHODS_BRIEF.md`](manuscript/METHODS_BRIEF.md)
- [`manuscript/SUPPLEMENT.md`](manuscript/SUPPLEMENT.md)

See [docs/methodology/PUBLICATION_READINESS.md](docs/methodology/PUBLICATION_READINESS.md) and [docs/methodology/RESEARCH_STATUS.md](docs/methodology/RESEARCH_STATUS.md) §6.

## Package map

```
src/lod_guide/
  theory/     estimands, propositions, audit, exact intervals
  s0…s7       guidance algorithm
  data/       real download + simulate + catalogue
  pipeline.py figures.py challenge.py
```
