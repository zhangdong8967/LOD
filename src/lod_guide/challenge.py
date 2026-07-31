"""
Challenge manifesto: why a new LoD guidance algorithm is needed.

Locked strategic stance (do not weaken in downstream wording):
  complement and operationalize EP17-class documents;
  challenge practice myths and underspecified local SOPs;
  do NOT claim to supersede EP17 (or YY/WS/IFU) as a legal/standards document.
"""

from __future__ import annotations

CHALLENGE_CLAIMS: list[dict[str, str]] = [
    {
        "id": "C1",
        "target": "Folklore fixed n=20 (or 60) for all LoD questions",
        "problem": (
            "Sample size is estimand-dependent. Comparing 90% vs 80% detection "
            "rates needs ~199 replicates/arm for 80% power; n=20 yields ~14% power."
        ),
        "algorithm_response": "S0 locks goal G1–G4; S5 returns powered/precision-based n.",
    },
    {
        "id": "C2",
        "target": "Always-parametric normal LoB (mean + k·SD)",
        "problem": (
            "Near-LoD blanks are often skewed, censored, or batch-heterogeneous; "
            "parametric LoB then miscalibrates LoD."
        ),
        "algorithm_response": "S2 diagnostics + S3 correction gate; hard-stop to S4b nonparametric.",
    },
    {
        "id": "C3",
        "target": "Pooling across days/lots/operators without checking poolability",
        "problem": "High ICC makes a single pooled LoD non-transportable.",
        "algorithm_response": "S2 ICC/Levene/between-stratum CV; S5 design-effect inflation.",
    },
    {
        "id": "C4",
        "target": "Using 1-(1-p)^n to compare reagents",
        "problem": "Metric saturates near 1 for both p=0.9 and p=0.8; differences vanish.",
        "algorithm_response": "G2 uses observed rates hat{p} and two-proportion power only.",
    },
    {
        "id": "C5",
        "target": "One protocol for binary, continuous, count, and multiclass assays",
        "problem": "Result types imply different single-trial models and success events.",
        "algorithm_response": "S1 type routing; diverse real + simulated benchmark catalogue.",
    },
]

# Locked one-sentence product intent (blueprint).
POSITIONING_STATEMENT = (
    "lod_guide is an assumption-gated, estimand-specific sample-size framework for "
    "clinical LoD verification (detection-limit claims G1/G2/G4): it plans replicate "
    "number and confirmation tests inside EP17-class workflows, complements consensus "
    "documents, challenges folklore SOPs (fixed n, saturated comparative metrics), and "
    "does not claim to supersede EP17 / YY / WS / manufacturer IFU as legal standards. "
    "LoB and LoQ modules are optional EP17 branches, not the research focus."
)

RELATION_TO_STANDARDS = (
    "Align with EP17-A2 LoB/LoD/LoQ vocabulary and dual parametric/nonparametric spirit; "
    "strengthen EP17’s statement that one protocol cannot fit all measurands into an "
    "executable S0–S7 decision tree with sample-size consequences; challenge practice "
    "myths with power tables and diagnostics—not the standards text itself."
)

CLAIMS_WE_MAY_MAKE: tuple[str, ...] = (
    "Verification n from tradition is often inadequate for comparative LoD claims.",
    "Distributional diagnostics should precede parametric LoB.",
    "Saturated hit metrics can erase reagent differences.",
    "Heterogeneity is a design factor, not only noise to pool away.",
    "Algorithm output can serve as a statistical appendix for verification narratives.",
)

CLAIMS_WE_DO_NOT_MAKE: tuple[str, ...] = (
    "That EP17 is wrong and must be replaced.",
    "That one new n replaces all EP17 study designs.",
    "That clinical reporting cutoffs can be changed by this algorithm alone without method-validation governance.",
    "That this package is a competing legal standard number.",
)


def manifesto_markdown() -> str:
    lines = [
        "# Challenging Folklore LoD Evaluation",
        "",
        POSITIONING_STATEMENT,
        "",
        "## Relation to standards (locked)",
        "",
        RELATION_TO_STANDARDS,
        "",
        "## What we may challenge",
        "",
    ]
    for c in CLAIMS_WE_MAY_MAKE:
        lines.append(f"- {c}")
    lines += ["", "## What we do not claim", ""]
    for c in CLAIMS_WE_DO_NOT_MAKE:
        lines.append(f"- {c}")
    lines += ["", "## Practice-myth claims (C1–C5)", ""]
    for c in CHALLENGE_CLAIMS:
        lines += [
            f"### {c['id']}. {c['target']}",
            "",
            f"**Problem.** {c['problem']}",
            "",
            f"**Algorithm response.** {c['algorithm_response']}",
            "",
        ]
    return "\n".join(lines)
