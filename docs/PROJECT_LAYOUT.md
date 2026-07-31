# Project layout (LOD)

## Quick start

```bash
./run.sh          # full pipeline
make paper-artifacts   # figures + tables only
make clean-outputs     # remove stale figure aliases
```

## Source vs generated

| Path | Role | Rebuild |
|------|------|---------|
| `src/lod_guide/` | **Source** — S0–S7 pipeline, theory P1–P18, research, paper builders | `pip install -e ".[dev]"` |
| `examples/` | **Source** — Python runners (`run_all_analyses.py`, …) | — |
| `run.sh` | **Source** — **preferred one-click entry** | `./run.sh` |
| `scripts/` | **Source** — fig1-tikz, theory-pdf, clean_outputs | — |
| `tests/` | **Source** — pytest | `make test` |
| `manuscript/` | **Source** — prose, LaTeX, TikZ | `make theory-pdf` |
| `docs/` | **Source** — methodology notes | — |
| `archive/` | **Source** — deprecated legacy scripts | — |
| `outputs/` | **Pointer** — README only; real outputs live in sibling dirs | — |
| `data/raw/` | **Inputs** — downloaded public deposits | `make download` |
| `data/research/` | **Generated** — study JSON/CSV | `./run.sh` or `make deep-research` |
| `data/audit/` | **Generated** — run logs | `./run.sh` |
| `figures/methodology/` | **Generated** — canonical plots (developer IDs) | `python -m lod_guide.paper.main_figures` |
| `paper_artifacts/` | **Generated** — captions, tables, numbered figure copies | `make paper-artifacts` |

## Code layers (logical, not folders)

```
S0–S7 pipeline (s0_goal … s7_sensitivity, pipeline.py)
    ↓
theory/          P1–P18 certificates
    ↓
research/        deep studies → data/research/*.json
    ↓
paper/           Fig 1–5 + Fig S* registry → figures/ + paper_artifacts/
```

## Figure naming

- **Developer ID** (on disk): `Fig1_decision_map.png`, `FigD1_miss_probability_beta.png`, …
- **Manuscript ID** (in paper): `Fig 1` … `Fig 5`, `Fig S1` … `Fig S9`, `Fig S-LoB`
- **Handoff copy**: `paper_artifacts/figures/Fig1_Fig1-decision-map.png` (from `registry.py`)

Only **15 figure sources** are in the manuscript registry; other `FigM*` / `FigC*` files are research module detail (supplement or internal).

## Cleanup

```bash
python scripts/clean_outputs.py          # preview stale aliases
python scripts/clean_outputs.py --apply  # remove aliases + LaTeX noise
make fig1-tikz
python -m lod_guide.paper.main_figures
make paper-artifacts
```

Legacy pre-package scripts: `archive/legacy_scripts/`.
