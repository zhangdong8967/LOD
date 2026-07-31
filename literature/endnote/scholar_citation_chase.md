# Google Scholar citation chase (manual → EndNote)

Use Scholar **only** for forward/backward chaining PubMed misses. English sources only.

---

## Seed papers (run “Cited by” and “Related articles”)

| Seed | Scholar query | Target |
|------|---------------|--------|
| Linnet & Kondratovich 2004 | `10.1373/clinchem.2003.029983` | Nonparametric LoD; sample size |
| Kondratovich & Linnet JALM | `10.1373/jalm.2016.020735` | EP17 verification probability; n=20 |
| Galitzine 2018 MCP | `10.1074/mcp.RA117.000322` | MSstatsLOBD; proteomics LoB/LoD |
| Armbruster & Pry 2008 | `PMC2556583` or title | Introductory LoB/LoD/LoQ |
| CLSI EP17-A2 | `"Evaluation of Detection Capability" EP17` | Grey lit citing the standard |

---

## Scholar boolean searches (paste in search box)

**Software / EP17 calculators (Block J):**

```
"detection capability" EP17 (software OR Excel OR "Analyse-it" OR "R package")
```

**Two-proportion LoD comparison (gap literature):**

```
"limit of detection" ("two proportion" OR "sample size" OR power) clinical
```

**Probit LoD design:**

```
probit "limit of detection" concentration immunoassay OR molecular
```

**Digital PCR LoD verification:**

```
"digital PCR" "limit of detection" verification replicates
```

---

## Import into EndNote from Scholar

1. Click **Cite** → **EndNote** (`.enw`) if available; else **BibTeX** → convert or use DOI paste.
2. Prefer records with a **DOI** → in EndNote: `Reference` → `Find Reference Updates`.
3. De-duplicate against PubMed import (PMID/DOI).
4. Set Research Notes: `Scholar; Block-X; chase from [seed DOI]`.

---

## Expected high-value Scholar-only items (check manually)

- Fleiss JL — *Statistical Methods for Rates and Proportions* (book; add as Book Section in EndNote)
- Chow SC — *Sample Size Calculations in Clinical Research* (book)
- Agresti — *Categorical Data Analysis* (Fisher/Boschloo chapters)
- Analyse-it EP17 validation white papers (web page → `Electronic Article`)
- Bioconductor MSstatsLOBD vignette (cite Galitzine 2018 + package URL)

---

## Do not import as peer-reviewed evidence

- Manufacturer IFU PDFs (Abbott, Roche, etc.) — folklore context only
- Blog posts / SEO “CLSI EP17 explained” pages
- Non-English theses
