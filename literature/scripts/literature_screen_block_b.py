#!/usr/bin/env python3
"""
Relevance screen for Block B (LoD sample size / verification) PubMed hits.

Reads PMIDs from endnote/blocks/block_B.nbib, scores clinical-lab relevance,
exports top records for fetch + close reading.

Usage:
  python literature/scripts/literature_screen_block_b.py
  python literature/scripts/literature_screen_block_b.py --top 15 --fetch
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIT = ROOT / "literature"
NBIB = LIT / "endnote" / "blocks" / "block_B.nbib"
OUT_CSV = LIT / "screening_block_B.csv"
OUT_MD = LIT / "notes" / "deep" / "BLOCK_B_READING_NOTES.md"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EMAIL = "lod_guide@local.dev"
TOOL = "lod_guide_literature"

# Positive signals (clinical / IVD / sample-size for LoD)
POSITIVE = [
    (r"\bclinical (lab|laboratory|chemistry)\b", 4),
    (r"\b(in vitro diagnostic|ivd|immunoassay|elisa)\b", 3),
    (r"\b(qpcr|pcr|molecular diagnos|digital pcr|nat\b)", 3),
    (r"\b(EP17|CLSI|detection capability)\b", 5),
    (r"\b(verification|validate|validation)\b", 2),
    (r"\b(sample size|power analysis|statistical power|replicate)\b", 3),
    (r"\b(two proportion|binomial|hit rate|detection rate|positive rate)\b", 4),
    (r"\b(limit of detection|limit of blank|LoD|LoB|LoQ)\b", 3),
    (r"\b(probit|logistic regression|dose.response)\b", 2),
    (r"\b(troponin|cardiac|hematology|proteomics|mass spectromet)\b", 2),
    (r"\b(Kondratovich|Linnet|Armbruster|EP17)\b", 6),
]

# Negative signals (exclude analytical-chemistry noise)
NEGATIVE = [
    (r"\b(environmental|soil|water sample|river|groundwater|wastewater)\b", -4),
    (r"\b(sensor|hydrogen|gas chromatograph|hplc method for pesticide)\b", -3),
    (r"\b(cancer therapy|drug delivery|nanoparticle synthesis)\b", -3),
    (r"\b(ovulation|fertility|pregnancy outcome)\b", -5),
    (r"\b(Salmonella|food safety|agricultural)\b", -2),
    (r"\b(machine learning classifier|deep learning detection)\b", -2),
    (r"\b(fiber.optic|microcantilever)\b", -6),
]


def parse_pmids(nbib: Path) -> list[str]:
    text = nbib.read_text(encoding="utf-8", errors="replace")
    return list(dict.fromkeys(re.findall(r"^PMID- (\d+)", text, re.M)))


def fetch_pubmed_batch(pmids: list[str]) -> list[dict]:
    records = []
    for i in range(0, len(pmids), 100):
        batch = pmids[i : i + 100]
        q = urllib.parse.urlencode(
            {"db": "pubmed", "id": ",".join(batch), "retmode": "xml", "tool": TOOL, "email": EMAIL}
        )
        with urllib.request.urlopen(f"{EUTILS}/efetch.fcgi?{q}", timeout=90) as resp:
            root = ET.fromstring(resp.read())
        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID") or ""
            title_el = article.find(".//ArticleTitle")
            title = "".join(title_el.itertext()).strip() if title_el is not None else ""
            journal = article.findtext(".//Journal/Title") or article.findtext(".//ISOAbbreviation") or ""
            year = (article.findtext(".//PubDate/Year") or "")[:4]
            authors = []
            for au in article.findall(".//Author")[:4]:
                last = au.findtext("LastName") or ""
                if last:
                    authors.append(last)
            parts = [p.text for p in article.findall(".//Abstract/AbstractText") if p.text]
            abstract = " ".join(parts).strip()
            doi = ""
            for eid in article.findall(".//ArticleId"):
                if eid.get("IdType") == "doi":
                    doi = (eid.text or "").lower()
            records.append(
                {
                    "pmid": pmid,
                    "doi": doi,
                    "title": title,
                    "authors": "; ".join(authors),
                    "year": year,
                    "journal": journal,
                    "abstract": abstract,
                }
            )
        time.sleep(0.35)
    return records


def score_record(rec: dict) -> tuple[int, list[str]]:
    blob = f"{rec['title']} {rec['abstract']} {rec['journal']}".lower()
    score = 0
    reasons: list[str] = []
    for pat, pts in POSITIVE:
        if re.search(pat, blob, re.I):
            score += pts
            reasons.append(f"+{pts}:{pat}")
    for pat, pts in NEGATIVE:
        if re.search(pat, blob, re.I):
            score += pts
            reasons.append(f"{pts}:{pat}")
    # Boost known core / B2
    if rec["pmid"] in {"33626838", "14764644", "18852857"}:
        score += 20
    return score, reasons


def classify(score: int) -> str:
    if score >= 12:
        return "include"
    if score >= 6:
        return "maybe"
    return "exclude"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--top", type=int, default=15, help="Top N for deep reading")
    p.add_argument("--fetch", action="store_true", help="Run literature_fetch on top N PMIDs")
    args = p.parse_args()

    pmids = parse_pmids(NBIB)
    print(f"Block B: {len(pmids)} PMIDs in {NBIB.name}")

    records = fetch_pubmed_batch(pmids)
    scored = []
    for rec in records:
        s, reasons = score_record(rec)
        scored.append({**rec, "score": s, "verdict": classify(s), "score_reasons": "|".join(reasons[:8])})

    scored.sort(key=lambda r: (-r["score"], r["year"]), reverse=False)

    # Write full screen CSV
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "rank",
                "pmid",
                "score",
                "verdict",
                "year",
                "title",
                "journal",
                "doi",
                "authors",
                "score_reasons",
                "abstract",
            ],
        )
        w.writeheader()
        for i, r in enumerate(scored, 1):
            w.writerow(
                {
                    "rank": i,
                    "pmid": r["pmid"],
                    "score": r["score"],
                    "verdict": r["verdict"],
                    "year": r["year"],
                    "title": r["title"],
                    "journal": r["journal"],
                    "doi": r["doi"],
                    "authors": r["authors"],
                    "score_reasons": r["score_reasons"],
                    "abstract": r["abstract"][:500],
                }
            )

    top = [r for r in scored if r["verdict"] != "exclude"][: args.top]
    if len(top) < args.top:
        top = scored[: args.top]

    # Write reading notes markdown
    lines = [
        "# Block B — sample size / verification (screened top {})".format(len(top)),
        "",
        f"Source: `{NBIB.relative_to(ROOT)}` ({len(pmids)} PubMed hits). "
        f"Full screen: `{OUT_CSV.relative_to(ROOT)}`.",
        "",
        "| Rank | Score | PMID | Verdict | Title |",
        "|------|-------|------|---------|-------|",
    ]
    for i, r in enumerate(top, 1):
        t = (r["title"][:55] + "…") if len(r["title"]) > 55 else r["title"]
        lines.append(f"| {i} | {r['score']} | {r['pmid']} | {r['verdict']} | {t} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, r in enumerate(top, 1):
        lines.extend(
            [
                f"## B-{i}. PMID {r['pmid']} (score {r['score']}, {r['verdict']})",
                "",
                f"**{r['authors']}. {r['title']} *{r['journal']}*. {r['year']}.**"
                + (f" doi:{r['doi']}" if r["doi"] else "")
                + "\n",
            ]
        )
        # Heuristic reading bullets
        ab = r["abstract"]
        if ab:
            lines.append("**Takeaway (abstract):**")
            for sent in ab.replace("\n", " ").split(". ")[:4]:
                if sent.strip():
                    lines.append(f"- {sent.strip()}.")
            lines.append("")
        lines.append("**Manuscript hook:**")
        if r["pmid"] in {"33626838", "14764644"}:
            lines.append("- Core prior art — verification probability / nonparametric LoD (see CORE_READING_NOTES).")
        elif re.search(r"sample size|power|replicate", ab, re.I):
            lines.append("- Supports C1/G2: sample size or power explicit for LoD context.")
        elif re.search(r"verification|validate", ab, re.I):
            lines.append("- EP17-style verification case study; cite for practice not powered comparison.")
        else:
            lines.append("- Context-dependent; verify full text before citing.")
        lines.append("")
        lines.append("---")
        lines.append("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "total": len(scored),
        "include": sum(1 for r in scored if r["verdict"] == "include"),
        "maybe": sum(1 for r in scored if r["verdict"] == "maybe"),
        "exclude": sum(1 for r in scored if r["verdict"] == "exclude"),
        "top_pmids": [r["pmid"] for r in top],
    }
    print(json.dumps(summary, indent=2))
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")

    if args.fetch and top:
        import subprocess

        pmid_arg = ",".join(r["pmid"] for r in top)
        subprocess.run(
            [sys.executable, str(LIT / "scripts" / "literature_fetch.py"), "--pmids", pmid_arg],
            check=False,
            cwd=ROOT,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
