#!/usr/bin/env python3
"""
Build structured close-reading notes from literature/notes/records/*.json.

Usage:
  python literature/scripts/literature_summarize.py --priority core
  python literature/scripts/literature_summarize.py --pmids 33626838,14764644

Writes:
  literature/notes/deep/CORE_READING_NOTES.md   (core + standard)
  literature/notes/deep/BLOCK_{block}_NOTES.md  (when --blocks used)
"""

from __future__ import annotations

import argparse
import csv
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIT = ROOT / "literature"
RECORDS = LIT / "notes" / "records"
DEEP = LIT / "notes" / "deep"
SCREENING = LIT / "screening.csv"

# Manuscript hooks keyed by block
BLOCK_HOOKS = {
    "A": "Standards framing (EP17 LoB/LoD/LoQ vocabulary)",
    "A2": "Introductory LoB/LoD/LoQ review for clinicians",
    "B": "Sample size / verification power (E2, C1, P8)",
    "B2": "Linnet/Kondratovich EP17 verification probability",
    "C": "Nonparametric LoB, skew, censoring (S2–S4, P5)",
    "D": "Probit/logistic hit-rate LoD design",
    "E": "LoQ / precision profile (LoQ, EP05)",
    "F": "Exact binomial confirmation (Fisher/Boschloo)",
    "G": "Estimands in diagnostics (ICH E9(R1) alignment)",
    "H": "Molecular / qPCR LoD verification",
    "I": "Proteomics MS LoB/LoD (MSstatsLOBD)",
}


