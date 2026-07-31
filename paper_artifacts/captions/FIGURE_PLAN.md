# Figure plan (unified main vs supplement)

## Main text — 5 figures only

| Fig | Role | Panels |
|-----|------|--------|
| **Fig 1** | S0–S7 workflow + P17 branch | single map |
| **Fig 2** | Why folklore fails | A: all-positive; B: G2 miss@20; C: saturation |
| **Fig 3** | Finite-sample theory | A: power gap; B: Fisher heatmap @ n=20; C: Pareto |
| **Fig 4** | Remedies | A: powered n*; B: exact power folklore vs n*; C: design SE |
| **Fig 5** | Tier-A LoD anchor | A: qPCR hit rate; B: n ratio; C: deposit vs n; D: G1/G2/G4 n |

## Supplement — module detail

| Fig | Replaces / expands |
|-----|---------------------|
| S-LoB | P17 LoB sample-split (continuous EP17 path) |
| S1 | Troponin LoQ demo (tier C) |
| S2 | Full power-vs-n curves (old Fig 2) |
| S3 | Full miss-β curves (old Fig 3) |
| S4 | All-positive standalone (old Fig 4) |
| S5 | Continuous n* 3-panel (old Fig 5–6) |
| S6 | Concentration r=c/LoD (old Fig 6) |
| S7 | Evidence landscape (old Fig 7) |
| S8 | Challenge bar chart |
| S9 | Full design SE 2-panel (old Fig 9) |

Build: `make paper-artifacts` → `paper.main_figures.generate_main_figures()` first.
