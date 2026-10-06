# lod-guide

Claim-specific sample-size planning for binary hit-rate LoD verification. Python package `lod_guide` plus the Clinical Chemistry ScholarOne bundle.

## Install

```bash
pip install -e ".[dev]"
PYTHONPATH=src pytest -q
```

Requires Python 3.10+.

## Regenerating main figures

```bash
PYTHONPATH=src python -m lod_guide.paper.main_figures
```

TIFF copies for upload live in `manuscript/figures/` (600 dpi, RGB).

## ScholarOne package

Assembled files are in `manuscript/`:

| File | Role |
|------|------|
| `Cover_letter.docx` | Cover letter |
| `Clinical_Chemistry_submission.docx` | Main text |
| `figures/Fig1_lod_replicate_planning.tif` | Figure 1 |
| `figures/Fig2_tierA_calibration.tif` | Figure 2 |
| `Figure_legends.docx` | Legends |
| `Tables_main.docx` | Tables 1–3 |
| `Online_Supplement.pdf` | Supplement |

Rebuild the Word bundle:

```bash
PYTHONPATH=src python scripts/assemble_manuscript_submission.py
```

Sources for that assemble step are under `submission/`.

## What the analysis is

Exact Fisher operating characteristics on a 1,225-cell equally spaced hit-rate lattice (50–99%), not a survey of laboratory lot differences. `n*` is a function of Δp. The 90%/80% pair is a worked example (`n*≈199` per arm), not a default for every protocol. Missing two-arm rates in the convenience audit are scored at that assigned pair.

## One-click research run

```bash
chmod +x run.sh
./run.sh --quick
```