def load_records(*, priority: str | None, pmids: set[str] | None, blocks: set[str] | None) -> list[dict]:
    screening = {}
    with SCREENING.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            screening[row.get("pmid", "")] = row

    out = []
    for path in sorted(RECORDS.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        pmid = data.get("pmid", path.stem)
        scr = screening.get(pmid, {})
        if pmids and pmid not in pmids:
            continue
        pr = scr.get("priority") or data.get("priority") or ""
        if priority and pr != priority:
            continue
        bl = scr.get("blocks") or data.get("blocks") or ""
        if blocks and not (set(bl.split("|")) & blocks):
            continue
        data["_screening"] = scr
        out.append(data)
    return out


def cite_line(r: dict) -> str:
    authors = r.get("authors") or "Unknown"
    year = r.get("year") or "n.d."
    title = r.get("title") or "Untitled"
    journal = r.get("journal") or ""
    doi = r.get("doi") or ""
    pmid = r.get("pmid") or ""
    parts = [f"{authors}. {title}. *{journal}*. {year}."]
    if doi:
        parts.append(f"doi:{doi}")
    if pmid:
        parts.append(f"PMID:{pmid}")
    return " ".join(parts)


def extract_bullets(abstract: str, pdf_preview: str) -> dict[str, list[str]]:
    """Heuristic extraction from abstract (+ PDF preview if present)."""
    text = (abstract + "\n" + pdf_preview).lower()
    bullets = {
        "problem": [],
        "methods": [],
        "results": [],
        "claims": [],
        "limits": [],
    }
    if not abstract:
        return bullets

    # Split abstract into sentences
    sentences = [s.strip() for s in abstract.replace("\n", " ").split(". ") if s.strip()]

    for s in sentences:
        sl = s.lower()
        if any(k in sl for k in ("background", "objective", "aim", "purpose", "however", "problem")):
            bullets["problem"].append(s.rstrip(".") + ".")
        elif any(k in sl for k in ("method", "procedure", "design", "we developed", "approach")):
            bullets["methods"].append(s.rstrip(".") + ".")
        elif any(k in sl for k in ("result", "found", "showed", "demonstrated", "probability", "power")):
            bullets["results"].append(s.rstrip(".") + ".")
        elif any(k in sl for k in ("conclusion", "recommend", "should", "suggest")):
            bullets["claims"].append(s.rstrip(".") + ".")
        elif any(k in sl for k in ("limit", "caution", "future", "not applicable")):
            bullets["limits"].append(s.rstrip(".") + ".")

    # Fallback: first/last sentences
    if not bullets["problem"] and sentences:
        bullets["problem"].append(sentences[0].rstrip(".") + ".")
    if not bullets["claims"] and len(sentences) > 1:
        bullets["claims"].append(sentences[-1].rstrip(".") + ".")

    return bullets


def lod_guide_hook(r: dict) -> str:
    blocks = (r.get("blocks") or "").split("|")
    hooks = [BLOCK_HOOKS.get(b, "") for b in blocks if b in BLOCK_HOOKS]
    pr = r.get("priority") or ""
    lines = []
    if hooks:
        lines.append("**Manuscript hooks:** " + "; ".join(h for h in hooks if h))
    if pr == "core":
        lines.append(
            "**Use in our paper:** Cite when stating prior art; contrast with "
            "assumption-gated S0–S7 + explicit decision risk L."
        )
    elif pr == "standard":
        lines.append("**Use in our paper:** Standards citation only; we complement, not supersede.")
    return "\n".join(lines)


def render_record(r: dict) -> str:
    pmid = r.get("pmid", "")
    status = r.get("download_status", "")
    pdf = r.get("pdf_path") or "(abstract only)"
    bullets = extract_bullets(r.get("abstract", ""), r.get("pdf_text_preview", ""))

    sections = [
        f"### PMID {pmid} — {r.get('title', '')[:100]}",
        "",
        cite_line(r),
        "",
        f"- **Full text:** {status} → `{pdf}`",
        f"- **Blocks:** {r.get('blocks', '')} | **Priority:** {r.get('priority', '')}",
        "",
        lod_guide_hook(r),
        "",
    ]

    for key, label in [
        ("problem", "Problem / gap"),
        ("methods", "Methods (their approach)"),
        ("results", "Results (quotable)"),
        ("claims", "Authors' conclusions"),
        ("limits", "Limitations / boundaries"),
    ]:
        items = bullets[key]
        if items:
            sections.append(f"**{label}:**")
            for it in items[:4]:
                sections.append(f"- {it}")
            sections.append("")

    if r.get("abstract"):
        sections.extend(["**Abstract (verbatim):**", "", f"> {textwrap.fill(r['abstract'], width=100)}", ""])

    sections.append("---")
    sections.append("")
    return "\n".join(sections)


def write_notes(records: list[dict], out_path: Path, title: str) -> None:
    DEEP.mkdir(parents=True, exist_ok=True)
    header = [
        f"# {title}",
        "",
        "Auto-generated scaffold from PubMed abstracts + OA PDF text previews. "
        "**Verify page numbers and numbers against PDF before citing.**",
        "",
        f"Records: {len(records)} | PDF available: {sum(1 for r in records if r.get('download_status')=='ok')}",
        "",
    ]
    body = [render_record(r) for r in records]
    out_path.write_text("\n".join(header + body), encoding="utf-8")
    print(f"Wrote {out_path}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--priority", choices=["core", "standard", "screen"])
    p.add_argument("--blocks", help="Comma-separated blocks")
    p.add_argument("--pmids", help="Comma-separated PMIDs")
    args = p.parse_args()

    pmids = {x.strip() for x in args.pmids.split(",")} if args.pmids else None
    blocks = {x.strip() for x in args.blocks.split(",")} if args.blocks else None

    records = load_records(priority=args.priority, pmids=pmids, blocks=blocks)
    if not records:
        print("No records found. Run literature_fetch.py first.")
        return 1

    if args.priority == "core" or (pmids and not args.blocks):
        write_notes(records, DEEP / "CORE_READING_NOTES.md", "Core literature — close-reading notes")
    if args.blocks:
        for b in sorted(blocks or []):
            sub = [r for r in records if b in (r.get("blocks") or "")]
            if sub:
                write_notes(sub, DEEP / f"BLOCK_{b}_NOTES.md", f"Block {b} — close-reading notes")
    elif args.priority and args.priority != "core":
        write_notes(records, DEEP / f"{args.priority.upper()}_READING_NOTES.md", f"{args.priority} reading notes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
