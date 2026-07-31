#!/usr/bin/env python3
"""
Fetch open-access PDFs + PubMed metadata for literature screening records.

Usage:
  python literature/scripts/literature_fetch.py --priority core
  python literature/scripts/literature_fetch.py --blocks B2,C,D --max-records 50
  python literature/scripts/literature_fetch.py --pmids 33626838,14764644

Outputs:
  literature/papers/pdfs/{pmid}_{slug}.pdf   (when OA PDF found)
  literature/notes/records/{pmid}.json         (metadata + abstract + download status)
  literature/notes/manifest.json               (run summary)
  literature/notes/READING_INDEX.md            (auto-generated index)

Only downloads legally open-access full text (PMC, Europe PMC, Unpaywall OA links).
Paywalled papers still get metadata + abstract for note-taking.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIT = ROOT / "literature"
SCREENING = LIT / "screening.csv"
PDF_DIR = LIT / "papers" / "pdfs"
NOTES_DIR = LIT / "notes" / "records"
MANIFEST = LIT / "notes" / "manifest.json"
INDEX_MD = LIT / "notes" / "READING_INDEX.md"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EUROPE_PMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UNPAYWALL = "https://api.unpaywall.org/v2"
UA = "Mozilla/5.0 (compatible; lod-guide-literature/1.0; mailto:lod@local.dev)"
EMAIL = "lod_guide@local.dev"
TOOL = "lod_guide_literature"


@dataclass
class Record:
    pmid: str
    doi: str = ""
    title: str = ""
    authors: str = ""
    year: str = ""
    journal: str = ""
    blocks: str = ""
    priority: str = ""
    abstract: str = ""
    pmcid: str = ""
    pdf_path: str = ""
    pdf_source: str = ""
    download_status: str = "pending"  # ok | abstract_only | failed | skipped
    notes: str = ""


def slugify(text: str, max_len: int = 60) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text.lower()).strip("_")
    return s[:max_len] or "paper"


def http_get(url: str, *, timeout: float = 60.0, accept: str | None = None, retries: int = 2) -> bytes:
    headers = {"User-Agent": UA}
    if accept:
        headers["Accept"] = accept
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_err = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise last_err  # type: ignore[misc]


def load_screening(*, priority: str | None, blocks: set[str] | None, pmids: set[str] | None, max_records: int) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    if SCREENING.exists():
        with SCREENING.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                pmid = row.get("pmid") or ""
                if pmids and pmid not in pmids:
                    continue
                if priority and row.get("priority") != priority:
                    continue
                if blocks:
                    row_blocks = set((row.get("blocks") or "").split("|"))
                    if not row_blocks & blocks:
                        continue
                if not pmid:
                    continue
                rows.append(row)
                seen.add(pmid)
    # Allow direct PMID fetch without screening.csv row
    if pmids:
        for pmid in pmids:
            if pmid not in seen:
                rows.append({"pmid": pmid, "blocks": "", "priority": "screen"})
    return rows[:max_records]


def fetch_pubmed_xml(pmids: list[str]) -> dict[str, Record]:
    out: dict[str, Record] = {}
    for i in range(0, len(pmids), 100):
        batch = pmids[i : i + 100]
        q = urllib.parse.urlencode(
            {"db": "pubmed", "id": ",".join(batch), "retmode": "xml", "tool": TOOL, "email": EMAIL}
        )
        raw = http_get(f"{EUTILS}/efetch.fcgi?{q}")
        root = ET.fromstring(raw)
        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID") or ""
            rec = Record(pmid=pmid)
            title_el = article.find(".//ArticleTitle")
            rec.title = "".join(title_el.itertext()).strip() if title_el is not None else ""
            rec.journal = article.findtext(".//Journal/Title") or article.findtext(".//ISOAbbreviation") or ""
            rec.year = (article.findtext(".//PubDate/Year") or article.findtext(".//ArticleDate/Year") or "")[:4]
            authors = []
            for au in article.findall(".//Author"):
                last = au.findtext("LastName") or ""
                fore = au.findtext("ForeName") or au.findtext("Initials") or ""
                if last:
                    authors.append(f"{last} {fore}".strip())
            rec.authors = "; ".join(authors[:8])
            parts = [p.text for p in article.findall(".//Abstract/AbstractText") if p.text]
            rec.abstract = " ".join(parts).strip()
            for eid in article.findall(".//ArticleId"):
                if eid.get("IdType") == "doi":
                    rec.doi = (eid.text or "").lower()
            out[pmid] = rec
        time.sleep(0.34)
    return out


def elink_pmc(pmids: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for pmid in pmids:
        q = urllib.parse.urlencode(
            {
                "dbfrom": "pubmed",
                "db": "pmc",
                "id": pmid,
                "retmode": "json",
                "tool": TOOL,
                "email": EMAIL,
            }
        )
        try:
            raw = http_get(f"{EUTILS}/elink.fcgi?{q}")
            data = json.loads(raw)
        except (urllib.error.URLError, json.JSONDecodeError):
            continue
        for linkset in data.get("linksets", []):
            if str(linkset.get("ids", [""])[0]) != pmid:
                continue
            for ldb in linkset.get("linksetdbs", []):
                if ldb.get("dbto") == "pmc" and ldb.get("linkname") == "pubmed_pmc":
                    links = ldb.get("links") or []
                    if links:
                        mapping[pmid] = f"PMC{links[0]}"
        time.sleep(0.2)
    return mapping


def unpaywall_oa(doi: str) -> str | None:
    if not doi:
        return None
    q = urllib.parse.urlencode({"email": EMAIL})
    url = f"{UNPAYWALL}/{urllib.parse.quote(doi)}?{q}"
    try:
        raw = http_get(url, timeout=30.0, accept="application/json")
        data = json.loads(raw)
    except (urllib.error.URLError, json.JSONDecodeError):
        return None
    best = data.get("best_oa_location") or {}
    return best.get("url_for_pdf") or best.get("url")


def europe_pmc_pdf(pmid: str) -> str | None:
    q = urllib.parse.urlencode({"query": f"EXT_ID:{pmid}", "format": "json", "resultType": "core"})
    try:
        raw = http_get(f"{EUROPE_PMC}/search?{q}", timeout=25.0, retries=1)
        data = json.loads(raw)
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError):
        return None
    results = data.get("resultList", {}).get("result") or []
    if not results:
        return None
    r0 = results[0]
    if r0.get("isOpenAccess") != "Y":
        return None
    pmcid = r0.get("pmcid")
    if pmcid:
        return f"https://europepmc.org/articles/{pmcid}?pdf=render"
    return None


def pmc_pdf_url(pmcid: str) -> str:
    num = pmcid.replace("PMC", "")
    return f"https://pmc.ncbi.nlm.nih.gov/articles/PMC{num}/pdf/"


def is_pdf(data: bytes) -> bool:
    return data[:4] == b"%PDF"


def download_pdf(url: str, dest: Path) -> bool:
    try:
        data = http_get(url, timeout=90.0)
    except urllib.error.URLError:
        return False
    if not is_pdf(data):
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return dest.stat().st_size > 1000


def extract_pdf_text(pdf_path: Path) -> str:
    if shutil.which("pdftotext"):
        proc = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    return ""


def pdf_matches_record(rec: Record, pdf_path: Path) -> bool:
    """Reject OA mislinks (e.g. wrong publisher PDF for PMID)."""
    text = extract_pdf_text(pdf_path)[:8000].lower()
    if not text:
        return True
    if rec.doi and rec.doi.lower().replace("https://doi.org/", "") in text.replace(" ", ""):
        return True
    title_tokens = [t for t in re.split(r"[^a-z0-9]+", rec.title.lower()) if len(t) > 4]
    hits = sum(1 for t in title_tokens[:8] if t in text)
    if title_tokens and hits < max(2, len(title_tokens[:4]) // 2):
        return False
    # Author check when PubMed author list is trustworthy
    if rec.authors:
        last = rec.authors.split(";")[0].split()[-1].lower()
        if len(last) > 2 and last not in text:
            return False
    return True


def try_download(rec: Record) -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    dest = PDF_DIR / f"{rec.pmid}_{slugify(rec.title)}.pdf"

    # Existing full_text_path in screening
    if rec.notes.startswith("existing:"):
        existing = Path(rec.notes.replace("existing:", ""))
        if existing.exists() and is_pdf(existing.read_bytes()):
            if not dest.exists():
                shutil.copy2(existing, dest)
            rec.pdf_path = str(dest.relative_to(ROOT))
            rec.pdf_source = "screening_csv"
            rec.download_status = "ok"
            return

    candidates: list[tuple[str, str]] = []
    if rec.pmcid:
        candidates.append(("pmc", pmc_pdf_url(rec.pmcid)))
        candidates.append(("europe_pmc", f"https://europepmc.org/articles/{rec.pmcid}?pdf=render"))
    candidates.append(("europe_pmc_search", ""))  # filled below
    oa = unpaywall_oa(rec.doi)
    if oa:
        candidates.append(("unpaywall", oa))

    ep = europe_pmc_pdf(rec.pmid)
    if ep:
        candidates.append(("europe_pmc_pmid", ep))

    if dest.exists() and dest.stat().st_size > 1000:
        if pdf_matches_record(rec, dest):
            rec.pdf_path = str(dest.relative_to(ROOT))
            rec.pdf_source = "cached"
            rec.download_status = "ok"
            return
        dest.unlink(missing_ok=True)

    for source, url in candidates:
        if not url:
            continue
        if download_pdf(url, dest):
            if pdf_matches_record(rec, dest):
                rec.pdf_path = str(dest.relative_to(ROOT))
                rec.pdf_source = source
                rec.download_status = "ok"
                return
            dest.unlink(missing_ok=True)
        time.sleep(0.2)

    rec.download_status = "abstract_only" if rec.abstract else "failed"


def merge_screening(row: dict, rec: Record) -> Record:
    rec.doi = rec.doi or (row.get("doi") or "")
    rec.title = rec.title or (row.get("title") or "")
    rec.authors = rec.authors or (row.get("authors") or "")
    rec.year = rec.year or (row.get("year") or "")
    rec.journal = rec.journal or (row.get("journal") or "")
    rec.blocks = row.get("blocks") or ""
    rec.priority = row.get("priority") or ""
    ftp = (row.get("full_text_path") or "").strip()
    if ftp and Path(ROOT / ftp).exists():
        rec.notes = f"existing:{ROOT / ftp}"
    return rec


def write_index(records: list[Record]) -> None:
    lines = [
        "# Literature reading index (auto-generated)",
        "",
        "Run: `python literature/scripts/literature_fetch.py --priority core`",
        "",
        "| PMID | Priority | PDF | Title | Blocks |",
        "|------|----------|-----|-------|--------|",
    ]
    for r in sorted(records, key=lambda x: (x.priority != "core", x.pmid)):
        pdf = "yes" if r.download_status == "ok" else "abstract only"
        title = (r.title[:70] + "…") if len(r.title) > 70 else r.title
        lines.append(f"| [{r.pmid}](records/{r.pmid}.json) | {r.priority} | {pdf} | {title} | {r.blocks} |")
    INDEX_MD.parent.mkdir(parents=True, exist_ok=True)
    INDEX_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Fetch OA PDFs and PubMed metadata for literature screening.")
    p.add_argument("--priority", choices=["core", "standard", "screen"], help="Filter screening.csv priority")
    p.add_argument("--blocks", help="Comma-separated blocks e.g. B2,C,D")
    p.add_argument("--pmids", help="Comma-separated PMIDs (overrides filters)")
    p.add_argument("--max-records", type=int, default=200)
    p.add_argument("--include-block-nbib", action="store_true", help="Also parse PMIDs from endnote/blocks/*.nbib")
    args = p.parse_args(argv)

    pmids: set[str] | None = None
    if args.pmids:
        pmids = {x.strip() for x in args.pmids.split(",") if x.strip()}

    blocks: set[str] | None = None
    if args.blocks:
        blocks = {x.strip() for x in args.blocks.split(",") if x.strip()}

    rows = load_screening(priority=args.priority, blocks=blocks, pmids=pmids, max_records=args.max_records)

    if args.include_block_nbib and blocks:
        nbib_dir = LIT / "endnote" / "blocks"
        for b in blocks:
            nbib = nbib_dir / f"block_{b}.nbib"
            if nbib.exists():
                text = nbib.read_text(encoding="utf-8", errors="replace")
                for m in re.finditer(r"^PMID- (\d+)", text, re.M):
                    if not rows and pmids is None:
                        rows.append({"pmid": m.group(1), "blocks": b, "priority": "screen"})
                    elif any(r.get("pmid") == m.group(1) for r in rows):
                        continue
                    else:
                        rows.append({"pmid": m.group(1), "blocks": b, "priority": "screen"})
        rows = rows[: args.max_records]

    if not rows:
        print("No records matched filters.", file=sys.stderr)
        return 1

    pmid_list = [r["pmid"] for r in rows]
    print(f"Fetching metadata for {len(pmid_list)} PMIDs…")

    meta = fetch_pubmed_xml(pmid_list)
    pmc_map = elink_pmc(pmid_list)

    records: list[Record] = []
    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    for row in rows:
        pmid = row["pmid"]
        rec = meta.get(pmid, Record(pmid=pmid))
        rec = merge_screening(row, rec)
        rec.pmcid = pmc_map.get(pmid, "")
        try:
            try_download(rec)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            rec.download_status = "abstract_only" if rec.abstract else "failed"
            rec.notes = f"download_error:{exc}"

        pdf_text = ""
        if rec.pdf_path:
            pdf_text = extract_pdf_text(ROOT / rec.pdf_path)

        payload = asdict(rec)
        payload["pdf_text_chars"] = len(pdf_text)
        payload["pdf_text_preview"] = pdf_text[:4000] if pdf_text else ""
        out_json = NOTES_DIR / f"{pmid}.json"
        out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        records.append(rec)
        status = rec.download_status
        print(f"  {pmid}: {status}  {rec.title[:60]}…" if len(rec.title) > 60 else f"  {pmid}: {status}  {rec.title}")
        time.sleep(0.25)

    summary = {
        "fetched": len(records),
        "pdf_ok": sum(1 for r in records if r.download_status == "ok"),
        "abstract_only": sum(1 for r in records if r.download_status == "abstract_only"),
        "failed": sum(1 for r in records if r.download_status == "failed"),
        "pmids": [r.pmid for r in records],
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_index(records)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
