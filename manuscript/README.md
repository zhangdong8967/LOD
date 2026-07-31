# Manuscript package (methods brief + Supplement)

| File | Role |
|------|------|
| [INTRODUCTION_FULL.md](INTRODUCTION_FULL.md) | **Complete §1 Introduction** (background, **§1.2 conceptual significance**, related work, hazards, contributions) |
| [WORKED_EXAMPLE.md](WORKED_EXAMPLE.md) | **Box 1** — lot comparison at LoD (G2): protocol → estimand → n=20 vs n≈199 |
| [COVER_LETTER.md](COVER_LETTER.md) | **Cover letter draft** — narrow claim, limitations upfront |
| [LOD_RESEARCH_SCOPE.md](../docs/methodology/LOD_RESEARCH_SCOPE.md) | **Scope lock:** LoD replicate planning only; LoB/LoQ out of scope |
| [DISCUSSION_PRIOR_WORK.md](DISCUSSION_PRIOR_WORK.md) | **§4 Discussion** — relation to prior work + **§4.5 broader significance** |
| [INTRO_RELATED_WORK.md](INTRO_RELATED_WORK.md) | Related work appendix + Block B screen metadata |
| [METHODS_BRIEF.md](METHODS_BRIEF.md) | English **methods / technical brief** draft (main text; §1 + §4 synced) |
| [THEORY_MONOGRAPH.md](THEORY_MONOGRAPH.md) | Three-layer theory map (A/B/C) + reproducibility |
| [THEORY_MONOGRAPH.tex](THEORY_MONOGRAPH.tex) | **LaTeX submission draft** (stat.ME / methods journal) |
| [SUPPLEMENT.md](SUPPLEMENT.md) | Online Supplement: **embeds** main Fig 1–5 + supplement Fig S1–S9 and Tables 1–8 from `paper_artifacts/` |

## Rebuild artifacts before submission polish

```bash
make paper-artifacts
```

Compile theory LaTeX:

```bash
make paper-artifacts    # figures first
make theory-pdf         # writes manuscript/THEORY_MONOGRAPH.pdf
```

If `pdflatex` is missing on macOS, install BasicTeX once:

```bash
brew install --cask basictex
eval "$(/usr/libexec/path_helper)"
sudo tlmgr update --self
sudo tlmgr install collection-latexrecommended amsmath booktabs hyperref microtype geometry
make theory-pdf
```

Alternative: start **Docker Desktop**, then `make theory-pdf` (uses `texlive/texlive` image).

Legacy one-liner (after pdflatex is on PATH):

```bash
cd manuscript && pdflatex THEORY_MONOGRAPH.tex && pdflatex THEORY_MONOGRAPH.tex
python examples/run_theory_verification.py
```

## Journal handoff

1. Copy Abstract–Discussion from `METHODS_BRIEF.md` into Word/LaTeX.
2. Insert **main-text** figures from `paper_artifacts/figures/Fig1_Fig1-decision-map.pdf` through `Fig5_Fig5-tierA-lod.pdf` (see [`FIGURE_PLAN.md`](../paper_artifacts/captions/FIGURE_PLAN.md)).
3. Paste or import CSVs from `paper_artifacts/tables/manuscript/`.
4. Attach `SUPPLEMENT.md` (or a PDF export) as Online Supplement.
5. Add author affiliations, COI, full Vancouver references.

## Scope honesty

This package supports a **methods / technical brief** submission path. It is **not** a finished full Clinical Chemistry research article (see `docs/methodology/PUBLICATION_READINESS.md`).
